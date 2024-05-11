import bisect
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

irregular_past_parts = [
    ("awoken", "awake"),
    ("been", "be"),
    ("begun", "begin"),
    ("bent", "bend"),
    ("bitten", "bite"),
    ("bought", "buy"),
    ("bound", "bind"),
    ("broken", "break"),
    ("built", "build"),
    ("burnt", "burn"),
    ("caught", "catch"),
    ("chosen", "choose"),
    ("done", "do"),
    ("driven", "drive"),
    ("dwelt", "dwell"),
    ("eaten", "eat"),
    ("fallen", "fall"),
    ("fed", "feed"),
    ("felt", "feel"),
    ("fled", "flee"),
    ("flown", "fly"),
    ("forgotten", "forget"),
    ("found", "find"),
    ("frozen", "freeze"),
    ("given", "give"),
    ("gone", "go"),
    ("ground", "grind"),
    ("heard", "hear"),
    ("held", "hold"),
    ("hidden", "hide"),
    ("knelt", "kneel"),
    ("known", "know"),
    ("laid", "lay"),
    ("lain", "lie"),
    ("lit", "light"),
    ("meant", "mean"),
    ("overcome", "overcome"),
    ("overthrown", "overthrow"),
    ("paid", "pay"),
    ("pleaded", "plead"),
    ("proven", "prove"),
    ("ridden", "ride"),
    ("risen", "rise"),
    ("sawn", "saw"),
    ("seen", "see"),
    ("sent", "send"),
    ("shaken", "shake"),
    ("shone", "shine"),
    ("shorn", "shear"),
    ("shot", "shoot"),
    ("shown", "show"),
    ("slept", "sleep"),
    ("slid", "slide"),
    ("smelt", "smell"),
    ("sown", "sow"),
    ("spent", "spend"),
    ("spilt", "spill"),
    ("spoilt", "spoil"),
    ("spoken", "speak"),
    ("stolen", "steal"),
    ("stood", "stand"),
    ("stridden", "stride"),
    ("struck", "strike"),
    ("stuck", "stick"),
    ("sung", "sing"),
    ("swept", "sweep"),
    ("swollen", "swell"),
    ("sworn", "swear"),
    ("swum", "swim"),
    ("taken", "take"),
    ("taught", "teach"),
    ("thought", "think"),
    ("thrown", "throw"),
    ("told", "tell"),
    ("torn", "tear"),
    ("understood", "understand"),
    ("wept", "weep"),
    ("woken", "wake"),
    ("won", "win"),
    ("worn", "wear"),
    ("wound", "wind"),
    ("written", "write"),
]

irregular_past = [
    ("ate", "eat"),
    ("began", "begin"),
    ("bit", "bite"),
    ("bought", "buy"),
    ("broke", "break"),
    ("brought", "bring"),
    ("built", "build"),
    ("came", "come"),
    ("caught", "catch"),
    ("chose", "choose"),
    ("dealt", "deal"),
    ("did", "do"),
    ("drank", "drink"),
    ("dreamt", "dream"),
    ("drew", "draw"),
    ("drove", "drive"),
    ("fed", "feed"),
    ("fell", "fall"),
    ("felt", "feel"),
    ("flew", "fly"),
    ("forgave", "forgive"),
    ("forgot", "forget"),
    ("fought", "fight"),
    ("found", "find"),
    ("froze", "freeze"),
    ("gave", "give"),
    ("got", "get"),
    ("grew", "grow"),
    ("had", "have"),
    ("heard", "hear"),
    ("held", "hold"),
    ("hid", "hide"),
    ("hit", "hit"),
    ("hung", "hang"),
    ("hurt", "hurt"),
    ("kept", "keep"),
    ("knew", "know"),
    ("laid", "lay"),
    ("led", "lead"),
    ("left", "leave"),
    ("lent", "lend"),
    ("let", "let"),
    ("lit", "light"),
    ("lost", "lose"),
    ("made", "make"),
    ("meant", "mean"),
    ("met", "meet"),
    ("paid", "pay"),
    ("put", "put"),
    ("ran", "run"),
    ("rang", "ring"),
    ("read", "read"),
    ("rode", "ride"),
    ("rose", "rise"),
    ("said", "say"),
    ("sang", "sing"),
    ("sank", "sink"),
    ("sat", "sit"),
    ("saw", "see"),
    ("sent", "send"),
    ("set", "set"),
    ("shone", "shine"),
    ("shook", "shake"),
    ("shot", "shoot"),
    ("showed", "show"),
    ("shut", "shut"),
    ("slept", "sleep"),
    ("slid", "slide"),
    ("smelt", "smell"),
    ("sold", "sell"),
    ("sought", "seek"),
    ("sowed", "sow"),
    ("spat", "spit"),
    ("spent", "spend"),
    ("spoke", "speak"),
    ("spread", "spread"),
    ("spun", "spin"),
    ("stole", "steal"),
    ("stood", "stand"),
    ("struck", "strike"),
    ("stuck", "stick"),
    ("stung", "sting"),
    ("stunk", "stink"),
    ("swam", "swim"),
    ("swept", "sweep"),
    ("swore", "swear"),
    ("swung", "swing"),
    ("taught", "teach"),
    ("thought", "think"),
    ("threw", "throw"),
    ("told", "tell"),
    ("took", "take"),
    ("tore", "tear"),
    ("understood", "understand"),
    ("went", "go"),
    ("wept", "weep"),
    ("withdrew", "withdraw"),
    ("woke", "wake"),
    ("won", "win"),
    ("wore", "wear"),
    ("wound", "wind"),
    ("wrote", "write"),
    ("wrung", "wring"),
 ]

def find_regular(pairs, irregular):
    index = bisect.bisect_left(pairs, (irregular, ""))
    if index != len(pairs):
        found = pairs[index]
        if found[0] == irregular:
            return found[1]

def bfr(word, pos):
    """
    Generate possible base forms of a word, and a new part of speech, given
    the inflected word and its part of speech.

    This algorithm is very crude. It only aims to increase the success
    of glossary lookup a modest amount.
    """
    if pos == 'VBD': # verb past tense: gave, walked
        regular = find_regular(irregular_past, word)
        if regular: return (regular, 'v')
        if word.endswith('ed'): return (word[:-2], 'v')
    elif pos == 'VBG': # verb gerund/present participle: walking
        if word.endswith('ing'):
            word = word[:-3]
            # Undo doubled consonants if present (e.g., swimming)
            return (word[:-1], 'v') if word[-1] == word[-2] else (word, 'v')
    elif pos == 'VBN': # verb past participle: given, walked
        regular = find_regular(irregular_past_parts, word)
        if regular: return (regular, 'v')
        if word.endswith('ed'): return (word[:-2], 'v')
    elif pos == 'VBP': # verb non-3rd person singular present: walk
        if word in ['are', 'am']: return ('be', 'v')
    elif pos == 'VBZ': # verb 3rd person singular present: walks
        if word.endswith('s'):
            return ('be', 'v') if word == 'is' else (word[:-1], 'v')
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
    def __init__(self, word, pos, lemma=None, approx=False):
        assert bool(pos) or bool(lemma)
        self.word = word
        self.pos = pos
        self.lemma = lemma
        self.approx = approx
    def __str__(self):
        return self.lemma if self.lemma else f"{self.word} ({self.pos}): ?"
    def __repr__(self):
        return f"{self.word} pos={self.pos} lemma={self.lemma} approx={self.approx}"
    
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
            # externally loaded custom logic on a per-language basis.
            if self.advise_func:
                pos_tags = self.advise_func(pos_tags)

            # Now do the general translation work: look up each word in the glossary.
            i = 0
            for tag in pos_tags:
                entry = None
                approx = False
                word, pos = tag
                
                # Skip the word "to" followed by an uninflected verb; we will
                # end up looking up the uninflected verb in the glossary without
                # looking up "to" before it.
                if pos == "TO" and i < len(pos_tags) - 1 and pos_tags[i + 1][1] == 'VB':
                    i += 1
                    continue 

                # nltk says that the part of speech of punctuation is just the
                # punctuation itself. If we find these tokens, then the lemma
                # (the term the glossary would produce) is just the same as the
                # token, and no further processing is needed.
                if not pos[0].isalpha():
                   lemma = word
                else:
                    # Normalize case; glossary should have lower-case form of word.
                    word = word.lower()
                    # See if we can convert from nltk parts of speech to the ones used
                    # by lk (LangKit). If yes, we can use POS to look up the word in the
                    # glossary with higher precision.
                    lk_pos = find_by_nltk(pos)
                    if lk_pos and lk_pos.lk:
                        # Lk might have more than one POS for a given nltk category;
                        # look for the word in glossary definitions using each POS
                        # until we find a match.
                        for x in lk_pos.lk.split():
                            expr = f'p:{x} d:{word}'
                            entry = self._find(expr)
                            if entry:
                                pos = x
                                break
                    if not entry:
                        # Try looking up the exact word, without a part of speech.
                        entry = self._find(f'd:{word}')
                        if not entry:
                            # Try doing base form reduction on the word. This
                            # will uninflect verbs, among other things.
                            bfr_word, new_pos = bfr(word, tag[1])
                            if bfr_word:
                                expr = f'p:{new_pos} d:{bfr_word}'
                                entry = self._find(expr)
                                if entry:
                                    pos = new_pos
                                    approx = True
                    lemma = None
                    if entry:
                        lemma = entry if isinstance(entry, str) else entry.lemma
                yield Hint(word, pos, lemma, approx)
                i += 1
