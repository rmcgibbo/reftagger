import re


def tokenize(text):
    """Very simple word tokenizer.
    """

    # punctuation
    text = re.sub(r'\.\.\.|\.', r' \g<0> ', text)
    text = re.sub(r'[;@#$%&:,?!\(\)"\']', r' \g<0> ', text)

    #parens, brackets, etc.
    text = re.sub(r'--', r' -- ', text)
    text = re.sub(r'([^\s])-([^\s])', r'\g<1> - \g<2>', text)

    #add extra space to make things easier
    text = " " + text + " "

    split = text.split()
    return split


def tokenize_with_pos(text):
    """Variant of ``tokenize`` that also returns the indices in
    ``text`` where each of the tokens begin.
    """

    WHITESPACE = set('\t\r\n ')
    SPECIAL_TOKENS = set(('...', ';', '@', '#', '$', '%', '&', ':', ',',
                          '?', '!', '(', ')', '.', '\"', '\'', '--', '-'))
    LONGEST_SPECIAL_TOKEN = max(len(e) for e in SPECIAL_TOKENS)
    SHORTEST_SPECIAL_TOKEN = min(len(e) for e in SPECIAL_TOKENS)


    def inner():
        current_token_start = None
        current_token = []

        i = 0
        while i < len(text):
            matched_special = False
            for n in range(LONGEST_SPECIAL_TOKEN, SHORTEST_SPECIAL_TOKEN - 1, -1):
                if text[i:i+n] in SPECIAL_TOKENS:
                    matched_special = True
                    break

            if text[i] in WHITESPACE:
                if current_token_start is not None:
                    yield (''.join(current_token), current_token_start)
                    current_token_start = None
                    current_token = []
            elif matched_special:
                if current_token_start is not None:
                    yield (''.join(current_token), current_token_start)
                yield text[i:i+n], i
                i += n-1
                current_token_start = None
                current_token = []
            else:
                if current_token_start is None:
                    current_token_start = i
                current_token.append(text[i])

            i += 1

        if current_token_start is not None:
            yield (''.join(current_token), current_token_start)

    return list(zip(*inner()))


def untokenize(tokens, positions=None):
    if positions is not None:
        return untokenize_with_positions(tokens, positions)
    return untokenize_heuristic(tokens)


def untokenize_with_positions(tokens, positions):
    with_whitespace = []
    length = 0

    for tok, pos in zip(tokens, positions):
        gap = pos - length
        if gap > 0:
            with_whitespace.append(' ' * gap)
            length += gap
        with_whitespace.append(tok)
        length += len(tok)

    return ''.join(with_whitespace)


def untokenize_heuristic(tokens):
    with_whitespace = []
    for i in range(len(tokens)):
        tok = tokens[i]
        with_whitespace.append(tok)

        if tok != '(' and i < len(tokens) - 1:
            if tokens[i+1] not in ('?', ')', ';', '!', ':', ',', '.', '...'):
                with_whitespace.append(' ')

    return ''.join(with_whitespace)



def test_1():
    s = 'Hello   Wo-rld... . sdf; sdf--ddd one.two'
    out1 = tokenize(s)
    out2, pos2 = list(tokenize_with_pos(s))

    assert untokenize(out2, pos2) == s
    assert list(out1) == list(out2)
    assert untokenize(out1) == 'Hello Wo - rld.... sdf; sdf -- ddd one. two'
