'''Download and tag training data from the refence section
of random J. Chem. Phys. papers
'''
import json
import argparse
import requests
import traceback
from bs4 import BeautifulSoup, Tag

from unidecode import unidecode
from bibtagger.tokenizer import tokenize
from bibtagger.print_tokens import render_tokens

unitokenize = lambda x: tokenize(unidecode(x)) if x is not None else []


def main():
    p = argparse.ArgumentParser()
    p.add_argument('-n', help='Number of articles to scrape', type=int, default=2)
    p.add_argument('-v', '--verbose', action="store_true", help='Print out the tagged citations in ASCII colors as they\'re tagged.')
    p.add_argument('dest', help='tokenized and tagged citations (jsonlines)')
    args = p.parse_args()

    with open(args.dest, 'a') as fout:
        for doi, article in sample_jcp(args.n):
            print('\n===== %s ======' % doi)
            for cit in article.find_all('div', {'class': 'citation'}):
                try:
                    tokens = list(itertokens(cit))
                    if args.verbose:
                        print(render_tokens(tokens))
                        json.dump({'tagged': tokens}, fout)
                    fout.write('\n')
                except UnexpectedTagError as e:
                    print()
                    print(e)
                    print()


class UnexpectedTagError(Exception):
    pass


def itertokens(citation_node):
    xmltag_to_ourtag = {
        'reference-volume': 'vol',
        'reference-fpage': 'page',
        'reference-year':'year',
        'reference-source': 'journ',
        'reference-surname': 'fam',
        'reference-given-names': 'given',
        'reference-issue': 'issue',
        'reference-suffix': 'fam',
        'reference-article-title': 'title',
    }

    tags_seen = set()
    children = list(citation_node.children)
    while len(children) > 0:
        part = children.pop(0)

        if isinstance(part, Tag):
            try:
                klass = part['class'][0]
            except:
                raise UnexpectedTagError(str(citation_node), part)


            if klass in ('citation-label', 'group-citation-label'):
                pass
            elif klass == 'reference-fpage':
                fpage = part.text
                if len(children) > 1 and children[1]['class'][0] == 'reference-lpage':
                    middle = children.pop(0)
                    part = children.pop(0)
                    lpage = part.text
                    yield from (('page', t) for t in unitokenize(fpage + middle + lpage))
                else:
                    yield from (('page', t) for t in unitokenize(fpage))
            else:
                if klass not in xmltag_to_ourtag:
                    raise UnexpectedTagError(str(citation_node), klass)
                else:
                    tags_seen.add(xmltag_to_ourtag[klass])

                yield from ((xmltag_to_ourtag[klass], t) for t in unitokenize(part.text))
        else:
            if 'given' in tags_seen:
                yield from ((None, t) for t in unitokenize(part))


def sample_jcp(n_articles):
    # issn for J. Chem. Phys.
    r = requests.get('http://api.crossref.org/works',
        params={'sample': n_articles, 'filter': 'issn:1089-7690'})

    dois = (e['DOI'] for e in r.json()['message']['items'])

    for doi in dois:
        r = requests.get('http://dx.doi.org/%s' % doi)
        yield doi, BeautifulSoup(r.content)

if __name__ == '__main__':
    main()
