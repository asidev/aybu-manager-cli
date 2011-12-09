from setuptools import setup, find_packages

setup(name='aybu-manager-cli',
      version=':versiontools:aybu.manager.cli:',
      description="AyBU instances manager cli",
      long_description="""AyBU instances manager command line interface""",
      classifiers=('License :: OSI Approved :: Apache Software License',
                   'Operating System :: POSIX :: Linux',
                   'Programming Language :: Python :: 2.7',
                   'Topic :: System :: Systems Administration'),
      keywords='',
      author='Giacomo Bagnoli',
      author_email='g.bagnoli@asidev.com',
      url='http://code.asidev.net/projects/aybu',
      license='Apache Software License',
      packages=find_packages(),
      namespace_packages=('aybu', 'aybu.manager'),
      include_package_data=True,
      zip_safe=False,
      install_requires=(
          'plac',
          'pyzmq',
          'requests',
      ),
      entry_points = """\
      [console_scripts]
        aybu_manager_cli = aybu.manager.cli.main:main
      """,
      tests_require=('nose', 'coverage'),
      setup_requires=('versiontools >= 1.8',),
      test_suite='tests',
)
