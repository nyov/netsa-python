:mod:`netsa.sql` --- SQL Database Access
========================================

.. automodule:: netsa.sql

    Overview
    --------

    The normal flow of code that works with databases using the
    :class:`netsa.sql` API looks like this::

        from netsa.sql import *

        select_stuff = db_query("""
            select a, b, c
              from test_table
              where a + b <= :threshold
            limit 10
        """)

        conn = db_connect("nsql-sqlite:/var/tmp/test_db.sqlite")

        for (a, b, c) in conn.execute(select_stuff, threshold=5):
            print ("a: %d, b: %d, c: %d, a + b: %d" % (a, b, c, a+b))

        # Alternatively:
        for (a, b, c) in select_stuff(conn, threshold=5):
            print ("a: %d, b: %d, c: %d, a + b: %d" % (a, b, c, a+b))

    First, the required queries are created as instances of the
    :class:`db_query` class.  Some developers prefer to have a
    separate module containing all of the queries grouped together.
    Others prefer to keep the queries close to where they are used.

    When the database is to be used, a connection is opened using
    :func:`db_connect`.  The query is executed using
    :meth:`db_connection.execute`, or by calling the query directly.
    The result of that call is then iterated over and the data processed.

    Connections and result sets are automatically closed when garbage
    collected.  If you need to make sure that they are collected as
    early as possible, make sure the values are not kept around in the
    environment (for example, by assigning ``None`` to the variable
    containing them when your work is complete, if the variable won't be
    leaving scope for a while.)

    Exceptions
    ----------

    .. autoexception:: sql_exception(message : str)

    .. autoexception:: sql_no_driver_exception(message : str)

    .. autoexception:: sql_invalid_uri_exception(message : str)

    Connecting
    ----------

    .. autofunction:: db_connect(uri, [user : str, password : str]) -> db_connection

    Connections and Result Sets
    ---------------------------

    .. autoclass:: db_connection(driver : db_driver, variants : str list)

        .. automethod:: get_driver() -> db_driver

        .. automethod:: clone() -> db_connection

        .. automethod:: execute(query_or_sql : db_query or str, [<param_name>=<param_value>, ...]) -> db_result

        .. automethod:: commit()

        .. automethod:: rollback()

        .. automethod:: get_variants() -> str seq

    .. autoclass:: db_result(connection : db_connection, query : db_query, params : dict)

        .. automethod:: get_connection() -> db_connection

        .. automethod:: get_query() -> db_query

        .. automethod:: get_params() -> dict

        .. automethod:: __iter__() -> iter

    Compiled Queries
    ----------------

    .. autoclass:: db_query(sql : str, [<variant> : str, ...])

        .. automethod:: __call__(self, _conn : db_connection, [<param_name>=<param_value>, ...]) -> db_result

        **Note that the following methods are primarily of interest to
        driver implementors.**

        .. automethod:: get_variant_sql(accepted_variants : str seq) -> str

        .. automethod:: get_variant_qmark_params(accepted_variants : str seq, params : dict) -> str, seq

        .. automethod:: get_variant_numeric_params(accepted_variants : str seq, params : dict) -> str, seq

        .. automethod:: get_variant_named_params(accepted_variants : str seq, params : dict) -> str, dict

        .. automethod:: get_variant_format_params(accepted_variants : str seq, params : dict) -> str, seq

        .. automethod:: get_variant_pyformat_params(accepted_variants : str seq, params : dict) -> str, dict

    Implementing a New Driver
    -------------------------

    In order to implement a new database driver, you should create a
    new module that implements a subclass of :class:`db_driver`, then
    calls :func:`register_driver` with an instance of that subclass in
    order to register the new driver.

    Your :class:`db_driver` subclass will, of course, return
    subclasses of :class:`db_connection` and :class:`db_result`
    specific to your database as well.  It should never be necessary
    to subclass :class:`db_query`---that class is meant to be a
    database-neutral representation of a "compiled" query.

    For most drivers, one of the ``get_variant_...`` methods of
    :class:`db_query` should provide the query in a form that the
    underlying database can easily digest.

    .. autoclass:: db_driver()

        .. automethod:: can_handle(uri_scheme : str) -> bool

        .. automethod:: connect(uri : str, user: str or None, password : str or None) -> db_connection

    .. autofunction:: register_driver(driver : db_driver)

    .. autofunction:: unregister_driver(driver : db_driver)

    Experimental Connection Pooling
    -------------------------------

    This version of :mod:`netsa.sql` contains experimental support for
    connection pooling.  Connections in a pool will be created before
    they're needed and kept available for re-use.  Note that since
    this API is still in the early stages of development, it is very
    likely to change between versions of `netsa-python`.

    .. autofunction:: db_create_pool(uri, [user : str, password : str], ...) -> db_pool

    .. autoclass:: db_pool()

        .. automethod:: get_driver() -> db_driver

        .. automethod:: connect() -> db_connection

    .. class:: db_driver()

        .. automethod:: create_pool(uri, user : str or None, password : str or None, ...) -> db_pool


    Why Not DB API 2.0?
    -------------------

    If you have experience with Python database APIs, you may be
    wondering why we have chosen to implement a new API rather than
    simply using the standard `DB API 2.0`_.

    In short, the problem is that the standard database API isn't
    really an API, but more a set of guidelines.  For example, each
    database driver may use a different mechanism for providing query
    parameters.  As another example, each API may also have different
    behaviors in the presence of threads.

    Specifically, the :mod:`sqlite` module uses the 'pyformat' param
    style, which allows named parameters to queries which are passed
    as a dict, using Python-style formats.  The :mod:`sqlite3` module,
    on the other hand, uses the 'qmark' param style, where ``?`` is
    used as a place-holder in queries, and the parameters are
    positional and passed in as a sequence.

    We've done work to make sure that it's simple to implement
    :mod:`netsa.sql`-style drivers over the top of `DB API 2.0`_-style
    drivers.  In fact, all of the currently deployed drivers are of
    this variety.  The only work that has to be done for such a driver
    is to start with one of the existing drivers, determine which
    paramstyle is being used, do any protection against threading
    issues that might be necessary, and turn the connection URI into a
    form that the driver you're using can handle.

    Once that's done, you still have the issue that different
    databases may require different SQL to operate---but that's a lot
    easier to handle than "some databases use named parameters and
    some use positional".  And, the variant system makes it easy to
    put different compatibility versions of the same query together.

    .. _`DB API 2.0`: http://www.python.org/dev/peps/pep-0249/
