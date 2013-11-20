#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''


    :copyright: (c) 2013 by Openlabs Technologies & Consulting (P) Ltd.
    :license: GPLv3, see LICENSE for more details

'''
import unittest
import tempfile

from pyPdf import PdfFileReader
import trytond.tests.test_tryton
from trytond.transaction import Transaction
from trytond.tests.test_tryton import POOL, USER, DB_NAME, CONTEXT
from trytond.pool import Pool

from openlabs_report_webkit import ReportWebkit


def register():
    """
    Register this report to a module
    """

    class UserReport(ReportWebkit):
        __name__ = 'res.user'

    Pool.register(
        UserReport,
        module='res', type_='report')


class ReportTestCase(unittest.TestCase):
    """
    Test the webkit reporting system
    """

    def setUp(self):
        register()

        trytond.tests.test_tryton.install_module('res')

        IRReport = POOL.get('ir.action.report')

        return
        with Transaction().start(DB_NAME, USER, context=CONTEXT):
            self.report_html, self.report_pdf = IRReport.create([{
                'name': 'HTML Report',
                'model': 'res.user',
                'report_name': 'res.user',
                'report_content_custom': 'Hello ${records[0].name}',
                'extension': 'html',
            }, {
                'name': 'PDF Report',
                'model': 'res.user',
                'report_name': 'res.user.pdf',
                'report_content_custom': 'Hello ${records[0].name}',
                'extension': 'pdf',
            }])

    def test_0010_render_report_xhtml(self):
        '''
        Render the report without PDF conversion
        '''
        UserReport = POOL.get('res.user', type='report')
        IRReport = POOL.get('ir.action.report')

        with Transaction().start(DB_NAME, USER, context=CONTEXT):
            IRReport.create({
                'name': 'HTML Report',
                'model': 'res.user',
                'report_name': 'res.user',
                'report_content': buffer('<h1>Hello, ${records[0].name}!</h1>'),
                'extension': 'html',
            })
            val = UserReport.execute([USER], {})
            self.assertEqual(val[0], u'html')
            self.assertEqual(
                str(val[1]), '<h1>Hello, Administrator!</h1>'
            )

    def test_0020_render_unicode(self):
        '''
        Render the report without PDF conversion but having unicode template
        '''
        UserReport = POOL.get('res.user', type='report')
        IRReport = POOL.get('ir.action.report')

        with Transaction().start(DB_NAME, USER, context=CONTEXT):
            IRReport.create({
                'name': 'HTML Report',
                'model': 'res.user',
                'report_name': 'res.user',
                'report_content': buffer("<h1>Héllø, ${data['name']}!</h1>"),
                'extension': 'html',
            })

            val = UserReport.execute([USER], {'name': u'Cédric'})
            self.assertEqual(val[0], u'html')
            self.assertEqual(
                str(val[1]), '<h1>Héllø, Cédric!</h1>'
            )

    def test_0030_render_pdf(self):
        '''
        Render the report in PDF
        '''
        UserReport = POOL.get('res.user', type='report')
        IRReport = POOL.get('ir.action.report')

        with Transaction().start(DB_NAME, USER, context=CONTEXT):
            IRReport.create({
                'name': 'HTML Report',
                'model': 'res.user',
                'report_name': 'res.user',
                'report_content': buffer("<h1>Héllø, ${data['name']}!</h1>"),
                'extension': 'pdf',
            })

            val = UserReport.execute([USER], {'name': u'Cédric'})
            self.assertEqual(val[0], u'pdf')

            with tempfile.TemporaryFile() as file:
                file.write(str(val[1]))
                pdf = PdfFileReader(file)

                # Probably the only thing you can check from a shitty PDF
                # format. God save Adobe and its god forsaken format.
                #
                # PDF IS EVIL
                self.assertEqual(pdf.getNumPages(), 1)


def suite():
    func = unittest.TestLoader().loadTestsFromTestCase
    suite = unittest.TestSuite()
    for testcase in (ReportTestCase,):
        suite.addTests(func(testcase))
    return suite


if __name__ == '__main__':
    suite = suite()
    unittest.TextTestRunner(verbosity=2).run(suite)
