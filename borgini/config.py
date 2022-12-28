"""
borgini.config
==============

All things ``config.ini``
"""
from __future__ import annotations

import configparser
import getpass
import os
import socket
import typing as t

NONE = "None"
DEFAULT = "DEFAULT"


class RawConfig:
    """Contains the ``configparser.ConfigParser`` object.

    Write to and read from the ``config.ini`` file. The boolean values
    get written to the file as strings, and they get read from the file
    into the buffer as strings too. Not all values are as they should be
    when read into Python so this will get subclassed into
    ``config.Proxy`` first.

    :param configpath: The path to the config.ini file - this depends on
        the profile used and whether this is run as ``"$USER"`` or as
        root.
    """

    def __init__(self, configpath: str | os.PathLike) -> None:
        self.configpath = configpath
        self.parser = configparser.ConfigParser(interpolation=None)

    def _read_kwargs(self, **kwargs: t.Dict[str, t.Any]):
        self.parser.read_dict(kwargs)

    def _load_default_values(self) -> None:
        hostname = socket.gethostname()
        user = getpass.getuser()
        self._read_kwargs(
            DEFAULT={
                "reponame": hostname,
                "repopath": NONE,
                "timestamp": "%Y-%m-%dT%H:%M:%S",
                "ssh": True,
                "prune": True,
            },
            SSH={"remoteuser": user, "remotehost": hostname, "port": "22"},
            BACKUP={
                "verbose": True,
                "stats": True,
                "list": True,
                "show-rc": True,
                "exclude-caches": True,
                "filter": "AME",
                "compression": "lz4",
            },
            PRUNE={
                "verbose": False,
                "stats": True,
                "list": True,
                "show-rc": True,
                "keep-daily": "7",
                "keep-weekly": "4",
                "keep-monthly": "6",
            },
            ENVIRONMENT={"keyfile": NONE},
        )

    def write_values(self) -> None:
        """Write values from ``ConfigParser`` to the config file."""
        with open(self.configpath, "w", encoding="utf-8") as configfile:
            self.parser.write(configfile)

    def write_new_config(self) -> None:
        """Load default values into the ``ConfigParser`` and write."""
        self._load_default_values()
        self.write_values()

    def read(self) -> None:
        """Read the ``config.ini`` file and avoid non-critical errors.

        Once the ``config.ini`` is read and loaded into the buffer write
        it back to the file as this class will filter out non-parsable
        configurations back to their default. If there is a key in the
        config.ini file that cannot be parsed skip reading it into
        buffer, as it will be removed once the config is subsequently
        written. Any new keys and configurations that may be added in
        the future will also be safely added to the config.
        """
        self._load_default_values()
        reader = configparser.ConfigParser(interpolation=None)
        reader.read(self.configpath)
        for section in reader:
            for key in dict(reader[section]):
                if section == DEFAULT or (
                    section != DEFAULT and key not in reader[DEFAULT]
                ):
                    try:
                        self.parser[section][key] = reader[section][key]

                    except KeyError:
                        pass

        self.write_values()


class Proxy:
    """Subclass ``RawConfig`` to inherit the ``ConfigParser`` object.

    Translate the string values into boolean and ``NoneType`` values or
    some of the tests will not work i.e. ``None`` and ``False`` will be
    ``True`` as the strings ``"None"`` and ``"False"`` Inherit
    ``RawConfig`` after the ``parser.Catch`` string has identified
    run-time errors.

    :param raw_config: Instantiated ``RawConfig`` object containing the
        ``configparser.ConfigParser`` object as ``parser``.
    """

    def __init__(self, raw_config: RawConfig) -> None:
        self.parser = raw_config.parser
        self.sections = self.section_list()

    def section_list(self) -> t.List[str]:
        """Index the sections of the config.ini file.

        :return: List of config sections.
        """
        sections = self.parser.sections()
        sections.append(DEFAULT)
        return sections

    def _filter_default(self, section: str) -> t.Dict[str, t.Any]:
        if section == DEFAULT:
            return dict(self.parser[section])

        return {
            k: v
            for k, v in self.parser[section].items()
            if k not in dict(self.parser[DEFAULT])
        }

    def _raw_dict(self) -> t.Dict[str, t.Any]:
        return {s: self._filter_default(s) for s in self.sections}

    @staticmethod
    def _convert_null(obj: t.Dict[str, t.Any]) -> t.Dict[str, t.Any]:
        return {s: {k: v for k, v in obj[s].items() if v != NONE} for s in obj}

    def _get_boolean(self, section: str, key: str) -> bool:
        try:
            if key.startswith("keep-"):
                raise ValueError

            return self.parser.getboolean(section, key)

        except ValueError:
            return self._filter_default(section)[key]

    def _convert_booleans(self, obj: t.Dict[str, t.Any]) -> t.Dict[str, t.Any]:
        return {s: {k: self._get_boolean(s, k) for k in obj[s]} for s in obj}

    @staticmethod
    def _filter_null(raw_dict: t.Dict[str, t.Any]) -> t.Dict[str, t.Any]:
        return {k: v for k, v in raw_dict.items() if v}

    def convert_proxy(self) -> t.Dict[str, t.Any]:
        """Convert ``ConfigParser`` into python friendly dictionary.

        :return: Dictionary object.
        """
        raw_dict = self._raw_dict()
        truthy = self._convert_null(raw_dict)
        obj = self._convert_booleans(truthy)
        return self._filter_null(obj)


class Config(Proxy):
    """Final config object suitable for running with python methods.

    Subclass the ``config.Proxy`` class to inherit the translated
    config object from ``ConfigParser`` -> ``Dict``.

    :param raw_config: The ``configparser.ConfigParser`` object.
    """

    def __init__(self, raw_config: RawConfig) -> None:
        super().__init__(raw_config)
        self.dict = self.convert_proxy()

    def _get_section(self, section: str) -> t.Dict[str, t.Any]:
        return self.dict[section]

    def get_key(self, section: str, key: str) -> str | None:
        """Get a key from the dictionary object in ``self``.

        If the value is not found such as the ``BORG_PASSPHRASE``
        environment variable (as the string value ``"None"`` would have
        been omitted by ``config.Proxy``) return ``None`` in its
        place to avoid an expected error and carry on omitting the key.

        :param section: The primary key and the section from
            ``configparser.ConfigParser``.
        :param key: The key containing the configured value.
        :return: The value of the called key.
        """
        try:
            return self._get_section(section)[key]

        except KeyError:
            return None

    def get_keytuple(
        self, **kwargs: t.Tuple[str, ...]
    ) -> tuple[str | bool | None, ...]:
        """Return multiple values at once from ``self.dict[section]``.

        Return as a tuple that can be unpacked by the keys passed to the
        method.

        :param kwargs: Sections to get.
        :return: A tuple of multiple any one or more values.
        """
        return tuple(
            self.get_key(s, k)
            for s in kwargs  # pylint: disable=consider-using-dict-items
            for k in kwargs[s]
        )

    @staticmethod
    def _get_flags(obj: t.Dict[str, str]) -> t.List[str]:
        return [f"--{k}" for k, v in obj.items() if v is True]

    @staticmethod
    def _get_keyvals(obj: t.Dict[str, str]) -> t.List[str]:
        return [f"--{k} {v}" for k, v in obj.items() if isinstance(v, str)]

    def return_all(self, section: str) -> t.Tuple[str, ...]:
        """Get all args belonging to a section.

        The (kw)args that are boolean flags only need to exist, as their
        existence in the script is the switch - so these are not
        returned as kwargs but rather args. Treat values that aren't
        boolean differently as the key and the value need to be
        included.

        :param section: The section from which the (kw)args should be
            retrieved.
        :return: A tuple of all switches prefixed with ``"--"`` and all
            kwargs.
        """
        obj = self.dict[section]
        args = self._get_flags(obj)
        args.extend(self._get_keyvals(obj))
        return tuple(args)
