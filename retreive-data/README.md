Scripts
-------

1. `download-citations.py`

  This script retreives the main source of training data, the CrossRef records associated
  with random DOIs. It uses the `sample` endpoint from the [CrossRef API](https://github.com/CrossRef/rest-api-doc/blob/master/rest_api.md). It also pulls down
  a styled version of the reference, formatted according to the  `american-chemical-society`,
  `apa`, or whatever.

    `{"URL": "http://dx.doi.org/10.1016/s0300-483x(96)03593-7", "score": 1.0, "issued": {"date-parts": [[1997, 4, 11]]}, "issue": "1", "volume": "119", "ISSN": ["0300-483X"], "prefix": "http://id.crossref.org/prefix/10.1016", "title": ["Animal models in autoimmune disease in immunotoxicity assessment"], "deposited": {"date-parts": [[2011, 7, 11]], "timestamp": 1310342400000}, "member": "http://id.crossref.org/member/78", "container-title": ["Toxicology"], "author": [{"given": "J", "family": "Farine"}], "source": "CrossRef", "subtitle": [], "type": "journal-article", "reference-count": 0, "indexed": {"date-parts": [[2015, 2, 6]], "timestamp": 1423247513443}, "DOI": "10.1016/s0300-483x(96)03593-7", "publisher": "Elsevier BV", "styled": [{"value": "Farine, J. (1997). Animal models in autoimmune disease in immunotoxicity assessment. Toxicology, 119(1), 29-35. doi:10.1016/s0300-483x(96)03593-7", "style": "apa"}, {"value": "Farine, J. Toxicology 1997, 119, 29-35.", "style": "american-chemical-society"}], "page": "29-35", "subject": ["Toxicology"]}`

  These contain both annotated information about a paper, like the journal,
  title, authors, etc, and also the styled reference, as it would be written
  in a paper.

2. `expand-citations.py`

  The styled references typically only include 1 version of the journal title.
  Usually this is the long version (Journal of Organic Chemistry) as opposed
  to the abbreviated title (J. Org. Chem.).

  We want our classifer to be able to handle both, so `expand-citations.py`
  adds new synthetic styled references to each of the entries, by
  find-and-replacing on the journal title and substituting its other variants.

  The output JSON format of `expand-citations.py` and `download-citations.py`
  are the same. `expand-citations.py` just adds a couple entries to the
  list of styled references in each citation.

3. `tag-citations.py`

  This script takes as input the result of `expand-citations.py` (or
  `download-citations.py`)

  It prroduces jsonlines output containing styled citations that have been
  tokenized and tagged.

    {"value": "J. Fransson, A. Talamelli, L. Brandt, and C. Cossu, Phys. Rev. Lett. 96, (2006).", "tagged": [["J.", "given"], ["Fransson", "fam"], [",", "None"], ["A.", "given"], ["Talamelli", "fam"], [",", "None"], ["L.", "given"], ["Brandt", "fam"], [",", "None"], ["and", "None"], ["C.", "given"], ["Cossu", "fam"], [",", "None"], ["Phys.", "journ"], ["Rev.", "journ"], ["Lett.", "journ"], ["96", "vol"], [",", "None"], ["(", "None"], ["2006", "year"], [").", "None"]]}
