import logging
import os

import dextra.dna.core as C
import dextra.dna.text as T
import pyspark.sql.functions as F
from pyspark.ml import PipelineModel

from .. import functions


class EncoderMixin:
    @property
    def encoder_weights(self):
        return os.path.join(self.config.lakes.models, 'products', 'word2vec')


class Learn(EncoderMixin,
            T.processors.Refining):
    SAVING_OPTIONS = {'mode': 'append'}

    ENCODER_FN_PARAMS = {
        'input_col': 'text_cleaned',
        'stop_words': 'english',
        'features': 128}

    def call(self, x):
        x = self.select_trusted_step(x)
        _ = self.fit_encoder_step(x)
        s = self.extract_stats_step(x)

        return s
    
    def select_trusted_step(self, x):
        x = x.where(x.tags_trusted_labels & (x.tags_split == 'train'))
        
        logging.info(f'Training Word2Vec encoder over {x.count()} samples.')

        return x

    def fit_encoder_step(self, x):
        with C.utils.stopwatch(mode='silent') as et:
            model = T.models.word2vec(**self.ENCODER_FN_PARAMS)
            model = model.fit(x)
            model.write().overwrite().save(self.encoder_weights)

        self.watches['encoder-training'] = et

        return model

    def extract_stats_step(self, x):
        return x.select(
            *(F.lit(str(v)).alias(k) for k, v in self.training_info().items()),
            F.current_timestamp().alias('trained_at'),

            functions.stats(F.to_timestamp('date_received')).alias('date_received_stats'),
            functions.stats('committed_at').alias('committed_at_stats'),

            F.collect_list(F.struct(
                'complaint_id',
                'committed_at',
            )).alias('records')
        )

    def training_info(self):
        return dict(
            model_name='word2vec',
            model_weights_path=self.encoder_weights,
            training_proc=self.fullname(),
            training=dict(
                model=self.ENCODER_FN_PARAMS,
            ))


class Encode(EncoderMixin,
             T.processors.Refining):

    SAVING_OPTIONS = {'mode': 'overwrite'}

    def call(self, x: F.DataFrame):
        x = x.repartition('product', 'issue')
        x = self.encode_text_with_word2vec_step(x)

        return x

    def encode_text_with_word2vec_step(self, x):
        with C.utils.stopwatch(mode='silent') as et:
            enc = PipelineModel.load(self.encoder_weights)
            x = enc.transform(x)

        self.watches['encode'] = et

        return x
