from setuptools import setup

# Need this to get around weird setuptools biz on py2.7
try:
    import multiprocessing, logging
except ImportError:
    pass


def get_requirements(filename='requirements.txt'):
    with open(filename, 'r') as f:
        return [line for line in f.readlines()]


long_description = file("README.rst").read().strip()


setup(
        name='fedbadges',
        version='0.1.4',
        description='fedmsg consumer for awarding open badges',
        long_description=long_description,
        author='Ross Delinger',
        author_email='rdelinge@redhat.com',
        url='https://github.com/rossdylan/fedbages',
        install_requires=get_requirements(),
        tests_require=["nose"],
        test_suite="nose.collector",
        include_package_data=True,
        packages=[
            'fedbadges',
            'fedbadges.consumers',
            'fedbadges.commands'],
        zip_safe=False,
        entry_points={
            'console_scripts': [
                "fedmsg-badges=fedbadges.commands.badges:badges"],
            'moksha.consumer': [
                "fedmsg-badges=fedbadges.consumers.yamlconsumer:YAMLBadgeConsumer"
            ]
        },
)
