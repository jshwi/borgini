"""
tests.conftest
==============

Automatically detected by pytest for custom fixtures
"""
import configparser
import os
import random
import secrets
import string
import sys

import pytest

import borgini

from . import HOST, BorgCommands, NoColorCapsys


@pytest.fixture(name="homedir", autouse=True)
def fixture_homedir(tmpdir):
    """Ensure the HOME directory is ``tmpdir``.

    :param tmpdir:  ``pytest`` ``tmpdir`` fixture for creating and
                    returning a temporary directory.
    """
    borgini.HOME = tmpdir


@pytest.fixture(name="main")
def fixture_main(monkeypatch):
    """Function for passing mock ``borgini.main`` commandline arguments
    to package's main function.

    :param monkeypatch: ``pytest`` fixture for mocking attributes.
    :return:            Function for using this fixture.
    """

    def _main(*args):
        args = [__name__, *args]
        monkeypatch.setattr(sys, "argv", args)
        borgini.main()

    return _main


@pytest.fixture(name="initialize_files")
def fixture_initialize_files(main, tmpconfigdir, nocolorcapsys):
    """Initialize the config files and return the stdout for testing.

    :param main:            Fixture for mocking ``borgini.main``.
    :param nocolorcapsys:   Capture stdout
    :param tmpconfigdir:    Absolute path to directory containing
                            ``config.ini``, ``include`` and
                            ``exclude`` files
    :return:                stdout from ``capsys``
    """
    with pytest.raises(SystemExit):
        main("--dry")
    assert os.path.isdir(tmpconfigdir)
    return nocolorcapsys.stdout()


@pytest.fixture(name="keygen")
def fixture_keygen():
    """Generate a random password.

    :return: Random password with a length of 16 characters
    """
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(16))


@pytest.fixture(name="tmpconfigdir")
def fixture_tmpconfigdir(tmpdir):
    """Make a config directory and return the value of that temporary
    directory.

    :param tmpdir:  The ``tmpdir`` fixture with ``pytest``
    :return:        Path to the random directory
    """
    configdir = os.path.join(tmpdir, "borgini")
    os.makedirs(configdir)
    borgini.funcs.CONFIGDIR = configdir
    return configdir


@pytest.fixture(name="nocolorcapsys")
def fixture_nocolorcapsys(capsys):
    """Instantiate capsys with the regex method."""
    return NoColorCapsys(capsys)


@pytest.fixture(name="update_config")
def fixture_update_config():
    """Update the config file with kwargs."""

    def _update_config(path, **kwargs):
        config = configparser.ConfigParser()
        config.read(path)
        config.read_dict(kwargs)
        with open(path, "w", encoding="utf-8") as file:
            config.write(file)

    return _update_config


@pytest.fixture(name="initialize_profile")
def fixture_initialize_profile():
    """Initialize a new profile with a variable name passed to the
    function.

    Once the profile is created return the captured stdout in the case
    it needs to be used a by a test
    """

    def _initialize_profile(main, tmpconfigdir, capsys, profile):
        with pytest.raises(SystemExit):
            main("--dry", "--select", profile)

        assert os.path.isdir(tmpconfigdir)
        return capsys.readouterr()[0]

    return _initialize_profile


@pytest.fixture(name="remove")
def fixture_remove():
    """Test the correct profile is removed when the ``--remove`` option
    is passed."""

    def _remove(main, nocolorcapsys):
        with pytest.raises(SystemExit):
            main("--dry", "--remove", "newprofile")

        return nocolorcapsys.stdout()

    return _remove


@pytest.fixture(name="randopts")
def fixture_randopts():
    """Generate an assortment of random options within the allowed
    values for the borgbackup arguments."""

    def _randopts():
        filterkwargs = [
            "A",
            "M",
            "U",
            "E",
            "d",
            "b",
            "c",
            "h",
            "s",
            "f",
            "i",
            "-",
            "x",
            "?",
        ]
        compressionkwargs = ["lz4", "zstd", "zlib", "lzma", "auto"]
        daily = ["1", "2", "3", "4", "5", "6", "7"]
        weekly = ["1", "2", "3", "4"]
        monthly = [
            "1",
            "2",
            "3",
            "4",
            "5",
            "6",
            "7",
            "8",
            "9",
            "10",
            "11",
            "12",
        ]
        randfkwargs = "".join(
            random.sample(filterkwargs, random.randrange(1, len(filterkwargs)))
        )
        randckwargs = random.choice(compressionkwargs)
        randdaily = random.choice(daily)
        randweekly = random.choice(weekly)
        randmonthly = random.choice(monthly)
        return {
            "DEFAULT": {"repopath": "/dev/null"},
            "SSH": {"port": random.randint(1, 9999)},
            "BACKUP": {
                "verbose": random.choice([True, False]),
                "stats": random.choice([True, False]),
                "list": random.choice([True, False]),
                "show-rc": random.choice([True, False]),
                "exclude-caches": random.choice([True, False]),
                "filter": randfkwargs,
                "compression": randckwargs,
            },
            "PRUNE": {
                "verbose": random.choice([True, False]),
                "stats": random.choice([True, False]),
                "list": random.choice([True, False]),
                "show-rc": random.choice([True, False]),
                "keep-daily": randdaily,
                "keep-weekly": randweekly,
                "keep-monthly": randmonthly,
            },
        }

    return _randopts


@pytest.fixture(name="invalid_keyfile")
def fixture_invalid_keyfile():
    """Output that should match up with the actual stdout when a keyfile
    argument does not lead to an existing file."""

    def _invalid_keyfile(**kwargs):
        announce = (
            "BORG_PASSPHRASE keyfile cannot be found\n"
            "attempting backup without keyfile\n\n"
            'add a valid keyfile or "None" to BORG_PASSPHRASE to stop '
            "receiving this message\n"
            "You can do this by running the command:\n"
            " . borgini EDITOR --config --select default\n\n"
        )
        borg_commands = BorgCommands(**kwargs)
        command_output = borg_commands.commands()
        return announce + command_output

    return _invalid_keyfile


@pytest.fixture(name="list_arg")
def fixture_list_arg():
    """Test for the correct stdout.

    Output in the tests should match what this returns
    """

    def list_arg(*profiles):
        _string = ""
        for profile in profiles:
            _string += (
                f"[{profile}]\n"
                f"reponame = {HOST}\n"
                "ssh = True\n"
                "prune = True\n\n"
            )
        return _string

    return list_arg


@pytest.fixture(name="initialize_files_expected")
def fixture_initialize_files_expected():
    """Output that should match up with the actual stdout when
    initializing a new profile."""

    def _initialize_files_expected(profile):
        return (
            f"First run detected for profile: {profile}\n"
            "Make all necessary changes to config before running this again\n"
            "You can do this by running the command:\n\n"
            f". borgini EDITOR --config --select {profile}\n\n"
            "Default settings have been written to the `include' and "
            "`exclude' lists\n"
            "These can be edited by running:\n\n"
            f". borgini EDITOR --include --select {profile}\n"
            f". borgini EDITOR --exclude --select {profile}\n"
        )

    return _initialize_files_expected


@pytest.fixture(name="edit_path_arg")
def fixture_edit_path_arg():
    """Representation of the stdout that should match with the actual
    stdout when running with an editor to edit a file."""

    def _edit_path_arg(path):
        path = borgini.funcs.normalize_ntpath(path)
        return f"vim {path}\n\n"

    return _edit_path_arg
