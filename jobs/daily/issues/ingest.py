import os
import logging
from argparse import ArgumentParser

import dextra.dna.core as C
import dextra.dna.commons as P


def parse_args():
    p = ArgumentParser('Ingest Issues on a Daily Basis Job')
    p.add_argument('--inputs', default=os.path.join(P.config.lakes.transient, 'issues'))
    p.add_argument('--outputs', default=os.path.join(P.config.lakes.raw, 'issues.parquet'))
    
    return p.parse_args()


def run(inputs, outputs):
    files = C.io.storage.listdir(inputs)

    if not files:
        return logging.info('Nothing to process today. See you tomorrow.')

    logging.info(f'The following files were found and will be ingested: {files}')

    x = [os.path.join(inputs, f) for f in files]
    x = C.io.stream.read(x)
    x = C.io.stream.conform(x)
    x = C.io.stream.merge(x)

    (P.processors.issues.Rawing(inputs=x, outputs=outputs)
     .setup(P.config)
     .perform()
     .describe()
     .save()
     .teardown())


if __name__ == '__main__':
    logging.basicConfig(**P.config.logging.default.asDict())
    args = parse_args()

    run(args.inputs, args.outputs)
