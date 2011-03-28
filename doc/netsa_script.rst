:mod:`netsa.script` --- The NetSA Scripting Framework
=====================================================

.. automodule:: netsa.script

    Exceptions
    ----------

    .. autoexception:: ParamError

    .. autoexception:: UserError(message)

    .. autoexception:: ScriptError(message)

    Metadata Functions
    ------------------

    The following functions define "metadata" for the script---they
    provide information about the name of the script, what the script
    is for, who to contact with problems, and so on.  Automated tools
    can use this information to allow users to browse a list of
    available scripts.

    .. autofunction:: set_title(script_title : str)

    .. autofunction:: set_description(script_description : str)

    .. autofunction:: set_version(script_version : str)

    .. autofunction:: set_package_name(script_package_name : str)

    .. autofunction:: set_contact(script_contact : str)

    .. autofunction:: set_authors(script_authors : str list)

    .. autofunction:: add_author(script_author : str)

    Script Parameters
    -----------------

    These calls are used to add parameters to a script.  When the
    script is called from the command-line, these are command-line
    arguments.  When a GUI is used to invoke the script, the params
    might be presented in a variety of ways.  This need to support
    both command-line and GUI access to script parameters is the
    reason that they've been standardized here.  It's also the reason
    that you'll find no "add an argument with this arbitrary handler
    function" here.

    If you do absolutely need deeper capabilities than are provided
    here, you can use one of the basic param types and then do
    additional checking in the ``main`` function.  Note, however, that
    a GUI will not aid users in choosing acceptable values for params
    defined in this way.  Also, make sure to raise :exc:`ParamError`
    with appropriate information when you reject a value, so that the
    error can be most effectively communicated back to the user.

    .. autofunction:: add_text_param(name : str, help : str, [required=False, default : str, default_help : str, expert=False, regex : str])

    .. autofunction:: add_int_param(name : str, help : str, [required=False, default : int, default_help : str, expert=False, minimum : int, maximum : int])

    .. autofunction:: add_float_param(name : str, help : str, [required=False, default : float, default_help : str, expert=False, minimum : float, maximum : float]) 

    .. autofunction:: add_date_param(name : str, help : str, [required=False, default : datetime, default_help : str, expert=False])

    .. autofunction:: add_label_param(name : str, help : str, [required=False, default : str, default_help : str, expert=False, regex : str])

    .. autofunction:: add_file_param(name : str, help : str, [required=False, default : str, default_help : str, expert=False, mime_type : str])

    .. autofunction:: add_dir_param(name : str, help : str, [required=False, default : str, default_help : str, expert=False])

    .. autofunction:: add_path_param(name : str, help : str, [required=False, default : str, default_help : str, expert=False])

    .. autofunction:: add_path_param(name : str, help : str, [required=False, default : str, default_help : str, expert=False])

    .. autofunction:: add_flag_param(name : str, help : str, [default=False, default_help : str, expert=False])

    .. autofunction:: get_param(name : str) -> value

    Verbose Output
    --------------

    .. autofunction:: get_verbosity() -> int

    .. autofunction:: display_message(text, [min_verbosity=1])

    Flow Data Parameters
    --------------------

    In order to standardize the large number of scripts that work with
    network flow data using the SiLK tool suite, the following calls
    can be used to work with flow data input.

    .. autofunction:: add_flow_annotation(script_annotation : str)

    .. autofunction:: add_flow_params([require_pull=False, without_params : str list])

    .. autofunction:: get_flow_params() -> Flow_params

    .. autoclass:: Flow_params([flow_class : str, flow_type : str, flowtypes : str list, sensors : str list, start_date : datetime, end_date : datetime, input_pipe : str, xargs : str, filenames : str list])

        .. automethod:: by_day() -> Flow_params iter

        .. automethod:: by_hour() -> Flow_params iter

        .. automethod:: by_sensor() -> Flow_params iter

        .. automethod:: get_argument_list() -> str list or None

        .. automethod:: get_class() -> str or None

        .. automethod:: get_end_date() -> datetime or None

        .. automethod:: get_filenames() -> str list or None

        .. automethod:: get_flowtypes() -> str list or None

        .. automethod:: get_input_pipe() -> str or None

        .. automethod:: get_sensors() -> str list or None

        .. automethod:: get_start_date() -> datetime or None

        .. automethod:: get_type() -> str or None

        .. automethod:: get_xargs() -> str or None

        .. automethod:: is_files() -> bool

        .. automethod:: is_pull() -> bool

        .. automethod:: using([flow_class : str, flow_type : str, flowtypes : str list, sensors : str list, start_date : datetime, end_date : datetime, input_pipe : str, xargs : str, filenames : str list]) -> Flow_params


    Producing Output
    ----------------

    Every output file that a script produces needs to be registered
    with the system, so that automated tools can be sure to collect
    everything.  Some scripts produce one or more set outputs.  For
    example "the report", or "the HTML version of the report".  Others
    produce a number of outputs based on the content of the data they
    process.  For example "one image for each host we identify as
    suspicious."

    .. autofunction:: add_output_file_param(name : str, help: str, [required=True, expert=False, description : str, mime_type='application/octet-stream'])

    .. autofunction:: get_output_file_name(name : str) -> str

    .. autofunction:: get_output_file(name : str) -> file

    .. autofunction:: add_output_dir_param(name : str, help : str, [required=True, expert=False, description : str, mime_type : str])

    .. autofunction:: get_output_dir_file_name(dir_name : str, file_name : str, [description : str, mime_type : str]) -> str

    .. autofunction:: get_output_dir_file(dir_name : str, file_name : str, [description : str, mime_type : str]) -> file

    Temporary Files
    ---------------

    .. autofunction:: get_temp_dir_file_name([file_name : str]) -> str

    .. autofunction:: get_temp_dir_file([file_name : str, append=False]) -> file

    .. autofunction:: get_temp_dir_pipe_name([pipe_name : str]) -> str

    Script Execution
    ----------------

    .. autofunction:: execute(func : callable)
