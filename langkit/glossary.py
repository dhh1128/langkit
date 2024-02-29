import bisect
import os
import re

NARROWER_EQUIV = '>'
BROADER_EQUIV = '<'
ROUGH_EQUIV = '~'
EXPLAINED_EQUIV = ':'
EXACT_EQUIV = ''
EQUIV_CHARS = NARROWER_EQUIV + BROADER_EQUIV + ROUGH_EQUIV + EXPLAINED_EQUIV
EQUIVS_PAT = re.compile(r'\s*([' + EQUIV_CHARS + r'])(.+?)(,|$)')

class DefnItem:
    def __init__(self, txt):
        print(f"txt = {txt}")
        ec = txt[0]
        if ec in EQUIV_CHARS:
            self.kind = ec
            self.value = txt[1:].lstrip()
        else:
            self.kind = EXACT_EQUIV
            self.value = txt.lstrip()
    def __str__(self):
        return self.kind + self.value
    def __lt__(self, other):
        if self.kind == EXACT_EQUIV:
            if other.kind == EXACT_EQUIV:
                return self.value < other.value
            return True
        else:
            if other.kind == EXACT_EQUIV:
                return False
            i = EQUIV_CHARS.index(self.kind)
            j = EQUIV_CHARS.index(other.kind)
            return True if i < j else (False if j < i else self.value < other.value)

class Defn:
    def __init__(self, txt):
        self._equivs = []
        self.parse(txt)

    def parse(self, txt):
        while txt:
            m = EQUIVS_PAT.match(txt)
            if m:
                self._equivs.append(DefnItem(m.group(1) + m.group(2).strip()))
                txt = txt[m.end():]
            else:
                self._equivs.append(DefnItem(txt))
                break
        self._equivs.sort()
        print(f"equivs = {self._equivs}")

    def __str__(self):
        return ', '.join([str(e) for e in self._equivs])

class Entry:
    def __init__(self, fields):
        if isinstance(fields, str):
            fields = fields.split('\t')
        self.word = fields[0]
        self.pos = fields[1]
        self.defn = fields[2]
        if len(fields) > 3 and self.fields[3]:
            self.notes = fields[3]
        else:
            self.notes = None

    def __lt__(self, other):
        return self.word < other.word

    def __str__(self):
        suffix = '' if self.notes is None else '\t' + self.notes 
        return self.word + '\t' + self.pos + '\t' + self.defn + suffix

class Glossary:
    def __init__(self):
        self.fname = None
        self._lang_to_en = []
        self._unsaved = False

    @staticmethod
    def load(fname):
        g = Glossary()
        g.fname = os.path.normpath(os.path.abspath(fname))
        with open(g.fname, 'rt') as f:
            lines = [l.strip() for l in f.readlines()]
        n = 0
        for line in lines:
            n += 1
            if line:
                try:
                    g._lang_to_en.append(Entry(line))
                except:
                    print(f"Couldn't parse line {n}: {line}")
        g._lang_to_en.sort()
        g._en_to_lang = []
        return g
    
    def save(self, fname=None):
        force = False
        if fname is None:
            fname = self.fname
        else:
            fname = os.path.normpath(os.path.abspath(fname))
            if self.fname is None:
                self.fname = fname
            else:
                force = fname != self.fname
        if force or self._unsaved:
            with open(fname, 'wt') as f:
                for entry in self.sorted_entries:
                    f.write(str(entry) + '\n')
                if not force:
                    self._unsaved = False
            return True

    def find_lang(self, word):
        index = bisect.bisect_left(self._lang_to_en, word, key=lambda x: x.word)
        if index < len(self._lang_to_en) and self._lang_to_en[index].word == word:
            return self._lang_to_en[index]
        
    def insert(self, word, pos, defn, notes=None):
        e = Entry((word, pos, defn, notes))
        index = bisect.bisect_left(self._lang_to_en, word, key=lambda x: x.word)
        self._lang_to_en.insert(index, e)
        self._unsaved = True
