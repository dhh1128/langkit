from ..phoneme import *
from ..phoneme import _ph, _v2n, _n2v

def test_uniqueness():
    dups = []
    for i in range(len(_ph)):
        a = _ph[i]
        for j in range(len(_ph)):
            if j != i:
                b = _ph[j]
                for n in range(len(a)):
                    if a[n] and (a[n] == b[n]):
                        dups = f"item {i} ({a}) and {j} ({b}) are identical in field {n}"
    assert not dups

def test_attrib_name_to_value():
    unrecognized_words = []
    for p in _ph:
        attrib_words = p[2].split(' ')
        for word in attrib_words:
            if attrib_name_to_value(word) is None:
                unrecognized_words.append(word)
    assert not unrecognized_words

def test_attrib_bits_to_name():
    for i in range(0, 29 + 1):
        try:
            assert attrib_bits_to_name(1 << i)
        except:
            print (_v2n)
            raise

def test_attrib_bits_to_phrase_vowels():
    broken = []
    descrips = [p[2] for p in _ph if 'vowel' in p[2]]
    # Conceivable vowels that I have manually confirmed do not exist in IPA or X-SAMPA's inventory
    exceptions = [
        OPEN | CENTRAL | UNROUNDED, 
        OPEN | CENTRAL | ROUNDED, 
        NEAR_OPEN | FRONT | ROUNDED,
        NEAR_OPEN | CENTRAL | ROUNDED,
        NEAR_OPEN | BACK | UNROUNDED,
        NEAR_OPEN | BACK | ROUNDED,
        MID | FRONT | ROUNDED,
        MID | FRONT | UNROUNDED,
        MID | CENTRAL | ROUNDED,
        MID | BACK | ROUNDED,
        MID | BACK | UNROUNDED,
        NEAR_CLOSE | BACK | UNROUNDED
    ]
    for o in VOWEL_OPENNESS:
        for p in VOWEL_POSITIONS:
            for r in VOWEL_ROUNDEDNESS:
                attribs = o | p | r
                if attribs not in exceptions:
                    phrase = attrib_bits_to_phrase(VOWEL | attribs)
                    if phrase not in descrips:
                        broken.append(f"{phrase} is missing")
    assert not broken

def show_relevant_bits(mask):
    shown = ''
    for k, v in _n2v.items():
        if '-' in k or '_' in k or 'mask' in k:
            continue
        if (mask & v) != v:
            continue
        shown += f"  {k} = {hex(v)}\n"
    return shown

def test_attrib_phrase_to_bits():
    broken = []
    def check(phrase, bits):
        n = attrib_phrase_to_bits(phrase)
        if n != bits:
             actual = attrib_bits_to_phrase(n)
             expected = attrib_bits_to_phrase(bits)
             print(show_relevant_bits(n | bits))
             error = f"{phrase} yielded {hex(n)} ({actual}), not {hex(bits)} ({expected})"
             assert not error
    check('alveolar lateral click', ALVEOLAR | LATERAL | CLICK)
    check('postalveolar click', POST_ALVEOLAR | CLICK)
    check('velar approximant', VOICED | VELAR | APPROXIMANT | PULMONIC)
    check('voiceless palatal-velar fricative', VOICELESS | PALATAL_VELAR | FRICATIVE | PULMONIC)
    check('voiceless uvular plosive', VOICELESS | UVULAR | PLOSIVE | PULMONIC)
    check('retroflex lateral approximant', VOICED | RETROFLEX | LATERAL | APPROXIMANT | PULMONIC)
    check('alveolar trill', VOICED | ALVEOLAR | TRILL | PULMONIC)
    check('alveolar nasal', VOICED | ALVEOLAR | NASAL | PULMONIC)
    check('voiced glottal fricative', VOICED | GLOTTAL | FRICATIVE | PULMONIC)
    check('voiced velar implosive', VOICED | VELAR | IMPLOSIVE)
    check('voiceless palatal plosive', VOICELESS | PLOSIVE | PALATAL | PULMONIC)
    check('near-open central rounded vowel', NEAR_OPEN | CENTRAL | ROUNDED | VOWEL)
    check('open front unrounded vowel', OPEN | FRONT | UNROUNDED | VOWEL)

def test_attrib_bits_to_phrase_round_trip():
    y = attrib_phrase_to_bits("voiced bilabial plosive")
    print(show_relevant_bits(y))
    x = attrib_bits_to_phrase(BILABIAL | PLOSIVE | VOICED)
    broken = []
    for p in _ph:
        expected = p[2]
        actual = attrib_bits_to_phrase(attrib_phrase_to_bits(expected))
        assert actual == expected

