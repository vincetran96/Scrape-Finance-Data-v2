# This module contains helper functions to download files

import json
import csv
import os
import requests


def save_binfile_url(url, filename=""):
    '''
    Save binary file with url to the file and a defined path
    '''
    local_filename = filename + url.split('/')[-1]
    with requests.get(url, stream=True) as r:
            r.raise_for_status()
            with open(local_filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192): 
                    if chunk: 
                        f.write(chunk)
                return local_filename

def save_jsonfile(obj, filename=""):
    '''
    Save JSON file with a defined path using utf-8 encoding
    '''

    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'w', encoding='utf-8') as writefile:
        json.dump(obj, writefile, ensure_ascii=False, indent=4)

def save_textfile(obj, filename=""):
    '''
    Save text file with a defined path using utf-8 encoding
    '''

    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'w', encoding='utf-8') as writefile:
        writefile.write(obj)

def save_csvfile_row(row, filename=""):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'w', encoding='utf-8') as writefile:
        writer = csv.writer(writefile)
        writer.writerow(row)

def save_csvfile_rows_add(rows, filename=""):
    '''
    Adds rows to existing CSV file
    '''
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'a+', encoding='utf-8') as writefile:
        writer = csv.writer(writefile)
        writer.writerows(rows)
