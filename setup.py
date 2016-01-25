import os
from setuptools import setup
import pypandoc


README = pypandoc.convert('README.md', 'rst')
version = '0.1.1'

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))


setup(
    name='django-normalized-filefield',
    version=version,
    packages=['normalized_filefield', ],
    include_package_data=True,
    install_requires=['django<1.10', ],
    license='MIT',
    description='Normalized file filed for Django',
    long_description=README,
    url='https://github.com/frnhr/django-normalized-filefield/',
    author='Fran Hrzenjak',
    author_email='fran@changeset.hr',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: Freeware',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
