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

class sale_order(osv.osv):
    _inherit = 'sale.order'

    _columns = {

        'representant_id': fields.related('partner_id', 'representant', type='many2one', relation='res.partner', string='Representative', store=True, readonly=True),
    }

    def onchange_partner_id(self, cr, uid, ids, part, context=None):
        res = super(sale_order, self).onchange_partner_id(cr, uid, ids,part,  context=context)
        if res['value']['partner_shipping_id']:
            part1 = self.pool.get('res.partner').browse(cr,uid, res['value']['partner_shipping_id'])
            if part1.invoicing_address:
                res['value']['partner_invoice_id'] = part1.invoicing_address.id
            else:
                add_def=self.pool.get('res.partner').search(cr,uid,[('id','=',part)])
                if add_def:
                    add_def_b=self.pool.get('res.partner').browse(cr,uid,add_def)
                    res['value']['partner_invoice_id'] = add_def_b[0].id
                
        return res

    def onchange_delivery_id(self, cr, uid, ids, company_id, partner_id, delivery_id, fiscal_position, context=None):  
        r = super(sale_order, self).onchange_delivery_id(cr, uid, ids, company_id, partner_id, delivery_id, fiscal_position, context=context)                                                                                                
        part = self.pool.get('res.partner').browse(cr, uid, delivery_id)
        if part.invoicing_address:
                r['value']['partner_invoice_id'] = part.invoicing_address
        else:
                r['value']['partner_invoice_id'] = partner_id          
        return r
    

sale_order()
