from setuptools import setup, find_packages

setup(
    name='reftag',
    author='Robert McGibbon',
    author_email='rmcgibbo@gmail.com',
    url='http://github.com/rmcgibbo/reftagger',
    packages=find_packages(),
    package_data={'bibtagger': ['fixeddata/*']},
)
