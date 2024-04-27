from ..tcoach import *

class FakeGlossary:
    def __init__(self, items):
        self.items = items
    def find(self, expr):
        for item in self.items:
            if item == expr:
                return [item]
            
glossary = FakeGlossary([
    "p:deixis d:this",
    "p:v d:be",
    "p:quant d:a",
    "p:n d:test",
])

class FakeAdviser:
    def advise(self, tags):
        returned = []
        for tag in tags:
            if tag[1] == 'VBZ':
                returned.append(('~', 'INSERTED'))
            returned.append(tag)
        return returned

def test_hints():
    tc = TranslationCoach(glossary, FakeAdviser())
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
    assert_hints("this is a test", 'deixis', 'INSERTED', 'd:be', 'DT', 'p:n d:test')

def test_bfr():
    assert bfr('are', 'VBP') == 'be'
    assert bfr('am', 'VBP') == 'be'
    assert bfr('is', 'VBZ') == 'be'
    assert bfr('taken', 'VBN') == 'tak'
    assert bfr('walked', 'VBN') == 'walk'
    assert bfr('running', 'VBG') == 'run'
    assert bfr('smiling', 'VBG') == 'smil'
    assert bfr('baked', 'VBD') == 'bak'
    assert bfr('heavenly', 'RB') == 'heaven'
    assert bfr('bigger', 'JJR') == 'big'
    assert bfr('highest', 'JJS') == 'high'
    assert bfr('pelagic', 'JJ') == 'pelag'
    assert bfr('childish', 'JJ') == 'child'
    assert bfr('childlike', 'JJ') == 'child'
    assert bfr('windy', 'JJ') == 'wind'
    