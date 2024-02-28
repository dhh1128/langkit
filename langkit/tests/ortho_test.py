from ..ortho import *

def test_simple():
    o = Orthography({'a': 'A', 'b': 'B'})
    assert o.from_ipa('appleb') == 'AppleB'
    assert o.to_ipa('AppleB') == 'appleb'

def test_doubles():
    o = Orthography({'tʃ': 'T', 'ʃ': 'SH', 't': '*', 'a': 'A', 'b': 'B', 'c': 'CH'})
    assert o.from_ipa('appleb') == 'AppleB'
    assert o.to_ipa('AppleB') == 'appleb'
    assert o.from_ipa('atʃb') == 'ATB'
    assert o.from_ipa('atʃtʃb') == 'ATTB'
    assert o.from_ipa('attʃb') == 'A*TB'
    assert o.from_ipa('atʃʃb') == 'ATSHB'
    assert o.from_ipa('atxʃb') == 'A*xSHB'
    assert o.from_ipa('atxʃbc') == 'A*xSHBCH'
    assert o.to_ipa('ATB') == 'atʃb' 
    assert o.to_ipa('ATTB') == 'atʃtʃb'
    assert o.to_ipa('A*TB') == 'attʃb'
    assert o.to_ipa('ATSHB') == 'atʃʃb'
    assert o.to_ipa('A*xSHB') == 'atxʃb'
    assert o.to_ipa('A*xSHBCH') == 'atxʃbc'
    assert o.to_ipa('A*xSHBcCH') == 'atxʃbcc'
    assert o.to_ipa('A*xSHBCCH') == 'atxʃbCc'
    assert o.to_ipa('A*xSHBCHH') == 'atxʃbcH'
