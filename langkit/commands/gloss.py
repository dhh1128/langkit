import re

from ..ui import *
from ..glossary import Entry, Defn

g = None
hits = []

def find(expr, try_fuzzy=True):
    global g, hits
    hits = g.find(expr, try_fuzzy=try_fuzzy)

def show_entry(e, num=None):
    if num:
        cwrite(f"\n{num}", PROMPT_COLOR)
        write(". ")
    cwrite(e.lexeme, LEX_COLOR)
    write(" (")
    cwrite(e.pos, POS_COLOR)
    write(")")
    for equiv in e.defn.equivs:
        cwrite('\n   * ', EQUIV_COLOR)
        write(equiv)
    if e.notes:
        write('\n')
        cwrite(wrap_line_with_indent('   # ' + e.notes), NOTE_COLOR)
    print('')

def show_hits(which=None, with_number=True):
    if not which:
        global hits
        which = hits
    if which:
        i = 1
        for hit in which:
            show_entry(hit, i if with_number else None)
            i += 1
        return True

def delete(entry):
    global g
    g.entries.remove(entry)
    print(f"Deleted {entry.lexeme}.")

def edit(entry):
    global g
    try:
        changed = False
        write('\n')
        new = prompt_options(f"   lex: {entry.lexeme}")
        if new: 
            hits = g.find(f'l:{new}')
            if hits:
                warn("Edit would overwrite {lex} entry that already exists.")
                return
            changed = entry.lexeme = new
            # Since lexeme has changed, it may sort differently.
            # Take it out of glossary entry list, then re-add it
            # to maintain proper sort order.
            g.entries.remove(entry)
            g.insert(entry)
        new = prompt_options(f"   pos: {entry.pos}")
        if new: changed = entry.pos = new
        new = prompt_options(f"   defn: {entry.defn} (/ to append)")
        if new:
            if new.startswith('/'):
                new = str(entry.defn) + ' ' + new 
            changed = entry.defn = Defn(new)
        notes = entry.notes if entry.notes else '.'
        new = prompt_options(f"   notes: {notes} (. = none)")
        if new:
            if new == '.': 
                new = ''
                changed = bool(entry.notes)
            else:
                changed = True
            entry.notes = new
        if changed:
            g.save(force=True)
            print("\nUpdated entry.")
        else:
            print("\nNo changes.")
    except KeyboardInterrupt:
        print("\n\nAbandoned edit.")

def add():
    global g
    added = False
    lex = prompt_options("   lex").strip()
    if lex:
        hits = g.find(f'l:{lex}!', try_fuzzy)
        if hits:
            show_hits(hits, with_number=False)
            if warn_confirm("Similar words exist. Continue?"):
                hits = None
        if not hits:
            pos = prompt_options("   pos")
            if pos:
                defn = prompt_options("   defn")
                if defn:
                    hits = g.find(f'd:*!{defn}')
                    if hits:
                        show_hits(hits, with_number=False)
                        if warn_confirm("There may already be a synonym. Continue?"):
                            hits = None
                    if not hits:
                        notes = prompt_options("   notes")
                        g.insert(Entry((lex, pos, defn, notes)))
                        g.save()
                        added = True
    if added:
        write("Added ")
        cwrite(lex, LEX_COLOR)
        write('.\n\n')
        show_stats()
    else:
        print("Nothing added.")

def remind_syntax():
    print('find <expr>, add, edit #, del #, quit')

def show_stats():
    global g
    keys = sorted(g.stats.keys(), reverse=True)
    keys.remove('entries')
    keys.insert(0, 'entries')
    stats = ', '.join([f"{key}: {g.stats[key]}" for key in keys])
    print(wrap_line_with_indent(stats))

SHORT_ENTRY_CMD_PAT = re.compile(r'^([ed])(\d+)$')

def cmd(lang, *args):
    """
    - work with glossary
    """
    global g
    g = lang.glossary
    show_stats()
    remind_syntax()
    while True:
        args = prompt('\n>').strip().split()
        if args:
            cmd = args[0].lower()

            # Tolerate a very short form, like e1 for edit 1
            m = SHORT_ENTRY_CMD_PAT.match(cmd)
            if m:
                cmd = m.group(1)
                args.insert(1, m.group(2))

            if input_matches(cmd, "find"):
                find(' '.join(args[1:]))
                if not show_hits():
                    print("Nothing found.")
            elif input_matches(cmd, "add"):
                add()
            elif input_matches(cmd, "edit"):
                if len(args) == 1 and len(hits) == 1: args.append('1')
                edit(hits[int(args[1])-1])
            elif input_matches(cmd, "delete"):
                if len(args) == 1 and len(hits) == 1: args.append('1')
                delete(hits[int(args[1])-1])
            elif input_matches(cmd, "quit"):
                break
            else:
                remind_syntax()
