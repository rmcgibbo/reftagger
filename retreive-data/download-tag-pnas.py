'''Download and tag training data from the refence section
of random J. Chem. Phys. papers
'''
import time
import sys
import json
import argparse
import requests
import traceback
from bs4 import BeautifulSoup, Tag

from unidecode import unidecode
from bibtagger.tokenizer import tokenize
from bibtagger.print_tokens import render_tokens

unitokenize = lambda x: tokenize(unidecode(x)) if x is not None else []
USER_AGENT = 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'


def main():
    p = argparse.ArgumentParser()
    p.add_argument('-n', help='Number of articles to scrape', type=int, default=2)
    p.add_argument('-v', '--verbose', action="store_true", help='Print out the tagged citations in ASCII colors as they\'re tagged.')
    p.add_argument('dest', help='tokenized and tagged citations (jsonlines)')
    args = p.parse_args()

    with open(args.dest, 'a') as fout:
        for doi, article in sample_pnas(args.n):
            print('\n===== %s ======' % doi)
            for cit in article.find_all('div', {'class': 'cit-metadata'}):
                try:
                    tokens = list(itertokens(cit))
                    if any(len(tok)>5 and tag is None for (tag, tok) in tokens):
                        print('ERROR LONG TOKEN NOT MATCHED IN', render_tokens(tokens), file=sys.stderr)
                        continue

                    if args.verbose:
                        print(render_tokens(tokens))
                        json.dump({'tagged': tokens}, fout)
                    fout.write('\n')
                except UnexpectedTagError as e:
                    print()
                    print(e)
                    print()
                # exit(1)


class UnexpectedTagError(Exception):
    pass


def itertokens(citation_node):
    htmlclass_to_tag = {
        'cit-vol': 'vol',
        'cit-fpage': 'page',
        'cit-lpage': 'page',
        'cit-pub-date':'year',
        # 'reference-source': 'journ',
        'cit-name-surname': 'fam',
        'cit-name-given-names':  'given',
        'cit-jnl-abbrev': 'journ',
        'cit-issue': 'issue',
        'cit-name-suffix': 'fam',
        'cit-article-title': 'title',
    }

    for part in citation_node.children:
        if isinstance(part, str):
            yield from ((None, t) for t in unitokenize(part))
        elif isinstance(part, Tag) and part.name == 'ol':
            for li in part.find_all('li'):
                for part in li.children:
                    if isinstance(part, Tag):
                        for auth_part in part.find_all('span'):
                            yield from ((htmlclass_to_tag[auth_part['class'][0]], t) for t in unitokenize(auth_part.text))
                    else:
                        yield from ((None, t) for t in unitokenize(part))

        elif isinstance(part, Tag) and part.name == 'cite':
            last_class = None
            for item in part.children:
                if isinstance(item, str):
                    tag = 'page' if last_class == 'cit-fpage' else None
                    yield from ((tag, t) for t in unitokenize(item))
                else:
                    if ('class' not in item.attrs) or item['class'][0] not in htmlclass_to_tag:
                        raise UnexpectedTagError(citation_node, item)
                    last_class = item['class'][0]
                    yield from ((htmlclass_to_tag[item['class'][0]], t) for t in unitokenize(item.text))


    # print(list(citation_node.children)[2])
    # exit(1)
    # klass = part['class'][0]

    # exit(1)
    # cit-auth-list

def sample_pnas(n_articles):
    #soup = BeautifulSoup(open('172.full', encoding='utf-8').read(), 'html.parser')
    ## soup = BeautifulSoup(open('untitled.txt',  encoding='utf-8').read())
    #yield '172.full', soup
    # issn for PNAS
    r = requests.get('http://api.crossref.org/works',
        params={'sample': n_articles, 'filter': 'issn:1091-6490'})
    dois = (e['DOI'] for e in r.json()['message']['items'])

    for doi in dois:
        r = requests.get('http://dx.doi.org/%s' % doi, headers={'User-Agent': USER_AGENT})
        soup = BeautifulSoup(r.content, 'html.parser')
        full_text_link = soup.find('a', {'rel': 'view-full-text'})
        if full_text_link is None:
            print(r.url)
            print(r.content)
            print('Skipping. No full text HTML availavle')
            time.sleep(4)
            continue

        r2 = requests.get('http://www.pnas.org' + full_text_link['href'])
        print(r2.url)
        yield doi, BeautifulSoup(r2.content)
        time.sleep(4)



if __name__ == '__main__':
    main()
