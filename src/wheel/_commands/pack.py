from __future__ import annotations

import email.policy
import os.path
import re
from email.generator import BytesGenerator
from email.parser import BytesParser

from ..wheelfile import WheelError, WheelFile

DIST_INFO_RE = re.compile(r"^(?P<namever>(?P<name>.+?)-(?P<ver>\d.*?))\.dist-info$")


def pack(directory: str, dest_dir: str, build_number: str | None) -> None:
    """Repack a previously unpacked wheel directory into a new wheel file.

    The .dist-info/WHEEL file must contain one or more tags so that the target
    wheel file name can be determined.

    :param directory: The unpacked wheel directory
    :param dest_dir: Destination directory (defaults to the current directory)
    """
    pass


def compute_tagline(tags: list[str]) -> str:
    """Compute a tagline from a list of tags.

    :param tags: A list of tags
    :return: A tagline
    """
    pass
