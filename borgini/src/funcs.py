"""
borgini.src.funcs
=================

Package entry point

Parse commandline arguments

Invoke classes, methods and functions
"""
import os
import re
import shutil
import subprocess
import sys

from . import HOME, Data, config


def get_configdir():
    """Get the path to the configuration files most suitable for active
    os and privilege.

    :return: Path to configuration dir for all profiles.
    """
    try:
        if os.getuid() == 0:
            return os.path.join("/etc", "xdg", "borgini")

        return os.path.join(HOME, ".config", "borgini")

    except AttributeError as err:
        raise AttributeError("Windows not currently supported") from err


CONFIGDIR = get_configdir()


def get_file_arg(namespace, files):
    """Detect that a file has been selected to edit or view.

    :param namespace:   The ``ArgumentParser`` ``Namespace.__dict__``.
    :param files:       The files dictionary returned from
                        ``src.data.Data``.
    :return:            Return an absolute path or ``None``.
    """
    notfile = "editor", "dry", "select", "list", "remove"
    for key in namespace:
        if key not in notfile and namespace[key]:
            try:
                return files[key]

            except KeyError:
                return files[f"{key}.ini"]

    return None


def normalize_ntpath(path):
    """Format NT path to a Unix-like path.

    :param path:    Path to format.
    :return:        Returns a formatted path if running Windows
                    otherwise the same path that came in.
    """
    normalized = "/".join(
        p[:-1] if re.match("^[a-zA-Z]:", p) else p
        for p in [p.lower() for p in path.split("\\")]
    )
    return normalized if path[0] == "/" else f"/{normalized}"


def edit_files(edit, file, pygments, dry):
    """Edit a config file with the editor of choice.

    :param edit:        The editor to edit with.
    :param file:        The path to the file to edit.
    :param pygments:    Instantiated ``src.print.PygmentPrint`` class
                        configured with user's style option.
    :param dry:         Dry mode for when we do not want to execute the
                        code.
    """
    file = normalize_ntpath(file)
    command = f"{edit} {file}"
    if dry:
        pygments.print(command, ini=False)
    else:
        subprocess.call(command, shell=True)


def read_file(filepath, pygments):
    """Read the file and print the output. If reading ``config.ini``
    color the text with ini-style syntax, otherwise shell-like syntax.

    :param filepath:    The file to read from.
    :param pygments:    Instantiated ``src.print.PygmentPrint`` class.
                        configured with user's style option.
    """
    ini = os.path.basename(filepath) == "config.ini"
    with open(filepath, encoding="utf-8") as file:
        lines = file.read()

    pygments.print(lines, ini=ini)


def edit_file(editor, namespace, files, pygments, dry):
    """Call the editor to edit a file. If the argument passed does not
    correspond to an existing file print help. If an editor is not
    provided go on to simply print the file content.

    :param editor:      The editor to edit the file with.
    :param namespace:   ``argparse.ArgumentParser's``
                        ``Namespace.__dict__``.
    :param files:       Dictionary of config file paths.
    :param pygments:    Instantiated ``src.print.PygmentPrint`` class
                        configured with user's style option.
    :param dry:         Dry mode for when we do not want to execute the
                        code.
    """
    filepath = get_file_arg(namespace, files)
    if editor:
        edit_files(editor, filepath, pygments, dry)
        sys.exit(0)

    elif filepath:
        read_file(filepath, pygments)
        sys.exit(0)


def get_path(borguser, hostname, port, repopath, ssh):
    """Get the path to the backup repository location. If ``ssh`` is
    ``True`` this will return the configured ssh path on the remote
    system. If ``ssh`` is ``False`` the repository will need exist on
    the localhost.

    Note: The ``repopath`` setting in the ``DEFAULT`` section will
    be the directory the repository is in, not the actual repository
    i.e. ``/path/to/repopath/reponame`` not ``/path/to/repopath``.

    :param borguser:    The remote's user invoking ``borg`` on that
                        machine.
    :param hostname:    The remote's hostname.
    :param port:        The port that the remote allows ssh through.
    :param repopath:    The path relative to root on the remote or the
                        localhost.
    :param ssh:         Boolean for whether using ssh or not.
    :return:            A path configured based on the ``config.ini``
                        parameters.
    """
    return f"ssh://{borguser}@{hostname}:{port}{repopath}" if ssh else repopath


def set_passphrase(keyfile, catch):
    """Export the ``BORG_PASSPHRASE`` environment variable from a
    keyfile.

    :param keyfile: The absolute path to the passphrase keyfile.
    :param catch:   ``src.parser.Catch`` - exit if necessary and inform
                    user why.
    """
    if keyfile:
        if os.path.isfile(keyfile):
            with open(keyfile, encoding="utf-8") as file:
                passphrase = file.read().strip()

            os.environ["BORG_PASSPHRASE"] = passphrase
        else:
            catch.announce_keyfile()


def initialize_config(configpath, catch):
    """If a ``config.ini`` file does not exist create the file and write
    the default values.

    Otherwise, read ``config.ini`` for it's values.
    """
    raw_config = config.RawConfig(configpath)
    if not os.path.isfile(configpath):
        raw_config.write_new_config()
        catch.announce_first_run()

    raw_config.read()
    return config.Config(raw_config)


def remove_profile(remove):
    """Remove selected profile.

    :param remove:  The profile entered to remove via
                    ``argparse.ArgumentParser`` and the commandline.
    """
    profiles = ""
    if remove:
        plural = "s" if len(remove) > 1 else ""
        for profile in remove:
            profiledir = os.path.join(CONFIGDIR, profile)
            if os.path.isdir(profiledir):
                shutil.rmtree(profiledir)
                profiles += f"\n. {profile}"
            else:
                print(f"profile `{profile}' does not exist")
                sys.exit(1)

        print(f"removed profile{plural}:{profiles}")
        sys.exit(0)


def list_profiles(show_profiles, pygments):
    """If ``show_profiles`` is ``True`` than display a list of profiles
    that exist otherwise do nothing.

    :param show_profiles:   Boolean switch from the commandline.
    :param pygments:        Instantiated ``src.print.PygmentPrint``
                            class configured with user's style option.
    """
    if show_profiles:
        profiles = os.listdir(CONFIGDIR)
        profiles.insert(0, profiles.pop(profiles.index("default")))
        for profile in profiles:
            data = Data(CONFIGDIR, profile)
            configpath = data.get_path("config.ini")
            raw_config = config.RawConfig(configpath)
            try:
                raw_config.read()

            except NotADirectoryError:
                continue

            _config = config.Config(raw_config)
            obj = _config.dict["DEFAULT"]
            del obj["timestamp"]
            out = f"[{profile}]\n"
            for key, val in obj.items():
                out += f"{key} = {val}\n"

            pygments.print(out)
        sys.exit(0)


def initialize_datafiles(data):
    """Write the default settings to the ``include``, ``exclude`` and
    ``styles`` files.

    :param data: ``src.data.Data``.
    """

    def comment(filetype):
        return (
            f"# --- {filetype} ---\n"
            "# This is an auto-generated list which should suite most users\n"
            f"# Remove any entries you do not want to {filetype} and add any "
            f"that you do\n"
            "#\n"
            "# . ensure you always use the absolute path for directories and "
            "files\n"
            "# . line and inline comments with `#' are supported\n"
            "#"
        )

    pathlists = (
        (
            f"{comment('include')}",
            "/home",
            "/root",
            "/var",
            "/usr/local",
            "/srv",
        ),
        (
            f"{comment('exclude')}",
            "/home/*/.cache/*",
            "/var/cache/*",
            "/var/tmp/*",
            "/var/run",
        ),
        (
            "# --- styles ---",
            "# Uncomment a single line to select style for syntax "
            "highlighting",
            "# `pygments' must be installed to use this feature",
            "#",
            "# . Install pygments by running:",
            "# . root:               `pip install pygments'",
            "# . user (recommended): `pip install pygments --user'",
            "#",
            '# STYLE="default"',
            '# STYLE="emacs"',
            '# STYLE="friendly"',
            '# STYLE="colorful"',
            '# STYLE="autumn"',
            '# STYLE="murphy"',
            '# STYLE="manni"',
            'STYLE="monokai"',
            '# STYLE="perldoc"',
            '# STYLE="pastie"',
            '# STYLE="borland"',
            '# STYLE="trac"',
            '# STYLE="native"',
            '# STYLE="fruity"',
            '# STYLE="bw"',
            '# STYLE="vim"',
            '# STYLE="vs"',
            '# STYLE="tango"',
            '# STYLE="rrt"',
            '# STYLE="xcode"',
            '# STYLE="igor"',
            '# STYLE="paraiso-light"',
            '# STYLE="paraiso-dark"',
            '# STYLE="lovelace"',
            '# STYLE="algol"',
            '# STYLE="algol_nu"',
            '# STYLE="arduino"',
            '# STYLE="rainbow_dash"',
            '# STYLE="abap"',
            '# STYLE="solarized-dark"',
            '# STYLE="solarized-light"',
            '# STYLE="sas"',
            '# STYLE="stata"',
            '# STYLE="stata-light"',
            '# STYLE="stata-dark"',
            '# STYLE="inkpot"',
        ),
    )
    data.initialize_data_files(pathlists)
