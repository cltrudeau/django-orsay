import os

from orsay import __version__

readme = os.path.join(os.path.dirname(__file__), 'README.rst')
long_description = open(readme).read()


SETUP_ARGS = dict(
    name='django-orsay',
    version=__version__,
    description='Static site build tools for photo sites',
    long_description=long_description,
    url='https://github.com/cltrudeau/django-orsay',
    author='Christopher Trudeau',
    author_email='ctrudeau+pypi@arsensa.com',
    license='MIT',
    include_package_data=True,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.7',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    keywords='django,static site,photo',
    #test_suite="load_tests.get_suite",
    install_requires=[
        'Django>=2.1',
        'screwdriver>=0.14.0',
    ],
    #tests_require=[
    #    'mock>=2.0.0',
    #]
)

if __name__ == '__main__':
    from setuptools import setup, find_packages

    SETUP_ARGS['packages'] = find_packages()
    setup(**SETUP_ARGS)
