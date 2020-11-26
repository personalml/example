import logging

import dextra.dna.core as C


def remove_if_exists(f):
    if not isinstance(f, str) or not C.io.storage.exists(f):
        return logging.warning(f'cannot remove input file {f}, as it does not exist.')

    C.io.storage.delete(f)
    logging.debug(f'Input file {f} removed.')
