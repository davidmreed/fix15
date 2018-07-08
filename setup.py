from setuptools import setup

setup(
    name='fix15',
    version='0.1.0',
    description='Convert 15-character Salesforce Ids to 18-character Ids in CSV files.',
    author='David Reed',
    author_email='david@ktema.org',
    packages=['fix15'],
    test_suite='nose.collector',
    tests_require=['nose'],
    entry_points={
        'console_scripts': [
            'fix15 = fix15.__main__:main'
        ]
    },
)