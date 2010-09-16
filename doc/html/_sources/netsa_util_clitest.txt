:mod:`netsa.util.clitest` --- Utility for testing CLI tools
===========================================================

.. automodule:: netsa.util.clitest

    Exceptions
    ----------

    .. autoexception:: TestingException

    Classes
    -------

    .. autoclass:: Environment([work_dir : str], [save_work_dir : bool], [debug : bool], [<env_name>=<env_val>, ...])

        .. automethod:: get_env(env_name : str) -> str

        .. automethod:: set_env(env_name : str, env_val : str)

        .. automethod:: del_env(env_name : str)

        .. automethod:: get_work_dir() -> str

        .. automethod:: run(command : str, [<keyword>=<value>, ...]) -> Result

        .. automethod:: cleanup()

    .. autoclass:: Result

        .. automethod:: success() -> bool

        .. automethod:: exited([code]) -> bool

        .. automethod:: exit_status() -> int or None

        .. automethod:: signal() -> int or None

        .. automethod:: signaled() -> bool

        .. automethod:: format_status() -> str

        .. automethod:: get_status() -> int

        .. automethod:: get_stdout() -> str

        .. automethod:: get_stderr() -> str

        .. automethod:: get_info() -> str

        
