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
import datetime
import openerp.addons.decimal_precision as dp

import time 
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare

class procurement_order(osv.osv):
    _inherit = 'procurement.order'
    _columns = {
        'sale_line_id_parent':fields.many2one('sale.order.line', 'Sale line ID 2')
    }

    def make_mo(self, cr, uid, ids, context=None):
        res=  super(procurement_order, self).make_mo(cr, uid, ids, context=context)
        production_obj = self.pool.get('mrp.production')
        procurement_obj = self.pool.get('procurement.order')
        for procurement in procurement_obj.browse(cr, uid, ids, context=context):
            if procurement.sale_line_id_parent:
                if procurement.sale_line_id_parent.order_id:
                    if procurement.sale_line_id_parent.order_id.loading_date:
                        date = procurement.sale_line_id_parent.order_id.loading_date
                        date = datetime.datetime.strptime(date,"%Y-%m-%d %H:%M:%S")
                        decal = datetime.timedelta(days=-1)
                        date = date + decal                     
                        production_obj.write(cr, uid, res[procurement.id],{'date_planned':date})

        return res  
