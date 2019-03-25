from setuptools import setup

# Need this to get around weird setuptools biz on py2.7
try:
    import multiprocessing
    import logging
except ImportError:
    pass


def get_requirements(filename='requirements.txt'):
    with open(filename, 'r') as f:
        return [line for line in f.readlines()]


long_description = open("README.rst").read().strip()


setup(
    name='fedbadges',
    version='1.0.2',
    description='fedmsg consumer for awarding open badges',
    long_description=long_description,
    license='GPLv2+',
    author='Ross Delinger',
    author_email='rdelinge@redhat.com',
    maintainer='Ralph Bean',
    maintainer_email='rbean@redhat.com',
    url='https://github.com/fedora-infra/fedbadges',
    install_requires=get_requirements(),
    tests_require=[
        "nose",
        "mock",
    ],
    test_suite="nose.collector",
    include_package_data=True,
    packages=[
        'fedbadges',
    ],
    zip_safe=False,
    entry_points={
        'console_scripts': [
            "fedmsg-badges=fedbadges.commands:badges"
        ],
        'moksha.consumer': [
            "fedmsg-badges=fedbadges.consumers:FedoraBadgesConsumer",
        ]
    },
)
