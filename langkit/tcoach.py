from collections import namedtuple
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize

from .pos import find_by_nltk, PLACEHOLDER

# Download NLTK resources if needed.
if not nltk.data.find('tokenizers/punkt'):
    nltk.download('punkt', quiet=True)
if not nltk.data.find('taggers/averaged_perceptron_tagger'):
    nltk.download('averaged_perceptron_tagger', quiet=True)

SimpleNormalizationRule = namedtuple('SimpleNormalizationRule', ['pattern', 'replacement'])
SimpleNormalizationRule.apply = lambda self, text: text.replace(self.pattern, self.replacement)
def snr(pattern, replacement): return SimpleNormalizationRule(pattern, replacement)

NRules = [
    snr('’', "'"),
    snr('“', '"'),
    snr('”', '"'),
    snr("won't", "will not"),
    snr("can't", "cannot"),
    snr("n't", ' not'),
    snr("'re", ' are'),
    snr("y'all", 'you all'),
    snr("'ll", " will"),
]

def bfr(word, pos):
    """
    Generate possible base forms of a word, and a new part of speech, given
    the inflected word and its part of speech.

    This algorithm is very crude. It only aims to increase the success
    of glossary lookup a modest amount.
    """
    if pos == 'VBD':
        if word.endswith('ed'): return (word[:-2], 'v')
    elif pos == 'VBG':
        if word.endswith('ing'):
            word = word[:-3]
            return (word[:-1], 'v') if word[-1] == word[-2] else (word, 'v')
    elif pos == 'VBN':
        if word.endswith('en') or word.endswith('ed'): return (word[:-2], 'v')
    elif pos == 'VBP':
        if word in ['are', 'am']: return ('be', 'v')
    elif pos == 'VBZ':
        if word.endswith('s'):
            return ('be', 'v') if word == 'is' else (word[:-1], 'v')
        if word == 'are': return ('be', 'v')
    elif pos == 'RB':
        if word.endswith('ly'): return (word[:-2], 'ad')
    elif pos == 'JJR':
        if word.endswith('er'):
            word = word[:-2]
            return (word[:-1], 'ad') if word[-1] == word[-2] else (word, 'ad')
    elif pos == 'JJS':
        if word.endswith('est'): return (word[:-3], 'ad')
    elif pos == 'JJ':
        if word.endswith('ly'): return (word[:-2], 'n')
        if word.endswith('ic'): return (word[:-2], 'n')
        if word.endswith('ish'): return (word[:-3], 'n')
        if word.endswith('like'): return (word[:-4], 'n')	
        if word.endswith('y'): return (word[:-1], 'n')
    elif pos.startswith('NN'):
        modified = False
        if word.endswith('ies'): return (word[:-3] + 'y', 'n') #bodies
        if word.endswith('s') and pos == 'NNS': 
            word = word[:-1] #smiles
            modified = True
        if word.endswith('tion'): return (word[:-4], 'v') #creation
        if word.endswith('or'): return (word[:-2], 'v') #sailor
        if word.endswith('er'): return (word[:-2], 'v') #farmer
        if modified: return (word, 'n')
    return None, None

class Hint:
    """
    Represents a hint about how to translate an English word.
    """
    def __init__(self, word, pos, lex=None, approx=False):
        assert bool(pos) or bool(lex)
        self.word = word
        self.pos = pos
        self.lex = lex
        self.approx = approx
    def __str__(self):
        return self.lex if self.lex else f"{self.word} ({self.pos}): ?"
    def __repr__(self):
        return f"{self.word} pos={self.pos} lex={self.lex} approx={self.approx}"
    
class TranslationCoach:
    """
    Coaches on translation from English into a given language.
    """
    def __init__(self, glossary, advise_func=None):
        self.glossary = glossary
        self.advise_func = advise_func

    def _find(self, expr):
        hits = self.glossary.find(expr)
        if hits:
            return hits[0]
        # Automatically try putting verbs in infinitive form.
        elif 'p:v' in expr and 'd:to ' not in expr:
            expr = expr.replace('d:', 'd:to ')
            hits = self.glossary.find(expr)
            if hits:
                return hits[0]

    def hints(self, paragraph):
        for nr in NRules:
            text = nr.apply(paragraph)

        sentences = sent_tokenize(paragraph)
        for sentence in sentences:

            # Tokenize the sentence into words
            words = word_tokenize(sentence)

            # Perform POS tagging
            pos_tags = nltk.pos_tag(words)

            # See if an adviser will help us translate this sentence. This allows
            # custom logic on a per-language basis.
            if self.advise_func:
                pos_tags = self.advise_func(pos_tags)

            # Now do the general translation work: look up each word in the glossary.
            for tag in pos_tags:
                entry = None
                # See if we can convert from nltk parts of speech to our own.
                # If so, then we can use part of speech to look up the word in the
                # glossary with high precision.
                pos = tag[1]
                if tag[1] == PLACEHOLDER.nltk:
                   lex = tag[0]
                else:
                    approx = False
                    lk_pos = find_by_nltk(pos)
                    if lk_pos and lk_pos.lk:
                        # We might have more than one POS for a given nltk category;
                        # try them all until we find a match.
                        for x in lk_pos.lk.split():
                            pos = x
                            expr = f'p:{x} d:{tag[0]}'
                            entry = self._find(expr)
                            if entry:
                                break
                    if not entry:
                        # Try looking up the exact word, without a part of speech.
                        entry = self._find(f'd:{tag[0]}')
                        if not entry:
                            # Try doing base form reduction on the word
                            word, new_pos = bfr(tag[0], tag[1])
                            if word:
                                expr = f'p:{new_pos} d:{word}'
                                entry = self._find(expr)
                                if entry:
                                    pos = new_pos
                                    approx = True
                    lex = None
                    if entry:
                        lex = entry if isinstance(entry, str) else entry.lexeme
                yield Hint(tag[0], pos, lex, approx)
