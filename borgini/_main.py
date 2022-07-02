"""
borgini._main
=============

Contains package entry point.
"""
from __future__ import annotations

import shutil
import sys

from . import funcs, parser
from ._core import BorgBackup, Data, PygmentPrint

__version__ = "1.0.0"


class Parser(parser.RawParser):
    """Inherit ``RawParser`` which inherits ``argparse.ArgumentParser``.

    Catch any incompatible arguments. Instantiate and access the
    ``Namespace`` object from this class.
    """

    def __init__(self) -> None:
        super().__init__()
        self.editor = self.args.editor
        self.editor_opts = any(
            v for k, v in self.arg_groups["EDITOR"].__dict__.items()
        )
        self.message = self._get_message()
        self._exit_error()

    def _check_editor(self) -> str | None:
        # exit the process if the editor argument has been incorrectly
        # supplied
        if not shutil.which(self.editor):
            return parser.getcolor(
                f"EDITOR must be installed: `{self.editor}' cannot be found",
                code=1,
            )
        if not self.editor_opts:
            return parser.getcolor(
                "EDITOR must be followed by a file to edit", code=1
            )
        return None

    def _get_message(self) -> str | None:
        if self.editor:
            return self._check_editor()
        return None

    def _exit_error(self) -> None:
        if self.message:
            print(self.message, file=sys.stderr)
            self.print_help()
            sys.exit(1)


def main() -> None:
    """Main function for package."""
    _parser = Parser()
    args = _parser.args
    profile = args.select
    dry = args.dry
    data = Data(funcs.CONFIGDIR, profile)
    data.make_appdir()
    funcs.initialize_datafiles(data)
    pygments = PygmentPrint(data.files["styles"])
    catch = parser.Catch(profile)
    _configpath = data.get_path("config.ini")
    _config = funcs.initialize_config(_configpath, catch)
    funcs.remove_profile(args.remove)
    funcs.list_profiles(args.list, pygments)
    funcs.edit_file(args.editor, args.__dict__, data.files, pygments, dry)
    funcs.set_passphrase(
        _config.get_key("ENVIRONMENT", "keyfile"), catch  # type: ignore
    )
    catch.check_repopath_config(
        _config.get_key("DEFAULT", "repopath")  # type: ignore
    )
    fullpath = funcs.get_path(
        *_config.get_keytuple(  # type: ignore
            SSH=("remoteuser", "remotehost", "port"),
            DEFAULT=("repopath", "ssh"),
        )
    )
    borg = BorgBackup(
        fullpath,
        pygments,
        dry,
        *_config.get_keytuple(DEFAULT=("reponame", "timestamp")),
    )
    backup = _config.return_all("BACKUP")
    include = data.get_include()
    exclude = data.get_exclude()
    borg.create(backup, exclude, include)
    if _config.get_key("DEFAULT", "prune"):
        pruneargs = _config.return_all("PRUNE")
        borg.prune(pruneargs)
