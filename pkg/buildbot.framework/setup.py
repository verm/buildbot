from setuptools import setup
execfile("../common.py")

setup(
    name='buildbot.framework',
    description = "Buildbot - framework",
    long_description = "\n\n".join([
        open("../README_HEADER.txt").read(),
        open("README.txt").read(),
    ]),

    zip_safe = True,
    packages=['buildbot.framework'],
    py_modules=['buildbot.config'],

    namespace_packages=['buildbot'],
    install_requires=[
        'setuptools',
        'twisted',
        'uthreads',
    ],

    test_suite='test',

    **setup_args)
