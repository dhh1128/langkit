import bisect
import os

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
        self.entries = []
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
                print(line)
                try:
                    g.entries.append(Entry(line))
                except:
                    print(f"Couldn't parse line {n}: {line}")
        g.entries.sort()
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

    def find(self, word):
        index = bisect.bisect_left(self.entries, word, key=lambda x: x.word)
        if index < len(self.entries) and self.entries[index].word == word:
            return self.entries[index]
        
    def insert(self, word, pos, defn, notes=None):
        e = Entry((word, pos, defn, notes))
        index = bisect.bisect_left(self.entries, word, key=lambda x: x.word)
        self.entries.insert(index, e)
        self._unsaved = True
