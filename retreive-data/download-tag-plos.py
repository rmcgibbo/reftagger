'''Download and tag training data from the refence section
of random PLoS ONE papers
'''
import json
import argparse
import requests
import traceback
from xml.etree import ElementTree as ET

from unidecode import unidecode
from bibtagger.tokenizer import tokenize
from bibtagger.print_tokens import render_tokens

unitokenize = lambda x: tokenize(unidecode(x)) if x is not None else []


def main():
    # itertokens
    p = argparse.ArgumentParser(description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('-n', help='Number of articles to scrape', type=int, default=2)
    p.add_argument('-v', '--verbose', action="store_true", help='Print out the tagged citations in ASCII colors as they\'re tagged.')
    p.add_argument('dest', help='tokenized and tagged citations (jsonlines)')
    args = p.parse_args()

    with open(args.dest, 'a') as fout:
        # pull random articles
        for doi, article in sample_plos_xml(args.n):
            # get all of the citations from the articles
            references = article.findall('back/ref-list/ref/mixed-citation')

            if args.verbose:
                print('\n\n==== PULLING FROM DOI %s ====\n' % doi)

            for ref in references:
                if ref.get('publication-type') != 'journal':
                    continue

                # tokenize each citation
                try:
                    tokens = list(itertokens(ref))
                    if args.verbose:
                        print(render_tokens(tokens))

                    json.dump({'tagged': tokens}, fout)
                    fout.write('\n')
                except UnexpectedTagError:
                    traceback.print_exc()


class UnexpectedTagError(Exception):
    pass


def itertokens(citation_node):
    xmltag_to_ourtag = {
        'volume': 'vol',
        'year':'year',
        'source': 'journ',
        'surname': 'fam',
        'given-names': 'given',
        'suffix': 'given',
        'article-title': 'title',
        'etal': None,
        'issue': 'issue',
        'issue-id': 'issue',
    }

    children = citation_node.getchildren()
    while len(children) > 0:
        part = children.pop(0)
        if part.tag == 'person-group':
            children = part.getchildren() + children
            part = children.pop(0)

        if part.tag in ('name'):
            for name_part in part.getchildren():
                assert name_part.tail is None
                for tok in unitokenize(name_part.text):
                    yield (xmltag_to_ourtag[name_part.tag], tok)

        elif part.tag in ('year', 'article-title', 'source', 'volume', 'etal', 'issue'):
            for tok in unitokenize(part.text):
                yield (xmltag_to_ourtag[part.tag], tok)

        elif part.tag == 'fpage':
            fpage, middle = part.text, part.tail
            if len(children) > 0 and children[0].tag == 'lpage':
                part = children.pop(0)
                lpage = part.text
                for tok in unitokenize(fpage + middle + lpage):
                    yield ('page', tok)
            else:
                for tok in unitokenize(fpage):
                    yield ('page', tok)
        elif part.tag == 'comment':
            pass

        else:
            ET.dump(citation_node)
            raise UnexpectedTagError('unexpected tag', part.tag)


        if part.tail is not None:
            for tok in unitokenize(part.tail):
                yield (None, tok)


def sample_plos_xml(n_articles):
    # issn for PLoS One
    r = requests.get('http://api.crossref.org/works',
        params={'sample': n_articles, 'filter': 'issn:1932-6203'})

    dois = (e['DOI'] for e in r.json()['message']['items'])

    for doi in dois:
        # print(doi)
        r = requests.get('http://journals.plos.org/plosone/article/asset',
                params={'id': doi+'.XML'})
        yield doi, ET.fromstring(r.content)


if __name__ == '__main__':
    main()
