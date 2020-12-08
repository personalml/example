import abc
from typing import List
import pyspark.sql.functions as F
import dextra.dna.core as C


class ExtractionBase(C.processors.Trusting, metaclass=abc.ABCMeta):
    ENTITY_FIELDS: List[str] = NotImplemented
    DATE_FIELD = 'ingested_at'

    SAVING_OPTIONS = {'mode': 'append', 'partitions': ['year', 'month']}

    def call(self, x):
        x = self.discard_duplicates(x, self.ENTITY_FIELDS, self.DATE_FIELD)

        return x.select(
            'complaint_id',
            *self.ENTITY_FIELDS,
            'date_received',
            'ingested_at',
            F.year('ingested_at').alias('year'),
            F.month('ingested_at').alias('month')
        )


class Users(ExtractionBase):
    ENTITY_FIELDS = ['customer_name']


class Products(ExtractionBase):
    ENTITY_FIELDS = ['product']


class SubProducts(ExtractionBase):
    ENTITY_FIELDS = ['sub_product']


class Addresses(ExtractionBase):
    ENTITY_FIELDS = ['zip_code', 'state']


class Channels(ExtractionBase):
    ENTITY_FIELDS = ['via']
