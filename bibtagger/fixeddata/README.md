Auxiliary Data
==============

These are data files that are not _exactly_ part of the training set, since they
they're not parsed citations. They're used in the token featurization to provide
semantically rich features that should make the classification more accurate.

1. `common-surnames.txt.gz`

    All surnames appearing 100 or more times in the 2000 US cencus. There are
    151671 of them, written in all caps. They're stored in flat text with
    newline separators. They were downloaded from this census.gov website

    http://www.census.gov/topics/population/genealogy/data/2000_surnames.html


2. `common-given-names.txt.gz`

    Common given (first) names, from the US Social Security Administration. I
    summed the counts accross the years of birth and took the the 1000 most
    common names. The data is from

    http://www.ssa.gov/oact/babynames/limits.html


3. `common-words.txt.gz`

    5000 most common english words. Newline separated. Data is from

    http://norvig.com/ngrams/count_1w.txt


4. `journals.txt.gz`

    List of journal titles, including both the full name, MedLine abbreviation
    and ISO abbreviation. There are a total of 52274 unique entries. The data
    comes from the PubMed and NCBI Molecular Biology Database Journals list.

    http://www.ncbi.nlm.nih.gov/books/NBK3827/table/pubmedhelp.pubmedhelptable45/


5. [WordNet](http://wordnet.princeton.edu/)

    We also use wordnet, through the `nltk` interface. See `featurize.py`.

