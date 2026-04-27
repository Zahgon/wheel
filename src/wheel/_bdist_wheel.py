"""
Create a wheel (.whl) distribution.

A wheel is a built archive format.
"""

from __future__ import annotations

import logging
import os
import re
import shutil
import stat
import struct
import sys
import sysconfig
import warnings
from collections.abc import Iterable, Sequence
from email.generator import BytesGenerator, Generator
from email.policy import EmailPolicy
from glob import iglob
from shutil import rmtree
from typing import TYPE_CHECKING, Callable, Literal, cast
from zipfile import ZIP_DEFLATED, ZIP_STORED

import setuptools
from packaging import tags
from packaging import version as _packaging_version
from setuptools import Command

from . import __version__ as wheel_version
from ._metadata import pkginfo_to_metadata
from .wheelfile import WheelFile

if TYPE_CHECKING:
    import types

# ensure Python logging is configured
try:
    __import__("setuptools.logging")
except ImportError:
    # setuptools < ??
    from . import _setuptools_logging

    _setuptools_logging.configure()

log = logging.getLogger("wheel")


def safe_name(name: str) -> str:
    """Convert an arbitrary string to a standard distribution name
    Any runs of non-alphanumeric/. characters are replaced with a single '-'.
    """
    return re.sub("[^A-Za-z0-9.]+", "-", name)


def safe_version(version: str) -> str:
    """
    Convert an arbitrary string to a standard version string
    """
    pass


setuptools_major_version = int(setuptools.__version__.split(".")[0])

PY_LIMITED_API_PATTERN = r"cp3\d"


def _is_32bit_interpreter() -> bool:
    return struct.calcsize("P") == 4


def python_tag() -> str:
    return f"py{sys.version_info[0]}"


def get_platform(archive_root: str | None) -> str:
    """Return our platform name 'win32', 'linux_x86_64'"""
    result = sysconfig.get_platform()
    if result.startswith("macosx") and archive_root is not None:
        from .macosx_libfile import calculate_macosx_platform_tag

        result = calculate_macosx_platform_tag(archive_root, result)
    elif _is_32bit_interpreter():
        if result == "linux-x86_64":
            # pip pull request #3497
            result = "linux-i686"
        elif result == "linux-aarch64":
            # packaging pull request #234
            # TODO armv8l, packaging pull request #690 => this did not land
            # in pip/packaging yet
            result = "linux-armv7l"

    return result.replace("-", "_")


def get_flag(
    var: str, fallback: bool, expected: bool = True, warn: bool = True
) -> bool:
    """Use a fallback value for determining SOABI flags if the needed config
    var is unset or unavailable."""
    pass


def get_abi_tag() -> str | None:
    """Return the ABI tag based on SOABI (if available) or emulate SOABI (PyPy2)."""
    pass


def safer_name(name: str) -> str:
    pass


def safer_version(version: str) -> str:
    pass


def remove_readonly(
    func: Callable[..., object],
    path: str,
    excinfo: tuple[type[Exception], Exception, types.TracebackType],
) -> None:
    pass


def remove_readonly_exc(func: Callable[..., object], path: str, exc: Exception) -> None:
    pass


class bdist_wheel(Command):
    description = "create a wheel distribution"

    supported_compressions = {
        "stored": ZIP_STORED,
        "deflated": ZIP_DEFLATED,
    }

    user_options = [
        ("bdist-dir=", "b", "temporary directory for creating the distribution"),
        (
            "plat-name=",
            "p",
            "platform name to embed in generated filenames "
            f"(default: {get_platform(None)})",
        ),
        (
            "keep-temp",
            "k",
            "keep the pseudo-installation tree around after "
            "creating the distribution archive",
        ),
        ("dist-dir=", "d", "directory to put final built distributions in"),
        ("skip-build", None, "skip rebuilding everything (for testing/debugging)"),
        (
            "relative",
            None,
            "build the archive using relative paths (default: false)",
        ),
        (
            "owner=",
            "u",
            "Owner name used when creating a tar file [default: current user]",
        ),
        (
            "group=",
            "g",
            "Group name used when creating a tar file [default: current group]",
        ),
        ("universal", None, "make a universal wheel (default: false)"),
        (
            "compression=",
            None,
            "zipfile compression (one of: {}) (default: 'deflated')".format(
                ", ".join(supported_compressions)
            ),
        ),
        (
            "python-tag=",
            None,
            f"Python implementation compatibility tag (default: '{python_tag()}')",
        ),
        (
            "build-number=",
            None,
            "Build number for this particular version. "
            "As specified in PEP-0427, this must start with a digit. "
            "[default: None]",
        ),
        (
            "py-limited-api=",
            None,
            "Python tag (cp32|cp33|cpNN) for abi3 wheel tag (default: false)",
        ),
    ]

    boolean_options = ["keep-temp", "skip-build", "relative", "universal"]

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    @property
    def wheel_dist_name(self):
        """Return distribution full name with - replaced with _"""
        pass

    def get_tag(self) -> tuple[str, str, str]:
        # bdist sets self.plat_name if unset, we should only use it for purepy
        # wheels if the user supplied it.
        pass

    def run(self):
        pass

    def write_wheelfile(
        self, wheelfile_base: str, generator: str = f"bdist_wheel ({wheel_version})"
    ):
        pass

    def _ensure_relative(self, path: str) -> str:
        # copied from dir_util, deleted
        pass

    @property
    def license_paths(self) -> Iterable[str]:
        pass

    def egg2dist(self, egginfo_path: str, distinfo_path: str):
        """Convert an .egg-info directory into a .dist-info directory"""
        pass
