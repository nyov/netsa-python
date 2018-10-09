# Copyright 2008-2016 by Carnegie Mellon University
# See license information in LICENSE-OPENSOURCE.txt

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
    allowed_arg_names = set(["regex", "regex_help"])
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
    if "regex_help" in kind_args:
        if not isinstance(kind_args["regex_help"], basestring):
            error = TypeError("text param expected str value for 'regex_help'")
            raise error

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
                                            for x in kind_args)))
        raise error

def check_param_label_args(kind_args):
    kind_arg_names = set(kind_args.iterkeys())
    allowed_arg_names = set(["regex", "regex_help"])
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
    if "regex_help" in kind_args:
        if not isinstance(kind_args["regex_help"], basestring):
            error = TypeError("text param expected str value for 'regex_help'")
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
                                            for x in kind_args)))
        raise error

def check_param_path_args(kind_args):
    if kind_args:
        error = TypeError("path param got unexpected keyword arguments: "
                          "%s" % (", ".join(repr(x)
                                            for x in kind_args)))
        raise error

def check_param_output_file_args(kind_args):
    if kind_args:
        error = TypeError("output file param got unexpected keyword arguments: "
                          "%s" % (", ".join(repr(x)
                                            for x in kind_args)))
        raise error

def check_param_output_dir_args(kind_args):
    if kind_args:
        error = TypeError("output dir param got unexpected keyword arguments: "
                          "%s" % (", ".join(repr(x)
                                            for x in kind_args)))
        raise error

def check_param_flag_args(kind_args):
    if kind_args:
        error = TypeError("flag param got unexpected keyword arguments: "
                          "%s" % (", ".join(repr(x)
                                            for x in kind_args)))
        raise error

def check_param_flow_class_args(kind_args):
    if kind_args:
        error = TypeError("flow class param got unexpected keyword arguments: "
                          "%s" % (", ".join(repr(x)
                                            for x in kind_args)))
        raise error

def check_param_flow_type_args(kind_args):
    if kind_args:
        error = TypeError("flow type param got unexpected keyword arguments: "
                          "%s" % (", ".join(repr(x)
                                            for x in kind_args)))
        raise error

def check_param_flow_flowtypes_args(kind_args):
    if kind_args:
        error = TypeError("flow flowtypes param got unexpected keyword "
                          "arguments: %s" %
                          (", ".join(repr(x) for x in kind_args)))
        raise error

def check_param_flow_sensors_args(kind_args):
    if kind_args:
        error = TypeError("flow sensors param got unexpected keyword "
                          "arguments: %s" %
                          (", ".join(repr(x) for x in kind_args)))
        raise error

def check_param_flow_date_args(kind_args):
    if kind_args:
        error = TypeError("flow date param got unexpected keyword "
                          "arguments: %s" %
                          (", ".join(repr(x) for x in kind_args)))
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

def parse_value(param, value, is_default=False):
    if param['kind'] == KIND_TEXT:
        return parse_param_text_value(param, value, is_default)
    elif param['kind'] == KIND_INT:
        return parse_param_int_value(param, value, is_default)
    elif param['kind'] == KIND_FLOAT:
        return parse_param_float_value(param, value, is_default)
    elif param['kind'] == KIND_DATE:
        return parse_param_date_value(param, value, is_default)
    elif param['kind'] == KIND_LABEL:
        return parse_param_label_value(param, value, is_default)
    elif param['kind'] == KIND_FILE:
        return parse_param_file_value(param, value, is_default)
    elif param['kind'] == KIND_DIR:
        return parse_param_dir_value(param, value, is_default)
    elif param['kind'] == KIND_PATH:
        return parse_param_path_value(param, value, is_default)
    elif param['kind'] == KIND_FLAG:
        return parse_param_flag_value(param, value, is_default)
    elif param['kind'] == KIND_FLOW_CLASS:
        return parse_param_text_value(param, value, is_default)
    elif param['kind'] == KIND_FLOW_TYPE:
        return parse_param_text_value(param, value, is_default)
    elif param['kind'] == KIND_FLOW_FLOWTYPES:
        return parse_param_text_value(param, value, is_default)
    elif param['kind'] == KIND_FLOW_SENSORS:
        return parse_param_text_value(param, value, is_default)
    elif param['kind'] == KIND_FLOW_DATE:
        # Sanity check it as a date, but return it as text
        return parse_param_flow_date_value(param, value, is_default)
    elif param['kind'] == KIND_OUTPUT_FILE:
        return parse_param_output_file_value(param, value, is_default)
    elif param['kind'] == KIND_OUTPUT_DIR:
        return parse_param_output_dir_value(param, value, is_default)
    else:
        if is_default:
            default_msg = " in script default"
        else:
            default_msg = ""
        error = ValueError("Unknown param kind: %s%s" %
                           (repr(param['kind']), default_msg))
        raise error

def parse_param_text_value(param, value, is_default):
    kind_args = param['kind_args']
    if is_default:
        default_msg = " in script default"
    else:
        default_msg = ""
    if 'regex' in kind_args:
        regex = kind_args['regex']
        regex_help = kind_args.get('regex_help',
                                   "did not match required pattern")
        try:
            regex = re.compile(regex)
        except:
            error = ValueError("Invalid regex for %s: %s" %
                               (param['name'], repr(regex)))
            raise error
        if not regex.match(value):
            error = ParamError(param, value, regex_help + default_msg)
            raise error
    return value

def parse_param_int_value(param, value, is_default):
    if is_default:
        default_msg = " in script default"
    else:
        default_msg = ""
    try:
        value = int(value)
    except ValueError:
        error = ParamError(param, value, "not a valid integer" + default_msg)
        raise error
    kind_args = param['kind_args']
    minimum = kind_args.get("minimum", None)
    maximum = kind_args.get("maximum", None)
    if (minimum != None and value < minimum or
        maximum != None and value > maximum):
        if maximum == None:
            error = ParamError(param, value, "%s must be >= %d%s" %
                               (minimum, default_msg))
        elif minimum == None:
            error = ParamError(param, value, "must be <= %d%s" %
                               (maximum, default_msg))
        else:
            error = ParamError(param, value,
                               "must be %d <= x <= %d%s" %
                               (minimum, maximum, default_msg))
        raise error
    return value

def parse_param_float_value(param, value, is_default):
    if is_default:
        default_msg = " in script default"
    else:
        default_msg = ""
    try:
        value = float(value)
    except ValueError:
        error = ParamError(param, value,
                           "not a valid floating point number" + default_msg)
        raise error
    kind_args = param['kind_args']
    minimum = kind_args.get("minimum", None)
    maximum = kind_args.get("maximum", None)
    if (minimum != None and value < minimum or
        maximum != None and value > maximum):
        if maximum == None:
            error = ParamError(param, value, "must be >= %g%s" %
                               (minimum, default_msg))
        elif minimum == None:
            error = ParamError(param, value, "must be <= %g" %
                               (maximum, default_msg))
        else:
            error = ParamError(param, value,
                               "must be %g <= x <= %g%s" %
                               (minimum, maximum, default_msg))
        raise error
    return value

def parse_param_date_value(param, value, is_default):
    if is_default:
        default_msg = " in script default"
    else:
        default_msg = ""
    try:
        value = make_datetime(value)
    except ValueError:
        error = ParamError(param, value, "not a valid date/time" + default_msg)
        raise error
    return value

def parse_param_label_value(param, value, is_default):
    if is_default:
        default_msg = " in script default"
    else:
        default_msg = ""
    kind_args = param['kind_args']
    regex = kind_args.get('regex', r"[^\s,]+")
    regex_help = kind_args.get('regex_help', "not a valid label")
    try:
        regex = re.compile(regex)
        if not regex.match(value):
            error = ParamError(param, value, regex_help + default_msg)
            raise error
    except:
        raise
        error = ValueError("Invalid regular expression")
        raise error
    return value

def parse_param_file_value(param, value, is_default):
    if is_default:
        return value
    if not os.path.exists(value):
        error = ParamError(param, value, "file does not exist")
        raise error
    elif os.path.isdir(value):
        error = ParamError(param, value, "file is a directory")
        raise error
    return value

def parse_param_dir_value(param, value, is_default):
    if is_default:
        return value
    if not os.path.exists(value):
        error = ParamError(param, value, "directory does not exist")
        raise error
    elif not os.path.isdir(value):
        error = ParamError(param, value, "is not a directory")
        raise error
    return value

def parse_param_path_value(param, value, is_default):
    return value

def parse_param_output_file_value(param, value, is_default):
    if value in ('-', 'stdout', 'stderr'):
        return value
    if is_default:
        return value
    if os.environ.get("SILK_CLOBBER", "0") in ("0", ""):
        if os.path.exists(value):
            error = ParamError(param, value, "output file already exists")
            raise error
    elif os.path.exists(value):
        if os.path.isdir(value):
            error = ParamError(param, value, "output file is a directory")
            raise error
    return value

def parse_param_output_dir_value(param, value, is_default):
    if is_default:
        return value
    if os.path.exists(value):
        if not os.path.isdir(value):
            error = ParamError(param, value, "output directory is a file")
            raise error
    return value

def parse_param_flag_value(param, value, is_default):
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

def parse_param_flow_date_value(param, value, is_default):
    if is_default:
        default_msg = " in script default"
    else:
        default_msg = ""
    # We want to return a date and a precision.
    precision_error = ParamError(
        param, value, "Date %s does not have at least day precision%s" %
        (value, default_msg))
    m = re_silk_datetime.match(value)
    if not m:
        parse_error = ParamError(
            param, value, "Did not match expected YYYY/MM/DD[:HH] format" +
            default_msg)
        raise parse_error
    year = m.group("year")
    if year == None:
        raise precision_error
    year = int(year)
    if year < 1970 or year > 2039:
        range_error = ParamError(
            param, value, ("Year value (%d) out of range: use 1970 <= "
                           "year <= 2039%s" % (year, default_msg)))
        raise range_error
    month = m.group("month")
    if month == None:
        raise precision_error
    month = int(month)
    if month < 1 or month > 12:
        range_error = ParamError(
            param, value, ("Month value (%d) out of range: use 1 <= month "
                           "<= 12%s" % (month, default_msg)))
        raise range_error
    max_day = calendar.monthrange(year, month)[1]
    day = m.group("day")
    if day == None:
        raise precision_error
    day = int(day)
    if day < 1 or day > max_day:
        range_error = ParamError(
            param, value, ("Day value (%d) out of range: use 1 <= day "
                           "<= %d%s" % (day, max_day, default_msg)))
        raise range_error
    hour = m.group("hour")
    if hour == None:
        return ("%04d/%02d/%02d" % (year, month, day),
                PRECISION_DAY)
    hour = int(hour)
    if hour < 0 or hour > 23:
        range_error = ParamError(
            param, value, ("Hour value (%d) out of range: use 0 <= hour "
                           "<= 23%s" % (hour, default_msg)))
        raise range_error
    minute = m.group("minute")
    if minute == None:
        return ("%04d/%02d/%02d:%02d" % (year, month, day, hour),
                PRECISION_HOUR)
    minute = int(minute)
    if minute < 0 or minute > 59:
        range_error = ParamError(
            param, value, ("Minute value (%d) out of range: use 0 <= minute "
                           "<= 23%s" % (minute, default_msg)))
        raise range_error
    second = m.group("second")
    if second == None:
        return ("%04d/%02d/%02d:%02d:%02d" % (year, month, day, hour, minute),
                PRECISION_MINUTE)
    second = int(second)
    if second < 0 or second > 59:
        range_error = ParamError(
            param, value, ("Second value (%d) out of range: use 0 <= minute "
                           "<= 23%s" % (second, default_msg)))
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
