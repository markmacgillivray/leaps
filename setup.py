from setuptools import setup, find_packages

setup(
    name = 'leaps',
    version = '2.0.0',
    packages = find_packages(),
    install_requires = [
        "Flask",
        "Flask-Login",
        "Flask-WTF",
        "requests",
        "tinycss2",
        "cairocffi",
        "WeasyPrint",
        "Flask-WeasyPrint"
    ],
    url = 'https://cottagelabs.com/',
    author = 'Cottage Labs',
    author_email = 'us@cottagelabs.com',
    description = 'A web API layer over an ES backend, with various useful plugins',
    license = 'MIT',
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: MIT',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
)
