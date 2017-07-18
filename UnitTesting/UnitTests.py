import unittest
from Preprocessing.MetaMapLite.MetaMap import MetaMap


class MetaMapClass(unittest.TestCase):
    def setUp(self):
        # Instantiate metamap obj with path to dir containing metamap install
        self.mm = MetaMap('/home/wlane/Applications/public_mm_lite/')
        self.concepts = ['right leg mass',
                         'right proximal tibial mass',
                         'asymptomatic',
                         'achy pain',
                         'new lumps',
                         'bumps',
                         'tingling in the foot and toes']

    def tearDown(self):
        self.mm = None

    def test_map_concepts(self):
        output = self.mm.map_concepts(self.concepts)
        self.assertEqual(output['bumps'], [])
        actual = output['achy pain']

        pass

if __name__ == '__main__':
    unittest.main()