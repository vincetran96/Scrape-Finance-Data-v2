# -*- coding: utf-8 -*-
# This module contains helper functions to download PDFs

import json
import os

import requests


URL = ""


def save_binfile_url(url, filename=""):
    """Save binary file with url to the file and a defined path
    """
    local_filename = filename + url.split('/')[-1]
    with requests.get(url, stream=True) as r:
            r.raise_for_status()
            with open(local_filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192): 
                    if chunk: 
                        f.write(chunk)
                return local_filename

def save_jsonfile(obj, filename=""):
    """Save JSON file with a defined path
    """
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'w', encoding='utf-8') as writefile:
        json.dump(obj, writefile, ensure_ascii=False, indent=4)
