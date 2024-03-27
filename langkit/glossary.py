import bisect
import os
import re

NARROWER_EQUIV = '>'
BROADER_EQUIV = '<'
ROUGH_EQUIV = '~'
EXPLAINED_EQUIV = ':'
EXACT_EQUIV = ''
EQUIV_CHARS = NARROWER_EQUIV + BROADER_EQUIV + ROUGH_EQUIV + EXPLAINED_EQUIV
EQUIVS_PAT = re.compile(r'\s*([' + EQUIV_CHARS + r'])(.+?)(\||$)')

class DefnItem:
    def __init__(self, txt):
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
        self.equivs = []
        self.parse(txt)

    def parse(self, txt):
        while txt:
            m = EQUIVS_PAT.match(txt)
            if m:
                self.equivs.append(DefnItem(m.group(1) + m.group(2).strip()))
                txt = txt[m.end():]
            else:
                self.equivs.append(DefnItem(txt))
                break
        self.equivs.sort()

    def __str__(self):
        return ' | '.join([str(e) for e in self.equivs])
    
class SearchExpr:
    def __init__(self, expr):
        self.expr = expr
        i = expr.find('*')
        j = expr.find('?')
        if i > -1:
            if j > -1:
                self._i = min(i, j)
            else:
                self._i = i
        elif j > -1:
            self._i = j
        else:
            self._i = -1
        self._regex = None if self._i == -1 else re.compile(expr.replace('?', '.').replace('*', '.*?'))

    @property
    def wildcarded(self):
        return self._i > -1

    @property
    def starter(self):
        return self.expr if self._i == -1 else self.expr[:self._i]

    def matches(self, txt):
        return self._regex.match(txt) if self._regex else (self.expr == txt)

class Entry:
    def __init__(self, fields):
        if isinstance(fields, str):
            fields = fields.split('\t')
        self.lexeme = fields[0]
        self.pos = fields[1]
        self.defn = Defn(fields[2])
        if len(fields) > 3 and self.fields[3]:
            self.notes = fields[3]
        else:
            self.notes = None

    def __lt__(self, other):
        return self.lexeme < other.lexeme

    def __str__(self):
        suffix = '' if self.notes is None else '\t' + self.notes 
        return self.lexeme + '\t' + self.pos + '\t' + self.defn + suffix

class Glossary:
    def __init__(self):
        self.fname = None
        self._lexeme_to_en = []
        self._unsaved = False
        self._en_to_lang = []

    @property
    def lexeme_count(self):
        return len(self._lexeme_to_en)

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
                    g._lexeme_to_en.append(Entry(line))
                except:
                    print(f"Couldn't parse line {n}: {line}")
        g._lexeme_to_en.sort()
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

    def find_lexeme(self, expr, max_hits=5):
        hits = []
        expr = SearchExpr(expr)
        initial_search = expr.starter
        index = bisect.bisect_left(self._lexeme_to_en, initial_search, key=lambda x: x.lexeme) if initial_search else 0
        while index < self.lexeme_count and max_hits != 0:
            entry = self._lexeme_to_en[index]
            if expr.matches(entry.lexeme):
                hits.append(entry)
                max_hits -= 1
            index += 1
        return hits
    
    def find_defn(self, expr, max_hits=5):
        hits = []
        expr = SearchExpr(expr)
        index = 0
        while index < self.lexeme_count and max_hits != 0:
            entry = self._lexeme_to_en[index]
            defn = entry.defn
            for item in entry.defn.equivs:
                if expr.matches(item.value):
                    hits.append(entry)
                    max_hits -= 1
            index += 1
        return hits
        
    def insert(self, lexeme, pos, defn, notes=None):
        e = Entry((lexeme, pos, defn, notes))
        index = bisect.bisect_left(self._lexeme_to_en, lexeme, key=lambda x: x.lexeme)
        self._lexeme_to_en.insert(index, e)
        self._unsaved = True
