"""Download random citations from the CrossRef DOI system (over their API),
including both the JSON metadata for the reference _and_ the styled citation
in one or more formats (American Chemical Society, AIP, APA, etc).

Each citation will be written as a line to the outputfile in JSON format
(jsonlines).
"""

# Example record
# {'DOI': '10.1016/s0300-483x(96)03593-7',
#  'prefix': 'http://id.crossref.org/prefix/10.1016',
#  'member': 'http://id.crossref.org/member/78',
#  'indexed': {'date-parts': [[2015, 2, 6]], 'timestamp': 1423247513443},
#  'deposited': {'date-parts': [[2011, 7, 11]], 'timestamp': 1310342400000},
#  'publisher': 'Elsevier BV',
#  'title': ['Animal models in autoimmune disease in immunotoxicity assessment'],
#  'ISSN': ['0300-483X'],
#  'score': 1.0,
#  'container-title': ['Toxicology'],
#  'subject': ['Toxicology'],
#  'reference-count': 0,
#  'author': [{'given': 'J', 'family': 'Farine'}],
#  'URL': 'http://dx.doi.org/10.1016/s0300-483x(96)03593-7',
#  'issue': '1',
#  'volume': '119',
#  'issued': {'date-parts': [[1997, 4, 11]]},
#  'subtitle': [],
#  'styled': [{'value': 'Farine, J. (1997). Animal models in autoimmune disease in immunotoxicity assessment. Toxicology, 119(1), 29-35. doi:10.1016/s0300-483x(96)03593-7',
#    'style': 'apa'},
#   {'value': 'Farine, J. Toxicology 1997, 119, 29-35.',
#    'style': 'american-chemical-society'}],
#  'page': '29-35',
#  'type': 'journal-article',
#  'source': 'CrossRef'}

import re
import json
import argparse
import requests
from pprint import pprint
from unidecode import unidecode


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    p.add_argument('file', help='File to append citations to (jsonlines format)')
    p.add_argument('-n', help='Number of citations to download', type=int, default=100)
    args = p.parse_args()

    # might want to customize this later.
    # STYLES = ['nature', 'american-chemical-society', 'american-institute-of-physics']
    # STYLES = ['organization']
    STYLES = ['society-of-biblical-literature-fullnote-bibliography']

    with open(args.file, 'a') as f:
        for item in sample(n=args.n, styles=STYLES):
            json.dump(item, f, sort_keys=True)
            f.write('\n')
            f.flush()


def get_styled(doi, styles=['american-chemical-society']):
    """Get the styled citation for a given DOI from CrossRef

    Example
    -------
    >>> get_styled('10.1016/s0300-483x(96)03593-7')
    [{'style': 'american-chemical-society', 'value': 'Farine, J. Toxicology 1997, 119, 29-35.'}]
    """

    out = []
    for style in styles:
        fmt = 'text/x-bibliography; style=%s' % style
        r = requests.get('http://dx.doi.org/%s' % doi, headers={'Accept': fmt})
        # content is utf-8 encoded. To simplify the downstream stuff, we convert
        # non-ascii unicode characters to "nearest" ascii characters using
        # unidecode.
        c = unidecode(r.content.decode('utf-8'))

        strip_prefixes = ['(1)', '1.', '1']
        for p in strip_prefixes:
            if c.startswith(p):
                c = c[len(p):]

        c = c.replace('Online: http://dx.doi.org/' , '')
        c = c.replace(doi + '.', '')
        c = c.replace(' No pages.', '')

        out.append({'style': style, 'value': c.strip()})

    return out


def sample(n=10, styles=['american-chemical-society', 'apa', 'nature']):
    def skip(item):
        if item['subtitle'] != []:
            # skip everything with a subtitle
            return True

        if len(item['title']) != 1:
            # title should be a list containing 1 string
            return True

        if len(item['title'][0].split()) < 2:
            # skip 1 word titles
            return True
        return False


    r = requests.get('http://api.crossref.org/works',
        params={'sample': n, 'filter': 'type:journal-article'})
    items = r.json()['message']['items']
    items = [x for x in items if not skip(x)]
    for item in items:
        item['styled'] = get_styled(item['DOI'], styles)
        pprint(item)
        print()
        yield item


if __name__ == '__main__':
    main()
