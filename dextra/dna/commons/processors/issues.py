from pyspark.sql import DataFrame, functions as F

import dextra.dna.core as C
import dextra.dna.text as T


class Rawing(T.processors.Rawing):
    """Issues Rawing Processor.

    transient → raw

    Adds ingestion timestamp to the transient data
    and append it to the raw data.

    """
    SAVING_OPTIONS = {'mode': 'overwrite'}
    SENSIBLE_COLUMNS = ('complaint_id', 'customer_name', 'state', 'zip_code')

    def call(self, x: DataFrame):
        x = self.hash_sensible_info(x, self.SENSIBLE_COLUMNS)
        x = self.exclude_sensible_info(x, 'consumer_message')

        x = x.withColumn('ingested_at', F.current_timestamp())

        return x


class Trusting(C.processors.Trusting):
    """issues Trusting Processor.

    raw → trusted

    Discard samples without :code:`ids` and remove
    entry duplicates by removing the older ones.

    """
    SAVING_OPTIONS = {'mode': 'overwrite'}

    def call(self, x: DataFrame):
        x = x.where(x.id.isNotNull())
        x = self.discard_duplicates(x, 'id', 'created_at')

        return x


class Refining(C.processors.Refining):
    """issues Refining Processor.

    trusted → refined

    Sort data according to its :code:`id` and
    :code:`created_at` to improve reading performance.

    """
    SAVING_OPTIONS = {'mode': 'overwrite'}

    def call(self, x: DataFrame):
        x = x.orderBy('id', 'created_at')

        return x
