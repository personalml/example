#!/bin/bash -xe

dna run daily/issues/ingest
dna run daily/issues/trust
dna run daily/issues/refine
dna run daily/entities/extract
dna run daily/issues/commit
