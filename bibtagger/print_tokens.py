from termcolor import colored

COLORMAP = {
    'page': 'red',
    'vol': 'magenta',
    'year': 'cyan',
    'journ': 'yellow',
    'given': 'magenta',
    'fam': 'red',
    None: 'white',
    'title': 'green',
    'issue': 'green',
 }


def render_tokens(tags_and_tokens):
    line = []
    n_tokens = len(tags_and_tokens)
    for i in range(n_tokens):
        tag, tok = tags_and_tokens[i]
        line.append(colored(tok, color=COLORMAP[tag]))
        if tok == '(':
            continue
        if i < n_tokens-1:
            tok1 = tags_and_tokens[i+1][1]
            if tok1 not in [',', ')', ';', ':', '.']:
                line.append(' ')
    return ''.join(line)
