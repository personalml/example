# Changelog

## [0.0.8](https://gitlab.dextra.com.br/dna/commons/tags/0.0.8) (2020-11-01)
### Additions
* Add `config/local/security.yml`

### Changes
* Upgrade to dna/core 0.4.8 and dna/core/text 0.4.2
* Comment incorrectly set dna/core/text dependency in `config/gcloud/.env`
* Limit docker exposure to localhost in `docker-compose.yml`

## [0.0.7](https://gitlab.dextra.com.br/dna/commons/tags/0.0.7) (2020-10-26)
### Additions
* Add CHANGELOG.md
* Add pre-commit optional feature

### Changes
* Add `config/local/spark-defaults.config` file and automatically copy it
  to its appropriate place during build
* Cleanup on docker configs
* Update dna/core/text version to 0.4.1
* KIND → BACKEND, inside `config/$ENV/.env`

## [0.0.6](https://gitlab.dextra.com.br/dna/commons/tags/0.0.6) (2020-10-18)
### Additions
* Move text package from core repo into here

### Changes
* Refactor test dependencies in `tests/requirements.txt`
* Eliminate global-level imports for external libraries in `text.models`

## [0.0.5](https://gitlab.dextra.com.br/dna/commons/tags/0.0.5) (2020-10-17)
### Additions
* Add .keep files to buckets in `datalake` as a reference
  point for new core users

### Changes
* Refactor job example
* Cleanup on Dockerfile

### Fixes
* Tests now import dextra.dna.commons so coverage is produced

## [0.0.4](https://gitlab.dextra.com.br/dna/commons/tags/0.0.4) (2020-09-22)
### Additions
* Add `config/$ENV/.env:SERVICE`

### Changes
* Add `ENV` and `KIND` properties to configs:
  multiple environments of a same backend can be created
* Cleanup in scripts folder
* Keep notebooks folder in git

### Deletions
* Remove scripts (moved to `dna/forge`)

## [0.0.3](https://gitlab.dextra.com.br/dna/commons/tags/0.0.3) (2020-06-20)
### Changes
* Comment optional dependencies in `requirements.txt`: user must now uncomment
  if they are going to use them

## [0.0.2](https://gitlab.dextra.com.br/dna/commons/tags/0.0.2) (2020-06-18)
### Changes
* Adjust git backend to gitlab, remove github during build

## [0.0.1](https://gitlab.dextra.com.br/dna/commons/tags/0.0.1) (2020-06-12)
### Additions
* Import project from github
