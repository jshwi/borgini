Status: Archived
==================
This repository has been archived and is no longer maintained

borgini
=======
|Inactive| |License| |PyPI| |CI| |CodeQL| |pre-commit.ci status| |codecov.io| |readthedocs.org| |python3.8| |Black| |isort| |docformatter| |pylint| |Security Status| |Known Vulnerabilities| |borgini|

.. |Inactive| image:: https://img.shields.io/badge/status-inactive-red.svg
    :target: https://img.shields.io/badge/status-inactive-red.svg
    :alt: Status Inactive
.. |License| image:: https://img.shields.io/badge/License-MIT-yellow.svg
   :target: https://opensource.org/licenses/MIT
   :alt: License
.. |PyPI| image:: https://img.shields.io/pypi/v/borgini
   :target: https://pypi.org/project/borgini/
   :alt: PyPI
.. |CI| image:: https://github.com/jshwi/borgini/actions/workflows/ci.yml/badge.svg
   :target: https://github.com/jshwi/borgini/actions/workflows/ci.yml
   :alt: CI
.. |CodeQL| image:: https://github.com/jshwi/borgini/actions/workflows/codeql-analysis.yml/badge.svg
   :target: https://github.com/jshwi/borgini/actions/workflows/codeql-analysis.yml
   :alt: CodeQL
.. |pre-commit.ci status| image:: https://results.pre-commit.ci/badge/github/jshwi/borgini/master.svg
   :target: https://results.pre-commit.ci/latest/github/jshwi/borgini/master
   :alt: pre-commit.ci status
.. |codecov.io| image:: https://codecov.io/gh/jshwi/borgini/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/jshwi/borgini
   :alt: codecov.io
.. |readthedocs.org| image:: https://readthedocs.org/projects/borgini/badge/?version=latest
   :target: https://borgini.readthedocs.io/en/latest/?badge=latest
   :alt: readthedocs.org
.. |python3.8| image:: https://img.shields.io/badge/python-3.8-blue.svg
   :target: https://www.python.org/downloads/release/python-380
   :alt: python3.8
.. |Black| image:: https://img.shields.io/badge/code%20style-black-000000.svg
   :target: https://github.com/psf/black
   :alt: Black
.. |isort| image:: https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336
   :target: https://pycqa.github.io/isort/
   :alt: isort
.. |docformatter| image:: https://img.shields.io/badge/%20formatter-docformatter-fedcba.svg
   :target: https://github.com/PyCQA/docformatter
   :alt: docformatter
.. |pylint| image:: https://img.shields.io/badge/linting-pylint-yellowgreen
   :target: https://github.com/PyCQA/pylint
   :alt: pylint
.. |Security Status| image:: https://img.shields.io/badge/security-bandit-yellow.svg
   :target: https://github.com/PyCQA/bandit
   :alt: Security Status
.. |Known Vulnerabilities| image:: https://snyk.io/test/github/jshwi/borgini/badge.svg
   :target: https://snyk.io/test/github/jshwi/borgini/badge.svg
   :alt: Known Vulnerabilities
.. |borgini| image:: https://snyk.io/advisor/python/docsig/badge.svg
   :target: https://snyk.io/advisor/python/borgini
   :alt: borgini

ini config for borg backup
--------------------------

A wrapper to quickly get you started backing up with borg

An easy to use ini style and profile based format

Requires:

    - Python 3 >= 3.5.0, plus development headers
    - OpenSSL >= 1.0.0, plus development headers
    - libacl (which depends on libattr), both plus development headers
    - liblz4 >= 1.7.0 (r129)
    - libzstd >= 1.3.0
    - libb2

    For information on how to install these dependencies for Borg:
    https://borgbackup.readthedocs.io/en/stable/installation.html

Initialize the config

.. code-block:: console

    $ borgini
    First run detected for profile: default
    Make all necessary changes to config before running this again
    You can do this by running the command:

    . borgini EDITOR --config --select default

    Default settings have been written to the ``include`` and ``exclude`` lists
    These can be edited by running:

    . borgini EDITOR --include --select default
    . borgini EDITOR --exclude --select default
..

.. note::
    the ``--select`` optional argument does not need to be passed if using the default profile

Edit the config

.. code-block:: console

    $ borgini vim --config
..

.. note::
    The selected editor is up to the user

    The following would also work (provided they are installed)

.. code-block:: console

    $ borgini code --config
    $ borgini gedit --config
    $ borgini notepad --config
..

Ensure to make necessary changes to the ``DEFAULT`` section

And ensure to configure the ``SSH`` section if an ssh repo is configured

The remaining configurations will suite most people

If you use the ``BORG_PASSPHRASE`` environment variable edit the ``ENVIRONMENT``
section to point to the keyfile

.. note::
    the file should contain one line and a password stored with safe read-write and ownership permissions

Edit the include and exclude files

.. code-block:: console

    $ borgini vim --include  # add a list of paths to back up
    $ borgini vim --exclude  # add a list of paths to exclude
..

.. note::
    The exclude list can contain subdirectories and files listed within the include list

    This will override their inclusion

To switch between profiles add ``--select PROFILE``

.. code-block:: console

    $ borgini vim --config  # edit default config
    $ borgini vim --config --select profile2  # edit profile2's config
    $ borgini vim --include --select profile2  # edit profile2's include file
    $ borgini vim --exclude --select profile2  # edit profile2's exclude file
    $ borgini --select profile2  # run profile2's backup
..

Add the following for nightly backups at 12:00 to your crontab

.. code-block:: console

    $ 0 0 * * * /usr/local/bin/borgini
    $ 0 0 * * * /usr/local/bin/borgini -s profile2  # easy for multiple repos
..
