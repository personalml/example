import os
import logging
from argparse import ArgumentParser

import dextra.dna.core as C
import dextra.dna.commons as P


def parse_args():
    p = ArgumentParser()
    p.add_argument('--inputs', default=os.path.join(P.config.lakes.trusted, 'issues.staged.parquet'))
    p.add_argument('--outputs', default=os.path.join(P.config.lakes.refined, 'issues.staged.parquet'))

    return p.parse_args()


def run(inputs, outputs):
    if not C.io.storage.exists(inputs):
        return logging.info('Nothing to refine today. See you tomorrow.')

    (P.processors.issues.Refining(inputs=inputs, outputs=outputs)
     .setup(P.config)
     .perform()
     .save()
     .describe()
     .teardown())


if __name__ == '__main__':
    logging.basicConfig(**P.config.logging.default.asDict())
    args = parse_args()

    run(args.inputs, args.outputs)
