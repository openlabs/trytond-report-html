# -*- coding: utf-8 -*-
'''


    :copyright: (c) 2013 by Openlabs Technologies & Consulting (P) Ltd.
    :license: GPLv3, see LICENSE for more details

'''
try:
    import cStringIO as StringIO
except ImportError:
    import StringIO
import time
import datetime
import tempfile
import subprocess

from genshi.template import MarkupTemplate
from trytond.pool import Pool
from trytond.transaction import Transaction
from trytond.report import Report, TranslateFactory, Translator, FORMAT2EXT


class ReportWebkit(Report):

    @classmethod
    def parse(cls, report, records, data, localcontext):
        '''
        Parse the report and return a tuple with report type and report.
        '''
        pool = Pool()
        User = pool.get('res.user')
        Translation = pool.get('ir.translation')

        localcontext['data'] = data
        localcontext['user'] = User(Transaction().user)
        localcontext['formatLang'] = lambda *args, **kargs: \
            cls.format_lang(*args, **kargs)
        localcontext['StringIO'] = StringIO.StringIO
        localcontext['time'] = time
        localcontext['datetime'] = datetime
        localcontext['context'] = Transaction().context

        translate = TranslateFactory(cls.__name__, Transaction().language,
            Translation)
        localcontext['setLang'] = lambda language: translate.set_language(
            language)
        localcontext['records'] = records

        # Convert to str as buffer from DB is not supported by StringIO
        report_content = (str(report.report_content) if report.report_content
            else False)

        if not report_content:
            raise Exception('Error', 'Missing report file!')

        result = cls.render_template(report_content, localcontext, translate)

        output_format = report.extension or report.template_extension
        if output_format in ('pdf',):
            result = cls.wkhtml_to_pdf(result)

        # Check if the output_format has a different extension for it
        oext = FORMAT2EXT.get(output_format, output_format)
        return (oext, result)

    @classmethod
    def render_template(cls, template_string, localcontext, translator):
        """

        """
        report_template = MarkupTemplate(template_string)

        # Since Genshi >= 0.6, Translator requires a function type
        report_template.filters.insert(
            0, Translator(lambda text: translator(text))
        )

        stream = report_template.generate(**localcontext)

        return stream.render('xhtml').encode('utf-8')

    @classmethod
    def wkhtml_to_pdf(cls, data, options=None):
        """
        Call wkhtmltopdf to convert the html to pdf
        """
        with tempfile.NamedTemporaryFile(
            suffix='.html', prefix='trytond_'
        ) as source_file:
            source_file.write(data)

            # Evaluate argument to run with subprocess
            args = ['wkhtmltopdf']
            # Add Global Options
            if options:
                for option, value in options.items():
                    args.append('--%s' % option)
                    if value:
                        args.append(value)
            # Add source file name and output file name
            args.extend([source_file.name, source_file.name + '.pdf'])

            # Run the above evaluated argument
            result = subprocess.Popen(args)
            # Wait until the above process is complete
            result.communicate()
            return open(source_file.name + '.pdf').read()
