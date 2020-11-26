import logging
import os
from argparse import ArgumentParser

import dextra.dna.core as C
import dextra.dna.commons as P


def parse_args():
    p = ArgumentParser()
    p.add_argument('--inputs', default=os.path.join(P.config.lakes.refined, 'issues.staged.parquet'))
    p.add_argument('--outputs', default=os.path.join(P.config.lakes.refined, 'issues.parquet'))

    return p.parse_args()


def run(inputs, outputs):
    if not C.io.storage.exists(inputs):
        return logging.info('Nothing to commit today. See you tomorrow.')

    if C.io.storage.exists(outputs):
        # Only pass committed if there's committed data. Otherwise,
        # the processor will attempt to load a None stream.
        logging.info(f'Committed data found at {outputs}. It will be passed '
                     f'to the processor so it can be subtracted from the '
                     f'staging data.')
        committed = outputs
    else:
        committed = None

    inputs = {'staged': inputs, 'committed': committed}

    (P.processors.issues.Committing(inputs, outputs)
      .setup(P.config)
      .perform()
      .save()
      .describe()
      .teardown())


if __name__ == '__main__':
    logging.basicConfig(**P.config.logging.default.asDict())
    args = parse_args()

    run(args.inputs, args.outputs)
