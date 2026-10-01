from setuptools import setup

setup(
    name='Communication',
    version='0.1',
    description='Package belonging to the common files of the strAItegize project, related to the communication.',
    author='Piotr Kluczyński',
    author_email='peklucz@gmail.com',
    packages=['communication'],
    install_requires=[
        'typing',
        'pydantic',
        'json',
    ],
)

setup(
    name='Others',
    version='0.1',
    description='Package belonging to the common files of the strAItegize project, related to various categories.',
    author='Piotr Kluczyński',
    author_email='peklucz@gmail.com',
    packages=['others'],
    install_requires=[
        'typing',
        'pydantic',
        'os',
        'uuid',
        'rich',
        'langchain_core'
    ],
)