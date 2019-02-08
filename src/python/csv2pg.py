#!/usr/bin/env python3

"""csv2pg -  Utility for loading a CSV file into PostgreSQL."""

import argparse
import csv
import sys

import config as cfg
import functions as f

def run(cmd):
    """Runs csv2db.

    This function is the main entry point for csv2pg.

    Parameters
    ----------
    cmd : str array
        The arguments passed

    Returns
    -------
    int
        The exit code.
    """
    args = parse_arguments(cmd)

    # Set verbose and debug output flags
    cfg.verbose = args.verbose
    if args.debug:
        cfg.verbose = True
        cfg.debug = True

    # Set table name
    cfg.table_name = args.table

    # Find all files
    f.verbose("Finding file.")
    file_name = f.find_all_files(args.file)
    f.debug("Found {0} files.".format(len(file_name)))
    f.debug(file_name)

    # Set DB type
    f.debug("DB type: {0}".format(args.dbtype))
    cfg.db_type = args.dbtype

    # Set DB default port, if needed
    if args.port is None:
        args.port = f.get_default_db_port(args.dbtype)
        f.debug("Using default port {0}".format(args.port))

    f.debug("Database details:")
    f.debug({"dbtype": args.dbtype, "user": args.user, "host": args.host, "port": args.port, "dbname": args.dbname})

    f.debug("Determine the file type for '{0}'".format(file_name))
    fic = magic.Magic(mime_encoding="True")
    try:
        file_format = fic.from_file(file_name)
    except FileNotFoundError:
        print("File {} not found".format(file_name))
        raise SystemExit

    csvfilename = convert_utf8(file_name, file_format)
    csvfile = open(csvfilename, newline='')
    csvreader = csv.reader(csvfile)
    csvheader = csvreader.__next__()                    # read the header
    f.verbose("Generating CREATE TABLE statement.")
    create_table = gen_table_ddl(file_name, args.column_type)
    create_table = gen_table_ddl(table_name, args.column_type, csvheader)

    copy_opts = args.optcp or "DELIMITER ',' CSV HEADER"
    copy_cmd = gen_copy_cmd(table_name, csvheader, csvfilename, copy_opts)

    # write the DDL to a file
    ddl_file_name = "{}.sql".format(args.ddl or table_name)
    ddl_file = open(ddl_file_name, "w+")
    ddl_file.write(create_table)
    ddl_file.write(copy_cmd)
    ddl_file.close()
    print("Generated SQL file: {}".format(ddl_file_name))


def convert_utf8(filename, filetype):
    """Convert filename to UTF-8 without BOM."""
    print("File {} appears to be in {} format.".format(filename, filetype))
    print("Converting to utf-8 without bom.")
    if filetype == 'utf-8':             # to handle BOM
        filetype = 'utf-8-sig'
    with open(filename, "rb") as fin:
        text = fin.read()
    text = text.decode(filetype).encode('utf-8')
    utf8_out = 'csv2pg-' + filename
    with open(utf8_out, "wb") as fou:
        fou.write(text)
    print("Converted file: {}".format(utf8_out))
    return utf8_out


def get_table_name(filename):
    """Extract the name component from the filename."""
    try:
        loc = filename.index('.')
        return filename[:loc]
    except ValueError:
        return filename


def gen_table_ddl(table_name, column_data_type, csvheader):
    """Creates the SQL CREATE TABLE statement."""
    col_set = f.raw_input_to_set(csvheader, True)
    if table_name is not None:
        ddl = "CREATE TABLE {0}".format(table_name)
    else:
        ddl = "CREATE TABLE <TABLE NAME>"
    ddl = ddl + "("
    cols = ""
    for col in col_set:
        cols += "  " + col + " " + column_data_type + ",\n"
    cols = cols[:-2]
    ddl = ddl + cols
    ddl = ddl + ");"
    return ddl


def gen_copy_cmd(tabname, colnames, filename, optcp):
    """Generate the copy command for the CSV file."""
    ddl = "\copy {}(".format(tabname)
    for c in colnames:
        ddl = ddl + "{}, ".format(c)
    ddl = ddl[:-2] + ") from '{}' {};\n".format(filename, optcp)
    return ddl


def parse_arguments(cmd):
    """Parses the arguments.

    Parameters
    ----------
    cmd : str array
        The arguments passed

    Returns
    -------
    arg
        Argparse object
    """

    # process command line arguments
    parser = argparse.ArgumentParser(prog="csv2pg",
                                     formatter_class=argparse.RawDescriptionHelpFormatter,
                                     description="A PostgresSQL loader for CSV files.\nVersion: {0}\n"
                                     .format(cfg.version))                                
    parser.add_argument('filename',
                        help='CSV file to be loaded into PostgreSQL table')
    parser.add_argument('-t', '--table',
                        help='table where the CSV file is copied')
    parser.add_argument('-d', '--ddl',
                        help='filename of create table statement')
    parser.add_argument('--optcp',
                        help='copy command options')

    parser.add_argument("-v", "--verbose", action="store_true", default=False,
                        help="Verbose output.")
    parser.add_argument("--debug", action="store_true", default=False,
                        help="Debug output.")

    parser.add_argument("-c", "--column-type", default="VARCHAR2(4000)",
                        help="The column type to use for the table generation.")


    parser.add_argument("--dbtype", default="postgres",
                             help="The database type. Choose one of {0}.".format([e.value for e in f.DBType]))
    parser.add_argument("-u", "--user",
                             help="The database user to load data into.")
    parser.add_argument("-p", "--password",
                             help="The database schema password.")
    parser.add_argument("-m", "--host", default="localhost",
                             help="The host name on which the database is running on.")
    parser.add_argument("-n", "--port",
                             help="The port on which the database is listening. " +
                                  "If not passed on the default port will be used " +
                                  "(Oracle: 1521, MySQL: 3306, PostgreSQL: 5432, DB2: 50000).")
    parser.add_argument("--dbname", default="postgre",
                             help="The name of the database.")

    return parser.parse_args(cmd)


if __name__ == "__main__":
    raise SystemExit(run(sys.argv[1:]))