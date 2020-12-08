import logging

import dextra.dna.text as T
from pyspark.sql import functions as F

from . import mixins
from ..functions import confirming_word_as_bool
from ..utils import remove_if_exists


class Rawing(mixins.InconsistentInputsMixin,
             mixins.BackupInputsMixin,
             T.processors.Rawing):
    """Issues Rawing Processor.

    transient → raw

    Operations:
    - Hash content in sensible columns.
    - Exclude sensible patterns in free text column ``consumer_message``.
    - Adds:
        - ingestion timestamp
        - simulated tag for "trusted issue label"
        - simulated tag for data split (train, test)

    """
    SAVING_OPTIONS = {'mode': 'append'}
    SENSIBLE_COLUMNS = ('complaint_id', 'customer_name')

    def call(self, x: F.DataFrame):
        x = self.encryption_step(x)
        x = self.add_tags_step(x)

        return x

    def encryption_step(self, x: F.DataFrame):
        x = self.hash_sensible_info(x, self.SENSIBLE_COLUMNS)

        patterns = {'numeric': r'\d+', **T.datasets.COMMON_PATTERNS}
        x = self.exclude_sensible_info(x, 'consumer_message', patterns)

        return x

    def add_tags_step(self, x: F.DataFrame):
        return (x.withColumn('ingested_at', F.current_timestamp())
                .withColumn('tags_trusted_labels', F.rand() < .1)
                .withColumn('tags_split', F.when(F.rand() < .5, 'train')
                            .otherwise('test')))


class Trusting(mixins.TearInputsMixin,
               T.processors.Trusting):
    """Issues Trusting Processor.

    raw → trusted

    Discard samples without ``ids`` and remove
    entry duplicates by removing the older ones.

    """
    SAVING_OPTIONS = {'mode': 'append'}

    def call(self, x: F.DataFrame):
        x = x.where(x.complaint_id.isNotNull())
        x = self.discard_duplicates(x, 'complaint_id', 'ingested_at')

        return x


class Refining(mixins.TearInputsMixin,
               T.processors.Refining):
    """Issues Refining Processor.

    trusted → refined

    Operations:
      - Parse textual columns into they meaningful types -- examples:
        - 'yes'       → True
        - '9/12/2020' → datetime(...)
      - Clean customer complaints in order to match keywords/apply ML models
      - Add committing info tags
      - Sort data by ``id``, improving reading performance

    """
    SAVING_OPTIONS = {'mode': 'append'}

    def call(self, x: F.DataFrame):
        x = self.parse_textual_cols_step(x)
        x = self.clean_text_step(x)

        x = x.orderBy('complaint_id')

        return x

    def parse_textual_cols_step(self, x: F.DataFrame):
        return (x.withColumn('date_received', F.to_date('date_received', 'M/d/yyyy'))
                .withColumn('disputed', confirming_word_as_bool('disputed'))
                .withColumn('timely_response', confirming_word_as_bool('timely_response')))

    def clean_text_step(self, x: F.DataFrame):
        return x.withColumn('text_cleaned', T.functions.clean(x.consumer_message))


class Committing(T.processors.Trusting):
    """Issues Committing Processor.

    refined → refined

    Commits staged issues refined data, discarding repetitions within the
    staged data based on their ``complaint_id``, as well as all issues that
    have already been added to the committed pool.

    This processor has two inputs, which means inputs data must be passed
    as a dict containing keys that match the argument names in the ``call``
    method. Example:

        >>> inputs = {'staged': ..., 'committed': ...}
        >>> output_pqt = ...
        >>> proc = Committing(inputs, output_pqt)

    """

    SAVING_OPTIONS = {'mode': 'append'}

    def call(self, staged, committed):
        s = self.discard_duplicates(staged, 'complaint_id', 'ingested_at')

        if committed:
            s = (s
                 .join(committed, on='complaint_id', how='left_anti')
                 .cache())

            # This line is very important,
            # as it consolidates the cache:
            persisting_records = s.count()

            logging.info(f'{persisting_records} staging records were not '
                         f'found in the lake and will be committed.')

        return s.withColumn('committed_at', F.current_timestamp())

    def teardown(self):
        remove_if_exists(self.inputs['staged'])

        self.processed.unpersist()
