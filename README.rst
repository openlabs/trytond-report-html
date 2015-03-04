Webkit based PDF report engine
==============================

.. image:: https://travis-ci.org/openlabs/trytond-report-webkit.png?branch=develop
    :target: https://travis-ci.org/openlabs/trytond-report-webkit

This package allows you to build HTML based reports and then convert them
into PDFs using `wkhtmltopdf` which uses the webkit rendering engine and
QT. (WebKit is the engine of Apples Safari).

The templates are written using `Genshi <http://genshi.edgewall.org>`_.
Though Genshi is not our favorite templating engine, it is a package
tryton core depends on, and the authors did not want to add another
template engine as its dependency. Genshi comes with a fairly good
`tutorial <http://genshi.edgewall.org/wiki/Documentation/xml-templates.html>`_.

The package also supports `Jinja's <http://jinja.pocoo.org/>`_ Template
`Inheritance <http://jinja.pocoo.org/docs/templates/#template-inheritance>`_.

Using this in your projects
===========================

Instead of using the default report class from trytond.report use the
ReportWebkit class from this package instead.

.. code-block:: python

    from openlabs_report_webkit import ReportWebkit

    class UserReport(ReportWebkit):
        __name__ = 'res.user'


Output Formats
--------------

To get PDF outputs (instead of standard html) ensure that the report
definition in xml clearly shows the extension as PDF. This could be
changed from the tryton administration section too.

To convert to PDFs this module needs either the ``wkhtmltopdf`` or 
``weasyprint`` installed.

Installing wkhtmltopdf (default)
````````````````````````````````

Installing wkhtmltopdf from debian repositories usually install an older
version which does not have support for features like page numbers at the
end of each page. So remember to install the latest one published by the
maintainers. For details refer to 
`wkhtmltopdf project website <http://wkhtmltopdf.org/>`_.

Installing weasyprint
`````````````````````

Weasyprint is a much lighter option (in comparison to wkhtmltopdf) but
with lesser features. Weasyprint can be installed from PYPI.

``pip install weasyprint``


To use weasyprint, your report implementation class must explicitly
override the convert api to use weasyprint. Example:

.. code-block:: python

    # TODO: an example here


Adding as a dependency
----------------------

You can add the report toolkit as a dependent package of your tryton
module by adding into the install_requires list on your setup.py script.
Remember to specify the version numbers carefully, or the latest version
of the package available would be installed.

For example if your module is for version 2.6 of tryton, the line to add
would be

.. code-block:: python

    install_requires = [
        ...,
        'openlabs_report_webkit>=2.6,<2.7'
        ...,
    ]

If you want to use weasyprint instead of whtmltopdf, it might be a good
idea to change the above line to

.. code-block:: python

    'openlabs_report_webkit[weasyprint]>=2.6,<2.7'

Gotchas!
========

The report file is missing
--------------------------

* Did you add the template file to the package_data in your setup.py ?
* Did you add the template file extension to the included files in
  MANIFEST ?
