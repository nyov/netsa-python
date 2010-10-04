:mod:`netsa.util.shell` --- Robust Shell Pipelines
==================================================

.. automodule:: netsa.util.shell

    Exceptions
    ----------

    .. autoexception:: PipelineException

    Building Commands and Pipelines
    -------------------------------

    .. autofunction:: command(<command spec>, [stderr : str or file, stderr_append=False, ignore_exit_status=False, ignore_exit_statuses : int seq]) -> command

    .. autofunction:: pipeline(<pipeline spec>, [stdin : str or file, stdout : str or file, stdout_append=False, ...]) -> pipeline

    Running Pipelines
    -----------------

    .. autofunction:: run_parallel(<pipeline spec>, ..., [vars : dict, ...])

    .. autofunction:: run_collect(<command spec>, ..., [vars : dict, ...]) -> str, str

    .. autofunction:: run_collect_files(<command spec>, ..., [vars : dict, ...]) -> file, file
