Webkit based PDF report engine
==============================

.. image:: https://travis-ci.org/openlabs/trytond-report-webkit.png?branch=2.6
    :target: https://travis-ci.org/openlabs/trytond-report-webkit

This package allows you to build HTML based reports and then convert them
into PDFs using `wkhtmltopdf` which uses the webkit rendering engine and
QT. (WebKit is the engine of Apples Safari).

The templates are written using `Genshi <http://genshi.edgewall.org>`_.
Though Genshi is not our favorite templating engine, it is a package
tryton core depends on, and the authors did not want to add another
template engine as its dependency. Genshi comes with a faily good
`tutorial <http://genshi.edgewall.org/wiki/Documentation/xml-templates.html>`_.

Using this in your projects
===========================

Instead of using the default report class from trytond.report use the
ReportWebkit class from this package instead.

::

    from openlabs_report_webkit import ReportWebkit

    class UserReport(ReportWebkit):
        __name__ = 'res.user'


Output Formats
--------------

To get PDF outputs (instead of standard html) ensure that the report
definition in xml clearly shows the extension as PDF. This could be
changed from the tryton administration section too.


Adding as a dependency
----------------------

You can add the report toolkit as a dependent package of your tryton
module by adding into the install_requires list on your setup.py script.
Remember to specify the version numbers carefully, or the latest version
of the package available would be installed.

For example if your module is for version 2.6 of tryton, the line to add
would be

::

    install_requires = [
        ...,
        'openlabs_report_webkit>=2.6,<2.7'
        ...,
    ]

Gotchas!
========

The report file is missing
--------------------------

* Did you add the template file to the package_data in your setup.py ?
* Did you add the template file extension to the included files in
  MANIFEST ?

PDF generation problems
-----------------------

* Check if wkhtmltopdf works well:  Installing it simply via 
  `sudo apt-get install wkhtmltopdf` on Ubuntu for exmaple will install a
  reduced functionality version which is probably not what you want.
