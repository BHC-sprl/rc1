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
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from operator import itemgetter
import time
from openerp.osv import fields, osv

class res_partner(osv.osv):
    _inherit = 'res.partner'
    
    def _order_amount(self,cr,uid,ids,field,arg,context=None):
        res={}
        for i in ids:
            amount=0.0
            so_ids=self.pool.get('sale.order').search(cr,uid,[('partner_id','=',i)])
            for so in so_ids:
                data=self.pool.get('sale.order').browse(cr,uid,so)
                if data.state in ('progress','manual','shipping_except'):
                    amount+=data.amount_total
            res[i]=amount
        return res
    
    def _order_amount_all(self,cr,uid,ids,field,arg,context=None):
        res={}
        for i in self.browse(cr,uid,ids):
            amount=i.order_amount + i.credit
            res[i.id]=amount
        return res
    
    def _credit_debit_overdue_get(self,cr,uid,ids,field,arg,context=None):

        res = {}        
        date = datetime.today()
        for i in ids:
            ttl = 0        
            invoice_ids = self.pool.get('account.invoice').search(cr, uid, [('partner_id','=',i),('type','=','out_invoice'),('date_due','<',date),('state','not in',('draft','paid','cancel'))])      
    
            if invoice_ids:
                for x in self.pool.get('account.invoice').browse(cr ,uid,invoice_ids):
                    ttl = ttl + x.amount_total
            res[i] = ttl 
        return res
        


    
    _columns = {
        'order_amount': fields.function(_order_amount,type='float',string='Total Current Orders',help="Order confirmed and not done"),
        'order_all': fields.function(_order_amount_all,type='float',string='Total',help="Total receivable + Total current orders"),
        'credit_limit_pacarbel': fields.float('Credit Limit Pacarbel'),   
        'credit_overdue': fields.function(_credit_debit_overdue_get,type="float", string='Total Receivable Overdue', help="Total amount this customer owes you. The invoice date is over"),
             
    }
    
res_partner()