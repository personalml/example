import logging
import os

import dextra.dna.core as C
from retry import retry


@retry(TimeoutError, tries=5, delay=1, backoff=2)
def remove_if_exists(f):
    if not isinstance(f, str) or not C.io.storage.exists(f):
        return logging.warning(f'cannot remove input file {f}, as it does not exist.')

    C.io.storage.delete(f)
    logging.debug(f'Input file {f} removed.')


@retry(TimeoutError, tries=5, delay=1, backoff=2)
def backup_if_exists(f, bk_bucket):
    if not isinstance(f, str):
        return

    if not C.io.storage.exists(f):
        return logging.warning(f'cannot remove input file {f}, as it does not exist.')

    # gs://dna_commons/transient/issues/file.csv --> dna_commons/transient/issues/file.csv
    bk = C.io.storage.without_protocol(f).lstrip('/')

    # gs://dna_commons/backup/dna_commons/transient/issues/file.csv
    bk = os.path.join(bk_bucket, bk)

    C.io.storage.move(f, bk)  # local --> os.move
    logging.debug(f'Input file {f} moved to {bk}.')
