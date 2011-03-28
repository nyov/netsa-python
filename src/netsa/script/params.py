# Copyright 2008-2010 by Carnegie Mellon University

# @OPENSOURCE_HEADER_START@
# Use of the Network Situational Awareness Python support library and
# related source code is subject to the terms of the following licenses:
# 
# GNU Public License (GPL) Rights pursuant to Version 2, June 1991
# Government Purpose License Rights (GPLR) pursuant to DFARS 252.225-7013
# 
# NO WARRANTY
# 
# ANY INFORMATION, MATERIALS, SERVICES, INTELLECTUAL PROPERTY OR OTHER 
# PROPERTY OR RIGHTS GRANTED OR PROVIDED BY CARNEGIE MELLON UNIVERSITY 
# PURSUANT TO THIS LICENSE (HEREINAFTER THE "DELIVERABLES") ARE ON AN 
# "AS-IS" BASIS. CARNEGIE MELLON UNIVERSITY MAKES NO WARRANTIES OF ANY 
# KIND, EITHER EXPRESS OR IMPLIED AS TO ANY MATTER INCLUDING, BUT NOT 
# LIMITED TO, WARRANTY OF FITNESS FOR A PARTICULAR PURPOSE, 
# MERCHANTABILITY, INFORMATIONAL CONTENT, NONINFRINGEMENT, OR ERROR-FREE 
# OPERATION. CARNEGIE MELLON UNIVERSITY SHALL NOT BE LIABLE FOR INDIRECT, 
# SPECIAL OR CONSEQUENTIAL DAMAGES, SUCH AS LOSS OF PROFITS OR INABILITY 
# TO USE SAID INTELLECTUAL PROPERTY, UNDER THIS LICENSE, REGARDLESS OF 
# WHETHER SUCH PARTY WAS AWARE OF THE POSSIBILITY OF SUCH DAMAGES. 
# LICENSEE AGREES THAT IT WILL NOT MAKE ANY WARRANTY ON BEHALF OF 
# CARNEGIE MELLON UNIVERSITY, EXPRESS OR IMPLIED, TO ANY PERSON 
# CONCERNING THE APPLICATION OF OR THE RESULTS TO BE OBTAINED WITH THE 
# DELIVERABLES UNDER THIS LICENSE.
# 
# Licensee hereby agrees to defend, indemnify, and hold harmless Carnegie 
# Mellon University, its trustees, officers, employees, and agents from 
# all claims or demands made against them (and any related losses, 
# expenses, or attorney's fees) arising out of, or relating to Licensee's 
# and/or its sub licensees' negligent use or willful misuse of or 
# negligent conduct or willful misconduct regarding the Software, 
# facilities, or other rights or assistance granted by Carnegie Mellon 
# University under this License, including, but not limited to, any 
# claims of product liability, personal injury, death, damage to 
# property, or violation of any laws or regulations.
# 
# Carnegie Mellon University Software Engineering Institute authored 
# documents are sponsored by the U.S. Department of Defense under 
# Contract FA8721-05-C-0003. Carnegie Mellon University retains 
# copyrights in all material produced under this contract. The U.S. 
# Government retains a non-exclusive, royalty-free license to publish or 
# reproduce these documents, or allow others to do so, for U.S. 
# Government purposes only pursuant to the copyright license under the 
# contract clause at 252.227.7013.
# @OPENSOURCE_HEADER_END@

# Note that params are *not* represented by objects, but by
# dictionaries.  This is a conscious choice since the information in
# param specs is shared between processes.  Using a purely data-based
# representation means no need to worry about version mismatches if we
# want to tweak the internals.

import calendar
import os
import re

from netsa.data.times import make_datetime

from netsa.script import ParamError

RegexType = type(re.compile(""))

########################################################################

def check_param_text_args(kind_args):
    kind_arg_names = set(kind_args.iterkeys())
    allowed_arg_names = set(["regex"])
    if not kind_arg_names <= allowed_arg_names:
        kind_arg_names -= allowed_arg_names
        error = TypeError("text param got unexpected keyword arguments: "
                          "%s" % (", ".join(repr(x)
                                            for x in kind_arg_names)))
        raise error
    if "regex" in kind_args:
        if not isinstance(kind_args["regex"], basestring):
            error = TypeError("text param expected str value for 'regex'")
            raise error
        try:
            re.compile(kind_args["regex"])
        except:
            error = ValueError("invalid regex for text param %s" %
                               kind_args['name'])

def check_param_int_args(kind_args):
    kind_arg_names = set(kind_args.iterkeys())
    allowed_arg_names = set(["minimum", "maximum"])
    if not kind_arg_names <= allowed_arg_names:
        kind_arg_names -= allowed_arg_names
        error = TypeError("int param got unexpected keyword arguments: "
                          "%s" % (", ".join(repr(x)
                                            for x in kind_arg_names)))
        raise error            
    if "minimum" in kind_args:
        if not isinstance(kind_args["minimum"], (int, long)):
            error = TypeError("int param expected int value for 'minimum'")
            raise error
    if "maximum" in kind_args:
        if not isinstance(kind_args["maximum"], (int, long)):
            error = TypeError("int param expected int value for 'maximum'")
            raise error

def check_param_float_args(kind_args):
    kind_arg_names = set(kind_args.iterkeys())
    allowed_arg_names = set(["minimum", "maximum"])
    if not kind_arg_names <= allowed_arg_names:
        kind_arg_names -= allowed_arg_names
        error = TypeError("float param got unexpected keyword arguments: "
                          "%s" % (", ".join(repr(x)
                                            for x in kind_arg_names)))
        raise error            
    if "minimum" in kind_args:
        if not isinstance(kind_args["minimum"], float):
            error = TypeError("float param expected float value for 'minimum'")
            raise error
    if "maximum" in kind_args:
        if not isinstance(kind_args["maximum"], float):
            error = TypeError("float param expected float value for 'maximum'")
            raise error

def check_param_date_args(kind_args):
    if kind_args:
        error = TypeError("date param got unexpected keyword arguments: "
                          "%s" % (", ".join(repr(x)
                                            for x in kind_arg_names)))
        raise error

def check_param_label_args(kind_args):
    kind_arg_names = set(kind_args.iterkeys())
    allowed_arg_names = set(["regex"])
    if not kind_arg_names <= allowed_arg_names:
        kind_arg_names -= allowed_arg_names
        error = TypeError("label param got unexpected keyword arguments: "
                          "%s" % (", ".join(repr(x)
                                            for x in kind_arg_names)))
        raise error
    if "regex" in kind_args:
        if not isinstance(kind_args["regex"], (basestring, RegexType)):
            error = TypeError("label param expected str or regex value "
                              "for 'regex'")
            raise error    

def check_param_file_args(kind_args):
    kind_arg_names = set(kind_args.iterkeys())
    allowed_arg_names = set(["mime_type"])
    if not kind_arg_names <= allowed_arg_names:
        kind_arg_names -= allowed_arg_names
        error = TypeError("file param got unexpected keyword arguments: "
                          "%s" % (", ".join(repr(x)
                                            for x in kind_arg_names)))
        raise error

def check_param_dir_args(kind_args):
    if kind_args:
        error = TypeError("dir param got unexpected keyword arguments: "
                          "%s" % (", ".join(repr(x)
                                            for x in kind_arg_names)))
        raise error

def check_param_path_args(kind_args):
    if kind_args:
        error = TypeError("path param got unexpected keyword arguments: "
                          "%s" % (", ".join(repr(x)
                                            for x in kind_arg_names)))
        raise error

def check_param_output_file_args(kind_args):
    if kind_args:
        error = TypeError("output file param got unexpected keyword arguments: "
                          "%s" % (", ".join(repr(x)
                                            for x in kind_arg_names)))
        raise error

def check_param_output_dir_args(kind_args):
    if kind_args:
        error = TypeError("output dir param got unexpected keyword arguments: "
                          "%s" % (", ".join(repr(x)
                                            for x in kind_arg_names)))
        raise error

def check_param_flag_args(kind_args):
    if kind_args:
        error = TypeError("flag param got unexpected keyword arguments: "
                          "%s" % (", ".join(repr(x)
                                            for x in kind_arg_names)))
        raise error

def check_param_flow_class_args(kind_args):
    if kind_args:
        error = TypeError("flow class param got unexpected keyword arguments: "
                          "%s" % (", ".join(repr(x)
                                            for x in kind_arg_names)))
        raise error

def check_param_flow_type_args(kind_args):
    if kind_args:
        error = TypeError("flow type param got unexpected keyword arguments: "
                          "%s" % (", ".join(repr(x)
                                            for x in kind_arg_names)))
        raise error

def check_param_flow_flowtypes_args(kind_args):
    if kind_args:
        error = TypeError("flow flowtypes param got unexpected keyword "
                          "arguments: %s" %
                          (", ".join(repr(x) for x in kind_arg_names)))
        raise error

def check_param_flow_sensors_args(kind_args):
    if kind_args:
        error = TypeError("flow sensors param got unexpected keyword "
                          "arguments: %s" %
                          (", ".join(repr(x) for x in kind_arg_names)))
        raise error

def check_param_flow_date_args(kind_args):
    if kind_args:
        error = TypeError("flow date param got unexpected keyword "
                          "arguments: %s" %
                          (", ".join(repr(x) for x in kind_arg_names)))
        raise error

########################################################################

# Parameter definitions, and encoding and decoding of the same.
KIND_TEXT = "KIND_TEXT"
KIND_INT = "KIND_INT"
KIND_FLOAT = "KIND_FLOAT"
KIND_DATE = "KIND_DATE"
KIND_LABEL = "KIND_LABEL"
KIND_FILE = "KIND_FILE"
KIND_DIR = "KIND_DIR"
KIND_PATH = "KIND_PATH"
KIND_FLAG = "KIND_FLAG"
KIND_FLOW_CLASS = "KIND_FLOW_CLASS"
KIND_FLOW_TYPE = "KIND_FLOW_TYPE"
KIND_FLOW_FLOWTYPES = "KIND_FLOW_FLOWTYPES"
KIND_FLOW_SENSORS = "KIND_FLOW_SENSORS"
KIND_FLOW_DATE = "KIND_FLOW_DATE"
KIND_OUTPUT_FILE = "KIND_OUTPUT_FILE"
KIND_OUTPUT_DIR = "KIND_OUTPUT_DIR"

param_kinds = {
    KIND_TEXT:           dict(check_args=check_param_text_args),
    KIND_INT:            dict(check_args=check_param_int_args),
    KIND_FLOAT:          dict(check_args=check_param_float_args),
    KIND_DATE:           dict(check_args=check_param_date_args),
    KIND_LABEL:          dict(check_args=check_param_label_args),
    KIND_FILE:           dict(check_args=check_param_file_args),
    KIND_DIR:            dict(check_args=check_param_dir_args),
    KIND_PATH:           dict(check_args=check_param_path_args),
    KIND_FLAG:           dict(check_args=check_param_flag_args),
    KIND_FLOW_CLASS:     dict(check_args=check_param_flow_class_args),
    KIND_FLOW_TYPE:      dict(check_args=check_param_flow_type_args),
    KIND_FLOW_FLOWTYPES: dict(check_args=check_param_flow_flowtypes_args),
    KIND_FLOW_SENSORS:   dict(check_args=check_param_flow_sensors_args),
    KIND_FLOW_DATE:      dict(check_args=check_param_flow_date_args),
    KIND_OUTPUT_FILE:    dict(check_args=check_param_output_file_args),
    KIND_OUTPUT_DIR:     dict(check_args=check_param_output_dir_args),
}

def check_param_kind(kind, kind_args):
    if kind not in param_kinds:
        error = TypeError("Unknown param kind %s" % str(kind))
        raise error
    param_kinds[kind]["check_args"](kind_args)

########################################################################

def parse_value(param, value):
    if param['kind'] == KIND_TEXT:
        return parse_param_text_value(param, value)
    elif param['kind'] == KIND_INT:
        return parse_param_int_value(param, value)
    elif param['kind'] == KIND_FLOAT:
        return parse_param_float_value(param, value)
    elif param['kind'] == KIND_DATE:
        return parse_param_date_value(param, value)
    elif param['kind'] == KIND_LABEL:
        return parse_param_label_value(param, value)
    elif param['kind'] == KIND_FILE:
        return parse_param_file_value(param, value)
    elif param['kind'] == KIND_DIR:
        return parse_param_dir_value(param, value)
    elif param['kind'] == KIND_PATH:
        return parse_param_path_value(param, value)
    elif param['kind'] == KIND_FLAG:
        return parse_param_flag_value(param, value)
    elif param['kind'] == KIND_FLOW_CLASS:
        return parse_param_text_value(param, value)
    elif param['kind'] == KIND_FLOW_TYPE:
        return parse_param_text_value(param, value)
    elif param['kind'] == KIND_FLOW_FLOWTYPES:
        return parse_param_text_value(param, value)
    elif param['kind'] == KIND_FLOW_SENSORS:
        return parse_param_text_value(param, value)
    elif param['kind'] == KIND_FLOW_DATE:
        # Sanity check it as a date, but return it as text
        return parse_param_flow_date_value(param, value)
    elif param['kind'] == KIND_OUTPUT_FILE:
        return parse_param_output_file_value(param, value)
    elif param['kind'] == KIND_OUTPUT_DIR:
        return parse_param_output_dir_value(param, value)
    else:
        error = Error("Unknown param kind: %s" % repr(param['kind']))
        raise error

def parse_param_text_value(param, value):
    kind_args = param['kind_args']
    if 'regex' in kind_args:
        regex = kind_args['regex']
        try:
            regex = re.compile(regex)
            if not regex.match(value):
                error = ParamError(param, value,
                                   "did not match required pattern")
                raise error
        except:
            error = ValueError("Invalid regex for %s: %s" %
                               (param['name'], repr(regex)))
            raise error
    return value

def parse_param_int_value(param, value):
    try:
        value = int(value)
    except ValueError:
        error = ParamError(param, value, "not a valid integer")
        raise error
    kind_args = param['kind_args']
    minimum = kind_args.get("minimum", None)
    maximum = kind_args.get("maximum", None)
    if (minimum != None and value < minimum or
        maximum != None and value > maximum):
        if maximum == None:
            error = ParamError(param, value, "%s must be >= %d" % minimum)
        elif minimum == None:
            error = ParamError(param, value, "must be <= %d" % maximum)
        else:
            error = ParamError(param, value,
                               "must be %d <= x <= %d" % (minimum, maximum))
        raise error
    return value

def parse_param_float_value(param, value):
    try:
        value = float(value)
    except ValueError:
        error = ParamError(param, value, "not a valid floating point number")
        raise error
    kind_args = param['kind_args']
    minimum = kind_args.get("minimum", None)
    maximum = kind_args.get("maximum", None)
    if (minimum != None and value < minimum or
        maximum != None and value > maximum):
        if maximum == None:
            error = ParamError(param, value, "must be >= %g" % minimum)
        elif minimum == None:
            error = ParamError(param, value, "must be <= %g" % maximum)
        else:
            error = ParamError(param, value,
                               "must be %g <= x <= %g" % (minimum, maximum))
        raise error
    return value

def parse_param_date_value(param, value):
    try:
        value = make_datetime(value)
    except ValueError:
        error = ParamError(param, value, "not a valid date/time")
        raise error
    return value

def parse_param_label_value(param, value):
    kind_args = param['kind_args']
    regex = kind_args.get('regex', r"[^\S,]+")
    try:
        regex = re.compile(regex)
        if not regex.match(value):
            error = ParamError(param, value, "did not match required pattern")
            raise error
    except:
        error = ValueError("Invalid regular expression")
        raise error
    return value

def parse_param_file_value(param, value):
    if not os.path.exists(value):
        error = ParamError(param, value, "file does not exist")
        raise error
    elif os.path.isdir(value):
        error = ParamError(param, value, "file is a directory")
        raise error
    return value

def parse_param_dir_value(param, value):
    if not os.path.exists(value):
        error = ParamError(param, value, "directory does not exist")
        raise error
    elif not os.path.isdir(value):
        error = ParamError(param, value, "is not a directory")
        raise error
    return value

def parse_param_path_value(param, value):
    return value

def parse_param_output_file_value(param, value):
    if os.environ.get("SILK_CLOBBER", "0") in ("0", ""):
        if os.path.exists(value):
            error = ParamError(param, value, "output file already exists")
            raise error
    elif os.path.exists(value):
        if os.path.isdir(value):
            error = ParamError(param, value, "output file is a directory")
            raise error
    return value

def parse_param_output_dir_value(param, value):
    if os.path.exists(value):
        if not os.path.isdir(value):
            error = ParamError(param, value, "output directory is a file")
            raise error
    return value

def parse_param_flag_value(param, value):
    if value or value == None:
        return True
    else:
        return False

re_silk_datetime = re.compile(r"""
^ \s*       (?P<year>\d\d?\d?\d?)
  (?:     / (?P<month>\d\d?)
  (?:     / (?P<day>\d\d?)
  (?:  [:T] (?P<hour>\d\d?)
  (?:     : (?P<minute>\d\d?)
  (?:     : (?P<second>\d\d?)
  (?:    \. (?P<fsec>\d+) )? )? )? )? )? )? \s* $
""", re.VERBOSE)

PRECISION_DAY = 1
PRECISION_HOUR = 2
PRECISION_MINUTE = 3
PRECISION_SECOND = 4
PRECISION_MSEC = 5

def parse_param_flow_date_value(param, value):
    # We want to return a date and a precision.
    precision_error = ParamError(
        param, value, "Date %s does not have at least day precision" % value)
    m = re_silk_datetime.match(value)
    if not m:
        parse_error = ParamError(
            param, value, "Did not match expected YYYY/MM/DD[:HH] format")
        raise parse_error
    year = m.group("year")
    if year == None:
        raise precision_error
    year = int(year)
    if year < 1970 or year > 2039:
        range_error = ParamError(
            param, value, ("Year value (%d) out of range: use 1970 <= "
                           "year <= 2039" % year))
        raise range_error
    month = m.group("month")
    if month == None:
        raise precision_error
    month = int(month)
    if month < 1 or month > 12:
        range_error = ParamError(
            param, value, ("Month value (%d) out of range: use 1 <= month "
                           "<= 12" % month))
        raise range_error
    max_day = calendar.monthrange(year, month)[1]
    day = m.group("day")
    if day == None:
        raise precision_error
    day = int(day)
    if day < 1 or day > max_day:
        range_error = ParamError(
            param, value, ("Day value (%d) out of range: use 1 <= day "
                           "<= %d" % (day, max_day)))
        raise range_error
    hour = m.group("hour")
    if hour == None:
        return ("%04d/%02d/%02d" % (year, month, day),
                PRECISION_DAY)
    hour = int(hour)
    if hour < 0 or hour > 23:
        range_error = ParamError(
            param, value, ("Hour value (%d) out of range: use 0 <= hour "
                           "<= 23" % hour))
        raise range_error
    minute = m.group("minute")
    if minute == None:
        return ("%04d/%02d/%02d:%02d" % (year, month, day, hour),
                PRECISION_HOUR)
    minute = int(minute)
    if minute < 0 or minute > 59:
        range_error = ParamError(
            param, value, ("Minute value (%d) out of range: use 0 <= minute "
                           "<= 23" % minute))
        raise range_error
    second = m.group("second")
    if second == None:
        return ("%04d/%02d/%02d:%02d:%02d" % (year, month, day, hour, minute),
                PRECISION_MINUTE)
    second = int(second)
    if second < 0 or second > 59:
        range_error = ParamError(
            param, value, ("Second value (%d) out of range: use 0 <= minute "
                           "<= 23" % second))
        raise range_error
    fsec = m.group("fsec")
    if fsec == None:
        return ("%04d/%02d/%02d:%02d:%02d:%02d" % (year, month, day, hour,
                                                   minute, second),
                PRECISION_SECOND)
    msec = int((fsec + '00')[:3])
    return ("%04d/%02d/%02d:%02d:%02d:%02d.%03d" %
            (year, month, day, hour, minute, second, msec),
            PRECISION_MSEC)

########################################################################

__all__ = """

    KIND_TEXT
    KIND_INT
    KIND_FLOAT
    KIND_DATE
    KIND_LABEL
    KIND_FILE
    KIND_DIR
    KIND_PATH
    KIND_FLAG

    KIND_FLOW_CLASS
    KIND_FLOW_TYPE
    KIND_FLOW_FLOWTYPES
    KIND_FLOW_SENSORS

    KIND_OUTPUT_FILE
    KIND_OUTPUT_DIR

    check_param_kind
    parse_value

""".split()
