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

import openerp.addons.decimal_precision as dp

import time 
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare

class stock_move(osv.osv):
    _inherit = "stock.move"


    def _prepare_procurement_from_move(self, cr, uid, move, context=None):
        print "_prepare_preocurement_from_move stock inherit"
        res=  super(stock_move, self)._prepare_procurement_from_move(cr, uid, move, context=context)
        print "res stock",res
        res['sale_line_id_parent']= move.procurement_id and move.procurement_id.sale_line_id and move.procurement_id.sale_line_id.id
        print "res stock2",res        
        return res
        
stock_move()