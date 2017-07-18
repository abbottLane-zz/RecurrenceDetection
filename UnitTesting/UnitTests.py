import unittest
from Preprocessing.MetaMapLite.MetaMap import MetaMap


class MetaMapClass(unittest.TestCase):
    def setUp(self):
        # Instantiate metamap obj with path to dir containing metamap install
        self.mm = MetaMap('/home/wlane/Applications/public_mm_lite/')
        self.concepts = ['right leg mass',
                         'right proximal tibial mass',
                         'achy pain',
                         'bumps'
                         ]

    def tearDown(self):
        self.mm = None

    def test_build_umls_concept(self):
        happy_case = "text|0.0|Tumor Mass|C3273930|[fndg]|\"Tumor Mass\"-tx-0-\"tumor\"-NN-0|tx|15:5|"
        empty_case = ""
        garbage_case ="abcdefg"

        happy_output = self.mm._build_umls_concepts(happy_case)
        empty_output = self.mm._build_umls_concepts(empty_case)
        garbage_output = self.mm._build_umls_concepts(garbage_case)

        self.assertEqual(type(happy_output), type([]))
        assert('sem_class' in happy_output[0].keys())
        assert ('start' in happy_output[0].keys())
        assert ('end' in happy_output[0].keys())
        assert ('desc' in happy_output[0].keys())
        assert ('cui' in happy_output[0].keys())

        self.assertEqual(empty_output, list())
        self.assertEqual(garbage_output, list())

    def test_map_concepts(self):
        output = self.mm.map_concepts(self.concepts)
        self.assertEqual(output['bumps'], [])

        response = output['right leg mass']
        self.assertEqual(len(response), 4)
        self.assertEqual(response[0]['cui'], 'C0230442')
        self.assertEqual(response[1]['cui'], 'C1279605')
        self.assertEqual(response[2]['cui'], 'C0577559')
        self.assertEqual(response[3]['cui'], 'C1306372')

        response = output['right proximal tibial mass']
        self.assertEqual(len(response), 5)
        self.assertEqual(response[0]['cui'], 'C0577559')
        self.assertEqual(response[1]['cui'], 'C1306372')
        self.assertEqual(response[2]['cui'], 'C0205107')
        self.assertEqual(response[3]['cui'], 'C0040184')
        self.assertEqual(response[4]['cui'], 'C0205090')


if __name__ == '__main__':
    unittest.main()