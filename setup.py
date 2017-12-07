# -*- coding: utf-8 -*-
from distutils.core import setup
import py2exe
setup(
    options = {"py2exe": {"packages": ["encodings"],
                          "bundle_files": 1}},
    zipfile = None,
    windows = ["InitializeWindow.py"],
)
