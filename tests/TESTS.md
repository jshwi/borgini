<!--
This file is auto-generated and any changes made to it will be overwritten
-->
# tests

## tests._tests

All tests for the package are in this module

import flaky for flaky tests which involve the date-time in their
output - there can be a slight skew when the date and time was set
between the output and the _expected


### Borg commands

Test commands run with `BorgBackup`.

Test that values written to the config file yield the correct result
when running borgbackup commands.


### Chosen style

Test usage of selected style.

Test that the first option written to the `styles`  file,
`monokai`, is collected.


### Default style

Test usage of default style.

Test that the `default` option written to the `styles`  file is
collected if all options are commented out.


### Edit invalid path arg

Test execution when editor called to open invalid file.

Test that the usage information is displayed when a file that does
not exist is entered and not the following when running with the
editor positional argument:


* `config`


* `include`


* `exclude`


* `styles`


### Edit path arg

Test execution of editor and the path provided.

Test the correct command is passed when attempting to edit a file
with the editor positional argument.

Run in dry mode for dumb terminal.


### Empty repo setting

Test settings for an empty repo.

Test that the correct stderr is displayed when the `config.ini`
file has not been configured to contain a path to the backup
repository. Assert non-zero exit-code.


### File exists error

Test error when a file already exists when initializing new one.

Demonstrate that `make_appdir` should not be in
`borgini.data.Data.__init__`


### Get configdir

Test retrieval of config dir.

Test the root config directory in /etc is returned when the UID is
0.


### Initialize files

Test initialization of files.

Test that `config.ini`, `include`, `exclude` and `styles`
are all initialized and that the correct message is displayed.


### Invalid keyfile

Test invalid keyfile.

Test the correct warning message is displayed when the process is
attempting to go on without a correct value for a keyfile.


### Invalid path arg

Test execution with an invalid path argument.

Test that the usage information is displayed when a file that does
not exist is entered and not the following:


* `config`


* `include`


* `exclude`


* `styles`


### List arg

Test printing of list.

Test for the correct output when the `--list` flag is used.


### No ssh

Test execution when SSH is not meant to be used.

Test the path is properly adjusted to not include the full ssh path
when `ssh` is False.


### Pass on not a directory err

Test silently passing by when no directory exists.

When running list and traversing the individual profile directories
without the exception to just ignore a file that doesn’t need to be
there (all items should be dirs in the CONFIGDIR’) \`-l/–list\`\`
will try to make a path out of the file and raise a
NotADirectoryError.

Test that this process can continue will an out-of-place file.


### Print version

Test printing of version on commandline.


### Random opts

Run this test function 10 times.

Random values will be generated and written to the config file

Test when activating the borgbackup commands that the correct values
have been parsed and retrieved by the process


### Read keyfile

Test loading of keyfile.

Test that the correct password is retrieved from a keyfile when the
keyfile path is supplied in the config file.


### Remove arg

Test call to remove.

First create a profile and test the remote function with it so that
we can test that the `--remove` flag properly removes profiles.


### Remove no exist

Test call to remove when target doesn’t exist.

Test that the correct warning is displayed when the `--remove`
option is passed with a profile name and that name does not exist.


### Repair config key err

Test repairing a config with a key error.

Test that an out-of-place section does not halt the process and is
subsequently corrected by the `configparser.ConfigParser` object.

Useful if there are any section updates in the code.


### Run call editor

Test running of called editor.

Test that no errors occur when the user opts to configure a file
with their favourite editor.

Mock `vim` for systems where `vim` isn’t installed.


### Run call main process

Test main.

Test that no errors occur when the main process is run with a
configured repo path.


### Run editor without arg

Test error message when argument needs to be provided to editor.

Test for the correct error message is displayed when an editor is
called without a file to edit.


### Run uninstalled editor

Test call to editor that is not installed.

Test for the correct error message is displayed when the entered
“editor” does not exist.


### Select profile

Test selection of profile.

Test the correct alternate profile is being used when the
`--select` flag is passed with a non-default profile.


### Show config

Test printing of config.

Test the correct stdout is displayed when running the `--config`
flag without an editor to show the config.


### Show exclude

Test printing of exclude config.

Test the correct stdout is displayed when running the `--exclude`
flag without an editor to show the exclude file.


### Show include

Test printing of include config.

Test the correct stdout is displayed when running the `--include`
flag without an editor to show the include file.


### Windows attr error

When user is on Windows.


