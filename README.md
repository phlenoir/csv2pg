# csv2pg

A DB loader for CSV files.

`csv2pg` takes CSV files and loads them into a database.
Rather than having to go through the CSV data first and find out what columns and data types are present in the CSV files,
`csv2pg` will read the header in each CSV file and automatically load data into the columns of the same name into the target table.
Spaces in the header column names are automatically replaced with `_` characters,
for example the column `station id` in the CSV file will be interpreted as `station_id` column in the table.

This approach allows you to get data into the database first and worry about the data cleansing part later,
which is usually much easier once the data is in the database rather than in the CSV files.

`csv2pg` is capable of scanning all CSV file headers at once and generate a `CREATE TABLE` statement with all the column names present.
This is particularly useful if the format of the CSV files has changed over time or because you want to load different CSV file types into the same database table.

## Setup

Need python 3.

### Installing python 3

On centos7 or equivalent do :

```console
sudo yum install python36
python36 --version
type -a python36
sudo ln -s /usr/bin/python36 /usr/bin/python3
python3 --version
```

### Creating virtualenv with python3

From csvdb/ directory type python3 -m venv path/to/my/virtualenv/. Note that if you are using (virtualbox to instanciate) a hosted linux box, the virtualenv cannot live in a shared directory between the host and the guest.

cd csv2pg/
python3 -m venv ../../csv2pg/env
