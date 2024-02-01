"""
tests.conftest
==============
"""

from __future__ import annotations

import configparser
import os
import random
import secrets
import string
import sys
import typing as t

import pytest

import borgini

from . import (
    DEVNULL,
    DRY,
    HOST,
    INITIALIZE_FILES,
    NEWPROFILE,
    REPOPATH,
    TMPCONFIGDIR,
    BorgCommands,
    EditPathArgFixture,
    InitializeFilesExpectedFixture,
    InitializeProfileFixture,
    InvalidKeyfileFixture,
    ListArgFixture,
    MockMainFixture,
    NoColorCapsys,
    RandOpts,
    RandOptsFixture,
    RemoveFixture,
    UpdateConfigFixture,
)


@pytest.fixture(name="homedir", autouse=True)
def fixture_homedir(tmpdir: str | os.PathLike) -> None:
    """Ensure the HOME directory is ``tmpdir``.

    :param tmpdir: Create and return temporary directory.
    """
    borgini.HOME = str(tmpdir)


@pytest.fixture(name="main")
def fixture_main(monkeypatch: pytest.MonkeyPatch) -> MockMainFixture:
    """Pass patched commandline arguments to package's main function.

    :param monkeypatch: Mock patch environment and attributes.
    :return: Function for using this fixture.
    """

    def _main(*args: str) -> None:
        _args = [__name__, *args]
        monkeypatch.setattr(sys, "argv", _args)
        borgini.main()

    return _main


@pytest.fixture(name=INITIALIZE_FILES)
def fixture_initialize_files(
    main: MockMainFixture,
    tmpconfigdir: str | os.PathLike,
    nocolorcapsys: NoColorCapsys,
) -> str:
    """Initialize the config files and return the stdout for testing.

    :param main: Patch package entry point.
    :param tmpconfigdir:  Absolute path to directory containing
        ``config.ini``, ``include``, ``exclude`` and ``styles``files.
    :param nocolorcapsys: Capture stdout and strip it of any ANSI escape
        codes.
    :return: Stdout from ``capsys``.
    """
    with pytest.raises(SystemExit):
        main(DRY)
    assert os.path.isdir(tmpconfigdir)
    return nocolorcapsys.stdout()


@pytest.fixture(name="keygen")
def fixture_keygen() -> str:
    """Generate a random password.

    :return: Random password with a length of 16 characters.
    """
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(16))


@pytest.fixture(name=TMPCONFIGDIR)
def fixture_tmpconfigdir(tmpdir: str | os.PathLike) -> str:
    """Make a config directory and return the path.

    :param tmpdir: Create and return temporary directory.
    :return: Path to the random directory.
    """
    configdir = os.path.join(tmpdir, "borgini")
    os.makedirs(configdir)
    borgini.funcs.CONFIGDIR = configdir
    return str(configdir)


@pytest.fixture(name="nocolorcapsys")
def fixture_nocolorcapsys(capsys: pytest.CaptureFixture) -> NoColorCapsys:
    """Instantiate capsys with the regex method.

    :param capsys: Capture sys out.
    :return: Instantiated ``NoColorCapsys`` object.
    """
    return NoColorCapsys(capsys)


@pytest.fixture(name="update_config")
def fixture_update_config() -> UpdateConfigFixture:
    """Update the config file with kwargs.

    :return: Function for using this fixture.
    """

    def _update_config(path: str | os.PathLike, **kwargs: t.Any) -> None:
        config = configparser.ConfigParser()
        config.read(path)
        config.read_dict(kwargs)
        with open(path, "w", encoding="utf-8") as file:
            config.write(file)

    return _update_config


@pytest.fixture(name="initialize_profile")
def fixture_initialize_profile() -> InitializeProfileFixture:
    """Initialize a new profile with variable name passed to the func.

    Once the profile is created return the captured stdout in the case
    it needs to be used a by a test.

    :return: Function for using this fixture.
    """

    def _initialize_profile(
        main: MockMainFixture,
        tmpconfigdir: str | os.PathLike,
        nocolorcapsys: NoColorCapsys,
        profile: str,
    ) -> str:
        with pytest.raises(SystemExit):
            main(DRY, "--select", profile)

        assert os.path.isdir(tmpconfigdir)
        return nocolorcapsys.readouterr()[0]

    return _initialize_profile


@pytest.fixture(name="remove")
def fixture_remove() -> RemoveFixture:
    """Test the correct profile is removed when using ``--remove``.

    :return: Function for using this fixture.
    """

    def _remove(main: MockMainFixture, nocolorcapsys: NoColorCapsys) -> str:
        with pytest.raises(SystemExit):
            main(DRY, "--remove", NEWPROFILE)

        return nocolorcapsys.stdout()

    return _remove


@pytest.fixture(name="randopts")
def fixture_randopts() -> RandOptsFixture:
    """Generate an assortment of random options.

    :return: Function for using this fixture.
    """

    def _randopts() -> RandOpts:
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
            "DEFAULT": {REPOPATH: DEVNULL},
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
def fixture_invalid_keyfile() -> InvalidKeyfileFixture:
    """Create an invalid keyfile.

    Output that should match up with the actual stdout when a keyfile
    argument does not lead to an existing file.

    :return: Function for using this fixture.
    """

    def _invalid_keyfile(**kwargs: t.Any) -> str:
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
def fixture_list_arg() -> ListArgFixture:
    """Test for the correct stdout.

    Output in the tests should match what this returns.

    :return: Function for using this fixture.
    """

    def list_arg(*profiles: str) -> str:
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
def fixture_initialize_files_expected() -> InitializeFilesExpectedFixture:
    """Output that matches with stdout when initializing profile.

    :return: Function for using this fixture.
    """

    def _initialize_files_expected(profile: str) -> str:
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
def fixture_edit_path_arg() -> EditPathArgFixture:
    """String to replace actual calling of an editor.

    Representation of the stdout that should match with the actual
    stdout when running with an editor to edit a file.

    :return: Function for using this fixture.
    """

    def _edit_path_arg(path):
        path = borgini.funcs.normalize_ntpath(path)
        return f"vim {path}\n\n"

    return _edit_path_arg
