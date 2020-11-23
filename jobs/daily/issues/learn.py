import os
import logging
from argparse import ArgumentParser

import dextra.dna.core as C
import dextra.dna.bowling as B


def parse_args():
    p = ArgumentParser('Learn Issues on a Daily Basis Job')
    p.add_argument('--inputs', default=os.path.join(B.config.lakes.trusted, 'issues.parquet'))
    p.add_argument('--outputs', default=os.path.join(B.config.lakes.refined, 'issues.parquet'))

    return p.parse_args()


def run(inputs, outputs):
    (B.processors.issues.LearningProducts(inputs=inputs, outputs=outputs)
     .setup(B.config)
     .perform()
     .describe()
     .save()
     .teardown())


if __name__ == '__main__':
    logging.basicConfig(**B.config.logging.default.asDict())
    args = parse_args()

    run(args.inputs, args.outputs)
