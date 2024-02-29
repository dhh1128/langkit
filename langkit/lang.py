import os
import json

from .glossary import Glossary

CFG_NAME = 'cfg.json'
GLOSSARY_NAME = 'glossary.txt'

def _FIXgenerate_syllables(pattern, vowels, consonants):
    i = pattern.find('V')
    if i > -1:
        for V in vowels:
            for result in _FIXgenerate_syllables(pattern[:i] + V + pattern[i + 1:], vowels, consonants):
                yield result
    else:
        i = pattern.find('C')
        if i > -1:
            for C in consonants:
                for result in _FIXgenerate_syllables(pattern[:i] + C + pattern[i + 1:], vowels, consonants):
                    yield result
        else:
            yield pattern


class Lang:
    def __init__(self, path):
        self.path = os.path.normpath(os.path.abspath(path))
        self.name = os.path.split(self.path)[1]
        self._syl = None
        if os.path.isfile(self.cfg_path):
            with open(self.cfg_path, 'rt') as f:
                self.cfg = json.loads(f.read())
        else:
            self.cfg = {}
        if os.path.isfile(self.gloss_path):
            self.glossary = Glossary.load(self.gloss_path)

    @property
    def cfg_path(self):
        return os.path.join(self.path, CFG_NAME)
    
    @property
    def gloss_path(self):
        return os.path.join(self.path, GLOSSARY_NAME)
    
    @property
    def sylpats(self):
        return self.cfg.get('sylpats', ['V', 'CV'])

    @property
    def vowels(self):
        return self.cfg.get('vowels', ['a', 'i'])

    @property
    def consonants(self):
        return self.cfg.get('consonants', ['k', 't', 'm'])

    @property
    def syllables(self):
        if self._syl is None:
            syl = []
            for pat in self.sylpats:
                for s in _FIXgenerate_syllables(pat, self.vowels, self.consonants):
                    syl.append(s)
            self._syl = syl
        return self._syl
