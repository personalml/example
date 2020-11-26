"""Rollback entire application.

The entire system is reset to tis original state by removing all staged files
and moving the ingestion files from ``backup`` to the ``transient`` zone.

"""

import logging
import os
from argparse import ArgumentParser
from typing import List

import dextra.dna.core as C
import dextra.dna.commons as P


def parse_args():
    p = ArgumentParser(description=__doc__)
    p.add_argument('--stages', default='raw,trusted,refined')
    p.add_argument('--only-staged', action='store_true')
    return p.parse_args()


def run(stages: List[str],
        only_staged: bool):
    purge_stages(stages, only_staged)
    roll_transient_backup()


def purge_stages(stages, only_staged):
    logging.info(f'Purging stages {stages}')

    for stage in stages:
        remove_if_exists(os.path.join(P.config.lakes[stage], 'issues.staged.parquet'))

    if only_staged:
        return

    remove_if_exists(os.path.join(P.config.lakes.refined, 'issues.parquet'))


def remove_if_exists(pqt):
    if C.io.storage.exists(pqt):
        C.io.storage.delete(pqt)
        logging.info(f'  - {pqt} removed')


def roll_transient_backup():
    source = os.path.join(
        P.config.lakes.backup,
        C.io.storage.without_protocol(P.config.lakes.transient).lstrip('/'),
        'issues')

    backed_files = C.io.storage.listdir(source)

    logging.info(f'Rolling transient backup in {source}')

    if not backed_files:
        return logging.info('0 files found. Nothing to rollback.')

    for f in backed_files:
        C.io.storage.move(
            os.path.join(source, f),
            os.path.join(P.config.lakes.transient, 'issues', f))
        logging.info(f'  - {f} moved to transient zone')


if __name__ == '__main__':
    logging.basicConfig(**P.config.logging.default.asDict())
    args = parse_args()

    run(stages=args.stages.split(','),
        only_staged=args.only_staged)
