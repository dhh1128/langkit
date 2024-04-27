import os

from ..ui import *
from ..tcoach import *

coach = None

def give_hints(coach, text):
    column = 1
    width = get_terminal_size()[0]
    for hint in coach.hints(text):
        out = hint.lex if hint.lex else str(hint)
        if column + len(out) >= width:
            print()
            column = 1
        if column > 1:
            write(' ')
            column += 1
        if hint.lex:
            cwrite(out, LEX_COLOR)
        else:
            write(out)
        column += len(out)
    print('')

def cmd(lang, *args):
    """
    [FNAME | SENTENCE] - help with translation
    """
    global coach
    coach = TranslationCoach(lang.glossary)
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
