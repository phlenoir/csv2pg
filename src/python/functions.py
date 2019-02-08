#!/usr/bin/env python3
#
# Name: functions.py
# Description: Common functions for csv2pg
#

import datetime
import glob
import gzip
import os
import zipfile
from enum import Enum

import config as cfg


class DBType(Enum):
    ORACLE = "oracle"
    MYSQL = "mysql"
    POSTGRES = "postgres"
    DB2 = "db2"


def open_file(file):
    """Opens a CSV file.

    The file can either be in plain text (.csv), zipped (.csv.zip), or gzipped (.csv.gz)

    Parameters
    ----------
    file : str
        The file to open

    Returns
    -------
    file-object
        A file object
    """
    if file.endswith(".zip"):
        zip_file = zipfile.ZipFile(file, mode="r")
        return zip_file.open(zip_file.infolist()[0], mode="r")
    elif file.endswith(".gz"):
        return gzip.open(file, mode="r")
    else:
        return open(file, mode='r')


def read_header(file):
    """Reads header and returns the column list.

    This function reads the first row of the CSV file and parses it for the column names.

    Parameters
    ----------
    file : file_object
        The file to read the header from

    Returns
    -------
    set([])
        A set with all the column names.
    """
    return raw_input_to_set(file.readline(), True)


def find_all_files(pattern):
    """Find all files of a given pattern.

    Parameters
    ----------
    pattern : str
        The pattern to search for

    Returns
    -------
    []
        List of files.
    """
    if os.path.isdir(pattern):
        # If path is directory find all CSV files, compressed or uncompressed
        pattern += "/*.csv*"
    return sorted(glob.glob(pattern))


def verbose(output):
    """Print verbose output.

    Parameters
    ----------
    output : str
        The output to print
    """
    if cfg.verbose:
        print(output)


def debug(output):
    """Print debug output.

    Parameters
    ----------
    output : Any
        The output to print"""
    if cfg.debug:
        if isinstance(output, list):
            output = ", ".join(output)
        elif isinstance(output, dict):
            output = ", ".join(str(key) + ": " + str(value) for key, value in output.items())
        print(("DEBUG: {0}: " + output).format(datetime.datetime.now()))


def get_db_connection(db_type, user, password, host, port, db_name):
    """ Connects to the database.

    Parameters
    ----------
    db_type : str
        The database type
    user : str
        The database user
    password : str
        The database user password
    host : str
        The database host or ip address
    port : str
        The port to connect to
    db_name : str
        The database or service name

    Returns
    -------
    conn
        A database connection
    """

    try:
        if db_type == DBType.ORACLE.value:
            import cx_Oracle
            return cx_Oracle.connect(user,
                                     password,
                                     host + ":" + port + "/" + db_name)
        elif db_type == DBType.MYSQL.value:
            import mysql.connector
            return mysql.connector.connect(
                                       user=user,
                                       password=password,
                                       host=host,
                                       port=int(port),
                                       database=db_name)
        elif db_type == DBType.POSTGRES.value:
            import psycopg2
            return psycopg2.connect("""user='{0}' 
                                       password='{1}' 
                                       host='{2}' 
                                       port='{3}' 
                                       dbname='{4}'""".format(user, password, host, port, db_name)
                                    )
        elif db_type == DBType.DB2.value:
            import ibm_db
            import ibm_db_dbi
            conn = ibm_db.connect("UID={0};PWD={1};HOSTNAME={2};PORT={3};DATABASE={4};"
                                  .format(user, password, host, port, db_name), "", "")
            return ibm_db_dbi.Connection(conn)

        else:
            raise ValueError("Database type '{0}' is not supported.".format(db_type))
    except ModuleNotFoundError as err:
        raise ConnectionError("Database driver module is not installed: {0}. Please install it first.".format(str(err)))


def raw_input_to_list(raw_line, header=False):
    """Returns a list of values from a raw CSV input.

    Parameters
    ----------
    raw_line : bytes, bytearray, str
        The raw line to convert
    header : bool
        If true, values will be upper case and spaces replaced with '_'.
        This is only good for header rows in the CSV files.

    Returns
    -------
    [str,]
        A list of string values
    """
    ret = raw_line
    if isinstance(raw_line, (bytes, bytearray)):
        ret = raw_line.decode()
    ret = ret.splitlines()[0]
    # If empty string return None, i.e. skip empty lines
    if not ret:
        return None
    ret = ret.split(",")
    for n in range(len(ret)):
        val = ret[n].replace('"', '').strip()
        # If line is a header line, i.e. column number, replace spaces with '_' and make names UPPER
        if header:
            val = val.replace(' ', '_',).upper()
        ret[n] = val
    return ret


def raw_input_to_set(raw_line, header=False):
    """Returns a set of values from a raw CSV input.

    Parameters
    ----------
    raw_line : bytes, bytearray, str
        The raw line to convert
    header : bool
        If true, values will be upper case and spaces replaced with '_'.
        This is only good for header rows in the CSV files.

    Returns
    -------
    set([str,])
        A set of string values
    """
    return set(raw_input_to_list(raw_line, header))


def get_default_db_port(db_type):
    """Returns the default port for a database.

    Parameters
    ----------
    db_type : str
        The database type

    Returns
    -------
    str
        The default port
    """
    if db_type == DBType.ORACLE.value:
        return "1521"
    elif db_type == DBType.MYSQL.value:
        return "3306"
    elif db_type == DBType.POSTGRES.value:
        return "5432"
    elif db_type == DBType.DB2.value:
        return "50000"
