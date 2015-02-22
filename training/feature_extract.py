"""This script takes tagged citations (training data) as produced by
`retreive-data/tag-citations.py` and does feature extraction, producing
the direct input data for the CRF model.

The features are word prefixes and suffixes, whether or not they
contain digits or dots, their lengths, and their relationship to the
words forward and backward in the sequence.
"""
import re
import sys
import json
import pickle
import argparse
from os.path import dirname, abspath, join, isfile
from collections import Counter

PROJECT_ROOT = join(dirname(abspath(__file__)), '..')
sys.path.insert(0, PROJECT_ROOT)
from bibtagger.featurize import featurize


def main():
    p = argparse.ArgumentParser(description=__doc__,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    p.add_argument('source', nargs='+', help='Tokenize and tagged citations (jsonlines format)')
    p.add_argument('dest', help='Featurized training data (pkl format)')
    p.add_argument('-n', '--n-rare', help='Minimum number of occurances of a '
        'token to label it \'rare\'.', type=int, default=10)

    args = p.parse_args()
    if isfile(args.dest):
        p.error('File exists. %s' % args.dest)

    phrases, y = [], []

    for source in args.source:
        with open(source, 'r') as f:
            for i, line in enumerate(f):
                item = json.loads(line)['tagged']
                if len(item) > 0:
                    yy, xx = zip(*item)
                    phrases.append(xx)
                    y.append([str(tag) for tag in yy])

    print('Featurizing')
    X = []
    for i, phrase in enumerate(phrases):
        if i % 100 == 0:
            print('%d/%d' % (i, len(phrases)))
        X.append(featurize(phrase))

    #print('len(X)', len(X))
    #print('len(y)', len(y))
    #print(X[0])
    #print(y[0])


    with open(args.dest, 'wb') as fout:
        pickle.dump({
            'X': X,
            'y': y,
        }, fout)


if __name__ == '__main__':
    main()

