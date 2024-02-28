from ..glossary import Glossary

import os

SAMPLE_GLOSS_PATH = os.path.join(os.path.dirname(__file__), 'sample-glossary.txt')
g = Glossary.load(SAMPLE_GLOSS_PATH)

def test_load():
    # prove basic loading and that empty lines are ignored
    assert len(g.entries) == 6
    assert g.entries[2].word == 'fry' # prove entries are sorted

def test_find():
    assert g.find('fry')
    assert g.find('not-there') is None