import os

import numpy as np

import dextra.dna.core as C
import dextra.dna.bowling as B


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
    
    def setUp(self):
        x = C.io.stream.read(os.path.join(self.config.lakes.transient, 'issues', 'issues.csv'),
                             multiLine=True,
                             escape='"',
                             header=True,
                             inferSchema=True)
        x = C.io.stream.conform(x)
        x = C.io.stream.merge(x)
        self.inputs = x

        self.outputs = os.path.join(self.config.lakes.raw, 'issues.parquet')

        self.p = B.processors.issues.Rawing(
            inputs=x,
            outputs=self.outputs,
            config=self.config)

    def test_schema_matches_exactly_expected(self):
        outputs = self.p(self.inputs)

        self.assertSchemaMatches(outputs, self.EXPECTED_SCHEMA)
    
    def test_has_sensible_columns_attr(self):
        self.assertEqual(('customer_name', 'complaint_id', 'state', 'zip_code'),
                         self.p.SENSIBLE_COLUMNS)

    def test_correctly_encrypts_data(self):
        sensible = self.p.SENSIBLE_COLUMNS

        unsecure = self.inputs.select(*sensible).toPandas().astype(str)
        outputs = self.p(self.inputs).select(*sensible).toPandas().astype(str)

        self.assertTrue(np.all(unsecure != outputs), 'some value was not encrypted')
