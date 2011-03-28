:mod:`netsa.util.compat` --- Python version compatibility code
==============================================================

.. module:: netsa.util.compat

The :mod:`netsa.util.compat` module provides some additional
functionality introduced between Python 2.4 and the latest versions of
Python.  Obviously new syntax features cannot be supported, but
certain utility functions in modules or built-in functions can be
added on for the sake of sanity.

The list of provided features is currently small, but is likely to
grow over time.

To use the compatibility features, simply import this module::

    import netsa.util.compat

There is no need to import any specific symbols from the module---it
will add the symbols directly where needed so that they may be
imported as normal.  Built-ins will also work wherever used.

The additional functions currently provided by this module are:

  * :func:`all`

  * :func:`any`

  * :func:`itertools.product`
      
