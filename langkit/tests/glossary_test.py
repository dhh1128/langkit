from ..glossary import *

import os
import random

SAMPLE_GLOSS_PATH = os.path.join(os.path.dirname(__file__), 'martian', 'glossary.txt')
g = Glossary.load(SAMPLE_GLOSS_PATH)

def assert_di(x, kind, txt=None):
    di = DefnItem(x)
    assert di.kind == kind
    if txt is None: txt = x.strip()
    assert str(di) == txt

def test_DefnItem_simple():
    assert_di('pickle', EXACT_EQUIV)
    for equiv in EQUIV_CHARS:
        assert_di(equiv + 'pickle', equiv)

def test_DefnItem_spaces():
    for equiv in EQUIV_CHARS:
        for ch in ' \t\r\n':
            assert_di(equiv + ch + 'pickle', equiv, equiv + 'pickle')
            assert_di(equiv + ' ' + ch + 'pickle', equiv, equiv + 'pickle')
    for ch in ' \t\r\n':
        assert_di(ch + 'pickle', EXACT_EQUIV, 'pickle')
        assert_di(' ' + ch + 'pickle', EXACT_EQUIV, 'pickle')

def test_DefnItem_sort():
    for i in range(10):
        items = [DefnItem('x')]
        content_chars = 'abcdefghijk'
        for j in range(len(EQUIV_CHARS)):
            equiv = EQUIV_CHARS[(j + 2) % len(EQUIV_CHARS)]
            items.append(DefnItem(equiv + content_chars[j:j+2]))
        random.shuffle(items)
        items.sort()
        assert items[0].kind == EXACT_EQUIV
        for j in range(len(EQUIV_CHARS)):
            assert items[1 + j].kind == EQUIV_CHARS[j]

def test_Defn_multi():
    defn = Defn('~def, <a, > bc , :something, another something')
    assert str(defn) == "another something, >bc, <a, ~def, :something"

def test_load():
    # prove basic loading and that empty lines are ignored
    assert len(g._lang_to_en) == 6
    assert g._lang_to_en[2].word == 'fry' # prove entries are sorted

def test_find():
    assert g.find_lang('fry')
    assert g.find_lang('not-there') is None