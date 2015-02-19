import re


def tokenize(text):
    """Very simple word tokenizer.
    """

    # punctuation
    text = re.sub(r'\.\.\.', r' ... ', text)
    text = re.sub(r'[;@#$%&:,?!\(\)\."\']', r' \g<0> ', text)

    #parens, brackets, etc.
    text = re.sub(r'--', r' -- ', text)
    text = re.sub(r'-', r' - ', text)

    #add extra space to make things easier
    text = " " + text + " "

    return text.split()
