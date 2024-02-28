from ..lang import *


def test_defs_folder():
    assert DEFS_FOLDER.endswith('/.langtool')


SAMPLE_LANG = '''
{
    "vowels": "aeiou",
    "consonants": "stpnmfhzdb",
    "sylpats": ["CV", "CCV", "CVC", "VC", "V"]
}
'''

def test_syllables():
    l = Lang('foo', SAMPLE_LANG)
    for s in l.syllables:
        pass #print(s)