import string
import gzip
import functools
from pprint import pprint
from os.path import join, dirname, abspath
from pkg_resources import resource_filename

import marisa_trie
from nltk.corpus import wordnet as wn
from bibtagger.tokenizer import untokenize, tokenize

def _load_reference(fname, lower=False):
    with gzip.open(resource_filename('bibtagger', join('fixeddata', fname))) as f:
        items = set()
        for line in f:
            line = line.strip().decode('utf-8')
            if lower:
                line = line.lower()
            items.add(line)
        return frozenset(items)


DIGITS = set([str(e) for e in range(10)])
UPPERCASE = set(string.ascii_uppercase)
COMMON_GIVEN_NAMES = _load_reference('common-given-names.txt.gz')
COMMON_SURNAMES = _load_reference('common-surnames.txt.gz', lower=True)
COMMON_WORDS = _load_reference('common-words.txt.gz')
JOURNAL_SET = _load_reference('journals.txt.gz')
JOURNAL_TRIE = marisa_trie.Trie(JOURNAL_SET)


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

    for i in range(n):
        local_features[i]['known_journal'] = False
    for i in range(n):
        matches = JOURNAL_TRIE.prefixes(untokenize(phrase[i:]))
        for match in matches:
            for j, tok in enumerate(tokenize(match)):
                local_features[i+j]['known_journal'] = True

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


if __name__ == '__main__':
    from pprint import pprint
    item = {"tagged": [
        ["fam", "Massague"], ["given", "J"], [None, ","], ["fam", "Seoane"],
        ["given", "J"], [None, ","], ["fam", "Wotton"], ["given", "D"],
        [None, "("], ["year", "2005"], [None, ")"], ["title", "Smad"],
        ["title", "transcription"], ["title", "factors"], [None, "."],
        ["journ", "Genes"], ["journ", "Dev"], ["vol", "19"], [None, ":"],
        ["page", "2783"], ["page", "-"], ["page", "2810"], [None, "."]]
    }
    features = featurize([e[1] for e in item['tagged']])
    pprint(features[15])
