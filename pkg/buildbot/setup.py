from setuptools import setup
execfile("../common.py")

setup(
    name='buildbot',
    description = "Buildbot - top-level package",
    long_description = open("README.txt").read(),

    install_requires=[
        'buildbot.framework==%s' % version,
        'buildbot.resources.core==%s' % version,
    ],

    **setup_args)
