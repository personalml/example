import os
import logging
from argparse import ArgumentParser

import dextra.dna.core as C
import dextra.dna.commons as P


def parse_args():
    p = ArgumentParser()
    p.add_argument('--inputs', default=os.path.join(P.config.lakes.refined, 'issues.parquet'))
    p.add_argument('--outputs', default=os.path.join(P.config.lakes.models, 'logs/encoder_trainings.parquet'))

    return p.parse_args()


def run(inputs, outputs):
    (C.Job(
        P.processors.products.LearningEncoder(inputs=inputs, outputs=outputs)
     )
     .setup(P.config)
     .describe()
     .perform()
     .teardown())


if __name__ == '__main__':
    logging.basicConfig(**P.config.logging.default.asDict())
    args = parse_args()

    run(args.inputs, args.outputs)
