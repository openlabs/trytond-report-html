Webkit based PDF report engine
==============================

.. image:: https://travis-ci.org/openlabs/trytond-report-webkit.png?branch=develop
    :target: https://travis-ci.org/openlabs/trytond-report-webkit


This package allows you to build HTML based reports and then convert them
into PDFs using either `wkhtmltopdf` which uses the webkit rendering engine and
QT. (WebKit is the engine of Apples Safari). or
`Weasyprint<http://http://weasyprint.org/>`_

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

        @classmethod
        def get_jinja_filters(cls, *args, **kwargs):
            """
            Add my custom filters
            """
            filters = super(UserReport, cls).get_jinja_filters(*args, **kwargs)
            filters.update({
                'nl2br': lambda value: value.replace('\n','<br>\n')
            })
            return filters


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


Template Filters
----------------

Tryton HTML reports arrive with some builtin Template filters (in addition
to the `built-in filters of Jinja2 <>`_) to make things easier:

dateformat(date, format='medium')
`````````````````````````````````

Format the date with the current language from the context. For other
possible formats, refer the 
`babel documentation <http://babel.pocoo.org/docs/dates/#date-and-time>`_.

Example

.. code-block:: html+jinja

    <td>Date</td>
    <td>{{ sale.date|dateformat }}</td>

datetimeformat(datetime, format)
````````````````````````````````

Format the datetime with the current language from the context. For other
possible formats, refer the 
`babel documentation <http://babel.pocoo.org/docs/dates/#date-and-time>`_.

Example

.. code-block:: html+jinja

    Created on {{ sale.create_date|datetimeformat('long') }}</td>

currencyformat(amount, currency, format=None)
`````````````````````````````````````````````

Return formatted currency value. For more formatting information refer
`babel documentation <http://babel.pocoo.org/docs/api/numbers/?highlight=format_currency#babel.numbers.format_currency>`_

Example

.. code-block:: html+jinja

    <td>Total Value</td>
    <td>{{ sale.total_amount|currencyformat(sale.currency.code) }}</td>

modulepath(name)
````````````````

Get the absolute Path of a file within a module

Example

.. code-block:: html+jinja

   <img src="{{ 'company/logo.png'|modulepath }}"/>



Of course you can add your own as stated above.


Including Styles
----------------

To include stylesheets, images or any other static data you have two options:

1. Have Tryton serving your files by adding the static-directory to your
   Tryton json_path
2. Bundle your static files inside the reports module and reference using

.. code-block:: html+jinja

    <link rel="stylesheet" href="{{ 'reports/main.css' | module_path }}" type="text/css">

The second approach comes with the downside that static files will only be
available on the server, so you can only see the formatted pdf

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
  
Authors and Contributors
------------------------

This module was built at `Openlabs <http://www.openlabs.co.in>`_. 

We gratefully acknowledge contributions by:

* `simon klemenc <https://github.com/hiaselhans>`_
* `Udo Spallek <https://github.com/udono>`_

Professional Support
--------------------

This module is professionally supported by `Openlabs <http://www.openlabs.co.in>`_.
If you are looking for on-site teaching or consulting support, contact our
`sales <mailto:sales@openlabs.co.in>`_ and `support
<mailto:support@openlabs.co.in>`_ teams.
