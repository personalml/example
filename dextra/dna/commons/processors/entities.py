from typing import List
import pyspark.sql.functions as F
import dextra.dna.core as C


class EntityExtracting(C.processors.Trusting):
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


class Users(EntityExtracting):
    ENTITY_FIELDS = ['customer_name']


class Products(EntityExtracting):
    ENTITY_FIELDS = ['product']


class SubProducts(EntityExtracting):
    ENTITY_FIELDS = ['sub_product']


class Addresses(EntityExtracting):
    ENTITY_FIELDS = ['zip_code', 'state']


class Channels(EntityExtracting):
    ENTITY_FIELDS = ['via']
