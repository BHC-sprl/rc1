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

class product_template(osv.osv):
    _inherit = 'product.template'    

    def _product_available(self, cr, uid, ids, name, arg, context=None):
        res = dict.fromkeys(ids, 0)
        for product in self.browse(cr, uid, ids, context=context):
            res[product.id] = {
                "dep_gaillette": sum([p.dep_gaillette for p in product.product_variant_ids]),
                "oncallqty": sum([p.oncallqty for p in product.product_variant_ids]),    
                "qty_production": sum([p.qty_production for p in product.product_variant_ids]),  
                "qty_waiting": sum([p.qty_waiting for p in product.product_variant_ids]),  
                'qty_reserved_production': sum([p.qty_reserved_production for p in product.product_variant_ids]),     
                                                                                 
            }
        return res


    def _colis_available(self, cr, uid, ids, name, arg, context=None):
        res = dict.fromkeys(ids, 0)
        for product in self.browse(cr, uid, ids, context=context):
            res[product.id] = {
                'qty_available_colis': sum([p.qty_available_colis for p in product.product_variant_ids]), 
                'incoming_qty_colis': sum([p.incoming_qty_colis for p in product.product_variant_ids]),      
                'outgoing_qty_colis': sum([p.outgoing_qty_colis for p in product.product_variant_ids]), 
                'virtual_available_colis': sum([p.virtual_available_colis for p in product.product_variant_ids]),                
                'oncallqty_colis': sum([p.oncallqty_colis for p in product.product_variant_ids]), 
                'dep_gaillette_colis': sum([p.dep_gaillette_colis for p in product.product_variant_ids]),     
                'qty_production_colis': sum([p.qty_production_colis for p in product.product_variant_ids]), 
                'qty_reserved_production_colis': sum([p.qty_reserved_production_colis for p in product.product_variant_ids]),    
                'qty_waiting_colis': sum([p.qty_waiting_colis for p in product.product_variant_ids]),
                                                                                 
            }
        return res 

    _columns = {
        'dep_gaillette': fields.function(_product_available, multi='dep_gaillette',type='float', string='Dep. Gaillette'),
        'oncallqty': fields.function(_product_available, type='float', multi='dep_gaillette',string='On call'),         
        'qty_production': fields.function(_product_available, type='float',  multi='dep_gaillette',string='In Production'),
        'qty_waiting': fields.function(_product_available, type='float', multi='dep_gaillette',string='Waiting'),
        'qty_reserved_production': fields.function(_product_available, multi='dep_gaillette',type='float', string='Reserved Production'),   
        
        'qty_available_colis': fields.function(_colis_available, type='float',  multi='qty_available_colis', string='Colis Qty Available'),  
        'incoming_qty_colis': fields.function(_colis_available, type='float', multi='qty_available_colis',string='Colis Incoming'),      
        'outgoing_qty_colis': fields.function(_colis_available, type='float', multi='qty_available_colis',string='Colis Outgoing'), 
        'virtual_available_colis': fields.function(_colis_available, type='float', multi='qty_available_colis',string='Colis Virtual Available '),                 
        'oncallqty_colis': fields.function(_colis_available, type='float', multi='qty_available_colis',string='Colis On call'),  
        'dep_gaillette_colis': fields.function(_colis_available, type='float', multi='qty_available_colis',string='Colis Dep. Gaillette'),      
        'qty_production_colis': fields.function(_colis_available, type='float', multi='qty_available_colis',string='Colis In Production'), 
        'qty_reserved_production_colis': fields.function(_colis_available, type='float', multi='qty_available_colis',string='Colis Reserved Production'),    
        'qty_waiting_colis': fields.function(_colis_available, type='float', multi='qty_available_colis',string='Colis Waiting'),
        'state': fields.selection([('unknow','Unknow'),
            ('draft', 'In Development'),
            ('sellable','Normal'),
            ('end','End of Lifecycle'),
            ('obsolete','Obsolete')], 'Status'),
        
                               
    }

product_template()

 
class product_product(osv.osv):
    _inherit = 'product.product'
    
    def _colis_available(self, cr, uid, ids, field_names=None, arg=False, context=None):
        res = {}
        prod =self.browse(cr, uid,ids)
        for p in prod:
            res[p.id] = {}
        for p in prod:
            carton = p.carton
            if carton > 0:
                res[p.id]['qty_available_colis'] =  math.ceil(float(p.qty_available)/float(carton))  
                res[p.id]['incoming_qty_colis'] = math.ceil(float(p.incoming_qty)/float(carton))  
                res[p.id]['outgoing_qty_colis'] = math.ceil(float(p.outgoing_qty)/float(carton))
                res[p.id]['virtual_available_colis'] = math.ceil(float(p.virtual_available)/float(carton))                 
                res[p.id]['oncallqty_colis'] =  math.ceil(float(p.oncallqty)/float(carton))
                res[p.id]['dep_gaillette_colis'] = math.ceil(float(p.dep_gaillette)/float(carton))     
                res[p.id]['qty_production_colis'] = math.ceil(float(p.qty_production)/float(carton))
                res[p.id]['qty_reserved_production_colis'] = math.ceil(float(p.qty_reserved_production)/float(carton))
                res[p.id]['qty_waiting_colis'] = math.ceil(float(p.qty_waiting)/float(carton))
            else:
                res[p.id]['qty_available_colis'] =  0  
                res[p.id]['incoming_qty_colis'] = 0  
                res[p.id]['outgoing_qty_colis'] = 0
                res[p.id]['virtual_available_colis'] =  0                
                res[p.id]['oncallqty_colis'] =  0
                res[p.id]['dep_gaillette_colis'] = 0     
                res[p.id]['qty_production_colis'] = 0
                res[p.id]['qty_reserved_production_colis'] = 0
                res[p.id]['qty_waiting_colis'] = 0                    
                
        return res
           
    def _get_domain_locations_gailette(self, cr, uid, ids, context=None):
        location_ids = []
        ware_ids =self.pool.get('stock.warehouse').search(cr, uid,[])
        if ware_ids:
            location = self.pool.get('stock.warehouse').browse(cr, uid, ware_ids[0])
            location_gail_id = location.lot_gaillette_id and location.lot_gaillette_id.id or None                    
            location_ids.append(location_gail_id)

        operator = context.get('compute_child', True) and 'child_of' or 'in'
        domain = context.get('force_company', False) and ['&', ('company_id', '=', context['force_company'])] or []
        return (                                                                                                                                                                                               
            domain + [('location_id', operator, location_ids)],
            domain + ['&', ('location_dest_id', operator, location_ids), '!', ('location_id', operator, location_ids)],
            domain + ['&', ('location_id', operator, location_ids), '!', ('location_dest_id', operator, location_ids)]
        )

    def _get_domain_locations_oncallqty(self, cr, uid, ids, context=None):
        location_ids = []
        ware_ids =self.pool.get('stock.warehouse').search(cr, uid,[])
        if ware_ids:
            location = self.pool.get('stock.warehouse').browse(cr, uid, ware_ids[0])
            location_id = location.lot_oncall_id and location.lot_oncall_id.id or None
            location_ids.append(location_id)

        operator = context.get('compute_child', True) and 'child_of' or 'in'
        domain = context.get('force_company', False) and ['&', ('company_id', '=', context['force_company'])] or []
        return (                                                                                                                                                                                               
            domain + [('location_id', operator, location_ids)],
            domain + ['&', ('location_dest_id', operator, location_ids), '!', ('location_id', operator, location_ids)],
            domain + ['&', ('location_id', operator, location_ids), '!', ('location_dest_id', operator, location_ids)]
        )    
    
    def _product_available(self, cr, uid, ids, field_names=None, arg=False, context=None):
        res = super(product_product, self)._product_available(cr, uid, ids, field_names=field_names, arg=arg,context=context)       
        context = context or {}
        field_names = field_names or []
        domain_products = [('product_id', 'in', ids)]

       # for gailette
        domain_quant_gail = self._get_domain_locations_gailette(cr, uid, ids, context)
        domain_quant_gail = domain_quant_gail[0]

        domain_quant_gail += domain_products
        if context.get('lot_id') or context.get('owner_id') or context.get('package_id'):
            if context.get('lot_id'):
                domain_quant_gail.append(('lot_id', '=', context['lot_id']))
            if context.get('owner_id'):
                domain_quant_gail.append(('owner_id', '=', context['owner_id']))
            if context.get('package_id'):
                domain_quant_gail.append(('package_id', '=', context['package_id']))

        quants_gail = self.pool.get('stock.quant').read_group(cr, uid, domain_quant_gail, ['product_id', 'qty'], ['product_id'], context=context)
        quants_gail = dict(map(lambda x: (x['product_id'][0], x['qty']), quants_gail))


       #------------------
       # for on call qty
       #------------------
        domain_quants_oncallqty = self._get_domain_locations_oncallqty(cr, uid, ids, context)
        domain_quants_oncallqty = domain_quants_oncallqty[0]
        domain_quants_oncallqty += domain_products
        if context.get('lot_id') or context.get('owner_id') or context.get('package_id'):
            if context.get('lot_id'):
                domain_quants_oncallqty.append(('lot_id', '=', context['lot_id']))
            if context.get('owner_id'):
                domain_quants_oncallqty.append(('owner_id', '=', context['owner_id']))
            if context.get('package_id'):
                domain_quants_oncallqty.append(('package_id', '=', context['package_id']))
      
        quants_oncallqty = self.pool.get('stock.quant').read_group(cr, uid, domain_quants_oncallqty, ['product_id', 'qty'], ['product_id'], context=context)
        quants_oncallqty = dict(map(lambda x: (x['product_id'][0], x['qty']), quants_oncallqty))
       
        for id in ids:

            res[id]['dep_gaillette']= quants_gail.get(id, 0.0)
            res[id]['oncallqty']= quants_oncallqty.get(id, 0.0)          
            production_ids = self.pool.get('mrp.production').search(cr, uid,[('product_id','=',id),('state','in',('ready','in_production'))])
            ttl_production = 0                 
            if production_ids:
                production_brw= self.pool.get('mrp.production').browse(cr, uid, production_ids)
                for line in production_brw:
                    ttl_production= ttl_production + line.product_qty
            res[id]['qty_production'] = ttl_production
            
            waiting_ids = self.pool.get('sale.order.line').search(cr, uid,[('product_id','=',id),('state','in',('confirmed',))])                
            ttl_res_waiting = 0                 
            if waiting_ids:
                sale_brw= self.pool.get('sale.order.line').browse(cr, uid, waiting_ids)
                for line in sale_brw:
                    ttl_res_waiting= ttl_res_waiting + line.product_uom_qty
            res[id]['qty_waiting'] = ttl_res_waiting                 
        

            reserved_ids = self.pool.get('stock.move').search(cr, uid,[('production_id','!=',False),('product_id','=',id),('state','not in',('cancel','done'))])                
            ttl_res_production = 0                
            if reserved_ids:
                stock_brw= self.pool.get('stock.move').browse(cr, uid, reserved_ids)
                for line in stock_brw:
                    ttl_res_production= ttl_res_production + line.product_qty                       
            res[id]['qty_reserved_production'] = ttl_res_production  
            res[id]['virtual_available'] = res[id]['virtual_available'] + ttl_production - ttl_res_production + quants_gail.get(id, 0.0)                 
        return res
                    
    _columns = {
#        'name': fields.char('Name', required=True, translate=True, select=True),                 
        'remarque': fields.text('Rem.',),
        'quality': fields.char('Quality',size=512), 
        'largeur': fields.float('Largeur (Metres)'),
        'longueur': fields.float('Longueur (Metres)'),        
        'grammage' : fields.float('Grammage (gr/m2)'), 
        'recompute_grammage': fields.boolean('Compute gramamge', help="if check, we will recompute the value after each production order"),
        'oncallqty': fields.function(_product_available, type='float', multi='dep_gaillette',string='On call'),     
        'dep_gaillette': fields.function(_product_available, type='float', multi='dep_gaillette',string='Dep. Gaillette'),               
        'qty_production': fields.function(_product_available, type='float',  multi='dep_gaillette',string='In Production'), 
        'qty_reserved_production': fields.function(_product_available, multi='dep_gaillette',type='float', string='Reserved Production'),    
        'qty_waiting': fields.function(_product_available, type='float', multi='dep_gaillette',string='Waiting'),
        'virtual_available': fields.function(_product_available, multi='dep_gaillette',
            type='float',  digits_compute=dp.get_precision('Product Unit of Measure'),
            string='Forecasted Quantity',
            help="Forecast quantity (computed as Quantity On Hand "
                 "- Outgoing + Incoming)\n"
                 "In a context with a single Stock Location, this includes "
                 "goods stored in this location, or any of its children.\n"
                 "In a context with a single Warehouse, this includes "
                 "goods stored in the Stock Location of this Warehouse, or any "
                 "of its children.\n"
                "Otherwise, this includes goods stored in any Stock Location "
              "with 'internal' type."),
        
        'qty_available_colis': fields.function(_colis_available, type='float',  multi='qty_available_colis', string='Colis Qty Available'),  
        'incoming_qty_colis': fields.function(_colis_available, type='float', multi='qty_available_colis',string='Colis Incoming'),      
        'outgoing_qty_colis': fields.function(_colis_available, type='float', multi='qty_available_colis',string='Colis Outgoing'), 
        'virtual_available_colis': fields.function(_colis_available, type='float', multi='qty_available_colis',string='Colis Virtual Available '),                 
        'oncallqty_colis': fields.function(_colis_available, type='float', multi='qty_available_colis',string='Colis On call'),  
        'dep_gaillette_colis': fields.function(_colis_available, type='float', multi='qty_available_colis',string='Colis Dep. Gaillette'),      
        'qty_production_colis': fields.function(_colis_available, type='float', multi='qty_available_colis',string='Colis In Production'), 
        'qty_reserved_production_colis': fields.function(_colis_available, type='float', multi='qty_available_colis',string='Colis Reserved Production'),    
        'qty_waiting_colis': fields.function(_colis_available, type='float', multi='qty_available_colis',string='Colis Waiting'),
                                 
        'print_schema': fields.char('Print Schema',size=512),
        'pantone': fields.char('Pantone',size=512),    
        'type_crochet': fields.selection([('0','0'), ('c','C'),('e','E'),],'Type crochet', ),
        'print_step' : fields.float('Print Step (cm)'),  
        'christmaes_product' : fields.boolean('Christmaes'), 
        'farde_id': fields.many2one('product.farde', 'Farde'), 
        'ink_formula': fields.char('Ink Formula',size=512), 
        'sleeves_ids': fields.one2many('product.sleeve','prod_to_farde', 'Sleeves'),    
        'developpement': fields.float('Development', help="When the draw is reproduce ?"),
        'print_two_face': fields.boolean('Print two faces'), 
        'qty_to_invoice': fields.integer("Qty/unit inv."),      
        'relief': fields.selection([('m','M'),('x','X'), ('g','G'),('d','D'),('s','S'),],'Relief', ),     
        'predecoupe': fields.boolean('Predecoupe'),        
        'paletissation_id': fields.selection([('m','M'), ('g','G')],'Paletissation'),   
        'f_pliage_1': fields.float('Format Pliage (CmXCm)'),
        'f_pliage_2': fields.float('Format Pliage (CmXCm)'),  
        'nbr_color': fields.selection([('0','0'), ('1','1'),('2','2'),('3','3'),('4','4'),('5','5'),('6','6'),('7','7'),('8','8'),],'Number of color'),
        'purcent_inking': fields.char('% Inking', size=64),
        'date_obsolete':fields.date("Obsolete Date"),
        'fsc_product': fields.boolean('FSC'),        
#        'translation_ids': fields.one2many('ir.translation', 'product_id'),

        }
     
    def farde_id_change(self, cr, uid, ids, farde_id, context=None):
        context = context or {}
        value = {}
        if not farde_id:
            return {}
        if ids:
            farde = self.pool.get('product.farde').browse(cr,uid,farde_id)            
            for x in farde.sleeves_ids:
                val = {'name': x.id, 'prod_to_farde':ids[0],'default_code':x.default_code or ''}
                self.pool.get('product.sleeve').create(cr ,uid,val)
            value = {
                'infographie': farde.infographie or '',
            }

        return {'value': value}
           

                
product_product()

class product_farde(osv.osv):
    _name = "product.farde"
 
    _columns = {
        'code': fields.char('Code',size=64),
        'name': fields.char('Farde Name',size=512), 
        'infographie': fields.text('Infographie'),    
        'sleeves_ids': fields.many2many('product.product','farde_to_prod','farde_id','sleeve_id', 'Sleeves'),       

 }
    
    
    def write(self, cr, uid, ids, vals, context=None):
        if ids:                         
            res =super(product_farde, self).write(cr, uid, ids, vals, context=context)
            if vals.get('code'):
                farde_ids = self.search(cr,uid,[('code','=',vals.get('code'))])
                if farde_ids:                    
                    if ids != farde_ids:
                        raise osv.except_osv(_('Error!'), _('There is another Farde with the same code!.'))                                                          
        return res
    
    def create(self, cr, uid, vals, context=None):        
        if vals.get('code'):
            farde_ids = self.search(cr,uid,[('code','=',vals.get('code'))])
            if farde_ids:                    
                raise osv.except_osv(_('Error!'), _('There is another Farde with the same code!.')) 
               
        res =super(product_farde, self).create(cr, uid, vals, context=context)  
        return res     
            
    def unlink(self, cr, uid, ids, context=None):      
        for i in ids:
            prod_ids = self.pool.get('product.product').search(cr,uid,[('farde_id','=',i)])
            if prod_ids:                    
                raise osv.except_osv(_('Error!'), _("You can't delete this farde, there is a product linked to it!.")) 
               
        res =super(product_farde, self).unlink(cr, uid, ids, context=context)  
        return res       
        
product_farde()

class product_category(osv.osv):
    _inherit = "product.category"
       
    def write(self, cr, uid, ids, vals, context=None):
        if ids:                         
            res =super(product_category, self).write(cr, uid, ids, vals, context=context)
            if vals.get('code'):
                cat_ids = self.search(cr,uid,[('code','=',vals.get('code'))])
                if cat_ids:                    
                    if ids != cat_ids:
                        raise osv.except_osv(_('Error!'), _('There is another Category with the same code!.'))                                                          
        return res
    
    def create(self, cr, uid, vals, context=None):        
        if vals.get('code'):
            cat_ids = self.search(cr,uid,[('code','=',vals.get('code'))])
            if cat_ids:                    
                raise osv.except_osv(_('Error!'), _('There is another category with the same code!.')) 
               
        res =super(product_category, self).create(cr, uid, vals, context=context)  
        return res     
            
    def unlink(self, cr, uid, ids, context=None):      
        for i in ids:
            prod_ids = self.pool.get('product.product').search(cr,uid,[('categ_id','=',i)])
            if prod_ids:                    
                raise osv.except_osv(_('Error!'), _("You can't delete this category, there is a product linked to it!.")) 
               
        res =super(product_category, self).unlink(cr, uid, ids, context=context)  
        return res       
        
product_category()

class product_sleeve(osv.osv):
    _name = "product.sleeve"
 
    _columns = {
        'name': fields.many2one('product.product','product'),          
        'default_code': fields.char('Default Code',size=64),    
        'ink_formula': fields.char('Ink Formula',size=64),   
        'prod_to_farde': fields.many2one('product.product','product'),     

 }
    
    def unlink(self, cr, uid, ids, context=None):      
        for i in ids:
            print "i",i
            sleeve_ids = self.pool.get('product.sleeve').search(cr,uid,[('name','=',i)])
            if sleeve_ids:                    
                raise osv.except_osv(_('Error!'), _("You can't delete this sleeve, there is a farde linked to it!.")) 
               
        res =super(product_sleeve, self).unlink(cr, uid, ids, context=context)  
        return res 
        
product_sleeve()
'''
class product_palettisation(osv.osv):
    _name = "product.palettisation"
 
    _columns = {
        'name': fields.char('Code',size=64), 
        'description': fields.char('Description',size=512),      

 }
    
product_palettisation()
'''

