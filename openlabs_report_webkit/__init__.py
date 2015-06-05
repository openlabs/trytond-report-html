# -*- coding: utf-8 -*-
'''


    :copyright: (c) 2013 by Openlabs Technologies & Consulting (P) Ltd.
    :license: GPLv3, see LICENSE for more details

'''

import os
import tempfile
from functools import partial

from jinja2 import Environment, FunctionLoader
from babel.dates import format_date, format_datetime
from babel.numbers import format_currency

try:
    import weasyprint
except ImportError:
    pass

from genshi.template import MarkupTemplate
from trytond.tools import file_open
from trytond.pool import Pool
from trytond.transaction import Transaction
from trytond.report import Report, TranslateFactory, Translator
from executor import execute


class ReportWebkit(Report):
    render_method = "webkit"

    @classmethod
    def render(cls, report, report_context):
        pool = Pool()
        Translation = pool.get('ir.translation')
        Company = pool.get('company.company')

        # Convert to str as buffer from DB is not supported by StringIO
        report_content = (str(report.report_content) if report.report_content
                          else False)
        if not report_content:
            raise Exception('Error', 'Missing report file!')

        translate = TranslateFactory(cls.__name__, Transaction().language,
                                     Translation)
        report_context['setLang'] = lambda language: translate.set_language(
            language)

        company_id = Transaction().context.get('company')
        report_context['company'] = Company(company_id)

        return cls.render_template(report_content, report_context, translate)

    @classmethod
    def convert(cls, report, data):
        # Convert the report to PDF if the output format is PDF
        # Do not convert when report is generated in tests, as it takes
        # time to convert to PDF due to which tests run longer.
        # Pool.test is True when running tests.
        output_format = report.extension or report.template_extension

        if output_format == "html" or Pool.test:
            return output_format, data
        elif cls.render_method == "webkit":
            return output_format, cls.wkhtml_to_pdf(data)
        elif cls.render_method == "weasyprint":
            return output_format, cls.weasyprint(data)

    @classmethod
    def render_template_genshi(cls, template_string, localcontext, translator):
        """
        Legacy genshi rendered for backward compatibility. If your report is
        still dependent on genshi, implement the method render_template in
        your custom report and call this method with the same arguments and
        return the value instead.
        """
        report_template = MarkupTemplate(template_string)

        # Since Genshi >= 0.6, Translator requires a function type
        report_template.filters.insert(
            0, Translator(lambda text: translator(text))
        )

        stream = report_template.generate(**localcontext)

        return stream.render('xhtml').encode('utf-8')

    @classmethod
    def jinja_loader_func(cls, name):
        """
        Return the template from the module directories using the logic
        below:

        The name is expected to be in the format:

            <module_name>/path/to/template

        for example, if the account_reports module had a base template in
        its reports folder, then you should be able to use:

            {% extends 'account_reports/report/base.html' %}
        """
        module, path = name.split('/', 1)
        try:
            with file_open(os.path.join(module, path)) as f:
                return f.read()
        except IOError:
            return None

    @classmethod
    def get_jinja_filters(cls):
        """
        Returns filters that are made available in the template context.
        By default, the following filters are available:

        * dateformat: Formats a date using babel
        * datetimeformat: Formats a datetime using babel
        * currencyformat: Formats the given number as currency
        * modulepath: Returns the absolute path of a file inside a
            tryton-module (e.g. sale/sale.css)

        For additional arguments that can be passed to these filters,
        refer to the Babel `Documentation
        <http://babel.edgewall.org/wiki/Documentation>`_.
        """

        def module_path(name):
            module, path = name.split('/', 1)
            with file_open(os.path.join(module, path)) as f:
                return 'file://' + f.name

        return {
            'dateformat': partial(format_date, locale=Transaction().language),
            'datetimeformat': partial(
                format_datetime, locale=Transaction().language
            ),
            'currencyformat': partial(
                format_currency, locale=Transaction().language
            ),
            'modulepath': module_path
        }

    @classmethod
    def get_environment(cls):
        """
        Create and return a jinja environment to render templates

        Downstream modules can override this method to easily make changes
        to environment
        """
        env = Environment(loader=FunctionLoader(cls.jinja_loader_func))
        env.filters.update(cls.get_jinja_filters())
        return env

    @classmethod
    def render_template(cls, template_string, localcontext, translator):
        """
        Render the template using Jinja2
        """
        env = cls.get_environment()

        # Update header and footer in context
        company = localcontext['company']
        localcontext.update({
            'header': env.from_string(company.header_html or ''),
            'footer': env.from_string(company.footer_html or ''),
        })
        report_template = env.from_string(template_string.decode('utf-8'))
        return report_template.render(**localcontext).encode('utf-8')

    @classmethod
    def weasyprint(cls, data, options=None):
        return weasyprint.HTML(string=data).write_pdf()

    @classmethod
    def wkhtml_to_pdf(cls, data, options=None):
        """
        Call wkhtmltopdf to convert the html to pdf
        """
        with tempfile.NamedTemporaryFile(
                suffix='.html', prefix='trytond_', delete=False
        ) as source_file:
            file_name = source_file.name
            source_file.write(data)
            source_file.close()

            # Evaluate argument to run with subprocess
            args = 'wkhtmltopdf'
            # Add Global Options
            if options:
                for option, value in options.items():
                    args += ' --%s' % option
                    if value:
                        args += ' "%s"' % value

            # Add source file name and output file name
            args += ' %s %s.pdf' % (file_name, file_name)
            # Execute the command using executor
            execute(args)
            return open(file_name + '.pdf').read()
