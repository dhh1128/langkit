from ..bfr import *

def test_bfr():
    assert bfr('are', 'VBP') == ('be', 'v')
    assert bfr('am', 'VBP') == ('be', 'v')
    assert bfr('is', 'VBZ') == ('be', 'v')
    assert bfr('taken', 'VBN') == ('take', 'v')
    assert bfr('walked', 'VBN') == ('walk', 'v')
    assert bfr('running', 'VBG') == ('run', 'v')
    assert bfr('smiling', 'VBG') == ('smile', 'v')
    assert bfr('baked', 'VBD') == ('bak', 'v')
    assert bfr('abruptly', 'RB') == ('abrupt', 'ad')
    assert bfr('bigger', 'JJR') == ('big', 'ad')
    assert bfr('highest', 'JJS') == ('high', 'ad')
    assert bfr('pelagic', 'JJ') == ('pelag', 'n')
    assert bfr('childish', 'JJ') == ('child', 'n')
    assert bfr('childlike', 'JJ') == ('child', 'n')
    assert bfr('windy', 'JJ') == ('wind', 'n')
    assert bfr('heavenly', 'JJ') == ('heaven', 'n')
    