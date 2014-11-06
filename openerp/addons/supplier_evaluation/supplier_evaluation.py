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
from openerp.tools.translate import _

class supplier_evaluation(osv.osv):
    _name = 'supplier.evaluation'
    _columns = {
        'name':fields.char('Name',size=512, required=True,),
        'config_id':fields.many2one('supplier.evaluation.configuration','Configuration'),        
        'ponderation': fields.integer('Ponderation',required=True),        
        'cote': fields.integer('Cote'),
        'ttl_line': fields.integer('Line Total'),
        'invoice_id': fields.many2one('account.invoice','Evaluation'),
    }
    
    def onchange_cote(self, cr, uid, ids, cote,ponderation, context=None): 
        res = {} 
        warning = {}                                                                                                                                                              
        if cote and ponderation:
            if cote > 0 and cote < 5:
                multi = cote * ponderation 
                res['ttl_line']=multi       
            else:
                res['ttl_line']=0                 
                warning = {
                    'title': _('Error!'),
                    'message' : _("The cote must be between 1 and 4.\n")
                }    
        else:
            res['ttl_line']=0              
            warning = {
                'title': _('Error!'),
                'message' : _("The cote must be between 1 and 4.\n")
            }              
        #print "on change",res       
        #return {'value': {'ttl_line': res},'warning':warning}
        return {'value': res,'warning':warning}    
supplier_evaluation()

class supplier_evaluation_configuration(osv.osv):
    _name = 'supplier.evaluation.configuration'
    _columns = {
        'name':fields.char('Rule', size=512, required=True, translate=True), 
        'ponderation': fields.integer('Ponderation',required=True),
    }
supplier_evaluation_configuration()