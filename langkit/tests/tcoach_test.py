from ..tcoach import *

class FakeGlossary:
    def __init__(self, items):
        self.items = items
    def find(self, expr):
        for item in self.items:
            if item == expr:
                return [item]
            
glossary = FakeGlossary([
    "p:det d:this",
    "p:v d:be",
    "p:quant d:a",
    "p:n d:test",
])

def mock_advise(tags):
    returned = []
    for tag in tags:
        if tag[1] == 'VBZ':
            returned.append(('INSERTED', '~'))
        returned.append(tag)
    return returned

def test_hints():
    tc = TranslationCoach(glossary, mock_advise)
    def assert_hints(text, *expected):
        results = [str(h) for h in tc.hints(text)]
        i = 0
        for ex in expected:
            found = ''
            while i < len(results):
                result = results[i]
                i += 1
                if ex in result:
                    found = result
                    break
            assert ex in found
    assert_hints("this is a test", 'p:det d:this', 'INSERTED', 'd:be', 'p:quant d:a', 'p:n d:test')

def test_bfr():
    assert bfr('are', 'VBP') == ('be', 'v')
    assert bfr('am', 'VBP') == ('be', 'v')
    assert bfr('is', 'VBZ') == ('be', 'v')
    assert bfr('taken', 'VBN') == ('take', 'v')
    assert bfr('walked', 'VBN') == ('walk', 'v')
    assert bfr('running', 'VBG') == ('run', 'v')
    assert bfr('smiling', 'VBG') == ('smil', 'v')
    assert bfr('baked', 'VBD') == ('bak', 'v')
    assert bfr('abruptly', 'RB') == ('abrupt', 'ad')
    assert bfr('bigger', 'JJR') == ('big', 'ad')
    assert bfr('highest', 'JJS') == ('high', 'ad')
    assert bfr('pelagic', 'JJ') == ('pelag', 'n')
    assert bfr('childish', 'JJ') == ('child', 'n')
    assert bfr('childlike', 'JJ') == ('child', 'n')
    assert bfr('windy', 'JJ') == ('wind', 'n')
    assert bfr('heavenly', 'JJ') == ('heaven', 'n')
    