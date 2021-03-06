"""
borgini.src
===========
"""
import datetime
import os
import pathlib
import shutil
import subprocess

from pygments import highlight
from pygments.formatters.terminal256 import Terminal256Formatter
from pygments.lexers.configs import IniLexer
from pygments.lexers.shell import BashLexer

HOME = str(pathlib.Path.home())


class BorgBackup:
    """``Borgbackup`` wrapper class,

    :param repopath:    Path to the backup repository - local dir if
                        ``ssh`` set to ``False``, remote server and repo
                        dir if ``ssh`` set to ``True``.
    :param pygments:    Instantiated ``src.print.PygmentPrint`` class
                        configured with user's style option.
    :param dry:         if ``--dry`` is passed through the commandline
                        then display the commandline arguments that
                        would be passed to ``borgbackup`` without
                        actually running the it.
    :param args:        Arguments parsed from the ``config.ini`` file
                        with ``configparser.ConfigParser``.
    """

    def __init__(self, repopath, pygments, dry, *args):
        self.repo = f"{repopath}/{args[0]}"
        self.pygments = pygments
        self.bin = shutil.which("borg")
        self.dry = dry if self.bin else True
        self.date = datetime.datetime.now().strftime(args[1])
        self.archive = f"{self.repo}::{args[0]}-{self.date}"

    @staticmethod
    def _separate_keep(args):
        keep = [
            args.pop(args.index(a))
            for a in list(args)
            if a.startswith("--keep-")
        ]
        return tuple(args), tuple(keep)

    def _run_borg(self, args):
        borgargs = " ".join(args)
        command = f"{self.bin} {borgargs}"
        subprocess.call(command, shell=True)

    def _dry_mode(self, args):
        borgargs = " ".join([f" {a}\n" for a in args])
        borg = self.bin if self.bin else "borg"
        self.pygments.print(f"\n{borg} {borgargs[1:-1]}", ini=False)

    def borg(self, *args):
        """Run ``borgbackup`` ``create`` to create a backup or ``prune``
        to prune an old backup according to the ``--keep-*`` settings.
        If ``--dry`` has been passed through the commandline only
        display the command that would occur - this won't run a backup
        or prune.

        :param args:    Arguments for the borg command to receive,
                        parsed from the ``config.ini``, the ``include``
                        and the ``exclude`` files
        """
        if self.dry:
            self._dry_mode(args)
        else:
            self._run_borg(args)

    def create(self, args, exclude, include):
        """Run the ``borg create`` command. Includes several
        miscellaneous boolean arguments and key-values parsed from the
        ``config.ini`` file. Includes the ``exclude`` arguments
        formatted as ``[--exclude ARG, ...]``. Includes the ``include``
        arguments formatted as ``[ARG, ...]``.

        :param args:    Flags that effect compression, whether stats are
                        shown, the command is verbose etc...
        :param exclude: Directories or files to exclude parsed from the
                        exclude list.
        :param include: Directories or files to include parsed from the
                        include list - files and dirs will be overridden
                        by exclude.
        """
        self.borg("create", *args, *exclude, f"{self.archive}", *include)

    def prune(self, args):
        """Run the ``borg prune`` command Includes several miscellaneous
        boolean arguments that can be further explored by running
        ``borgini --config``.

        :param args:    Flags that effect compression, whether stats are
                        shown, the command is verbose etc...
        """

        pruneargs, keep = self._separate_keep(list(args))
        self.borg("prune", *pruneargs, f"{self.repo}", *keep)


class Data:
    """Resolve the directory the configurations belong to. Get the list
    of files to include and exclude. Allow the files to contain comments
    and avoid parsing them.

    :param profile: The profile that ``borgini`` is being run under.
    """

    def __init__(self, appdir, profile):
        self.dirname = os.path.join(appdir, profile)
        self.files = self._get_file_obj()

    def _get_file_obj(self):
        paths = "config.ini", "include", "exclude", "styles"
        return {p: os.path.join(self.dirname, p) for p in paths}

    def make_appdir(self):
        """Create the configuration directory for all the user's
        settings.
        """
        if not os.path.isdir(self.dirname):
            os.makedirs(self.dirname)

    def _get_paths(self, *args):
        return tuple(self.files[arg] for arg in args)

    def initialize_data_files(self, pathlists):
        """If the ``include`` or ``exclude`` files do not exist
        write the starter templates to file.

        :param pathlists:   Tuple containing two tuples of lines to
                            write to file.
        """
        for count, datafile in enumerate(
            self._get_paths("include", "exclude", "styles")
        ):
            if not os.path.isfile(datafile):
                with open(datafile, "w") as file:
                    for path in pathlists[count]:
                        file.write(f"{path}\n")

    @staticmethod
    def _read_datafile(path):
        with open(path) as file:
            readfile = file.read().strip()

        return readfile.splitlines()

    def _parse_datafile(self, path):
        files = self._read_datafile(path)

        # remove string starting at the hash symbol if inline
        # comment or remove entire line if the first index is the
        # hash symbol
        return [f"'{f.split('#')[0].strip()}'" for f in files if f[0] != "#"]

    def get_path(self, key):
        """Get the path of the file by calling it's key

        :param key: Name of the basename file
        :return:    The file's absolute path
        """
        return self.files[key]

    def _get_files(self, path):
        pathlist = []
        if os.path.isfile(path):
            pathlist.extend(self._parse_datafile(path))

        return pathlist

    def _format_include(self, path):
        return tuple(self._get_files(path))

    def get_include(self):
        """The tuple of directories and files to include from the
        ``include`` file

        :return: Tuple of paths to include in backups for that profile
        """
        include_path = self.get_path("include")
        return self._format_include(include_path)

    @staticmethod
    def _format_exclude(pathlist):
        return tuple([f"--exclude {e}" for e in pathlist])

    def get_exclude(self):
        """Return the values obtained from the ``exclude`` file

        Unlike the ``include`` file this doesn't necessarily need to
        be populated

        Every item will automatically be prefixed with ``--exclude``
        for the ``borgbackup`` commandline

        :return:    A lit of paths to exclude - this will override items
                    in ``include``

        """
        exclude_path = self.get_path("exclude")
        exclude_list = self._get_files(exclude_path)
        return self._format_exclude(exclude_list)


class PygmentPrint:
    """Instantiate with the path leading to the config file for syntax
    styles. Class will read the file and maintain it's config throughout
    the process.

    :param styles: The path to the ``styles`` config file.
    """

    def __init__(self, styles):
        self.styles = styles
        self.style = self.read_styles()

    def read_styles(self):
        """Read the ``styles`` file into the buffer. Parse the
        configuration that is uncommented and ignore the rest.
        """
        with open(self.styles) as file:
            contents = file.readlines()

        for content in contents:
            try:
                if content[0] != "#":
                    return content.split("=")[1].replace('"', "").strip()

            except IndexError:
                pass

        return "default"

    def print(self, string, ini=True):
        """Print with ``pygments``. Read the string entered in method
        Configure syntax highlighting for either shell or ini files and
        processes.

        :param string:  What is to be printed.
        :param ini:     ``True`` for printing ini files, ``False`` for
                        shell.
        """
        if string:
            lexer = IniLexer if ini else BashLexer
            string = highlight(
                string, lexer(), Terminal256Formatter(style=self.style)
            )
            print(string)
