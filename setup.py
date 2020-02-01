from setuptools import setup

setup(
    name='fix15',
    version='0.1.0',
    description='Convert 15-character Salesforce Ids to 18-character Ids in CSV files.',
    author='David Reed',
    author_email='david@ktema.org',
    url='https://github.com/davidmreed/fix15',
    license='MIT License',
    packages=['fix15'],
    test_suite='nose.collector',
    tests_require=['nose'],
    keywords=['Salesforce'],
    platforms='Any',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Utilities'
    ],
    entry_points={
        'console_scripts': [
            'fix15 = fix15.__main__:main'
        ]
    },
)