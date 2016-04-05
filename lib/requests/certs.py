#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
certs.py
~~~~~~~~

This module returns the preferred default CA certificate bundle.

If you are packaging Requests, e.g., for a Linux distribution or a managed
environment, you can change the definition of where() to return a separately
packaged CA bundle.
"""

import os.path


def where():
    """Return the preferred certificate bundle."""
    # vendored bundle inside Requests

    ## on Unix systems, the below is where Requests looks for it by default
    #return '/etc/ssl/certs/ca-certificates.crt'

    ## in this packaged version, the file has instead been included directly
    return os.path.join(os.path.dirname(__file__), 'ca-certificates.crt')

if __name__ == '__main__':
    print(where())
