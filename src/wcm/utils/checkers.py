import argparse
import errno
import os
import re
import sys

ERROR_INVALID_NAME = 123


def is_pathname_valid(pathname: str) -> bool:
    """
    `True` if the passed pathname is a valid pathname for the current OS;
    `False` otherwise.
    """
    # If this pathname is either not a string or is but is empty, this pathname
    # is invalid.
    try:
        if not isinstance(pathname, str) or not pathname:
            return False

        # Strip this pathnames Windows-specific drive specifier (e.g., `C:\`)
        # if any. Since Windows prohibits path components from containing `:`
        # characters, failing to strip this `:`-suffixed prefix would
        # erroneously invalidate all valid absolute Windows pathnames.
        _, pathname = os.path.splitdrive(pathname)

        # Directory guaranteed to exist. If the current OS is Windows, this is
        # the drive to which Windows was installed (e.g., the "%HOMEDRIVE%"
        # environment variable); else, the typical root directory.
        root_dirname = os.environ.get('HOMEDRIVE', 'C:') \
            if sys.platform == 'win32' else os.path.sep
        assert os.path.isdir(root_dirname)  # ...Murphy and her ironclad Law

        # Append a path separator to this directory if needed.
        root_dirname = root_dirname.rstrip(os.path.sep) + os.path.sep

        # Test whether each path component split from this pathname is valid or
        # not, ignoring non-existent and non-readable path components.
        for pathname_part in pathname.split(os.path.sep):
            try:
                os.lstat(root_dirname + pathname_part)
            # If an OS-specific exception is raised, its error code
            # indicates whether this pathname is valid or not. Unless this
            # is the case, this exception implies an ignorable kernel or
            # filesystem complaint (e.g., path not found or inaccessible).
            #
            # Only the following exceptions indicate invalid pathnames:
            #
            # * Instances of the Windows-specific "WindowsError" class
            #   defining the "winerror" attribute whose value is
            #   "ERROR_INVALID_NAME". Under Windows, "winerror" is more
            #   fine-grained and hence useful than the generic "errno"
            #   attribute. When a too-long pathname is passed, for example,
            #   "errno" is "ENOENT" (i.e., no such file or directory) rather
            #   than "ENAMETOOLONG" (i.e., file name too long).
            # * Instances of the cross-platform "OSError" class defining the
            #   generic "errno" attribute whose value is either:
            #   * Under most POSIX-compatible OSes, "ENAMETOOLONG".
            #   * Under some edge-case OSes (e.g., SunOS, *BSD), "ERANGE".
            except OSError as exc:
                if hasattr(exc, 'winerror'):
                    if exc.winerror == ERROR_INVALID_NAME:
                        return False
                elif exc.errno in {errno.ENAMETOOLONG, errno.ERANGE}:
                    return False
    # If a "TypeError" exception was raised, it almost certainly has the
    # error message "embedded NUL character" indicating an invalid pathname.
    except TypeError:
        return False
    # If no exception was raised, all path components and hence this
    # pathname itself are valid. (Praise be to the curmudgeonly python.)
    else:
        return True
    # If any other exception was raised, this is an unrelated fatal issue
    # (e.g., a bug). Permit this exception to unwind the call stack.
    #
    # Did we mention this should be shipped with Python already?


def argparse_is_path(string):
    if not is_pathname_valid(string):
        msg = '%r is not a valid path' % string
        raise argparse.ArgumentTypeError(msg)
    return string


def is_ip(string):
    if not re.match(r'^(?:(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(?:25[0-5]|2[0-4]\d|[01]?\d\d?)(?::\d+)?$', string):
        msg = '%r is not a ip address' % string
        raise argparse.ArgumentTypeError(msg)
    return string


def is_uri(string):
    return string


def is_tg_id(string):
    return string


def is_bool(string):
    if isinstance(string, bool):
        return string
    if string.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif string.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        msg = '%r is not a boolean' % string
        raise argparse.ArgumentTypeError(msg)


def clone(obj):
    if isinstance(obj, list):
        result = []
        for item in obj:
            result.append(clone(item))
        return result
    elif isinstance(obj, dict):
        result = {}
        for key, val in obj.items():
            result[key] = clone(val)
        return result
    else:
        return obj


def concat_list(first_list, second_list):
    result = []
    for item in first_list:
        result.append(clone(item))
    for item in second_list:
        if item not in result:
            result.append(clone(item))


def concat_dict(first_dict, second_dict):
    result = {}
    for key, val in first_dict.items():
        if isinstance(val, list):
            if key in second_dict and second_dict[key] is not None:
                result[key] = clone(second_dict[key])
            else:
                result[key] = clone(val)
        elif isinstance(val, dict):
            if key in second_dict and second_dict[key] is not None:
                if isinstance(second_dict[key], dict):
                    result[key] = concat_dict(first_dict[key], second_dict[key])
                else:
                    result[key] = clone(val)
            else:
                result[key] = concat_dict(first_dict[key], {})
        else:
            if key in second_dict and second_dict[key] is not None:
                result[key] = clone(second_dict[key])
            else:
                result[key] = clone(val)
    for key, val in second_dict.items():
        if key not in result:
            result[key] = clone(val)
    return result
