from .given_names import abbreviations


def test_1():

    assert abbreviations('J') == {'J', 'J.'}
    assert abbreviations('Miguel') == {'M', 'M.', 'Miguel'}
    assert abbreviations('Miguel Thomas') == {'Miguel Thomas', 'M T.', 'M.T.', 'M. Thomas', 'M. T.', 'Miguel T.', 'M Thomas'}
    assert abbreviations('S.') == {'S', 'S.'}
    assert abbreviations('B. I.') == {'B. I.', 'B.I.', 'B I.'}

    assert abbreviations('John A. T.') == {'J A.T.', 'John A.T.', 'J.A.T.', 'John A. T.', 'J. A. T.', 'J A. T.'}
    assert abbreviations('R. I. C. C.') == {'R I. C. C.', 'R I.C.C.', 'R.I.C.C.', 'R. I. C. C.'}
    assert abbreviations('Radboud J. Duintjer') == {'R.J.D.', 'R.J.Duintjer', 'R. J. D.', 'Radboud J. Duintjer', 'Radboud J. D.', 'R. J. Duintjer', 'Radboud J.D.', 'R J.D.', 'R J. Duintjer', 'R J. D.'}
    assert abbreviations('Karl A. Von') == {'K A.V.', 'Karl A. Von', 'K.A.V.', 'K.A.Von', 'Karl A.V.', 'K A. V.', 'Karl A. V.', 'K A. Von', 'K. A. Von', 'K. A. V.'}
