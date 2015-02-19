from .tokenizer import tokenize


def tokenize_and_tag(text, chunk_sets):
    # all tokens separated by whitespace
    text = ' '.join(tokenize(text)) + ' '
    tokens = text.split()


    chunks = []
    chunk2tag = []

    for k in chunk_sets:
        for c in chunk_sets[k]:
            tc = tokenize(c)

            # only use chunks if every token within the chunk is actually
            # one of our tokens
            if all(t in tokens for t in tc):
                chunks.append(' '.join(tc) + ' ')
                chunk2tag.append(k)

    labels = greedy_label(text, chunks)
    start_end = []
    tags = []

    # print(text)
    # print(chunks)
    # print()
    # for i, _ in labels:
    #     print(chunks[i])
    # print()
    #
    # print(tokens)
    # print()

    for i in range(len(labels)):
        # print([(tags[t], tokens[t]) for t in range(len(tags))])

        t, start = labels[i]
        end = start + len(chunks[t])
        if i == 0:
            tags.extend([None for _ in tokenize(text[:start])])

        tags.extend([chunk2tag[t] for _ in tokenize(text[start:end])])

        if i < len(labels)-1:
            # interior space between matched blocks
            next_start = labels[i+1][1]
            interspace = text[end:next_start]
            tags.extend([None for _ in tokenize(interspace)])

        if i == len(labels)-1:
            # text after the last matched block
            tags.extend([None for _ in tokenize(text[end:])])

    if len(labels) == 0:
        tags = [None]




    if len(tokens) != len(tags):
        print(text)
        print(len(labels))
        print(chunk_sets)
        print('chunks', chunks)
        print('tokens', tokens)
        print('tags', tags)
        print(list(zip(tags, tokens)))
        assert False


    return tokens, tags


def greedy_label(text, chunks):
    """Find non-overlapping chunks in text.

    Parameters
    ----------
    text : str
    chunks : list of str

    Returns
    -------
    matches : list of 2-tuples
        Each element in the returned list is a length-2 tuple `(i, j)` s.t.
        `i` is the index of the matching chunk and `j` is the index in
        `text` where the substring match begins.

    Example
    -------
    >>> text = 'hello hello; world'
    >>> greedy_label(text, ['hello', 'world'])
    [(0, 0), (0, 6), (1, 13)]

    # the semantics of the return value is that chunk[0] matches begining
    # at text[0], then chunk[0] matches again at beggining text[6], and then
    # chunk[1] matches beginning at text[13].
    """
    stack = []

    p = 0
    while True:
        gap = {}
        matchlength = {}

        # for label, ch in chunks.items():
        for label, ch in enumerate(chunks):
            if len(ch) > 0:
                i = text.find(ch, p)
                if i > -1:
                    gap[label] = i-p
                    matchlength[label] = len(ch)

        if len(gap) == 0:
            # we're at the end of the text, with no more
            # matching chunks in text[p:]
            break

        # sort the chunks that match text[p:]. we want to pick the one that
        # introduces the smallest gap. if two chunks both introduce the
        # same gap, then we take the one that's longest.
        label = min(gap.keys(), key=lambda k: (gap[k], -matchlength[k]))
        stack.append((label, p+gap[label]))
        p += gap[label] + matchlength[label]

    return stack

