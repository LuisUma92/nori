from setuptools import setup

def readme():
    with open('README.md') as f:
        return f.read()

setup(
    name='nori',
    version='1.0.0001',
    long_description=readme(),
    long_description_content_type='text/markdown',
    packages=['nori'],
    scripts=['bin/nori']
)
