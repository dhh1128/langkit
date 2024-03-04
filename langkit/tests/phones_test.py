from ..phones import *

def check_3(func, should_be_true, should_be_false, should_be_none):
    assert func(should_be_true) == True
    assert func(should_be_false) == False
    assert func(should_be_none) is None

def test_is_rounded():
    check_3(is_rounded, 'o', 'i', 't')

def test_is_vowel():
    check_3(is_vowel, 'a', 's', None)

def test_is_voiced():
    check_3(is_voiced, 'd', 'x', 'u')

def test_is_interrupted():
    check_3(is_interrupted, 'd', 'x', None)

def test_is_nasal():
    check_3(is_nasal, 'm', 'x', None)

def test_is_consonant():
    check_3(is_consonant, 'p', 'u', None)

def test_get_place():
    assert get_place('a') == 'open central'
    assert get_place('t') == 'alveolar'

def test_get_manner():
   assert get_manner('a') is None
   assert get_manner('s') == 'fricative'

def test_can_add_std():
    def ok(a, b):
        assert can_add_std(a, b) == True
    def bad(a, b):
        assert can_add_std(a, b) == False
    ok('t', 'a')
    ok('a', 't')
    bad('t', 't')
    bad('t', 'h')
    bad('a', 'ə')
    bad('a', 'ɒ')
    bad('a', 'æ')
    ok('a', 'i')
    ok('u', 'e')
    bad('z', 's')
    ok('s', 'l')

NO_MAX = 1000000
def assert_syl(vowels, consonants, syls, min_count=0, max_count=NO_MAX, must_include=None, cant_include=None):
    n = 0
    cant = []
    s = []
    for item in conceivable_syllables(vowels, consonants, *syls):
        s.append(item)
        if must_include:
            try:
                i = must_include.index(item)
                del must_include[i]
            except ValueError:
                pass
        if cant_include:
            if item in cant_include:
                cant.append(item)
        n += 1
    if min_count > 0:
        assert n >= min_count
    if max_count >= 0 and max_count <= NO_MAX:
        assert n <= max_count
    if must_include == []: must_include = None
    if cant == []: cant = None
    assert must_include is None
    assert cant is None
    return s

def test_syllables_easy():
    assert_syl('ai', 'sm', ['V', 'CV'], 6, 6, ['a', 'sa'], ['sm', 'aa'])

def test_syllables_complex():
    syl = assert_syl('aeiou', 'smphntk', ['CCCV'], 40)
    long_syl = [s for s in syl if len(s) == 4]
    assert long_syl == []


#need to prevent a consonant from being reused without intervening vowel
#need to allow a lang to declare combinations that it doesn't support (e.g., ps)
