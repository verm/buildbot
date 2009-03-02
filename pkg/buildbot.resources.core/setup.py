from setuptools import setup
execfile("../common.py")

setup(
    name='buildbot.resources.core',
    description = "Buildbot - core resources",
    long_description = "\n\n".join([
        open("../README_HEADER.txt").read(),
        open("README.txt").read(),
    ]),

    zip_safe = True,
    packages=['buildbot.resources.core'],

    namespace_packages=['buildbot', 'buildbot.resources'],
    install_requires=[
        'setuptools',
        'buildbot>=1.0',
    ],

    test_suite='test',

    **setup_args)
