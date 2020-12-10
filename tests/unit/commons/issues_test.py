import datetime
import os

import dextra.dna.core as C
import numpy as np
import pandas as pd
import pyspark.sql.functions as F

import dextra.dna.commons as P


class RawingTest(C.testing.SparkTestCase):
    EXPECTED_SCHEMA = {
        'complaint_id': 'string',
        'consumer_message': 'string',
        'customer_name': 'string',
        'date_received': 'string',
        'disputed': 'string',
        'issue': 'string',
        'product': 'string',
        'resolution': 'string',
        'state': 'string',
        'sub_issue': 'string',
        'sub_product': 'string',
        'tags': 'string',
        'timely_response': 'string',
        'via': 'string',
        'zip_code': 'int',
        'ingested_at': 'timestamp',
        'tags_trusted_labels': 'boolean',
        'tags_split': 'string',
        # 'tags': 'array<string>',
        # 'profile': {'name': 'string', 'group': 'string'}
        # 'entries': [{'text': 'string', 'created_at': 'timestamp'}]
    }

    _inputs = None

    @property
    def inputs(self):
        if self._inputs is None:
            x = os.path.join(self.config.lakes.transient, 'issues', 'issues.csv')
            x = C.io.stream.read(x)
            x = C.io.stream.conform(x)
            x = C.io.stream.merge(x)
            self._inputs = x

        return self._inputs

    def setUp(self):
        self.outputs = os.path.join(self.config.lakes.raw, 'issues.parquet')

        self.p = P.processors.issues.Rawing(
            inputs=self.inputs,
            outputs=self.outputs,
            config=self.config)

    def test_schema_matches_exactly_expected(self):
        outputs = self.p(self.inputs)

        self.assertSchemaMatches(outputs, self.EXPECTED_SCHEMA)

    def test_has_sensible_columns_attr(self):
        self.assertEqual(('complaint_id', 'customer_name'),
                         self.p.SENSIBLE_COLUMNS)

    def test_correctly_encrypts_data(self):
        sensible = self.p.SENSIBLE_COLUMNS

        unsecure = self.inputs.select(*sensible).toPandas().astype(str)
        outputs = self.p(self.inputs).select(*sensible).toPandas().astype(str)

        self.assertTrue(np.all(unsecure != outputs), 'some value was not encrypted')

    def test_has_correct_row_numbers(self):
        expected_products = ('Credit reporting', 'Consumer Loan', 'Credit reporting',
                             'Debt collection', 'Debt collection', 'Mortgage')

        y = self.p(self.inputs)
        actual = [r[0] for r in y.select('product').collect()]

        np.testing.assert_array_equal(expected_products, actual)


class TrustingTest(C.testing.SparkTestCase):
    INPUT_DATA = [(None, '2020-01-01', 'Hello there!'),
                  ('1', '2020-01-01', 'Hello there!'),
                  ('1', '2020-01-02', 'Hello there!'),
                  ('2', '2020-01-01', 'Hello there!'),
                  ('3', '2020-01-01', 'Hello there!')]

    _inputs = None

    @property
    def inputs(self):
        if self._inputs is None:
            self._inputs = self.spark.createDataFrame(
                self.INPUT_DATA, ['complaint_id', 'ingested_at', 'consumer_message'])

        return self._inputs

    def setUp(self):
        self.p = P.processors.issues.Trusting(self.inputs, ..., self.config)

    def test_call(self):
        y = self.p(self.inputs)

        self.assertEqual(3, y.count())
        self.assertEqual(0, y.where(y.complaint_id.isNull()).count())

        c, cd = y.select(
            F.count('complaint_id'),
            F.countDistinct('complaint_id')
        ).collect()[0]

        self.assertEqual(c, cd)


class RefiningTest(C.testing.SparkTestCase):
    EXPECTED_SCHEMA = {
        'complaint_id': 'string',
        'date_received': 'date',
        'disputed': 'boolean',
        'timely_response': 'boolean',
        'consumer_message': 'string',
        'text_cleaned': 'string',
    }

    INPUT_DATA = [('1', '9/12/2020', 'no', 'yes', 'Hello there.'),
                  ('2', '9/13/2020', 'no', 'no', 'Hello there.'),
                  ('3', '9/14/2020', 'yes', 'yes', 'Hello there.'),
                  ('4', '9/15/2020', 'yes', 'no', 'Hello there.')]
    EXPECTED_OUTPUT_DATA = [('1', datetime.date(2020, 9, 12), False, True, 'Hello there.', 'hello there'),
                            ('2', datetime.date(2020, 9, 13), False, False, 'Hello there.', 'hello there'),
                            ('3', datetime.date(2020, 9, 14), True, True, 'Hello there.', 'hello there'),
                            ('4', datetime.date(2020, 9, 15), True, False, 'Hello there.', 'hello there')]

    _inputs = None

    @property
    def inputs(self):
        if self._inputs is None:
            self._inputs = self.spark.createDataFrame(
                self.INPUT_DATA,
                ['complaint_id', 'date_received', 'disputed',
                 'timely_response', 'consumer_message'])

        return self._inputs

    @property
    def expected_output_data(self):
        cols = ['complaint_id', 'date_received', 'disputed',
                'timely_response', 'consumer_message', 'text_cleaned']
        return pd.DataFrame(self.EXPECTED_OUTPUT_DATA, columns=cols)

    def setUp(self):
        self.outputs = os.path.join(self.config.lakes.raw, 'issues.parquet')

        self.p = P.processors.issues.Refining(self.inputs, ..., self.config)

    def test_call(self):
        y = self.p(self.inputs)

        np.testing.assert_array_equal(self.expected_output_data, y.toPandas())

    def test_schema_matches_exactly_expected(self):
        outputs = self.p(self.inputs)

        self.assertSchemaMatches(outputs, self.EXPECTED_SCHEMA)
