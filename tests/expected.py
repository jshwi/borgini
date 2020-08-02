"""
tests.expected
==============

Expected stdout and stderr for tests
"""
from . import USER, HOST

EMPTY_REPO_SETTING = (
    "Path to repo not configured\n"
    "Make all necessary changes to config before running this again\n"
    "You can do this by running the command:\n\n"
    ". borgini EDITOR --config --select default\n"
)
INVALID_PATH_ARG = (
    "usage: borgini [-h] [-l] [-d] [--select PROFILE]\n"
    "                               [--remove PROFILE [PROFILE ...]] [-c] "
    "[-i] [-e]\n"
    "                               [-s]\n"
    "                               [EDITOR]\n"
    "borgini: error: unrecognized arguments: --invalid\n"
)
SHOW_CONFIG = (
    "[DEFAULT]\n"
    f"reponame = {HOST}\n"
    "repopath = None\n"
    "timestamp = %Y-%m-%dT%H:%M:%S\n"
    "ssh = True\n"
    "prune = True\n"
    "\n"
    "[SSH]\n"
    f"remoteuser = {USER}\n"
    f"remotehost = {HOST}\n"
    "port = 22\n"
    "\n"
    "[BACKUP]\n"
    "verbose = True\n"
    "stats = True\n"
    "list = True\n"
    "show-rc = True\n"
    "exclude-caches = True\n"
    "filter = AME\n"
    "compression = lz4\n"
    "\n"
    "[PRUNE]\n"
    "verbose = False\n"
    "stats = True\n"
    "list = True\n"
    "show-rc = True\n"
    "keep-daily = 7\n"
    "keep-weekly = 4\n"
    "keep-monthly = 6\n"
    "\n"
    "[ENVIRONMENT]\n"
    "keyfile = None\n\n"
)
BLURB_TOP = """
# This is an auto-generated list which should suite most users
"""
BLURB_BOTTOM = """
#
# . ensure you always use the absolute path for directories and files
# . line and inline comments with `#' are supported
#
"""
SHOW_INCLUDE = (
    "# --- include ---"
    + BLURB_TOP
    + "# Remove any entries you do not want to include and add any that you do"
    + BLURB_BOTTOM
    + "/home\n"
    "/root\n"
    "/var\n"
    "/usr/local\n"
    "/srv\n\n"
)
SHOW_EXCLUDE = (
    "# --- exclude ---"
    + BLURB_TOP
    + "# Remove any entries you do not want to exclude and add any that you do"
    + BLURB_BOTTOM
    + "/home/*/.cache/*\n"
    "/var/cache/*\n"
    "/var/tmp/*\n"
    "/var/run\n\n"
)
REMOVE_ARG = "removed profile:\n. newprofile\n"
REMOVE_NO_EXIST = "profile `newprofile' does not exist\n"
