# commons
[![Documentation](https://img.shields.io/badge/docs-0.0.8-orange.svg?style=flat-square)](http://storage.googleapis.com/dna-core/index.html)
[![Python required version: 3.7](https://img.shields.io/badge/python-3.7-blue.svg?style=flat-square)](https://www.python.org/downloads/release/python-370)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)


This project was created by the [DnA Forge](gitlab.dextra.com.br/dna/forge).
Please refer to the core [documentation](http://storage.googleapis.com/dna-core/index.html)
for instruction on how to build, run and test it.

## Usage
```shell
dna start
dna explore  # A local jupyter server is now
             # available at localhost:8086
dna test     # run all tests from repo
```

## Pre-commit
Mark to automatically check a bunch of stuff (run tests, force code style, check packages vulnerabilities, etc.) and ensure pep8 before commit/push
```shell
pip install safety pre-commit
pre-commit install
pre-commit install -t pre-push
```
