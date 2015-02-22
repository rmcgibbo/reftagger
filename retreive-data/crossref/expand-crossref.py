"""Create _new_ styled entries from data download by `download-citations.py`
from each variant of the `container-title` entry.

For example, say we download the following AIP styled citation:

{
 'container-title': ['Pesq. agropec. bras.',
                     'Pesquisa Agropecuaria Brasileira'],
 'styled': [
     {'style': 'american-institute-of-physics',
     'value': 'N.P. Stamford, C.E. de R. e S. Santos, R. Medeiros, '
              'and A.D.S. de Freitas, Pesquisa Agropecuaria '
              'Brasileira 34, 1831 (1999).'}]
}

This script will create a new entry in the `styled` list containing the
reference with the other `container-title`.

"""
import json
import copy
import argparse
from unidecode import unidecode
from pprint import pprint


def main():
    p = argparse.ArgumentParser(description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('source', help='Input (jsonlines)')
    p.add_argument('dest', help='Output (jsonlines)')
    args = p.parse_args()

    with open(args.source, 'r') as fin, open(args.dest, 'w') as fout:
        for i, line in enumerate(fin):
            if (i % 100) == 0:
                print('LINE %d' % i)

            newcit = expand_journal_abbreviations(json.loads(line))
            json.dump(newcit, fout)
            fout.write('\n')


def expand_journal_abbreviations(cit):
    if len(cit['container-title']) <= 1:
        return cit

    container_titles = list(map(unidecode, cit['container-title']))
    new_styled = []

    for s in cit['styled']:
        for ct in container_titles:
            if s['value'].find(ct) != -1:
                for jj, ot in enumerate(container_titles):
                    new_value = s['value'].replace(ct, ot)
                    if all(new_value != ss['value'] for ss in cit['styled']):

                        new_styled.append({
                            'value': new_value,
                            'style': s['style'] + '-abbrev-%d' % jj
                        })

    cit['styled'].extend(new_styled)
    return cit


if __name__ == '__main__':
    main()
