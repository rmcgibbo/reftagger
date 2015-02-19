from .chunker import greedy_label, tokenize_and_tag


def test_1():
    text = 'hello hello ; world'
    chunks = ['hello', 'hello ;', 'world', 'sdf']
    assert greedy_label(text, chunks) == [(0, 0), (1, 6), (2, 14)]


def test_2():
    text = 'A.B.; J. Chem. Phys.'
    chunk_sets = {
        'label_AB': ['A.B.'],
        'label_J': ['J. Chem. Phys.'],}

    tokens, tags = tokenize_and_tag(text, chunk_sets)
    assert tokens == ['A', '.', 'B', '.', ';', 'J', '.', 'Chem', '.', 'Phys', '.']
    assert tags == ['label_AB', 'label_AB', 'label_AB', 'label_AB', None, 'label_J', 'label_J', 'label_J', 'label_J', 'label_J', 'label_J']


def test_3():
    text = 'a A.B.; J. Chem. Phys. b'
    chunk_sets = {
        'label_AB': ['A.B.'],
        'label_J': ['J. Chem. Phys.'],}

    tokens, tags = tokenize_and_tag(text, chunk_sets)
    z = list(zip(tokens, tags))
    assert z == [
        ('a', None), ('A', 'label_AB'),
        ('.', 'label_AB'), ('B', 'label_AB'),
        ('.', 'label_AB'), (';', None),
        ('J', 'label_J'), ('.', 'label_J'),
        ('Chem', 'label_J'), ('.', 'label_J'),
        ('Phys', 'label_J'), ('.', 'label_J'),
        ('b', None)]


def test_4():
    text = 'Farine, J. (1997). Title. Toxicology, 119(1), 29-35.'
    chunk_sets = {
        'family': ['Farine'],
        'given': ['J.'],
        'year': ['1997'],
        'title': ['Title'],
        'journal': ['Toxicology'],
    }
    chunk_sets = {
        'page': ['29-35', '29', '35'],
        'year': ['1997'],
        'fam': ['Farine'],
        'journ': ['Toxicology'],
        'vol': ['119'],
        'given': ['J.'],
        'title': ['Title']
    }
    tokens, tags = tokenize_and_tag(text, chunk_sets)
    z = list(zip(tokens, tags))
    print(z)


def test_5():
    text = 'Jafelicci Jr . , M . , & Loh , W . ( 1999 ) . Editorial . Journal of the Brazilian Chemical Society , 10 ( 5 ) .'
    chunks = ['10', 'Editorial', 'Jafelicci', 'Jr .', 'Loh', 'Braz', 'Chem', 'Soc', 'Journal', 'of', 'the', 'Brazilian', 'Chemical', 'Society', '', '', 'M .', 'W .', '1999']
    greedy_label(text, chunks)


def test_6():
    text = '03'
    chunk_sets = {0: ['0'], 3: ['3']}
    tokenize_and_tag(text, chunk_sets)


def test_7():
    text = 'A . Dow and R . Pichardo - Mendoza , Topology and Its Applications 160 , 2207 ( 2013 ) .'
    chunk_sets = {
        'title': ["Efimov's problem and Boolean algebras"],
        'given': {'A', 'A.', 'Alan', 'R', 'R.', 'Roberto'},
        'fam': ['Dow', 'Pichardo-Mendoza'],
        'journ': ['Topology and Its Applications'],
        'vol': ['160'],
        'page': ['2207-2231', '2207'],
        'issue': ['17'],
        'year': ['2013']
    }
    tokens, tags = tokenize_and_tag(text, chunk_sets)
    z = list(zip(tokens, tags))
    assert z == [('A', 'given'), ('.', 'given'), ('Dow', 'fam'),
        ('and', None), ('R', 'given'), ('.', 'given'),
        ('Pichardo', 'fam'), ('-', 'fam'), ('Mendoza', 'fam'),
        (',', None), ('Topology', 'journ'), ('and', 'journ'),
        ('Its', 'journ'), ('Applications', 'journ'), ('160', 'vol'),
        (',', None), ('2207', 'page'), ('(', None), ('2013', 'year'),
        (')', None), ('.', None)]
