import string
import gzip
import functools
from pprint import pprint
from os.path import join, dirname, abspath
from pkg_resources import resource_filename
from nltk.corpus import wordnet as wn

DIGITS = set([str(e) for e in range(10)])
UPPERCASE = set(string.ascii_uppercase)
REFERENCE_DATA = resource_filename('bibtagger', 'fixeddata')

with gzip.open(join(REFERENCE_DATA, 'common-given-names.txt.gz')) as f:
    COMMON_GIVEN_NAMES = frozenset({e.strip().decode('utf-8').lower() for e in f.readlines()})
with gzip.open(join(REFERENCE_DATA,'common-surnames.txt.gz')) as f:
    COMMON_SURNAMES = frozenset({e.strip().decode('utf-8').lower() for e in f.readlines()})
with gzip.open(join(REFERENCE_DATA, 'common-words.txt.gz')) as f:
    COMMON_WORDS = frozenset({e.strip().decode('utf-8').lower() for e in f.readlines()})


def common_hypernym(synsets):
    """Walk up the hypernym tree above a collection of WordNet synsets
    finding the first (hyper) synset that's in COMMON_WORDS.
    """
    if len(synsets) == 0:
        return ''

    names = {l.name().split('_')[0].lower() for syn in synsets for l in syn.lemmas()}
    intersect = names.intersection(COMMON_WORDS)
    if len(intersect) > 0:
        # just deterministically pick one of the words to use. we'll
        # take the shortest.
        return min(intersect, key=len)
    else:
        hypersets = [hyper for s in synsets for hyper in s.hypernyms()]
        return common_hypernym(hypersets)


def featurize(phrase):
    @functools.lru_cache(maxsize=1024)
    def get_local_features(word):
        word_lower = word.lower()

        hypernym = ''
        in_wordnet = 'NA'
        if len(word) > 4:
            synsets = wn.synsets(word)
            in_wordnet = len(synsets) > 0
            hypernym = common_hypernym(wn.synsets(word))

        return {
            'word': word,
            'prefix4': word[:4],
            'hypernym': hypernym,
            'in_wordnet': in_wordnet,
            'common_given': word_lower in COMMON_GIVEN_NAMES,
            'common_surname': word_lower in COMMON_SURNAMES,
            'cont_num': len(set(word).intersection(DIGITS)) > 0,
            'all_num': all(l in DIGITS for l in word),
        }

    n = len(phrase)
    local_features = [get_local_features(word) for word in phrase]
    shift_features = [{} for _ in local_features]

    for i in range(1, n):
        shift_features[i].update({k+'[-1]': v for k, v in local_features[i-1].items()})
    for i in range(n-1):
        shift_features[i].update({k+'[+1]': v for k, v in local_features[i+1].items()})

    features = []
    for i in range(n):
        features.append(
            ['%s=%s' % (k,v) for k, v in local_features[i].items()] +
            ['%s=%s' % (k,v) for k, v in shift_features[i].items()]
        )
    features[0].append('__BOS__')
    features[-1].append('__EOS__')



    return features
