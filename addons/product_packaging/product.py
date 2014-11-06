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
import math
import re

def is_pair(x):
    return not x%2

  

class product_product(osv.osv):
    
    def find_make_to_stock(self,cr ,uid, *args):
        procure_method='Make To Order'    
        args6 = [('name','=',procure_method)]         
        route = self.pool.get('stock.location.route').search(cr, uid, args6)
        return [(6,0,route)]  

    _inherit = 'product.product'
    _columns={
        'carton': fields.integer('Number of units per package'),
        'palette': fields.integer('Number of packages per pallet'),
        'infographie': fields.text('Graphics'),     
        'colis_ean13':fields.many2one('product.ean14','EAN Colis'),    
        'ean13': fields.many2one('product.ean13','EAN13 Barcode', help="International Article Number used for product identification."), 
        'customer_code_ids': fields.one2many('customer.code','product_id','Customer code',),                        
              }
    
    
    
    _defaults={
        'route_ids': find_make_to_stock,
        'list_price': 0,
    }
    
    def _check_ean_key(self, cr, uid, ids, context=None):
        super(product_product, self)._check_ean_key(cr, uid, ids, context=context)
        return True
    
    def _check_default_code_key(self, cr, uid, ids, context=None):
        prod_obj = self.browse(cr, uid, ids)
        prod_ids = self.search(cr, uid, [('default_code','=',prod_obj.default_code)])
        res = True
        if prod_ids:
            if ids == prod_ids:
                res = True
            elif ids not in prod_ids:
                res = False

        return res
        
    _constraints = [(_check_ean_key, 'You provided an invalid "EAN13 Barcode" reference. You may use the "Internal Reference" field instead.', ['ean13']),
                   (_check_default_code_key, 'The product default code must be unique', ['default_code']) ]
    
    
    #_sql_constraints = [
    #    ('ref_uniq', 'unique(default_code)', 'La référence du produit doit être unique!'),
    #]
    
    def name_search(self, cr, user, name='', args=None, operator='ilike', context=None, limit=100):
        super(product_product, self).name_search(cr, user, name='', args=None, operator='ilike', context=None, limit=100)
        if not args:
            args = [] 
        if name:
            ids = self.search(cr, user, [('default_code','=',name)]+ args, limit=limit, context=context)
            if not ids: 
                ids = self.search(cr, user, [('ean13','=',name)]+ args, limit=limit, context=context)
            #search on customer code
            if not ids and context.get('partner_id') :
                code_search_ids = self.pool.get('customer.code').search(cr, user, [('name','like',name), ('partner_id','=',context.get('partner_id'))], limit=limit)
                code_ids = self.pool.get('customer.code').browse(cr, user, code_search_ids, context=context)                              
                for code in code_ids:
                    ids.append(code.product_id.id)                
            if not ids: 
                # Do not merge the 2 next lines into one single search, SQL search performance would be abysmal
                # on a database with thousands of matching products, due to the huge merge+unique needed for the
                # OR operator (and given the fact that the 'name' lookup results come from the ir.translation table
                # Performing a quick memory merge of ids in Python will give much better performance
                ids = set(self.search(cr, user, args + [('default_code', operator, name)], limit=limit, context=context))
                if not limit or len(ids) < limit:
                    # we may underrun the limit because of dupes in the results, that's fine
                    limit2 = (limit - len(ids)) if limit else False
                    ids.update(self.search(cr, user, args + [('name', operator, name)], limit=limit2, context=context))
                ids = list(ids)
            if not ids: 
                ptrn = re.compile('(\[(.*?)\])')
                res = ptrn.search(name)
                if res: 
                    ids = self.search(cr, user, [('default_code','=', res.group(2))] + args, limit=limit, context=context)
        else:
            ids = self.search(cr, user, args, limit=limit, context=context)
        result = self.name_get(cr, user, ids, context=context)
        return result
    
    
    def ean13_change(self, cr, uid, ids, ean13, context=None):
        context = context or {}
        value = {}
        if not ean13:
            return {}
        code = self.pool.get('product.ean13').browse(cr,uid,ean13)            

        value = {
            'ean13': ean13 or None,
            'colis_ean13': code.ean14 or None,
            
        }

        return {'value': value}
  
    def write(self, cr, uid, ids, vals, context=None):
        if ids:
            prod =self.browse(cr, uid,ids[0])   
                                                      
            if vals.get('colis_ean13'):
                if prod.colis_ean13:
                    #modification d'un ean existant
                    self.pool.get('product.ean14').write(cr, uid, prod.colis_ean13.id, {'product_id': None})
                #ajout ean s'il n'y en avait pas 
                self.pool.get('product.ean14').write(cr, uid, vals.get('colis_ean13'), {'product_id':ids[0]}) 
            else:
                if prod.colis_ean13:
                    #retire l'ean s'il y en avait un avant
                    self.pool.get('product.ean14').write(cr, uid, prod.colis_ean13.id, {'product_id': None})    
                    
            if vals.get('ean13'):
                if prod.ean13:
                    #modification d'un ean existant
                    self.pool.get('product.ean13').write(cr, uid, prod.ean13.id, {'product_id': None})
                #ajout ean s'il n'y en avait pas 
                self.pool.get('product.ean13').write(cr, uid, vals.get('ean13'), {'product_id':ids[0]}) 
            else:
                if prod.ean13:
                    #retire l'ean s'il y en avait un avant
                    self.pool.get('product.ean13').write(cr, uid, prod.ean13.id, {'product_id': None})                              

        res =super(product_product, self).write(cr, uid, ids, vals, context=context)
        return res
    
    def create(self, cr, uid, vals, context=None):
        res =super(product_product, self).create(cr, uid, vals, context=context)
        prod =self.browse(cr ,uid, res)  
        if prod.farde_id:
            farde = self.pool.get('product.farde').browse(cr,uid,prod.farde_id.id)          
            for x in farde.sleeves_ids:
                val = {'name': x.id, 'prod_to_farde':prod.id,'default_code':x.default_code or ''}
                t = self.pool.get('product.sleeve').create(cr ,uid,val)         
        if prod.colis_ean13:
            self.pool.get('product.ean14').write(cr, uid, prod.colis_ean13.id, {'product_id':res})
        if prod.ean13:
            self.pool.get('product.ean13').write(cr, uid, prod.ean13.id, {'product_id':res})            
        return res    
   
    def copy(self, cr, uid, id, default=None, context=None):
        default['default_code'] = ''
        return super(product_product, self).copy(cr, uid, id, default=default, context=context)
   
   
product_product()

class product_ean13(osv.osv):
    _name = "product.ean13"
    _columns = {
        'name':fields.char('EAN 13', size=13),
        'product_id':fields.many2one('product.product', 'Product'),
        'need_ean14': fields.boolean("Need EAN 14 ?"),
        'ean14':fields.many2one('product.ean14','EAN 14'),        
    }
    
    def _check_ean_name_key(self, cr, uid, ids, context=None):
        prod_obj = self.browse(cr, uid, ids)
        prod_ids = self.search(cr, uid, [('name','=',prod_obj.name)])        
        res = True
        if prod_ids:
            if len(prod_ids)>1:
                return False

        return res        

    
        
    _constraints = [(_check_ean_name_key, 'EAN13 must be unique', ['name']),]
    
    def action_generate_ean(self, cr, uid, ids, *args):
        if ids:
            current = self.browse(cr, uid, ids[0])            
            vals = {}
            test = False
            new_ean = ''
            new_ean_14 = ''
            while test != True: 
                ref = self.pool.get('ir.sequence').get(cr, uid, 'product.ean13')
                sum=0
                for i in range(12):
                    if is_pair(i):
                        sum += int(ref[i])
                    else:
                        sum += 3 * int(ref[i])
                new_ean_cc = int(math.ceil(sum / 10.0) * 10 - sum)
                new_ean = ref + str(new_ean_cc)
                 
                #find if there is a doublo
                double = self.search(cr ,uid, [('name',"=",new_ean)])
                if not double:
                    #create ean14:
                    if current.need_ean14:
                        first_chiffre = "1"
                        sum=0
                        treize_chiffre = str(first_chiffre) + str(ref)    
                        for i in range(13):
                            if is_pair(i):
                                sum += int(treize_chiffre[i])
                            else:
                                sum += 3 * int(treize_chiffre[i])
                        new_ean_cc = int(math.ceil(sum / 10.0) * 10 - sum)
                        new_ean_14 = treize_chiffre + str(new_ean_cc)  
                        new_ean_14 = self.pool.get("product.ean14").create(cr,uid, {'name':new_ean_14})                     
                    test = True
            vals = {'name': new_ean, 'ean14': new_ean_14}
            self.write(cr, uid, ids[0], vals)

                             
        return True        
product_ean13() 


class product_ean14(osv.osv):
    _name = "product.ean14"
    _columns = {
        'name':fields.char('EAN 14', size=14),
        'product_id':fields.many2one('product.product', 'Product'),  
    }
          
product_ean14() 

class customer_code(osv.osv):    
    _name = "customer.code"
    _columns = {                    
        'partner_id':fields.many2one('res.partner','Partner',),
        'name':fields.char('Code',size=64),
        'product_id':fields.many2one('product.product','Product',),        
        }
        
customer_code()
