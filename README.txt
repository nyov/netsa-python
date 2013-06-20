NetSA Python
============

The netsa-python library is a grab-bag of Python routines and
frameworks that we have found helpful when developing analyses using
the SiLK toolkit. Of particular note are the netsa.script NetSA
Scripting Framework, which provides a standard framework for writing
scripts that process flow data, and the netsa.util.shell command
line processing system, which provides tools for managing extremely
complicated collections of shell processes that should fail or
succeed together (extremely useful when working with named pipes).

NOTE: Version 1.4 of NetSA Python is the last major version
      that will support Python 2.4 or 2.5.  Future major versions
      of NetSA Python will require Python 2.6 or greater.

Installation
------------

Building and installing netsa-python is done using the standard
setup.py mechanism.  The following commands should suffice in most
cases:

    python setup.py build
    python setup.py install    # as root

Building an RPM
---------------

Please use the provided netsa-python.spec file to build netsa-python
and netsa_silk RPMs.  Note that if you already have an older version of
netsa-python installed, you may need to use a virtualenv to build the
RPMs, in order to avoid having the older installed version of netsa-python
take priority over the new version during the build process.  Using
bdist_rpm to produce netsa-python RPMs will result in incorrect RPMs.
