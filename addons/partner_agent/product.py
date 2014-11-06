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

class product_template(osv.osv):
    _inherit = 'product.template'

    def write(self, cr, uid, ids, vals, context=None): 
        if ids:
            if vals.get('seller_ids'): 
                for v in vals['seller_ids']:
                    print "v",v
                    if v[0] == 0:
                        part = self.pool.get('res.partner').browse(cr, uid, v[2]['name'])
                        if part.fsc == True:
                            prod = self.pool.get('product.product')
                            prod_ids = prod.search(cr, uid, [('product_tmpl_id','=',ids[0])])
                            if prod_ids:
                                prod.write(cr, uid, prod_ids, {'track_all':True})  

        res = super(product_template, self).write(cr, uid, ids, vals, context=context)
        return res
 
 

    def create(self, cr, uid, vals, context=None):
        res = super(product_template, self).create(cr, uid, vals, context=context)        
        if vals.get('seller_ids'): 
            for v in vals['seller_ids']:
                if v[0] == 0:
                    part = self.pool.get('res.partner').browse(cr, uid, v[2]['name'])
                    if part.fsc == True:
                        prod = self.pool.get('product.product')
                        prod_ids = prod.search(cr, uid, [('product_tmpl_id','=',res)])
                        if prod_ids:
                            prod.write(cr, uid, prod_ids, {'track_all':True})  

      #  res = super(product_template, self).create(cr, uid, vals, context=context)
        return res
 
product_template()