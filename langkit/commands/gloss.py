from ..ui import *

LEX_COLOR = 'yellow'
POS_COLOR = 'red'
NOTE_COLOR = 'green'
EQUIV_COLOR = 'blue'

def show_hits(hits):
    if hits:
        i = 1
        for hit in hits:
            cwrite(f"\n{i}", PROMPT_COLOR)
            write(". ")
            cwrite(hit.lexeme, LEX_COLOR)
            write(" (")
            cwrite(hit.pos, POS_COLOR)
            write(")")
            for equiv in hit.defn.equivs:
                cwrite('\n   * ', EQUIV_COLOR)
                print(equiv)
            if hit.notes:
                cwrite('\n')
                cprint(wrap_line_with_indent('   # ' + hit.notes), NOTE_COLOR)
            print('')
            i += 1
    else:
        print("Nothing found.")

def add(g):
    added = False
    lex = prompt("  lexeme?")
    if lex:
        hits = g.find_lexeme("*" + lex)
        if hits:
            show_hits(hits)
            answer = prompt("Similar words exist. Continue? y/N", WARNING_COLOR).lower()
            if answer and "yes".startswith(answer):
                hits = None
        if not hits:
            pos = prompt("  pos?")
            if pos:
                defn = prompt("  definition?")
                if defn:
                    hits = g.find_defn('*' + defn.replace(' ', '*'))
                    if hits:
                        show_hits(hits)
                        answer = prompt("There may already be a synonym. Continue? y/N", WARNING_COLOR).lower()
                        if answer and "yes".startswith(answer):
                            hits = None
                    if not hits:
                        notes = prompt("  notes?")
                        g.insert(lex, pos, defn, notes)
                        g.save()
                        added = True
    if added:
        cwrite("Added ")
        cwrite(lex, LEX_COLOR)
        cwrite('.\n\n')
        show_stats(g)
    else:
        print("Nothing added.")

def remind_syntax():
    print('lex <expr>, def <expr>, add, quit')

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
        args = prompt('>').strip().split()
        if args:
            cmd = args[0].lower()
            if "lex".startswith(cmd):
                show_hits(g.find_lexeme(args[1]))
            elif "def".startswith(cmd):
                show_hits(g.find_defn(args[1]))
            elif "add".startswith(cmd):
                add(g)
            elif "quit".startswith(cmd):
                break
            else:
                remind_syntax()
