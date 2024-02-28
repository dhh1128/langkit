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