from setuptools import setup
setup(
    name='strAItegize-common-package',
    version='0.1',
    description='Package belonging to the common files of the strAItegize project.',
    author='Piotr Kluczyński',
    author_email='peklucz@gmail.com',
    packages=['strAItegize_common'],
    install_requires=[
        'typing',
        'pydantic',
        'uuid',
        'rich',
        'langchain_core'
    ],
)