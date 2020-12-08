"""Ingest issues from a CSV into our datalake.

The ingestion will happen onto the lake described by the configuration
of the environment running this job.

"""
import logging
import os
from argparse import ArgumentParser

import dextra.dna.core as C
import dextra.dna.commons as P


def parse_args():
    p = ArgumentParser(description=__doc__)
    p.add_argument('--inputs', default=os.path.join(P.config.lakes.transient, 'issues'))
    p.add_argument('--outputs', default=os.path.join(P.config.lakes.raw, 'issues.staged.parquet'))

    return p.parse_args()


def run(inputs, outputs):
    files = [os.path.join(inputs, f)
             for f in C.io.storage.listdir(inputs)
             if f.endswith('.csv')]

    if not files:
        return logging.info('Nothing to process today. See you tomorrow.')

    logging.info(f'The following files were found and will be ingested: {files}')

    (P.processors.issues.Rawing(inputs=files, outputs=outputs)
     .setup(P.config)
     .perform()
     .save()
     .describe()
     .teardown())


if __name__ == '__main__':
    logging.basicConfig(**P.config.logging.default.asDict())
    args = parse_args()

    run(args.inputs, args.outputs)
