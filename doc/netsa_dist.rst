:mod:`netsa.dist` --- Common Installation Procedures
====================================================

.. module:: netsa.dist

The :mod:`netsa.dist` module is intended primarily for NetSA
development team, to provide a common set of practices for generating
documentation, running tests, and distributing and installing our
software.  If you are not a member of the NetSA dev team, you're
likely to be better served by using the standard :mod:`distutils`
module or the more powerful `setuptools`_ package.

.. _`setuptools`: http://pypi.python.org/pypi/setuptools/

Overview
--------

:mod:`netsa.dist` provides a set of extensions to :mod:`distutils`,
along with an alternative API for specifying the contents of the
distribution.  The extensions provide for automatic generation of
documentation using `Sphinx`_ (including PDF, HTML, and man pages),
automatic generation of Python-readable version information from
configuration metadata, and targets for running automated tests.  The
alternative API allows for specification of project metadata in a
similar style to the metadata of :mod:`netsa.script`.

.. _`Sphinx`: http://sphinx.pocoo.org/

New ``setup.py`` Commands
-------------------------

When running ``setup.py`` for a project that uses :mod:`netsa.dist`,
all of the normal commands (``build``, ``install``, ``sdist``, etc.)
are available, along with the following:

``check``
    Run all automated tests for the project.

``check_unit``
    Run automated unit tests for the project.

``check_other``
    Run all other automated tests for the project.

``gen_version``
    Generates any "version" files required by the project.  See
    :func:`add_version_file`.

``gen_doc_html``
    Generates an HTML manual for this project, placing it in
    ``doc/html``.  This manual is in the normal style for Python
    documentation.  It is never automatically generated.

``gen_doc_tools_web``
    Generates an HTML manual for this project and create a tarball out
    of it, placing the results in
    ``dist/<name>-<version>-doc-web.tar.gz``.  This manual is designed
    for use on the `NetSA Tools`_ website, and this command is used
    only to generate documentation to be deployed at that site.

``gen_doc_man``
    Creates generated man pages for the project, placing them under
    ``doc/man``.  This is automatically called when generating a
    source distribution, and the results will be included in the
    source tarball.  When installing, :mod:`netsa.dist` will attempt
    to run this command, but if it fails it will use a pre-generated
    copy if available.

``gen_doc_pdf``
    Generates a PDF manual for this project, placing it in the top
    level directory.  This is automatically called when generating a
    source distribution, and the resulting manual will be included in
    the source tarball.  This manual is not installed, however, only
    included with the distribution.

``netsa_dist``
    Generates the standard items for a NetSA distribution.  Namely, a
    source code release tarball in ``dist/<name>-<version>.tar.gz``
    and a documentation tarball in
    ``dist/<name>-<version>-doc-web.tar.gz`` for deployment to the
    `NetSA Tools`_ website.

``netsa_src_license``
    Modifies the source files in place to update their license
    section.  The license in ``LICENSE-xxx.txt`` is used for a section
    that begins with ``@xxx_HEADER_START@``.  Backup files are
    created, just in case.

.. _`NetSA Tools`: http://tools.netsa.cert.org/

Project Layout
--------------

The files of the project are expected to be arranged mostly as follows:

.. list-table::
    :header-rows: 1
    :widths: 1, 100

    * - Directory
      - Purpose
    * - bin
      - Contains Python scripts to be installed as executables.
    * - doc
      - Contains Sphinx documentation sources, including ``conf.py``.
        See :func:`disable_documentation`, and `Documentation
        Configuration`_.
    * - src
      - Contains Python source code and data files to be installed in
        Python packages.  See :func:`add_package`,
        :func:`add_package_data`, and :func:`add_module_py`.

The following directories are used to contain outputs, and any extra files in them may be automatically destroyed by the ``clean`` command:

.. list-table::
    :header-rows: 1
    :widths: 1, 100

    * - Directory
      - Purpose
    * - build
      - A variety of intermediate products are stored here while building the project.
    * - dist
      - Final products (tarballs) are stored here.
    * - doc/html
      - HTML documentation generated with ``gen_doc_html`` will do here.
    * - doc/man
      - manpage documentation generated with ``gen_doc_man`` will go here.

.. _`Documentation Configuration`:

Documentation Configuration
---------------------------

To support simpler common configuration for documentation output, a
convenience module is create during documentation generation.  Under
most circumstances, you should be able to use the following
``conf.py`` without changes::

    from netsa_sphinx_config import *

    add_static_path("static_html")

Importing all symbols from :mod:`netsa_sphinx_config` sets all of the
settings to their normal values for a NetSA project, including
producing output appropriate for use on the `NetSA Tools`_ website
automatically.

If you need to make modifications, just replace or modify the values
of standard `Sphinx build options`_.

.. _`Sphinx build options`: http://sphinx.pocoo.org/config.html

The following function is provided to allow automatic generation of
man pages.  Any man page generated from the documentation will be
automatically generated and included in source distributions, and
automatically installed in the appropriate location.

.. function:: netsa_sphinx_config.add_man_page(source_file : str, man_page : str, description : str, [section = 1])

    Add a new man page to be generated from the given *source_file*
    (without extension).  The name of the resulting file is
    *man_page*.*section*. Note that when Sphinx generates man pages,
    the top-level heading from the input file is ignored, and the
    title used is "*man_page* - *description*" instead.  This way, you
    can use the same input file to produce installed man pages and to
    produce man pages for display in the HTML output.

Project Configuration
---------------------

The following functions are used to set metadata for the project:

.. autofunction:: set_name(project_name : str)

.. autofunction:: set_title(project_title : str)

.. autofunction:: set_description(project_description : str)

.. autofunction:: set_version(project_version : str)

.. autofunction:: set_copyright(project_copyright : str)

.. autofunction:: set_license(project_license : str)

.. autofunction:: set_maintainer(project_maintainer : str)

.. autofunction:: set_author(project_author : str)

.. autofunction:: set_url(project_url : str)

.. autofunction:: set_download_url(project_download_url : str)

Choosing which files should be installed where is accomplished with the following functions:

.. autofunction:: add_package

.. autofunction:: add_package_data

.. autofunction:: add_module_py

.. autofunction:: add_module_ext

.. autofunction:: add_script

.. autofunction:: add_install_data

.. autofunction:: add_extra_files

In order to avoid recording the version number in both the
``setup.py`` file and the source code, you can use the following
functions to automatically generate a file with the version number in
it, and read it back at run time:

.. autofunction:: add_version_file(version_file_name : str, [version_file_template = "%s\\n"])

.. autofunction:: netsa.find_version(source_file : str, [num_levels = 3]) -> str

The following functions allow automated tests to be added and run from
``setup.py``:

.. autofunction:: add_unit_test_module(script_unit_test_module : str)

.. autofunction:: add_other_test_module(script_other_test_module : str)

Finally, once the project is fully configured, use this function to
handle command-line options and actually running the tasks:

.. autofunction:: execute()
