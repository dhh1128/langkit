import os

from ..ui import *
from ..tcoach import *

def give_hints(coach, text):
    column = 1
    width = get_terminal_size()[0]
    for hint in coach.hints(text):
        if get_verbose():
            out = repr(hint) + ' '
        else:
            out = hint.lex if hint.lex else str(hint)
            if column + len(out) >= width:
                print()
                column = 1
            if column > 1:
                write(' ')
                column += 1
        if hint.lex and not get_verbose():
            color = EQUIV_COLOR if hint.approx else LEX_COLOR
            cwrite(out, color)
        else:
            write(out)
        column += len(out)
    print('')

def cmd(lang, *args):
    """
    [-v] [FNAME | SENTENCE] - help with translation
    """
    global coach
    coach = TranslationCoach(lang.glossary)
    if args and args[0] == '-v':
        set_verbose(True)
        args = args[1:]
    if not args:
        while True:
            text = prompt(">")
            if text:
                if input_matches(text, "quit"):
                    break
                give_hints(coach, text)
    elif len(args) == 1 and os.path.isfile(args[0]):
        with open(args[0], 'r') as f:
            text = f.read()
        give_hints(coach, text)
    else:
        text = ' '.join(args)
        give_hints(coach, text)
