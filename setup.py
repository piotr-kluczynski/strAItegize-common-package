from setuptools import setup, find_packages
setup(
    name='strAItegize-common-package',
    version='0.1',
    description='Package belonging to the common files of the strAItegize project.',
    author='Piotr Kluczyński',
    author_email='peklucz@gmail.com',
    packages=find_packages(),
    install_requires=[
        'pydantic',
        'rich',
        'langchain_core'
    ],
)