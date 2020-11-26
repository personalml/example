import os
import logging
from argparse import ArgumentParser

import dextra.dna.core as C
import dextra.dna.commons as P


def parse_args():
    p = ArgumentParser()
    p.add_argument('--inputs', default=os.path.join(P.config.lakes.trusted, 'issues.parquet'))
    p.add_argument('--outputs', default=os.path.join(P.config.lakes.refined, 'issues.parquet'))

    return p.parse_args()


def run(inputs, outputs):
    (P.processors.issues.LearningProducts(inputs=inputs, outputs=outputs)
     .setup(P.config)
     .perform()
     .describe()
     .save()
     .teardown())


if __name__ == '__main__':
    logging.basicConfig(**P.config.logging.default.asDict())
    args = parse_args()

    run(args.inputs, args.outputs)
