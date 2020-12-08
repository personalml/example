# Commons
[![Documentation](https://img.shields.io/badge/docs-0.0.8-orange.svg?style=flat-square)](http://storage.googleapis.com/dna-core/index.html)
[![Python required version: 3.7](https://img.shields.io/badge/python-3.7-blue.svg?style=flat-square)](https://www.python.org/downloads/release/python-370)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)

This project was created by the [DnA Forge](https://gitlab.dextra.com.br/dna/forge).
Please refer to the core [documentation](https://docs-dna-core.dextra.com.br/)
for instruction on how to build, run and test it.

## Introduction

Exemplifies a python project using the DnA Core and Text libraries.

### Data and Problem Domain Set

The dataset used in this project is the customer-issues. It can be found at
the `dna_commons` bucket in the `dxtdna` Google Cloud project. Additionally,
you can check it in Kaggle:
[dushyantv/consumer_complaints](https://www.kaggle.com/dushyantv/consumer_complaints).

We simulate a dataflow in which users will daily post they complaints into
a bucket. We ingest these text complaints and store them in a more
efficient data representation (multiple parquet files), persisted in
the data lake referenced in the `config/{ENV}/lakes.yml` file.

## Usage
```shell
dna start    # Equivalent to `dna start local`
dna explore  # A local jupyter server is now
             # available at localhost:8086
dna test     # run all tests from repo
```
