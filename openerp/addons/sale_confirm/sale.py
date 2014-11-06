# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from lxml import etree
import math
import pytz
import re

import openerp
from openerp import SUPERUSER_ID
from openerp import pooler, tools
from openerp.osv import osv, fields
from openerp.tools.translate import _
from openerp import netsvc

import time 
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare

class sale_order(osv.osv):
    _inherit = 'sale.order'
    _columns = {
        'state': fields.selection([
            ('draft', 'Draft Quotation'),  
            ('toconfirm','To Confirm'),
            ('sent', 'Quotation Sent'),
            ('cancel', 'Cancelled'),
            ('waiting_date', 'Waiting Schedule'),
            ('progress', 'Sales Order'),
            ('manual', 'Sale to Invoice'),
            ('shipping_except', 'Shipping Exception'),
            ('invoice_except', 'Invoice Exception'),                   
            ('done', 'Done'),
            ], 'Status', readonly=True,help="Gives the status of the quotation or sales order.\
              \nThe exception status is automatically set when a cancel operation occurs \
              in the invoice validation (Invoice Exception) or in the picking list process (Shipping Exception).\nThe 'Waiting Schedule' status is set when the invoice is confirmed\
               but waiting for the scheduler to run on the order date.", select=True),
        'date_order': fields.date('Date', required=True, readonly=True, select=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)], 'toconfirm': [('readonly', False)]}),
        'user_id': fields.many2one('res.users', 'Salesperson', states={'draft': [('readonly', False)], 'sent': [('readonly', False)], 'toconfirm': [('readonly', False)]}, select=True, track_visibility='onchange'),
        'partner_id': fields.many2one('res.partner', 'Customer', readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)], 'toconfirm': [('readonly', False)]}, required=True, change_default=True, select=True, track_visibility='always'),
        'partner_invoice_id': fields.many2one('res.partner', 'Invoice Address', readonly=True, required=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)], 'toconfirm': [('readonly', False)]}, help="Invoice address for current sales order."),
        'partner_shipping_id': fields.many2one('res.partner', 'Delivery Address', readonly=True, required=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)], 'toconfirm': [('readonly', False)]}, help="Delivery address for current sales order."),
        'order_policy': fields.selection([
                ('manual', 'On Demand'),
            ], 'Create Invoice', required=True, readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)], 'toconfirm': [('readonly', False)]},
            help="""This field controls how invoice and delivery operations are synchronized."""),
        'pricelist_id': fields.many2one('product.pricelist', 'Pricelist', required=True, readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)], 'toconfirm': [('readonly', False)]}, help="Pricelist for current sales order."),
        'project_id': fields.many2one('account.analytic.account', 'Contract / Analytic', readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)], 'toconfirm': [('readonly', False)]}, help="The analytic account related to a sales order."),
        'order_line': fields.one2many('sale.order.line', 'order_id', 'Order Lines', readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)], 'toconfirm': [('readonly', False)]}),
    }
     
    def action_button_todraft(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'draft'})
        return True
    
    def action_button_toconfirm(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'toconfirm'})
        return True

sale_order()

class sale_order_line(osv.osv):
    _inherit = 'sale.order.line'
    
    _columns = {
        'product_uom_qty': fields.float('Quantity', digits=(10,0), required=True, readonly=True, states={'draft': [('readonly', False)]}),
    }
    
sale_order_line()