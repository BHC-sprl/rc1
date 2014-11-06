# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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

import logging
from datetime import datetime
from dateutil.relativedelta import relativedelta
from operator import itemgetter
import time
from openerp import SUPERUSER_ID
from openerp import pooler, tools
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp.tools.float_utils import float_round
import openerp.addons.decimal_precision as dp

class account_payment_term_line(osv.osv):
    _inherit = "account.payment.term.line"
    _columns = {
        'month': fields.integer('Month',),
    }
account_payment_term_line()

class account_payment_term(osv.osv):
    _inherit = "account.payment.term"

    
    def compute(self, cr, uid, id, value, date_ref=False, context=None):
        
        if not date_ref:
            date_ref = datetime.now().strftime('%Y-%m-%d')
        date_tmp = datetime.now().strftime('%Y-%m-%d')
        pt = self.browse(cr, uid, id, context=context)
        amount = value
        result = []
        obj_precision = self.pool.get('decimal.precision')
        prec = obj_precision.precision_get(cr, uid, 'Account')
        for line in pt.line_ids:
            if line.value == 'fixed':
                amt = round(line.value_amount, prec)
            elif line.value == 'procent':
                amt = round(value * line.value_amount, prec)
            elif line.value == 'balance':
                amt = round(amount, prec)
            if amt:
                next_date = (datetime.strptime(date_ref, '%Y-%m-%d') + relativedelta(days=line.days))
                if line.days2 < 0:
                    next_first_date = next_date + relativedelta(day=1,months=1) #Getting 1st of next month
                    next_date = next_first_date + relativedelta(days=line.days2)
                if line.days2 > 0:
                    next_date += relativedelta(day=line.days2, months=1)
                if line.month and line.month !=0:
                    if line.days2 < 0:
                        next_date = datetime.strptime(date_ref, '%Y-%m-%d')                        
                        print "1",next_date
                        
                        next_first_date = next_date + relativedelta(day=1,months=1) #Getting 1st of next month
                        print "2", next_first_date
                        next_date = next_first_date + relativedelta(days=line.days2)
                        print "3",next_date
                       # date_tmp2 = datetime.now()#.strftime('%Y-%m-%d')
                       # tmp_month = date_tmp2.month
                       # tmp_month = tmp_month + line.month
                        print "type",type(next_date)
                        date_tmp = next_date + relativedelta(days=line.days, months=line.month)
                        print "4",date_tmp                          
                    else:                 
                        date_tmp = date_tmp.replace(day=line.days2)                                           
                    result.append( (date_tmp.strftime('%Y-%m-%d'), amt) )
                    amount -= amt
                else:
                    result.append( (next_date.strftime('%Y-%m-%d'), amt) )
                    amount -= amt

        amount = reduce(lambda x,y: x+y[1], result, 0.0)
        dist = round(value-amount, prec)
        if dist:
            result.append( (time.strftime('%Y-%m-%d'), dist) )
        return result
    
account_payment_term()