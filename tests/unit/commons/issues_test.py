import os

import numpy as np

import dextra.dna.core as C
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
        'zip_code': 'string',
        'ingested_at': 'timestamp',
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
        self.assertEqual(('complaint_id', 'customer_name', 'state', 'zip_code'),
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
