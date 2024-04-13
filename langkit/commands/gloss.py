import json
import sys

def wrap_line_with_indent(text, width):
    lines = []
    text = text.rstrip()
    if text:
        for i in range(len(text)):
            if text[i] != ' ':
                break
        if i > 0:
            indent = ' ' * i
        while len(text) > width:
            space_index = text.rfind(' ', 0, width)
            if space_index == -1:
                # If no space found within width, just split at width
                lines.append(text[:width])
                text = indent + text[width:]
            else:
                lines.append(text[:space_index].rstrip())
                text = indent + text[space_index + 1:]
        lines.append(text)
    return '\n'.join(lines)

def wrap_text_with_indent(text, width):
    wrapped = []
    lines = text.split('\n')
    for line in lines:
        wrapped.append(wrap_line_with_indent(line, width))
    return '\n'.join(wrapped)

def display(hits):
    if hits:
        i = 1
        for hit in hits:
            sys.stdout.write(f"\n{i}. " + wrap_text_with_indent(hit.pretty, 79) + '\n')
            i += 1
    else:
        print("Nothing found.")


def prompt(txt):
    sys.stdout.write(f"{txt} > ")
    return input().strip()

def add(g):
    lex = prompt("lexeme?")
    pos = prompt("pos?")
    defn = prompt("definition?")
    hits = g.find_defn(defn.replace(' ', '*'))
    if hits:
        display(hits)
        answer = prompt("There may already be a synonym. Continue? y/N").lower()
        if not answer or not "yes".startswith(answer):
            print("Canceled add.")
            return
    notes = prompt("notes?")
    g.insert(lex, pos, defn, notes)
    g.save()
    print(f"{g.lexeme_count} items in glossary.")

def remind_syntax():
    print('lex <expr>, def <expr>, add, quit')

def cmd(lang, *args):
    """
    - work with glossary
    """
    g = lang.glossary
    print(f"{g.lexeme_count} items in glossary.")
    remind_syntax()
    while True:
        sys.stdout.write('> ')
        args = input().strip().split()
        if args:
            cmd = args[0].lower()
            if "lex".startswith(cmd):
                display(g.find_lexeme(args[1]))
            elif "def".startswith(cmd):
                display(g.find_defn(args[1]))
            elif "add".startswith(cmd):
                add(g)
            elif "quit".startswith(cmd):
                break
            else:
                remind_syntax()
