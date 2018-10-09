# Copyright 2008-2016 by Carnegie Mellon University
# See license information in LICENSE-OPENSOURCE.txt

import logging
from logging import root, Formatter, StreamHandler
from logging import *
import logging.config as config
import logging.handlers as handlers
import os

_programName = "python"
_logFilename = None

def setProgramName(name):
    global _programName
    _programName = name

def setLogFilename(filename):
    global _logFilename
    _logFilename = filename

import datetime

class SilkscreenFormatter(Formatter):
    def format(self, record):
        return ("%s %s[%d] " % (str(datetime.datetime.utcnow()),
                                _programName, os.getpid())) \
            + Formatter.format(self, record)

BASIC_FORMAT = "(%(name)s): %(levelname)s %(message)s"

def basicConfig(**kwargs):
    if len(root.handlers) == 0:
        if 'program_name' in kwargs:
            setProgramName(kwargs['program_name'])
        if 'filename' in kwargs:
            setLogFilename(kwargs['filename'])
        filename = _logFilename
        if filename:
            mode = kwargs.get("filemode", "a")
            hdlr = FileHandler(filename, mode)
        else:
            stream = kwargs.get("stream")
            hdlr = StreamHandler(stream)
        fs = kwargs.get("format", BASIC_FORMAT)
        dfs = kwargs.get("datefmt", None)
        fmt = SilkscreenFormatter(fs, dfs)
        hdlr.setFormatter(fmt)
        root.addHandler(hdlr)
        level = kwargs.get("level")
        if level:
            root.setLevel(level)

logging.basicConfig = basicConfig
