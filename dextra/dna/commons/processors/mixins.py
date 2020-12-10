import logging

import dextra.dna.core as C
from pyspark.sql.utils import AnalysisException

from ..utils import backup_if_exists, remove_if_exists


class InconsistentInputsMixin(C.processors.Processor):
    """Load (possibly inconsistent) inputs, conform and
    merge all of them before calling the processor.

    """

    def load(self):
        super().load()

        for i, x in self.loaded.items():
            x = C.io.stream.conform(x)
            x = C.io.stream.merge(x)

            self.loaded[i] = x

        return self


class TearInputsMixin:
    """Delete all ingested inputs that are paths to files.

    During the teardown stage, processors that contain this Mixin will
    automatically remove all inputs that are valid paths. This is useful when
    creating incremental pipelines with a final commit step. In such cases,
    the input should only be preserved if the pipeline fails.
    """

    def teardown(self):
        for f in C.utils.to_list(self.inputs):
            remove_if_exists(f)

        return self


class BackupInputsMixin:
    """Similar to ``TearInputsMixin``, but moves the inputs to the backup
    bucket during teardown.

    """
    def teardown(self):
        for f in C.utils.to_list(self.inputs):
            backup_if_exists(f, self.config.lakes.backup)

        return self


class DeltaCommitMixin:
    def discard_already_committed(self, staged):
        try:
            committed = C.io.stream.read(self.outputs)
            logging.info(f'Committed pool {self.outputs} exists. '
                         f'Removing repetitions in staged data.')

            return staged.join(committed, on='complaint_id', how='left_anti')

        except AnalysisException as error:
            if 'Path does not exist' in error.desc:
                logging.info(f'Committed records not found in {self.outputs}. '
                             f'All staged records will be committed.')
                return staged

            # I don't know which error this is. Delegate to
            # error handling in the upper execution stack.
            raise
