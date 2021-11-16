import os
import json


DEFS_FOLDER = os.path.normpath(os.path.join(os.path.expanduser('~'), '.langtool'))


def _generate_syllables(pattern, vowels, consonants):
    i = pattern.find('V')
    if i > -1:
        for V in vowels:
            for result in _generate_syllables(pattern[:i] + V + pattern[i + 1:], vowels, consonants):
                yield result
    else:
        i = pattern.find('C')
        if i > -1:
            for C in consonants:
                for result in _generate_syllables(pattern[:i] + C + pattern[i + 1:], vowels, consonants):
                    yield result
        else:
            yield pattern


class Lang:
    def __init__(self, name, data=None):
        self.name = name
        self.folder = os.path.join(DEFS_FOLDER, name)
        self.raw = {}
        if data:
            self.load_data(data)
        else:
            self.load_file()

    @property
    def file(self):
        return os.path.join(DEFS_FOLDER, self.name + '.json')

    def load_file(self):
        with open(self.file, 'rt') as f:
            data = json.loads(f.read())
        self.load_data(data)

    def load_data(self, data):
        if isinstance(data, str):
            data = json.loads(data)
        self.vowels = data.get('vowels', [])
        self.consonants = data.get('consonants', [])
        self.sylpats = data.get('sylpats', [])
        self.dictionary = data.get('dictionary', {})
        self._syl = None

    def save(self):
        data = {
            "vowels": self.vowels,
            "consonants": self.consonants,
            "sylpats": self.syllables,
            "dictionary": self.dictionary
        }
        with open(self.file, 'wt') as f:
            f.write(json.dumps(data))

    @property
    def syllables(self):
        if self._syl is None:
            syl = []
            for pat in self.sylpats:
                for s in _generate_syllables(pat, self.vowels, self.consonants):
                    syl.append(s)
            self._syl = syl
        return self._syl
