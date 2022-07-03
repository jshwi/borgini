"""
tests._tests
============

All tests for the package are in this module

import flaky for flaky tests which involve the date-time in their
output - there can be a slight skew when the date and time was set
between the output and the _expected
"""
from __future__ import annotations

import configparser
import os
from unittest import mock
from unittest.mock import Mock

import freezegun
import pytest

import borgini

from . import (
    BorgCommands,
    EditPathArgFixture,
    InitializeFilesExpectedFixture,
    InitializeProfileFixture,
    InvalidKeyfileFixture,
    ListArgFixture,
    MockMainFixture,
    NoColorCapsys,
    RandOptsFixture,
    RemoveFixture,
    UpdateConfigFixture,
    expected,
)


@pytest.mark.usefixtures("tmpconfigdir")
def test_initialize_files(
    initialize_files: str,
    initialize_files_expected: InitializeFilesExpectedFixture,
) -> None:
    """Test initialization of files.

    Test that ``config.ini``, ``include``, ``exclude`` and ``styles``
    are all initialized and that the correct message is displayed.

    :param initialize_files: Initialize all the configuration files in a
        temporary directory.
    :param initialize_files_expected: Expected output when initializing
        files.
    """
    _expected = initialize_files_expected("default")
    assert initialize_files == _expected


@pytest.mark.usefixtures("tmpconfigdir", "initialize_files")
def test_empty_repo_setting(
    main: MockMainFixture, nocolorcapsys: NoColorCapsys
) -> None:
    """Test settings for an empty repo.

    Test that the correct stderr is displayed when the ``config.ini``
    file has not been configured to contain a path to the backup
    repository. Assert non-zero exit-code.

    :param main: Patch package entry point.
    :param nocolorcapsys: Capture stdout and strip it of any ANSI escape
        codes.
    """
    with pytest.raises(SystemExit) as pytest_err:
        main("--dry")
    err = nocolorcapsys.stderr()
    assert err == expected.EMPTY_REPO_SETTING
    assert pytest_err.value.code == 1


@freezegun.freeze_time("2021-02-07T16:12:58")
@pytest.mark.usefixtures("tmpconfigdir", "initialize_files")
def test_borg_commands(
    main: MockMainFixture,
    update_config: UpdateConfigFixture,
    nocolorcapsys: NoColorCapsys,
    tmpconfigdir: str,
) -> None:
    """Test commands run with ``BorgBackup``.

    Test that values written to the config file yield the correct result
    when running borgbackup commands.

    :param main: Patch package entry point.
    :param update_config: Update the test config with parameters.
    :param nocolorcapsys: Capture stdout and strip it of any ANSI escape
        codes.
    :param tmpconfigdir:  Absolute path to directory containing
        ``config.ini``, ``include``, ``exclude`` and ``styles``files.
    """
    configpath = os.path.join(tmpconfigdir, "default", "config.ini")
    borg_commands = BorgCommands(
        DEFAULT={"reponame": expected.HOST, "repopath": "/dev/null"},
        SSH={
            "remoteuser": expected.USER,
            "remotehost": expected.HOST,
            "port": "22",
        },
    )
    _expected = borg_commands.commands()
    update_config(configpath, DEFAULT={"repopath": "/dev/null"})
    main("--dry")
    out = nocolorcapsys.stdout()
    assert out == _expected


@pytest.mark.usefixtures("tmpconfigdir", "initialize_files")
def test_show_config(
    main: MockMainFixture, nocolorcapsys: NoColorCapsys
) -> None:
    """Test printing of config.

    Test the correct stdout is displayed when running the ``--config``
    flag without an editor to show the config.

    :param main: Patch package entry point.
    :param nocolorcapsys: Capture stdout and strip it of any ANSI escape
        codes.
    """
    with pytest.raises(SystemExit):
        main("--config")
    out = nocolorcapsys.stdout()
    assert out == expected.SHOW_CONFIG


@pytest.mark.usefixtures("tmpconfigdir", "initialize_files")
def test_show_include(
    main: MockMainFixture, nocolorcapsys: NoColorCapsys
) -> None:
    """Test printing of include config.

    Test the correct stdout is displayed when running the ``--include``
    flag without an editor to show the include file.

    :param main: Patch package entry point.
    :param nocolorcapsys: Capture stdout and strip it of any ANSI escape
        codes.
    """
    with pytest.raises(SystemExit):
        main("--include")
    out = nocolorcapsys.stdout()
    assert out == expected.SHOW_INCLUDE


@pytest.mark.usefixtures("tmpconfigdir", "initialize_files")
def test_show_exclude(
    main: MockMainFixture, nocolorcapsys: NoColorCapsys
) -> None:
    """Test printing of exclude config.

    Test the correct stdout is displayed when running the ``--exclude``
    flag without an editor to show the exclude file.

    :param main: Patch package entry point.
    :param nocolorcapsys: Capture stdout and strip it of any ANSI escape
        codes.
    """
    with pytest.raises(SystemExit):
        main("--exclude")
    out = nocolorcapsys.stdout()
    assert out == expected.SHOW_EXCLUDE


@pytest.mark.usefixtures("tmpconfigdir", "initialize_files")
def test_invalid_keyfile(  # pylint: disable=too-many-arguments
    main: MockMainFixture,
    invalid_keyfile: InvalidKeyfileFixture,
    update_config: UpdateConfigFixture,
    nocolorcapsys: NoColorCapsys,
    tmpconfigdir: str,
) -> None:
    """Test invalid keyfile.

    Test the correct warning message is displayed when the process is
    attempting to go on without a correct value for a keyfile.

    :param main: Patch package entry point.
    :param invalid_keyfile: Invalid keyfile.
    :param update_config: Update the test config with parameters.
    :param nocolorcapsys: Capture stdout and strip it of any ANSI escape
        codes.
    :param tmpconfigdir: Absolute path to directory containing
        ``config.ini``, ``include``, ``exclude`` and ``styles``files.
    """
    configpath = os.path.join(tmpconfigdir, "default", "config.ini")
    _expected = invalid_keyfile(
        DEFAULT={"reponame": expected.HOST, "repopath": "/dev/null"},
        SSH={
            "remoteuser": expected.USER,
            "remotehost": expected.HOST,
            "port": "22",
        },
    )
    update_config(
        configpath,
        DEFAULT={"repopath": "/dev/null"},
        ENVIRONMENT={"keyfile": "/dev/null"},
    )
    main("--dry")
    out = nocolorcapsys.stdout()
    assert out == _expected


@pytest.mark.usefixtures("tmpconfigdir", "initialize_files")
def test_invalid_path_arg(
    main: MockMainFixture, nocolorcapsys: NoColorCapsys
) -> None:
    """Test execution with an invalid path argument.

    Test that the usage information is displayed when a file that does
    not exist is entered and not the following:

    - ``config``
    - ``include``
    - ``exclude``
    - ``styles``

    :param main: Patch package entry point.
    :param nocolorcapsys: Capture stdout and strip it of any ANSI escape
        codes.
    """
    with pytest.raises(SystemExit):
        main("--invalid")
    err = nocolorcapsys.stderr()
    assert err == expected.INVALID_PATH_ARG


@pytest.mark.usefixtures("tmpconfigdir", "initialize_files")
def test_edit_invalid_path_arg(
    main: MockMainFixture, nocolorcapsys: NoColorCapsys
) -> None:
    """Test execution when editor called to open invalid file.

    Test that the usage information is displayed when a file that does
    not exist is entered and not the following when running with the
    editor positional argument:

    - ``config``
    - ``include``
    - ``exclude``
    - ``styles``

    :param main: Patch package entry point.
    :param nocolorcapsys: Capture stdout and strip it of any ANSI escape
        codes.
    """
    with pytest.raises(SystemExit):
        main("vim", "--invalid")
    err = nocolorcapsys.stderr()
    assert err == expected.INVALID_PATH_ARG


@mock.patch("shutil.which")
@pytest.mark.usefixtures("tmpconfigdir", "initialize_files")
def test_edit_path_arg(
    mock_which: Mock,
    main: MockMainFixture,
    edit_path_arg: EditPathArgFixture,
    nocolorcapsys: NoColorCapsys,
    tmpconfigdir: str,
) -> None:
    """Test execution of editor and the path provided.

    Test the correct command is passed when attempting to edit a file
    with the editor positional argument.

    Run in dry mode for dumb terminal.

    :param mock_which: Mock ``shutil.which`` object
    :param main: Patch package entry point.
    :param edit_path_arg: Expected output when setting an editor.
    :param nocolorcapsys: Capture stdout and strip it of any ANSI escape
        codes.
    :param tmpconfigdir:  Absolute path to directory containing
        ``config.ini``, ``include``, ``exclude`` and ``styles``files.
    """
    mock_which.return_value = "vim"
    path = os.path.join(tmpconfigdir, "default", "include")
    _expected = edit_path_arg(path)
    with pytest.raises(SystemExit):
        main("vim", "--include", "--dry")

    out = nocolorcapsys.stdout()
    assert out == _expected


@freezegun.freeze_time("2021-02-07T16:12:58")
@pytest.mark.usefixtures("tmpconfigdir", "initialize_files")
def test_read_keyfile(  # pylint: disable=too-many-arguments
    main: MockMainFixture,
    update_config: UpdateConfigFixture,
    tmpdir: str | os.PathLike,
    capsys: pytest.CaptureFixture,
    tmpconfigdir: str,
    keygen: str,
) -> None:
    """Test loading of keyfile.

    Test that the correct password is retrieved from a keyfile when the
    keyfile path is supplied in the config file.

    :param main: Patch package entry point.
    :param update_config: Update the test config with parameters.
    :param tmpdir: Create and return temporary test directory.
    :param capsys: Silence stdout.
    :param tmpconfigdir:  Absolute path to directory containing
        ``config.ini``, ``include``, ``exclude`` and ``styles``files.
    :param keygen: Generate a keyfile and read its random password value
        to the ``BORG_PASSPHRASE`` environment variable.
    """
    configpath = os.path.join(tmpconfigdir, "default", "config.ini")
    keyfile = os.path.join(tmpdir, "borgsecret")
    with open(keyfile, "w", encoding="utf-8") as file:
        file.write(keygen)
    update_config(
        configpath,
        DEFAULT={"repopath": "/dev/null"},
        ENVIRONMENT={"keyfile": keyfile},
    )
    main("--dry")
    capsys.readouterr()
    assert os.environ["BORG_PASSPHRASE"] == keygen


@freezegun.freeze_time("2021-02-07T16:12:58")
@pytest.mark.usefixtures("tmpconfigdir", "initialize_files")
def test_no_ssh(
    main: MockMainFixture,
    update_config: UpdateConfigFixture,
    nocolorcapsys: NoColorCapsys,
    tmpconfigdir: str,
) -> None:
    """Test execution when SSH is not meant to be used.

    Test the path is properly adjusted to not include the full ssh path
    when ``ssh`` is False.

    :param main: Patch package entry point.
    :param update_config: Update the test config with parameters.
    :param nocolorcapsys: Capture stdout and strip it of any ANSI escape
        codes.
    :param tmpconfigdir:  Absolute path to directory containing
        ``config.ini``, ``include``, ``exclude`` and ``styles``files.
    """
    configpath = os.path.join(tmpconfigdir, "default", "config.ini")
    borg_commands = BorgCommands(
        DEFAULT={
            "reponame": expected.HOST,
            "repopath": "/dev/null",
            "ssh": False,
        }
    )
    _expected = borg_commands.commands()
    update_config(configpath, DEFAULT={"repopath": "/dev/null", "ssh": False})
    main("--dry")
    out = nocolorcapsys.stdout()
    assert out == _expected


@pytest.mark.usefixtures("tmpconfigdir", "initialize_files")
def test_select_profile(
    main: MockMainFixture,
    initialize_files_expected: InitializeFilesExpectedFixture,
    initialize_profile: InitializeProfileFixture,
    nocolorcapsys: NoColorCapsys,
    tmpconfigdir: str,
) -> None:
    """Test selection of profile.

    Test the correct alternate profile is being used when the
    ``--select`` flag is passed with a non-default profile.

    :param main: Patch package entry point.
    :param initialize_files_expected: Expected output when initializing
        files.
    :param initialize_profile: Create a test profile.
    :param nocolorcapsys: Capture stdout and strip it of any ANSI escape
        codes.
    :param tmpconfigdir:  Absolute path to directory containing
        ``config.ini``, ``include``, ``exclude`` and ``styles``files.
    """
    _expected = initialize_files_expected("newprofile")
    out = initialize_profile(main, tmpconfigdir, nocolorcapsys, "newprofile")
    assert out == _expected


@pytest.mark.usefixtures("tmpconfigdir", "initialize_files")
def test_list_arg(
    main: MockMainFixture,
    list_arg: ListArgFixture,
    initialize_profile: InitializeProfileFixture,
    nocolorcapsys: NoColorCapsys,
    tmpconfigdir: str,
) -> None:
    """Test printing of list.

    Test for the correct output when the ``--list`` flag is used.

    :param main: Patch package entry point.
    :param list_arg: Expected arg.
    :param initialize_profile: Create a test profile.
    :param nocolorcapsys: Capture stdout and strip it of any ANSI escape
        codes.
    :param tmpconfigdir:  Absolute path to directory containing
        ``config.ini``, ``include``, ``exclude`` and ``styles``files.
    """
    _expected = list_arg("default", "newprofile")
    initialize_profile(main, tmpconfigdir, nocolorcapsys, "newprofile")
    with pytest.raises(SystemExit):
        main("--dry", "--list")
    out = nocolorcapsys.stdout()
    assert out == _expected


@pytest.mark.usefixtures("tmpconfigdir", "initialize_files")
def test_remove_no_exist(
    main: MockMainFixture, remove: RemoveFixture, nocolorcapsys: NoColorCapsys
) -> None:
    """Test call to remove when target doesn't exist.

    Test that the correct warning is displayed when the ``--remove``
    option is passed with a profile name and that name does not exist.

    :param main: Patch package entry point.
    :param remove: Run commandline arguments to remove a profile
    :param nocolorcapsys: Capture stdout and strip it of any ANSI escape
        codes.
    """
    out = remove(main, nocolorcapsys)
    assert out == expected.REMOVE_NO_EXIST


@pytest.mark.usefixtures("tmpconfigdir", "initialize_files")
@pytest.mark.usefixtures()
def test_remove_arg(
    main: MockMainFixture,
    remove: RemoveFixture,
    initialize_profile: InitializeProfileFixture,
    nocolorcapsys: NoColorCapsys,
    tmpconfigdir: str,
) -> None:
    """Test call to remove.

    First create a profile and test the remote function with it so that
    we can test that the ``--remove`` flag properly removes profiles.

    :param main: Patch package entry point.
    :param remove: Run commandline arguments to remove a profile
    :param initialize_profile: Create a test profile.
    :param nocolorcapsys: Capture stdout and strip it of any ANSI escape
        codes.
    :param tmpconfigdir:  Absolute path to directory containing
        ``config.ini``, ``include``, ``exclude`` and ``styles``files.
    """
    # calls `initialize_newprofile_files' unlike the above
    initialize_profile(main, tmpconfigdir, nocolorcapsys, "newprofile")
    out = remove(main, nocolorcapsys)
    assert not os.path.isdir(os.path.join(tmpconfigdir, "newprofile"))
    assert out == expected.REMOVE_ARG


@pytest.mark.usefixtures("tmpconfigdir", "initialize_files")
def test_file_exists_error(
    main: MockMainFixture,
    initialize_profile: InitializeProfileFixture,
    tmpconfigdir: str,
    nocolorcapsys: NoColorCapsys,
) -> None:
    """Test error when a file already exists when initializing new one.

    Demonstrate that ``make_appdir`` should not be in
    ``borgini.data.Data.__init__``

    :param main: Patch package entry point.
    :param initialize_profile: Create a test profile.
    :param tmpconfigdir:  Absolute path to directory containing
        ``config.ini``, ``include``, ``exclude`` and ``styles``files.
    :param nocolorcapsys: Capture stdout and strip it of any ANSI escape
        codes.
    """
    initialize_profile(main, tmpconfigdir, nocolorcapsys, "profile1")
    borgini.Data(tmpconfigdir, "profile1").make_appdir()
    initialize_profile(main, tmpconfigdir, nocolorcapsys, "profile2")
    borgini.Data(tmpconfigdir, "profile2").make_appdir()
    with open(os.path.join(tmpconfigdir, "profile3"), "w", encoding="utf-8"):
        # touch file
        pass
    with pytest.raises(FileExistsError):
        borgini.Data(tmpconfigdir, "profile3").make_appdir()


@freezegun.freeze_time("2021-02-07T16:12:58")
@pytest.mark.parametrize("_", range(10))
@pytest.mark.usefixtures("tmpconfigdir", "initialize_files")
def test_random_opts(  # pylint: disable=too-many-arguments
    main: MockMainFixture,
    randopts: RandOptsFixture,
    update_config: UpdateConfigFixture,
    nocolorcapsys: NoColorCapsys,
    tmpconfigdir: str,
    _: int,
) -> None:
    """Run this test function 10 times.

    Random values will be generated and written to the config file

    Test when activating the borgbackup commands that the correct values
    have been parsed and retrieved by the process

    :param main: Patch package entry point.
    :param randopts: Parse random commandline arguments.
    :param update_config: Update the test config with parameters.
    :param nocolorcapsys: Capture stdout and strip it of any ANSI escape
        codes.
    :param tmpconfigdir:  Absolute path to directory containing
        ``config.ini``, ``include``, ``exclude`` and ``styles``files.
    """
    configpath = os.path.join(tmpconfigdir, "default", "config.ini")
    obj = randopts()
    borg_commands = BorgCommands(**obj)
    _expected = borg_commands.commands()
    update_config(configpath, **obj)
    main("--dry")
    out = nocolorcapsys.stdout()
    assert out == _expected


@mock.patch("shutil.which")
def test_run_editor_without_arg(
    mock_which: Mock, main: MockMainFixture, nocolorcapsys: NoColorCapsys
) -> None:
    """Test error message when argument needs to be provided to editor.

    Test for the correct error message is displayed when an editor is
    called without a file to edit.

    :param mock_which: Mock ``shutil.which`` object.
    :param main: Patch package entry point.
    :param nocolorcapsys: Capture stdout and strip it of any ANSI escape
        codes.
    """
    mock_which.return_value = "vim"
    with pytest.raises(SystemExit) as pytest_err:
        main("vim")
    err = nocolorcapsys.stderr()
    assert err == "EDITOR must be followed by a file to edit\n"
    assert pytest_err.value.code == 1


@mock.patch("shutil.which")
def test_run_uninstalled_editor(
    mock_which: Mock, main: MockMainFixture, nocolorcapsys: NoColorCapsys
) -> None:
    """Test call to editor that is not installed.

    Test for the correct error message is displayed when the entered
    "editor" does not exist.

    :param mock_which: Mock ``shutil.which`` object.
    :param main: Patch package entry point.
    :param nocolorcapsys: Capture stdout and strip it of any ANSI escape
        codes.
    """
    mock_which.return_value = None
    with pytest.raises(SystemExit) as pytest_err:
        main("vim")
    err = nocolorcapsys.stderr()
    assert err == "EDITOR must be installed: `vim' cannot be found\n"
    assert pytest_err.value.code == 1


@pytest.mark.usefixtures("tmpconfigdir", "initialize_files")
def test_repair_config_key_err(
    main: MockMainFixture,
    update_config: UpdateConfigFixture,
    tmpconfigdir: str,
    capsys: pytest.CaptureFixture,
) -> None:
    """Test repairing a config with a key error.

    Test that an out-of-place section does not halt the process and is
    subsequently corrected by the ``configparser.ConfigParser`` object.

    Useful if there are any section updates in the code.

    :param main: Patch package entry point.
    :param update_config: Update the test config with parameters.
    :param tmpconfigdir:  Absolute path to directory containing
        ``config.ini``, ``include``, ``exclude`` and ``styles``files.
    :param capsys: Silence stdout.
    """
    bad_section = "NOT_A_SECTION"
    configpath = os.path.join(tmpconfigdir, "default", "config.ini")
    update_config(
        configpath,
        **{
            "DEFAULT": {"repopath": "/dev/null"},
            bad_section: {"bad_key": "null"},
        },
    )
    main("--dry")
    capsys.readouterr()  # silence
    config = configparser.ConfigParser()
    config.read(configpath)
    with pytest.raises(KeyError):
        _ = config[bad_section]


@pytest.mark.usefixtures("tmpconfigdir", "initialize_files")
def test_pass_on_not_a_directory_err(
    main: MockMainFixture, tmpconfigdir: str, capsys: pytest.CaptureFixture
) -> None:
    """Test silently passing by when no directory exists.

    When running list and traversing the individual profile directories
    without the exception to just ignore a file that doesn't need to be
    there (all items should be dirs in the `CONFIGDIR') `-l/--list' will
    try to make a path out of the file and raise a NotADirectoryError.

    Test that this process can continue will an out-of-place file.

    :param main: Patch package entry point.
    :param tmpconfigdir:  Absolute path to directory containing
        ``config.ini``, ``include``, ``exclude`` and ``styles``files.
    :param capsys: Silence stdout.
    """
    out_of_place_file = os.path.join(tmpconfigdir, "out_of_place_file.txt")
    with open(out_of_place_file, "w", encoding="utf-8"):
        # create an empty file
        pass
    with pytest.raises(SystemExit):
        main("--list")
    capsys.readouterr()  # silence


@pytest.mark.usefixtures("tmpconfigdir", "initialize_files")
def test_chosen_style(tmpconfigdir: str) -> None:
    """Test usage of selected style.

    Test that the first option written to the ``styles`` file,
    ``monokai``, is collected.

    :param tmpconfigdir:  Absolute path to directory containing
        ``config.ini``, ``include``, ``exclude`` and ``styles``files.
    """
    styles = os.path.join(tmpconfigdir, "default", "styles")
    pygments = borgini.PygmentPrint(styles)
    assert pygments.style == "monokai"


@pytest.mark.usefixtures("tmpconfigdir", "initialize_files")
def test_default_style(tmpconfigdir: str) -> None:
    """Test usage of default style.

    Test that the ``default`` option written to the ``styles`` file is
    collected if all options are commented out.

    :param tmpconfigdir:  Absolute path to directory containing
        ``config.ini``, ``include``, ``exclude`` and ``styles``files.
    """
    styles = os.path.join(tmpconfigdir, "default", "styles")
    with open(styles, encoding="utf-8") as file:
        content = [r for r in file.readlines() if "monokai" not in r]
    with open(styles, "w", encoding="utf-8") as file:
        for line in content:
            file.write(f"{line}\n")
    pygments = borgini.PygmentPrint(styles)
    assert pygments.style == "default"


@pytest.mark.usefixtures("tmpconfigdir", "initialize_files")
@mock.patch("subprocess.call")
def test_run_call_main_process(
    mock_subproc_call: Mock,
    main: MockMainFixture,
    update_config: UpdateConfigFixture,
    tmpconfigdir: str,
) -> None:
    """Test main.

    Test that no errors occur when the main process is run with a
    configured repo path.

    :param mock_subproc_call: Mock ``subprocess.call`` object.
    :param main: Patch package entry point.
    :param update_config: Update the test config with parameters.
    :param tmpconfigdir:  Absolute path to directory containing
        ``config.ini``, ``include``, ``exclude`` and ``styles``files.
    """
    configpath = os.path.join(tmpconfigdir, "default", "config.ini")
    update_config(configpath, DEFAULT={"repopath": "/dev/null"})
    process_mock = mock.Mock()
    attrs = {"wait.return_value": ("output", "error")}
    process_mock.configure_mock(**attrs)
    mock_subproc_call.return_value = process_mock
    main()


@mock.patch("shutil.which")
@mock.patch("subprocess.call")
def test_run_call_editor(
    mock_which: Mock, mock_subproc_call: Mock, main: MockMainFixture
) -> None:
    """Test running of called editor.

    Test that no errors occur when the user opts to configure a file
    with their favourite editor.

    Mock ``vim`` for systems where ``vim`` isn't installed.

    :param mock_which: Mock ``shutil.which`` object.
    :param mock_subproc_call: Mock ``subprocess.call`` object.
    :param main: Patch package entry point.
    """
    process_mock = mock.Mock()
    attrs = {"wait.return_value": ("output", "error")}
    process_mock.configure_mock(**attrs)
    mock_subproc_call.return_value = process_mock
    mock_which.return_value = None
    with pytest.raises(SystemExit):
        main("vim", "--config")


@pytest.mark.parametrize(
    "uid,expects",
    [
        (0, os.path.join("/etc", "xdg", "borgini")),
        (1, os.path.join(borgini.HOME, ".config", "borgini")),
    ],
    ids=["root", "user"],
)
def test_get_configdir(
    monkeypatch: pytest.MonkeyPatch, uid: int, expects: str
) -> None:
    """Test retrieval of config dir.

    Test the root config directory in /etc is returned when the UID is
    0.

    :param monkeypatch: Mock patch environment and attributes.
    :param uid: 0 for root, > 0 for all other users.
    :param expects: Expected path.
    """

    def _mockreturn():
        return uid

    monkeypatch.setattr(os, "getuid", _mockreturn)
    path = borgini.funcs.get_configdir()
    assert path == expects


def test_windows_attr_error(monkeypatch: pytest.MonkeyPatch) -> None:
    """When user is on Windows.

    :param monkeypatch: Mock patch environment and attributes.
    """

    def _raise_attr_error():
        raise AttributeError

    monkeypatch.setattr(os, "getuid", _raise_attr_error)
    with pytest.raises(AttributeError) as err:
        borgini.funcs.get_configdir()

    assert str(err.value) == "Windows not currently supported"


def test_print_version(
    monkeypatch: pytest.MonkeyPatch,
    main: MockMainFixture,
    nocolorcapsys: NoColorCapsys,
) -> None:
    """Test printing of version on commandline.

    :param monkeypatch: Mock patch environment and attributes.
    :param main: Patch package entry point.
    :param nocolorcapsys: Capture system output while stripping ANSI
        color codes.
    """
    monkeypatch.setattr("borgini.parser.__version__", "1.0.0")
    with pytest.raises(SystemExit):
        main("--version")

    assert nocolorcapsys.stdout().strip() == "1.0.0"
