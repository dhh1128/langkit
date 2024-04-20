from ..glossary import *

import io
import os
import random

SAMPLE_GLOSS_PATH = os.path.join(os.path.dirname(__file__), 'martian', 'glossary.txt')
g = Glossary.load(SAMPLE_GLOSS_PATH)

SAMPLE_MD_GLOSS_PATH = SAMPLE_GLOSS_PATH.replace('.txt', '.md')
g_md = Glossary.load(SAMPLE_MD_GLOSS_PATH)
MD_PRE = "# A glossary\n\na paragraph of text\n* some stuff\n* some more stuff\n\n## Glossary"
MD_POST = "# A section after glossary\nsome stuff after a glossary"


def test_MatchExpr():
    def assert_me(text, starter, fwi):
        me = MatchExpr(text)
        assert me.starter == starter
        assert me.first_wildcard_index == fwi
        assert bool(fwi > -1) == me.wildcarded
    assert_me("abc", "abc", -1)
    assert_me("ab*c", "ab", 2)
    assert_me("ab?c", "ab", 2)
    assert_me("*abc", "", 0)
    assert_me("?abc", "", 0)

def test_searchexpr():
    entry = Entry(("abc", "123", "def xyz", "notes"))
    def assert_matches(expr):
        se = SearchExpr(expr)
        assert se.matches(entry)
    assert_matches("lex:abc")
    assert_matches("l:abc")
    assert_matches("pos:123")
    assert_matches("defn:*xyz")
    assert_matches("not:notes")
    assert_matches("abc*")

def test_searchexpr_starter():
    def assert_starter(expr, starter):
        se = SearchExpr(expr)
        assert se.starter == starter
    assert_starter("lex:abc pos:v", "abc")
    assert_starter("pos:v lex:ab*c", "ab")
    assert_starter("def:abc pos:v", "")
    assert_starter("lex:*abc notes:notes pos:v", "")
    
def test_searchexpr_fuzzify():
    def assert_fuzzy(expr, fuzzy_equiv):
        se = SearchExpr(expr)
        original = str(se)
        changed = se.fuzzify()
        assert str(se) == fuzzy_equiv
        assert changed == (original != fuzzy_equiv)
    assert_fuzzy("lex:abc", "l:*abc*")
    assert_fuzzy("pos:abc", "p:abc")
    assert_fuzzy("notes:?abc", "n:?abc*")
    assert_fuzzy("defn:?abc?", "d:?abc?")
    assert_fuzzy("defn:abc xyz", "d:*abc*xyz*")


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

def test_DefnItem_gloss_and_explanation():
    def assert_gex(item, gloss, explanation):
        di = DefnItem(item)
        assert di.gloss == gloss
        assert di.explanation == explanation
    assert_gex("abc", "abc", '')
    assert_gex("abc (xyz)", "abc", 'xyz')
    assert_gex("abc (xyz", "abc", 'xyz')
    assert_gex("abc xyz)", "abc xyz)", '')

def test_Defn_multi():
    defn = Defn('~def/ <a/> bc / :something/ another something')
    assert len(defn.equivs) == 5
    # Should render in different order, with all spacing canonicalized
    assert str(defn) == "another something / >bc / <a / ~def / :something"

def test_load():
    # prove basic loading and that empty lines are ignored
    assert len(g.entries) == 6
    assert g.entries[2].lexeme == 'fry' # prove entries are sorted

def test_load_markdown():
    assert len(g_md.entries) == 6
    assert g_md.entries[2].lexeme == 'fry'
    assert g_md.pre.find(MD_PRE) > -1
    assert g_md.post.find(MD_POST) > -1

def test_save_simple():
    buf = io.StringIO()
    g.save(handle=buf)
    output = buf.getvalue()
    assert HEADER in output
    assert DIVIDER in output
    i = output.find('fry |')
    j = output.find('swallow |')
    assert i > -1
    assert j > -1
    assert i < j

def test_save_markdown():
    buf = io.StringIO()
    g_md.save(handle=buf)
    txt = buf.getvalue()
    assert txt.find(MD_PRE) > -1
    assert txt.find(MD_POST) > -1
    assert txt.find("sweet | a | ~having a sugary flavor") > -1

def test_find_simple():
    assert g.find('l:fry')
    assert not g.find('l:not-there')
    assert not g.find('d:fry')
    assert g.find('d:to cook*')

def test_find_lexeme_wildcards():
    assert g.find('l:fr*')
    assert g.find('l:?ry')
    assert g.find('l:*ry')
    assert not g.find('l:*not*')

def test_find_defn_simple():
    assert g.find('d:a yellow fruit')
    assert not g.find('d:purple vegetable')

def test_find_defn_wildcards():
    assert len(g.find('d:*fruit')) > 1

def test_find_anywhere():
    assert len(g.find('swallow')) == 1
    assert len(g.find('vinegar')) == 1
