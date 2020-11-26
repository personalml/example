import logging
import os

import dextra.dna.core as C

from ..utils import remove_if_exists


class InconsistentInputsMixin:
    """Load (possibly inconsistent) inputs, conform and
    merge all of them before calling the processor.

    """

    def load(self):
        super().load()

        x = self.loaded['inputs']
        x = C.io.stream.read(x)
        x = C.io.stream.conform(x)
        x = C.io.stream.merge(x)

        self.loaded['inputs'] = x

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
    def teardown(self):
        for f in C.utils.to_list(self.inputs):
            if not isinstance(f, str):
                continue

            if not C.io.storage.exists(f):
                logging.warning(f'Processor {self.fullname()} cannot remove '
                                f'input file {f}, as it does not exist.')
                continue

            # gs://dna_commons/backup/dna_commons/transient/issues/file.csv
            bk = os.path.join(self.config.lakes.backup,
                              C.io.storage.without_protocol(f).lstrip('/'))
            C.io.storage.move(f, bk)
            logging.debug(f'Input file {f} moved to {bk}.')

        return self
