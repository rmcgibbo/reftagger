"""Tag the syled citations downloaded by `download-citations.py`

The output is written as jsonlines, with one line per reference. The lines
have structure like the following. The entry `tagged` in the line gives
the tokenized-and-tagged version of the free-form styled citation
(in `value`).

{'tagged': [['J.', 'given'], ['Fransson', 'fam'],
  [',', 'None'], ['A.', 'given'],
  ['Talamelli', 'fam'], [',', 'None'],
  ['L.', 'given'], ['Brandt', 'fam'], [',', 'None'],
  ['and', 'None'],  ['C.', 'given'],
  ['Cossu', 'fam'],  [',', 'None'],
  ['Physical', 'journ'],  ['Review', 'journ'],
  ['Letters', 'journ'],   ['96', 'vol'],
  [',', 'None'],  ['(', 'None'],
  ['2006', 'year'], [')', 'None']],
 'value': 'J. Fransson, A. Talamelli, L. Brandt, and C. Cossu, Physical Review Letters 96, (2006).'}
"""
import json
import re
import string
import argparse
import sys
import traceback
from os.path import abspath, dirname, join, commonprefix
from difflib import SequenceMatcher
from pprint import pprint

from titlecase import titlecase
from termcolor import colored
from unidecode import unidecode

from bibtagger.tokenizer import tokenize
from bibtagger.chunker import tokenize_and_tag
from bibtagger.given_names import abbreviations


def main():
    p = argparse.ArgumentParser(description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('source', help='source : DOI metadata and styled citations for each reference (jsonlines)')
    p.add_argument('dest', help='dest : tokenized and tagged citations (jsonlines)')
    p.add_argument('-v', '--verbose', action="store_true", help='Print out the tagged citations in ASCII colors as they\'re being tagged. This helps a lot to debug')
    args = p.parse_args()

    with open(args.source, 'r') as fin, open(args.dest, 'a') as fout:
        for i, line in enumerate(fin):
            if (i % 50 == 0):
                print('LINE %d' % i)

            item = json.loads(line)

            # the styled string should not have any html in it. this
            # means that CrossRef messed up
            if any('<?xml' in s['value'] or 'http://' in s['value'] for s in item['styled']):
                print('SKIPPING GARBAGE ITEM')
                print(item['styled'])
                continue


            props = extract_properties(item)
            if props is None:
                continue

            for s in item['styled']:
                tagged = tag_citation(s['value'], props, verbose=args.verbose)
                if tagged is None:
                    continue

                json.dump({'value': s['value'], 'tagged': tagged}, fout)
                fout.write('\n')


def extract_properties(item):
    """Extract a dict of properties from a the DOI metadata for a citation.
    The keys are the different tags within the citation, and the values are
    tokens that (should/could) indicate that tag.

    Example
    -------
    {'title': ['Shorter', 'Notices'],
     'given': ['P.'],
     'journ': ['Eng', 'Hist', 'Rev', 'The', 'English', 'Historical', 'Review'],
     'page': ['976-977', '976', '977'],
     'fam': ['HORDEN'],
     'vol': ['CVI'],
     'year': ['1991']}
     """
    if 'author' not in item:
        return None
    if any('family' not in a or 'given' not in a for a in item['author']):
        return None

    def author_given(item):
        out = set()
        for auth in item['author']:
            out.update(abbreviations(unidecode(auth['given'])))
        return out



    try:
        page = [item.get('page', '')]
        if '-' in page[0]:
            page_from, page_to = page[0].split('-')
            page.append(page_from)
            page.append('%s-%s' % (page_from, page_to[-2:]))

        assert len(item['title']) == 1
        title = unidecode(item['title'][0])

        props = {
            'page': page,
            'vol': [item.get('volume', '')],
            'year': [str(item['issued']['date-parts'][0][0])],
            'journ': [unidecode(j) for j in item['container-title']],
            'given': author_given(item),
            'title': [title, titlecase(title)],
            'fam': [unidecode(part) for auth in item['author'] for part in auth['family'].split()],
            'issue': [item.get('issue', '')],
        }
    except ValueError as e:
        # caused by given names that are more than 2 words.
        # print('ERROR', file=sys.stderr)
        # traceback.print_exc()
        print('-----')
        print(e)
        print(item['styled'])
        print('----')
        # raise
        return None

    return props


def tag_citation(text, props, verbose=True):
    def skip(w):
        return 'doi' in w

    text = ' '.join([e for e in text.split() if not skip(e)])
    tokens, tags = tokenize_and_tag(text, props)


    if verbose:
        c = {'page': 'red', 'vol': 'magenta', 'year': 'cyan', 'journ': 'yellow',
             'given': 'magenta', 'fam': 'red', None: 'white', 'title': 'green',
             'issue': 'green'}

        line = []
        n_tokens = len(tokens)
        for i in range(n_tokens):
            tok = tokens[i]
            line.append(colored(tok, color=c[tags[i]]))
            if tok == '(':
                continue
            if i < n_tokens-1:
                tok1 = tokens[i+1]
                if tok1 not in [',', ')', ';', ':', '.']:
                    line.append(' ')
        print(''.join(line))

    if not any(t=='journ' for t in tags):
        print('ERROR NO JOURNAL ENTRY MATCHED IN', text, file=sys.stderr)
        #print(props, file=sys.stderr)
        print()
        return None

    if any(len(tok)>5 and tag is None for (tok, tag) in zip(tokens, tags)):
        print('ERROR LONG TOKEN NOT MATCHED IN', text, file=sys.stderr)
        print(props, file=sys.stderr)
        print()
        return None


    return list(zip(tokens, tags))

if __name__ == '__main__':
    main()
