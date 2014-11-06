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

from operator import itemgetter
import time
from openerp.osv import fields, osv

class account_invoice(osv.osv):
    _inherit = 'account.invoice'
    
    def _ttl_evaluation(self, cr, uid, ids, name, arg, context=None):
        if not ids: 
            return {}
        res = {}         
        for x in self.browse(cr,uid, ids): 
            ttl = 0
            for y in x.evaluation_ids:
                ttl = ttl+ y.ttl_line
            res[x.id]=ttl
        return res
    
    
    def _get_evaluation(self, cr, uid, context=None):                                                                                                                                                                                           
        if context is None:
            context = {} 
        res = []
        search_eval_conf=self.pool.get('supplier.evaluation.configuration').search(cr, uid,[],)
        brw_eval_conf = self.pool.get('supplier.evaluation.configuration').browse(cr,uid,search_eval_conf,context)  
        for conf in brw_eval_conf:
            vals={
            'ponderation':conf.ponderation,
            'name':conf.name
            }          
            res.append([0,0,vals]) 
            

        return res    
    
    _columns = {
        'evaluation_ids':fields.one2many('supplier.evaluation', 'invoice_id','Evaluation'), 
        'ttl_evaluation': fields.function(_ttl_evaluation, string='Total Evaluation', type='float', store=True), 
    }
    
    _defaults = {
        'evaluation_ids': _get_evaluation,
    }
      
account_invoice()