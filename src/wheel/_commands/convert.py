from __future__ import annotations

import os.path
import re
from abc import ABCMeta, abstractmethod
from collections import defaultdict
from collections.abc import Iterator
from email.message import Message
from email.parser import Parser
from email.policy import EmailPolicy
from glob import iglob
from pathlib import Path
from textwrap import dedent
from zipfile import ZipFile

from packaging.tags import parse_tag

from .. import __version__
from .._metadata import generate_requirements
from ..wheelfile import WheelFile

egg_filename_re = re.compile(
    r"""
    (?P<name>.+?)-(?P<ver>.+?)
    (-(?P<pyver>py\d\.\d+)
     (-(?P<arch>.+?))?
    )?.egg$""",
    re.VERBOSE,
)
egg_info_re = re.compile(
    r"""
    ^(?P<name>.+?)-(?P<ver>.+?)
    (-(?P<pyver>py\d\.\d+)
    )?.egg-info/""",
    re.VERBOSE,
)
wininst_re = re.compile(
    r"\.(?P<platform>win32|win-amd64)(?:-(?P<pyver>py\d\.\d))?\.exe$"
)
pyd_re = re.compile(r"\.(?P<abi>[a-z0-9]+)-(?P<platform>win32|win_amd64)\.pyd$")
serialization_policy = EmailPolicy(
    utf8=True,
    mangle_from_=False,
    max_line_length=0,
)
GENERATOR = f"wheel {__version__}"


def convert_requires(requires: str, metadata: Message) -> None:
    pass


def convert_pkg_info(pkginfo: str, metadata: Message) -> None:
    parsed_message = Parser().parsestr(pkginfo)
    for key, value in parsed_message.items():
        key_lower = key.lower()
        if value == "UNKNOWN":
            continue

        if key_lower == "description":
            description_lines = value.splitlines()
            if description_lines:
                value = "\n".join(
                    (
                        description_lines[0].lstrip(),
                        dedent("\n".join(description_lines[1:])),
                        "\n",
                    )
                )
            else:
                value = "\n"

            metadata.set_payload(value)
        elif key_lower == "home-page":
            metadata.add_header("Project-URL", f"Homepage, {value}")
        elif key_lower == "download-url":
            metadata.add_header("Project-URL", f"Download, {value}")
        else:
            metadata.add_header(key, value)

    metadata.replace_header("Metadata-Version", "2.4")


def normalize(name: str) -> str:
    pass


class ConvertSource(metaclass=ABCMeta):
    name: str
    version: str
    pyver: str = "py2.py3"
    abi: str = "none"
    platform: str = "any"
    metadata: Message

    @property
    def dist_info_dir(self) -> str:
        pass

    @abstractmethod
    def generate_contents(self) -> Iterator[tuple[str, bytes]]:
        pass


class EggFileSource(ConvertSource):
    def __init__(self, path: Path):
        if not (match := egg_filename_re.match(path.name)):
            raise ValueError(f"Invalid egg file name: {path.name}")

        # Binary wheels are assumed to be for CPython
        self.path = path
        self.name = normalize(match.group("name"))
        self.version = match.group("ver")
        if pyver := match.group("pyver"):
            self.pyver = pyver.replace(".", "")
            if arch := match.group("arch"):
                self.abi = self.pyver.replace("py", "cp")
                self.platform = normalize(arch)

        self.metadata = Message()

    def generate_contents(self) -> Iterator[tuple[str, bytes]]:
        pass


class EggDirectorySource(EggFileSource):
    def generate_contents(self) -> Iterator[tuple[str, bytes]]:
        pass


class WininstFileSource(ConvertSource):
    """
    Handles distributions created with ``bdist_wininst``.

    The egginfo filename has the format::

        name-ver(-pyver)(-arch).egg-info

    The installer filename has the format::

        name-ver.arch(-pyver).exe

    Some things to note:

    1. The installer filename is not definitive. An installer can be renamed
       and work perfectly well as an installer. So more reliable data should
       be used whenever possible.
    2. The egg-info data should be preferred for the name and version, because
       these come straight from the distutils metadata, and are mandatory.
    3. The pyver from the egg-info data should be ignored, as it is
       constructed from the version of Python used to build the installer,
       which is irrelevant - the installer filename is correct here (even to
       the point that when it's not there, any version is implied).
    4. The architecture must be taken from the installer filename, as it is
       not included in the egg-info data.
    5. Architecture-neutral installers still have an architecture because the
       installer format itself (being executable) is architecture-specific. We
       should therefore ignore the architecture if the content is pure-python.
    """

    def __init__(self, path: Path):
        self.path = path
        self.metadata = Message()

        # Determine the initial architecture and Python version from the file name
        # (if possible)
        if match := wininst_re.search(path.name):
            self.platform = normalize(match.group("platform"))
            if pyver := match.group("pyver"):
                self.pyver = pyver.replace(".", "")

        # Look for an .egg-info directory and any .pyd files for more precise info
        egg_info_found = pyd_found = False
        with ZipFile(self.path) as zip_file:
            for filename in zip_file.namelist():
                prefix, filename = filename.split("/", 1)
                if not egg_info_found and (match := egg_info_re.match(filename)):
                    egg_info_found = True
                    self.name = normalize(match.group("name"))
                    self.version = match.group("ver")
                    if pyver := match.group("pyver"):
                        self.pyver = pyver.replace(".", "")
                elif not pyd_found and (match := pyd_re.search(filename)):
                    pyd_found = True
                    self.abi = match.group("abi")
                    self.platform = match.group("platform")

                if egg_info_found and pyd_found:
                    break

    def generate_contents(self) -> Iterator[tuple[str, bytes]]:
        pass


def convert(files: list[str], dest_dir: str, verbose: bool) -> None:
    pass
