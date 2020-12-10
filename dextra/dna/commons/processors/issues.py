import dextra.dna.text as T
import pyspark.sql.functions as F

from . import mixins
from ..functions import confirming_word_as_bool


class Rawing(mixins.InconsistentInputsMixin,
             mixins.BackupInputsMixin,
             T.processors.Rawing):
    """Issues Rawing Processor.

    transient/issues/* → raw/issues

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
        x = self.exclude_sensible_info(x, 'consumer_message', {
            'hash': r'X+(\sX+)*',
            'numeric': r'\d+',
            **T.datasets.COMMON_PATTERNS
        })

        return x

    def add_tags_step(self, x: F.DataFrame):
        return (x.withColumn('ingested_at', F.current_timestamp())
                .withColumn('tags_trusted_labels', F.rand() < .1)
                .withColumn('tags_split', F.when(F.rand() < .5, 'train')
                            .otherwise('test')))


class Trusting(mixins.TearInputsMixin,
               T.processors.Trusting):
    """Issues Trusting Processor.

    raw/issues → trusted/issues

    Discard samples without ``ids`` and remove
    entry duplicates by removing the older ones.

    """
    SAVING_OPTIONS = {'mode': 'append'}

    def call(self, x: F.DataFrame):
        x = x.where(x.complaint_id.isNotNull() &
                    x.consumer_message.isNotNull() &
                    (x.consumer_message != ''))

        x = self.discard_duplicates(x, 'complaint_id', 'ingested_at')

        return x


class Refining(mixins.TearInputsMixin,
               T.processors.Refining):
    """Issues Refining Processor.

    trusted/issues → refined/issues

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
        return x.withColumn('text_cleaned', T.functions.clean('consumer_message'))


class Committing(mixins.DeltaCommitMixin,
                 mixins.TearInputsMixin,
                 T.processors.Trusting):
    """Issues Committing Processor.

    refined/issues.staged → refined/issues

    Commits staged issues refined data, discarding repetitions within the
    staged data based on their ``complaint_id``, as well as all issues that
    have already been added to the committed pool (``mixins.DeltaCommitMixin``
    takes care of this part).

    """
    SAVING_OPTIONS = {'mode': 'append'}

    def call(self, x):
        x = self.discard_duplicates(x, 'complaint_id', 'ingested_at')
        x = self.discard_already_committed(x)

        return x.withColumn('committed_at', F.current_timestamp())
