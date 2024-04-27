from ..pos import find_nltk

def test_find_nltk():
    assert find_nltk('JJ').lk == 'ad'
    assert find_nltk('JJ').descrip == 'adjective'
    assert find_nltk('does not exist') == None