#!/usr/bin/env python
# python specifics
import sys
import logging
import os
import math
import numpy as np


def readlines_from_file(filename, contains=None):
    """
    Read a file and return the whole file or specific lines.

    Parameters
    ----------
    filename : str
        The location and filename to be read.
    contains : list of str
        A list of string of identifiers for the lines that is to be
        returned. If None, the whole file is returned.

    Returns
    -------
    lines : list of str
        The list of strings containing the whole or specific
        lines from a file.

    """

    inputfile = file_handler(filename, status='r')
    file_data = inputfile.readlines()
    file_handler(file_handler=inputfile)
    lines = []

    # first check if contains is a list
    is_list = is_sequence(contains)

    if contains is not None:
        # this can be a bit faster (comprehension), but do not care for this
        # now
        for line_index, line in enumerate(file_data):
            if is_list:
                for element in contains:
                    if element in line:
                        lines.append(line)
            else:
                if contains in line:
                    lines = line
    else:
        lines = file_data

    return lines


def file_handler(filename="", file_handler=None, status=None):
    """
    Open and close files.

    Parameters
    ----------
    filename : str, optional
        The name of the file to be handled (defaults to '').
    file_handler : object, optional
        An existing `file` object. If not supplied a file is
        created. Needed for file close, otherwise not.
    status : str, optional
        The string containing the status to write, read, append etc.
        If not supplied, assume file close and `file_handler` need
        to be supplied.

    Returns
    -------
    file_handler : object
        If `status` is supplied
        A `file` object

    """

    # set logger
    logger = logging.getLogger(sys._getframe().f_code.co_name)

    if status is None:
        if file_handler is None:
            logger.error("Could not close an empty file handler. Exiting.")
            sys.exit(1)
        file_handler.close()
    else:
        try:
            file_handler = open(filename, status)
            return file_handler
        except IOError:
            logger.error("Could not open " + filename + ". Exiting.")
            sys.exit(1)


def file_exists(file_path):
    """
    Check if the file exists.

    Parameters
    ----------
    file_path : string
        The file path to be checked.

    Returns
    -------
    status : bool
        If file does not exists or `file_path` empty, else False.
    """

    # set logger
    logger = logging.getLogger(sys._getframe().f_code.co_name)

    status = True
    try:
        os.stat(file_path)
    except OSError:
        if not file_path:
            logger.error("File path is empty.")
            sys.exit(1)
        else:
            logger.error("Could not locate "+file_path+".")
        status = False

    return status


def is_sequence(arg):
    """
    Checks to see if something is a sequence (list).

    Parameters
    ----------
    arg : str
        The string to be examined.

    Returns
    -------
    sequence : bool
        Is True if `arg` is a list.

    """

    sequence = (not hasattr(arg, "strip") and
                hasattr(arg, "__getitem__") or
                hasattr(arg, "__iter__"))

    return sequence


def test_string_content(string):
    """
    Detects if string is integer, float or string.

    Parameters
    ----------
    string : string
        An input string to be tested.

    Returns
    -------
    string
        A string with value 'int' if input is an integer,
        'float' if the input is a float and 'string' if it
        is just a regular string.

    """
    try:
        float(string)
        return 'int' if ((string.count('.') == 0) and \
                         ('e' not in string) and \
                         ('E' not in string)) else 'float'
    except ValueError:
        return 'string'


def is_numbers(s, splitter=" "):
    """
    Check if a string only contains numbers.

    Parameters
    ----------
    s: str
        The input string
    splitter : string, optional
        The splitting character to be used, defaults to blank spaces.

    Returns
    -------
    is_nums: bool
        Is True if all entries in the input string is a numbers,
        otherwise False.

    """

    entries = s.split(splitter)
    is_nums = True
    for entry in entries:
        if not is_number(entry):
            is_nums = False
            return is_nums

    return is_nums


def is_number(s):
    """
    Check if a string is a number.

    Parameters
    ----------
    s: str
        The input string

    Returns
    -------
    is_num: bool
        Is True if the input string is a number, otherwise False

    """

    try:
        float(s)
        is_num = True
    except ValueError:
        is_num = False

    return is_num


def remove_newline(fobj, num_newlines=1):
    """
    Removes the newline at the end of a file.

    Usefull to run after a for loop that writes a newline character
    at each step. Other solutions cannot handle very large files.

    Parameters
    ----------
    fobj : object
        A file object.
    num_newlines : int, optional
        The number of newlines to remove. Defaults to 1.

    """

    # remove last newline, check number of chars, different
    # for each OS
    remove_chars = len(os.linesep) + num_newlines - 1
    fobj.truncate(fobj.tell() - remove_chars)

    return


def dir_to_cart(v, lattice):
    """
    Convert direct coordinates to cartesian.

    Parameters
    ----------
    v : ndarray
        | Dimension: (3)

        The direct vector to be converted.
    lattice : ndarray
        | Dimension: (3,3)

        The crystal lattice, where the first lattice vector is
        [0,:], the second, [1,:] etc.

    Returns
    -------
    cart : ndarray
        | Dimension: (3)

        The cartesian vector.

    """

    cart = np.dot(v, lattice)

    return cart


def cart_to_dir(v, lattice):
    """
    Convert cartesian coordinates to direct.

    Parameters
    ----------
    v : ndarray
        | Dimension: (3)

        The cartersian vector.
    lattice : ndarray
        | Dimension: (3,3)
        The crystal lattice, where the first lattice vector is
        (0,:), the second, (1,:) etc.

    Returns
    -------
    direct : ndarray
        | Dimension: (3)
        The direct vector.

    """

    direct = np.dot(v, np.linalg.inv(lattice))

    return direct


def lat_to_reclat(lattice):
    """
    Convert the lattice to the reciprocal lattice.

    Parameters
    ----------
    lattice : ndarray
        | Dimension: (3,3)
        The crystal lattice, where the first lattice vector is
        (0,:), the second, (1,:) etc.

    Returns
    -------
    lattice_rec : ndarray
        | Dimension: (3,3)
        Reciprocal lattice including the 2:math:`\pi` factor,
        see `lattice` for layout.

    Notes
    -----
    In general, `lattice_rec`=2pi*(lattice.T)^-1

    """

    lattice_trans = np.transpose(lattice)
    lattice_rec = 2 * math.pi * np.linalg.inv(lattice_trans)

    return lattice_rec
