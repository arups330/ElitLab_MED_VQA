import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import validate_repository as validator
import update_catalog

class PreservationTests(unittest.TestCase):
    def setUp(self):
        self.nb = {'nbformat':4,'cells':[{'cell_type':'code','source':['print(1)'],'outputs':[{'output_type':'stream','name':'stdout','text':['1\n']}],'execution_count':1}]}
        self.raw = json.dumps(self.nb).encode()
        self.record = {'original_sha256':hashlib.sha256(self.raw).hexdigest(),
                       'code_cells_sha256':validator.fingerprint(self.nb['cells']),
                       'outputs_sha256':validator.fingerprint([self.nb['cells'][0]['outputs']]),'output_count':1}

    def test_new_working_output_is_allowed(self):
        updated = copy.deepcopy(self.nb)
        updated['cells'][0]['source'] = ['print(2)']
        updated['cells'][0]['outputs'][0]['text'] = ['2\n']
        self.assertEqual(validator.notebook_errors(updated),[])
        self.assertEqual(validator.snapshot_errors(self.raw,self.record),[])

    def test_original_output_tampering_is_detected(self):
        modified = copy.deepcopy(self.nb)
        modified['cells'][0]['outputs'] = []
        self.assertIn('original saved outputs differ',validator.snapshot_errors(json.dumps(modified).encode(),self.record))

    def test_malformed_output_is_rejected(self):
        self.nb['cells'][0]['outputs'] = [{'output_type':'unknown'}]
        self.assertTrue(validator.notebook_errors(self.nb))

    def test_launch_platform_is_not_swapped(self):
        path = 'notebooks/training/open/test.ipynb'
        self.assertIn('colab.research.google.com/github/',update_catalog.launch_url(path,'Colab'))
        self.assertIn('kaggle.com/kernels/welcome?src=',update_catalog.launch_url(path,'Kaggle'))

    def test_base_and_adapter_pipelines_are_separate(self):
        self.assertEqual(update_catalog.classify('notebooks/evaluation/base_models/open/a.ipynb')[0],'A')
        self.assertEqual(update_catalog.classify('notebooks/evaluation/open/a.ipynb')[0],'B')

if __name__ == '__main__': unittest.main()
