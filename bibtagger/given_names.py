import re
import itertools


def abbreviations(given, only_period=False):
    split = given.split()


    if len(split) > 1:
        #a0 = abbreviations(split[0])
        abrvs = (
            abbreviations(s, only_period=i>0)
            for i, s in enumerate(split))
        prod = itertools.product(*abrvs)
        out = {' '.join(item) for item in prod}

        extra = set()
        for o in out:
            if re.search('\.\s\w\.', o):
                extra.add(o.replace('. ', '.'))
        out.update(extra)
        return out


    if len(split) == 1:
        item = split[0]
        first_letter = item[0]

        if only_period:
            return {item, first_letter+'.'}
        else:
            return {item, first_letter, first_letter+'.'}

    raise ValueError(given)
