import bisect
import os
import re

NARROWER_EQUIV = '>'
BROADER_EQUIV = '<'
ROUGH_EQUIV = '~'
EXPLAINED_EQUIV = ':'
EXACT_EQUIV = ''
EQUIV_CHARS = NARROWER_EQUIV + BROADER_EQUIV + ROUGH_EQUIV + EXPLAINED_EQUIV
EQUIVS_PAT = re.compile(r'\s*([' + EQUIV_CHARS + r'])(.+?)(/|$)')
COLUMNS = ['lexeme', 'pos', 'definition', 'notes']
COLUMN_COUNT = len(COLUMNS)
COLUMN_SEP = ' | '
HEADER = COLUMN_SEP.join(COLUMNS)
DIVIDER = re.sub('[a-zA-Z]', '-', HEADER)
DIVIDER_PAT = re.compile(r'\s*' + r"\s*\|\s*".join(['-+']*len(COLUMNS)) + r'\s*')

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
        return ' / '.join([str(e) for e in self.equivs])
    
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
            fields = [f.strip() for f in fields.split('|')]
        self.lexeme = fields[0]
        self.pos = fields[1]
        self.defn = Defn(fields[2])
        if len(fields) > 3 and fields[3]:
            self.notes = fields[3]
        else:
            self.notes = ''

    def __lt__(self, other):
        return self.lexeme < other.lexeme

    def __str__(self):
        suffix = '' if self.notes is None else COLUMN_SEP + self.notes 
        return self.lexeme + COLUMN_SEP + self.pos + COLUMN_SEP + str(self.defn) + suffix

def _is_header(entry: Entry) -> bool:
    return entry.lexeme == COLUMNS[0]

_DIVIDER_LEX_PAT = re.compile('-{2,}$')
def _is_divider(entry: Entry) -> bool:
    return _DIVIDER_LEX_PAT.match(entry.lexeme)

class Glossary:
    def __init__(self):
        self.pre = ''
        self.fname = None
        self._lexeme_to_gloss = []
        self._unsaved = False
        self._gloss_to_lexeme = []
        self.post = ''

    @property
    def lexeme_count(self):
        return len(self._lexeme_to_gloss)

    @staticmethod
    def load(fname):
        g = Glossary()
        g.fname = os.path.normpath(os.path.abspath(fname))
        with open(g.fname, 'rt') as f:
            lines = f.readlines()
        pre = True
        found_header = False
        found_divider = False
        found_nonblank_post = False
        n = 0
        for line in lines:
            stripped = line.strip()
            n += 1
            entry = '|' in stripped
            if entry:
                e = None
                try:
                    e = Entry(stripped)
                    pre = False
                except Exception as ex:
                    entry = False
                    if g.lexeme_count:
                        pre = False
                if e:
                    if _is_header(e):
                        if found_header or found_divider:
                            raise Exception(f"Didn't expect header on line {n}.")
                        found_header = True
                    elif _is_divider(e):
                        if found_divider or not found_header:
                            raise Exception(f"Didn't expect divider on line {n}.")
                        found_divider = True
                    else:
                        if found_nonblank_post:
                            raise Exception(f"Didn't expect a new entry on line {n}.")
                        g._lexeme_to_gloss.append(e)
                        g.post = ''
            if not entry:
                if pre:
                    g.pre += line
                else:
                    if line.strip():
                        found_nonblank_post = True
                    g.post += line
        g._lexeme_to_gloss.sort()
        return g
    
    def save(self, fname=None, handle=None):
        force = bool(handle)
        if fname is None:
            fname = self.fname
        else:
            fname = os.path.normpath(os.path.abspath(fname))
            if self.fname is None:
                self.fname = fname
            else:
                force = fname != self.fname
        if force or self._unsaved:
            f = handle
            if not f:
                f = open(fname, 'wt')
            try:
                if self.pre.strip():
                    f.write(self.pre)
                f.write(HEADER + '\n' + DIVIDER + '\n')
                for entry in self._lexeme_to_gloss:
                    f.write(str(entry) + '\n')
                if self.post.strip():
                    f.write(self.post)
                if not force:
                    self._unsaved = False
            finally:
                if not handle:
                    f.close()
            return True

    def find_lexeme(self, expr, max_hits=5):
        hits = []
        expr = SearchExpr(expr)
        initial_search = expr.starter
        index = bisect.bisect_left(self._lexeme_to_gloss, initial_search, key=lambda x: x.lexeme) if initial_search else 0
        while index < self.lexeme_count and max_hits != 0:
            entry = self._lexeme_to_gloss[index]
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
            entry = self._lexeme_to_gloss[index]
            defn = entry.defn
            for item in entry.defn.equivs:
                if expr.matches(item.value):
                    hits.append(entry)
                    max_hits -= 1
            index += 1
        return hits
        
    def insert(self, lexeme, pos, defn, notes=None):
        e = Entry((lexeme, pos, defn, notes))
        index = bisect.bisect_left(self._lexeme_to_gloss, lexeme, key=lambda x: x.lexeme)
        self._lexeme_to_gloss.insert(index, e)
        self._unsaved = True
