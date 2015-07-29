# -*- coding: utf-8 -*-
"""
    company.py

    :copyright: (c) 2015 by Openlabs Technologies & Consulting (P) Limited
    :license: BSD, see LICENSE for more details.
"""
from trytond.pool import PoolMeta
from trytond.model import fields

__metaclass__ = PoolMeta
__all__ = ['Company']


class Company:
    __name__ = 'company.company'

    header_html = fields.Text('Header Html')
    footer_html = fields.Text('Footer Html')
