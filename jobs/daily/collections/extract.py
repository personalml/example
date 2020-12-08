"""Extract a normalized set of entities from the eventual base of issues.

By default, the entities extracted are: users, products, sub-products,
addresses (zip-code and state) and channels.

"""
import logging
import os
from argparse import ArgumentParser

import dextra.dna.core as C
import dextra.dna.commons as P


def parse_args():
    p = ArgumentParser(description=__doc__)
    p.add_argument('--inputs', default=os.path.join(P.config.lakes.refined, 'issues.staged.parquet'))
    p.add_argument('--output_dir', default=os.path.join(P.config.lakes.refined, 'collections'))

    return p.parse_args()


def as_proc_args(entity, inputs, output_dir):
    """Convert the entity tag, the input and output path to arguments for
    a processor in ``collections``.
    """
    return inputs, os.path.join(output_dir, f'{entity}.parquet')


def run(inputs, output_dir):
    if not C.io.storage.exists(inputs):
        return logging.info('Nothing to extract today. See you tomorrow.')

    (C.Job(
        P.processors.collections.Users(*as_proc_args('users', inputs, output_dir)),
        P.processors.collections.Products(*as_proc_args('products', inputs, output_dir)),
        P.processors.collections.SubProducts(*as_proc_args('sub_products', inputs, output_dir)),
        P.processors.collections.Addresses(*as_proc_args('addresses', inputs, output_dir)),
        P.processors.collections.Channels(*as_proc_args('channels', inputs, output_dir)),
    )
     .setup(P.config)
     .describe()
     .perform()
     .teardown())


if __name__ == '__main__':
    logging.basicConfig(**P.config.logging.default.asDict())
    args = parse_args()

    run(args.inputs, args.output_dir)
