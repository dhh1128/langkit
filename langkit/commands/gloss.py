from ..ui import *
from ..glossary import Entry, Defn

LEX_COLOR = 'yellow'
POS_COLOR = 'red'
NOTE_COLOR = 'green'
EQUIV_COLOR = 'blue'

def show_entry(e, idx=None):
    if idx:
        cwrite(f"\n{idx}", PROMPT_COLOR)
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

def show_hits(hits, g, with_actions=True):
    if hits:
        i = 1
        for hit in hits:
            show_entry(hit, i)
            i += 1
        if with_actions:
            offer_entry_actions(hits, g)
    else:
        print("Nothing found.")

def offer_entry_actions(hits, g):
    write('\n')
    args = prompt_options('edit #, del #').split()
    try:
        if args:
            cmd = args[0]
            index = int(args[1]) - 1
            if input_matches(cmd, "edit"):
                edit(hits[index], g)
            elif input_matches(cmd, "del"):
                delete(hits[index], g)
    except:
        warn("Bad command.")
        
def delete(entry, g):
    g.entries.remove(entry)
    print(f"Deleted {entry.lexeme}.")

def edit(entry, g):
    try:
        changed = False
        write('\n')
        new = prompt_options(f"   lex: {entry.lexeme}")
        if new: 
            hits = g.find(f'l:{new}', try_fuzzy=False)
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
        new = prompt_options(f"   defn: {entry.defn}")
        if new: changed = entry.defn = Defn(new)
        new = prompt_options(f"   notes: {entry.notes} OR . for none")
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

def add(g):
    added = False
    lex = prompt_options("   lex").strip()
    if lex:
        hits = g.find(f'l:{lex}', try_fuzzy=False)
        if hits:
            show_hits(hits, g, with_actions=False)
            if warn_confirm("Similar words exist. Continue?"):
                hits = None
        if not hits:
            pos = prompt_options("   pos")
            if pos:
                defn = prompt_options("   defn")
                if defn:
                    hits = g.find(f'd:{defn}')
                    if hits:
                        show_hits(hits, g, with_actions=False)
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
        show_stats(g)
    else:
        print("Nothing added.")

def remind_syntax():
    print('lex <expr>, def <expr>, add, edit, quit')

def show_stats(g):
    keys = sorted(g.stats.keys(), reverse=True)
    keys.remove('entries')
    keys.insert(0, 'entries')
    stats = ', '.join([f"{key}: {g.stats[key]}" for key in keys])
    print(wrap_line_with_indent(stats))

def cmd(lang, *args):
    """
    - work with glossary
    """
    g = lang.glossary
    show_stats(g)
    remind_syntax()
    while True:
        args = prompt('\n>').strip().split()
        if args:
            cmd = args[0].lower()
            if input_matches(cmd, "find"):
                show_hits(g.find(' '.join(args[1:])), g)
            elif input_matches(cmd, "add"):
                add(g)
            elif input_matches(cmd, "quit"):
                break
            else:
                remind_syntax()
