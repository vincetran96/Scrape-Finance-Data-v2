# -*- coding: utf-8 -*-
# This module contains helper functions to download PDFs

import requests


URL = ""


def save_file_url(url, filepath=""):
    """Save file with url to the file
    """
    local_filename = filepath + url.split('/')[-1]
    with requests.get(url, stream=True) as r:
            r.raise_for_status()
            with open(local_filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192): 
                    # If you have chunk encoded response uncomment if
                    # and set chunk_size parameter to None.
                    if chunk: 
                        f.write(chunk)
                return local_filename
