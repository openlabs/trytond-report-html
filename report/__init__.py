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

import pdfkit
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

        # Convert to str as buffer from DB is not supported by StringIO
        report_content = (str(report.report_content) if report.report_content
            else False)

        if not report_content:
            raise Exception('Error', 'Missing report file!')

        # Since Genshi >= 0.6, Translator requires a function type
        translator = Translator(lambda text: translate(text))

        report_template = MarkupTemplate(report_content)
        report_template.filters.insert(0, translator)

        localcontext['records'] = records
        stream = report_template.generate(**localcontext)

        result = stream.render('xhtml').encode('utf-8')

        output_format = report.extension or report.template_extension
        if output_format in ('pdf',):
            result = cls.wkhtml_to_pdf(result)

        # Check if the output_format has a different extension for it
        oext = FORMAT2EXT.get(output_format, output_format)
        return (oext, result)

    @classmethod
    def wkhtml_to_pdf(cls, data, options=None):
        """
        Call wkhtmltopdf to convert the html to pdf
        """
        with tempfile.TemporaryFile(prefix='trytond_') as file:
            file.write(data)
            return pdfkit.from_file(file, False, options=options)
