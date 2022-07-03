"""
borgini.parser
==============

Parse the commandline arguments and check arguments for errors and exit
informatively
"""
from __future__ import annotations

import argparse
import sys
import typing as t

from ._version import __version__


def getcolor(string: str, code: int) -> str:
    """Return a given string in color depending on the code provided.

    :param string: String to color.
    :param code: Corresponding ANSI escape code.
    :return: The colored string.
    """
    return f"\u001b[0;3{code};40m{string}\u001b[0;0m"


class RawParser(argparse.ArgumentParser):
    """Inherit ``ArgumentParser`` to be parsed from the commandline.

    Format a separate ``Namespace`` object to get arguments by group.
    """

    def __init__(self) -> None:
        # noinspection PyTypeChecker
        super().__init__(
            prog=getcolor("borgini", 6),
            formatter_class=lambda prog: argparse.HelpFormatter(
                prog, max_help_position=42
            ),
        )
        self._add_arguments()
        self._add_editor_args()
        self.args = self.parse_args()
        self.arg_groups: t.Dict[str | None, argparse.Namespace] = {}
        self._get_argument_group()
        self._version_request()

    def _add_editor_args(self) -> None:
        editor_args = self.add_argument_group(title="EDITOR")
        editor_args.add_argument(
            "-c", "--config", action="store_true", help="edit or view config"
        )
        editor_args.add_argument(
            "-i",
            "--include",
            action="store_true",
            help="edit or view list of files and directories to include",
        )
        editor_args.add_argument(
            "-e",
            "--exclude",
            action="store_true",
            help="edit or view list of files and directories to exclude",
        )
        editor_args.add_argument(
            "-s",
            "--styles",
            action="store_true",
            help="edit or view list of styles for syntax highlighting",
        )

    def _add_arguments(self) -> None:
        """Parse args from sys.argv."""
        self.add_argument(
            "editor",
            metavar="EDITOR",
            nargs="?",
            action="store",
            help="edit settings e.g. $ borgini vim --config",
        )
        self.add_argument(
            "-l", "--list", action="store_true", help="list existing profiles"
        )
        self.add_argument(
            "-d",
            "--dry",
            action="store_true",
            help="view the commandline arguments that would be run",
        )
        self.add_argument(
            "-v",
            "--version",
            action="store_true",
            help="show version and exit",
        )
        self.add_argument(
            "--select",
            action="store",
            default="default",
            metavar="PROFILE",
            help="create or select an alternative settings profile",
        )
        self.add_argument(
            "--remove",
            metavar="PROFILE",
            nargs="+",
            action="store",
            help="remove profile or profiles",
        )

    def _get_argument_group(self) -> None:
        for group in self._action_groups:
            # noinspection PyProtectedMember
            group_dict = {
                a.dest: getattr(self.args, a.dest, None)
                # pylint: disable=protected-access
                for a in group._group_actions
            }
            self.arg_groups[group.title] = argparse.Namespace(**group_dict)

    def _version_request(self) -> None:
        # print version if `--version` is passed to commandline
        if self.args.version:
            print(__version__)
            sys.exit(0)


class Catch:
    """Exit if it can be determined essential values are missing.

    Exit informatively.

    :param profile: Profile that the process is running under so that
        suggestion commands can be displayed.
    """

    def __init__(self, profile: str) -> None:
        self.profile = profile

    def show_command(self, arg: str) -> str:
        """Format and color the example commands provided.

        :param arg: The argument the command would need.
        :return: The formatted and colored example command.
        """
        return f". borgini EDITOR --{arg} --select {self.profile}"

    def check_repopath_config(self, repopath: str) -> None:
        """Exit process if the path to the backup repo not provided.

        Exit with a non-zero exit status.

        :param repopath: Path to back up repository or ``None``.
        """
        if not repopath:
            print(
                f"{getcolor('Path to repo not configured', 3)}\n"
                "Make all necessary changes to config before running this "
                "again\n"
                "You can do this by running the command:\n\n"
                f"{self.show_command('config')}",
                file=sys.stderr,
            )
            sys.exit(1)

    def announce_first_run(self) -> None:
        """Announce that a new default config file has been initialized.

        Not an error. Exit with zero exit status.
        """
        print(
            f"{getcolor('First run detected for profile', 3)}: "
            f"{getcolor(self.profile, 6)}\n"
            "Make all necessary changes to config before running this again\n"
            f"You can do this by running the command:\n\n"
            f"{self.show_command('config')}\n\n"
            "Default settings have been written to the `include' and "
            "`exclude' lists\n"
            "These can be edited by running:\n\n"
            f"{self.show_command('include')}\n"
            f"{self.show_command('exclude')}"
        )
        sys.exit(0)

    def announce_keyfile(self) -> None:
        """Announce keyfile has been created.

        If the keyfile section of the config file has been populated
        but the keyfile cannot be found let the user know as this would
        make it clearer as to why the backup might fail eventually if
        ``borgbackup`` prompts for a passphrase.

        If no keyfile is necessary then the field should be ``None``
        which this message would also notify the user about.
        """
        print(
            f'{getcolor("BORG_PASSPHRASE keyfile cannot be found", 3)}\n'
            f"attempting backup without keyfile\n\n"
            'add a valid keyfile or "None" to BORG_PASSPHRASE to stop '
            "receiving this message\n"
            "You can do this by running the command:\n",
            f"{self.show_command('config')}\n",
        )
