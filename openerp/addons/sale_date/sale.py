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

class sale_order(osv.osv):
    _inherit = 'sale.order'
    
    def _ttl_palette(self,cr,uid,ids,field,arg,context=None):
        res={}
        if ids:            
            sale_nr=self.browse(cr,uid,ids)
            for s in sale_nr:
                tmp = 0
                if s.order_line:
                    for x in s.order_line:
                        if x.palette:
                            tmp = tmp + x.palette
                    res[s.id]= tmp

        return res 
    
    def _ttl_poids_net(self,cr,uid,ids,field,arg,context=None):
        res={}
        if ids:            
            sale_nr=self.browse(cr,uid,ids)
            for s in sale_nr:
                tmp = 0
                if s.order_line:
                    for x in s.order_line:
                        if x.pds_ttl:
                            tmp = tmp + (x.pds_ttl or 0)
                    res[s.id]= tmp

        return res  
    
    def _ttl_poids_brut(self,cr,uid,ids,field,arg,context=None):
        res={}
        if ids:            
            sale_nr=self.browse(cr,uid,ids)
            for s in sale_nr:
                tmp = 0
                tmp_pale = 0
                if s.order_line:
                    for x in s.order_line:
                        if x.pds_ttl:
                            tmp = tmp + x.pds_ttl
                  #      if x.palette:
                  #          if x.product_id and x.product_id.paletissation_id:
                  #              tmp_pale = tmp_pale + (x.product_id.paletissation_id.weight_net or 0)
                    res[s.id]= (tmp + tmp_pale)

        return res         
    
    _columns = {
        'loading_date': fields.datetime('Loading Date'),
        'desired_time':fields.datetime('Desired Time'),   
        'credit': fields.related('partner_id','credit',type="float", string='Credit', store=True),   
        'credit_overdue': fields.related('partner_id','credit_overdue',type="float", string='Credit Overdue', store=True),                
        'order_amount': fields.related('partner_id','order_amount',type="float",string="Total Current Orders",help="Order confirmed and not done", store=True),
        'order_all': fields.related('partner_id','order_all',type="float",string="Total",help="Total receivable + Total current orders", store=True),
        'credit_limit_pacarbel': fields.related('partner_id','credit_limit_pacarbel',type="float", string='Credit Limit Pacarbel', store=True),         
        'credit_limit': fields.related('partner_id','credit_limit',type="float", string='Credit Limit', store=True),   
        'deliver_id': fields.many2one('res.partner', 'Deliver'),   
        'ttl_palette':fields.function(_ttl_palette,type='float',string='Total Palette'),     
        'pds_net_ttl':fields.function(_ttl_poids_net,type='float',string='Total Poids Net'), 
        'pds_brut_ttl':fields.function(_ttl_poids_brut,type='float',string='Total Poids Brut'),       
        'country':fields.related('partner_shipping_id','country_id','name',type="char",size=64, string='Country', store=True),  
        'city':fields.related('partner_shipping_id','city',type="char",size=64, string='City', store=True),          
           
    }
    
    #definition pour le bouton
    def check_discount(self,cr,uid,ids,context=None):
        sale_br = self.browse(cr, uid, ids)        
        for sale in sale_br: 
            if sale.ttl_palette > 0:
                ctp = self.pool.get('customer.to.palette').search(cr, uid,[('name','=',sale.partner_id.id)])
                if ctp:                    
                    ptp = self.pool.get('palette.to.product').search(cr,uid, [('customer_to_pal_id','=',ctp[0]),('min','<=',sale.ttl_palette),('max','>=',sale.ttl_palette)])                    
                    if ptp:
                        for line in sale.order_line:
                            if line.product_id:
                                protpal = self.pool.get('product.to.palette').search(cr, uid, [('product_to_pal_id','=',ptp[0]),('name','=',line.product_id.id)])
                                if protpal:
                                    protpal_br = self.pool.get('product.to.palette').browse(cr, uid, protpal[0])
                                    self.pool.get('sale.order.line').write(cr, uid, line.id,{'discount':protpal_br.discount})
                                else:
                                    self.pool.get('sale.order.line').write(cr, uid, line.id,{'discount':0})                                    
                                    
                    else:
                        for line in sale.order_line:
                            if line.product_id:
                                self.pool.get('sale.order.line').write(cr, uid, line.id,{'discount':0})                                      
                                
                else:
                    for line in sale.order_line:
                        if line.product_id:
                            self.pool.get('sale.order.line').write(cr, uid, line.id,{'discount':0})                    
                    

        return True       
    
    def onchange_partner_id(self, cr, uid, ids, part, context=None):
        warning = {}    
        warning_msgs = False
        title = False                  
        if part:        
            part1 = self.pool.get('res.partner').browse(cr,uid, part)
            if part1.credit_limit_pacarbel > 0:
                tmp = part1.credit_limit_pacarbel - part1.order_all
                if tmp < 0:
                    warning_msgs = _('The Pacarbel credit limit is over')
                    title = _("Pacarbel Credit Limit !")                        

                    warning = {
                               'title': title,
                               'message' : warning_msgs
                            }
                    
            elif part1.credit_limit > 0:
                tmp = part1.credit_limit - part1.order_all
                if tmp < 0:
                    warning_msgs = _('The credit limit is over')
                    title = _("Credit Limit ! ")                        

                    warning = {
                               'title': title,
                               'message' : warning_msgs
                            }  
        
        result = super(sale_order, self).onchange_partner_id(cr, uid, ids, part, context)    
        if part:        
            part1 = self.pool.get('res.partner').browse(cr,uid, part)        
            result['value']['deliver_id'] = part1.deliver_id and part1.deliver_id.id or None            
        if result.get('warning',False):
            warning['title'] = title and title +' & '+ result['warning']['title'] or result['warning']['title']
            warning['message'] = warning_msgs and warning_msgs + ' ' + result['warning']['message'] or result['warning']['message']

        return {'value': result.get('value',{}), 'warning':warning}
              
        
                   
sale_order()

class sale_order_line(osv.osv):
    _inherit = 'sale.order.line'
    _columns = {
        'loading_date_confirmed': fields.datetime('Loading Date Confirmed'),
        'partial_loading_date_ids':fields.one2many('sale.order.line.date','partial_loading_date_id','Partial Loading Date'),       
        'desired_time':fields.datetime('Desired Time'),  
             

    }
           
    '''      
    def product_id_change(self, cr, uid, ids, pricelist, product, qty=0,
            uom=False, qty_uos=0, uos=False, name='', partner_id=False,
            lang=False, update_tax=True, date_order=False, packaging=False, fiscal_position=False, flag=False, context=None):
        
        res = super(sale_order_line, self).product_id_change(cr, uid, ids, pricelist, product, qty, uom, qty_uos, uos, name, partner_id,
            lang, update_tax, date_order, packaging, fiscal_position, flag, context)
        print "r",res
        if product:
            print "if"
            context_partner = {'lang': lang, 'partner_id': partner_id}
            product_obj = self.pool.get('product.product')            
            product_obj = product_obj.browse(cr, uid, product, context=context_partner)
            
            res['value']['qty_in_stock'] = product_obj.qty_available or 0
            res['value']['pds_ttl'] = (qty * product_obj.weight_net) or 0
            if product_obj.qty_available > qty:
                res['value']['pds_delivery'] =  (qty * product_obj.weight_net) or 0
            else:
                res['value']['pds_delivery'] =  (qty * product_obj.qty_available) or 0
                
        print "rrr",res                                    
        return res
        '''
            
            
sale_order_line()

class sale_order_line_date(osv.osv):
    _name = 'sale.order.line.date'
    _order = 'name'    
    _columns = {
        'partial_loading_date_id': fields.many2one('sale.order.line','Partial Loading Date'),
        'name':fields.datetime('Partial Loading Date'),
    }
                   
sale_order_line_date()

class customer_to_palette(osv.osv):
    _name = 'customer.to.palette'
    _order = 'name'    
    _columns = {
        'name': fields.many2one('res.partner','Partner', required=True),
        'palettes_ids':fields.one2many('palette.to.product', 'customer_to_pal_id',string="Palette"),
    }    
    

    def create(self, cr, uid, vals, context=None):
        ids=self.search(cr,uid,[('name','=',vals['name'])])
        if len(ids)>0:
            raise osv.except_osv(_('Error !'), _('You can have only one configuration per customer'))
        return super(customer_to_palette, self).create(cr, uid, vals, context)  
      
customer_to_palette()   

class palette_to_product(osv.osv):
    _name = 'palette.to.product'
    _order = 'min'    
    _columns = {
        'name':fields.char('Name',size=64),
        'customer_to_pal_id': fields.many2one('customer.to.palette','Partner'),
        'min':fields.integer('Number of Palette Min', required=True),
        'max':fields.integer('Number of Palette Max', required=True),        
        'product_ids':fields.one2many('product.to.palette', 'product_to_pal_id',string="Product"),        
    }    
    
    
    def _check_overlap(self, cursor, user, ids, context=None):
        for x in self.browse(cursor, user, ids, context=context):                     
            where = []
            if x.min:
                where.append("((max>='%s') or (max is null))" % (x.min,))
            if x.max:
                where.append("((min<='%s') or (min is null))" % (x.max,))
            cursor.execute('SELECT id ' \
                    'FROM palette_to_product ' \
                    'WHERE '+' and '.join(where) + (where and ' and ' or '')+
                        'customer_to_pal_id = %s ' \
                        'AND id <> %s', (
                            x.customer_to_pal_id.id,
                            x.id))
            if cursor.fetchall():
                return False
        return True

    _constraints = [
        (_check_overlap, 'You cannot have 2 Discount that overlap!',
            ['min', 'max'])
    ]

palette_to_product() 

class product_to_palette(osv.osv):
    _name = 'product.to.palette'
    _order = 'name'    
    _columns = {
        'product_to_pal_id': fields.many2one('palette.to.product','Palette'),                
        'name': fields.many2one('product.product','Product', required=True),
        'discount':fields.float('Discount (%)', required=True),
    }    
product_to_palette()  

class pricelist_updater(osv.osv):
    _name ="pricelist.updater"
    _columns={
        'name':fields.char('Name',size=64),
        'updater_line':fields.one2many('pricelist.updater.line','pricelist_updater_id' ,'Line'), 
        'pricelist': fields.many2one('product.pricelist', string="Pricelist", required=True),
        'version_pricelist':fields.many2one('product.pricelist.version',"PriceList Version",required=True)       
              
    }
    
    def write(self, cr, uid, ids, vals, context=None):
        res =super(pricelist_updater, self).write(cr, uid, ids,vals, context=context)
        print "res w",res  
        self.launch_updater(cr,uid,ids,context)       
        return res         
            
    def create(self, cr, uid, vals, context=None):
        
        res =super(pricelist_updater, self).create(cr, uid, vals, context=context)
        print "res c",res  
        self.launch_updater(cr,uid,res,context)       
        return res          
    #definition pour le bouton
    def launch_updater(self,cr,uid,ids,context=None):
        pricelist_br = self.browse(cr, uid, ids)        
        for liste in pricelist_br: 
            if liste.pricelist and liste.version_pricelist:
                #clean the pricelist item
                clean_ids =self.pool.get('product.pricelist.item').search(cr, uid, [('price_version_id','=',liste.version_pricelist.id)])
                self.pool.get('product.pricelist.item').unlink(cr ,uid, clean_ids)
                #create new one
                for line in liste.updater_line:
                    if line.name:
                        #create the product name for the sql request
                        tmp = ''
                        for car in line.name:
                            if car == '*':
                                tmp = tmp+ '_'
                            elif car == '#':
                                tmp = tmp + '[0-9]'
                            elif car == '@':
                                tmp = tmp + '(a|Z)'
                            elif car =='.':
                                break
                            else:
                                tmp = tmp + car
                        where = []
                        if tmp:
                            where.append("((name_template SIMILAR TO '%s'))" % (tmp,))
                        if line.lenght:
                            where.append("((longueur='%s'))" % (line.lenght,)) 
                        if line.width:  
                            where.append("((largeur='%s'))" % (line.width,))                             
                        if line.purcent_inking:  
                            where.append("((purcent_inking='%s'))" % (line.purcent_inking,))                             
                        if line.nbr_color:                                                  
                            where.append("((nbr_color='%s') )" % (line.nbr_color,))                                                              
                        print "w",where                           
                        cr.execute('SELECT id ' \
                                'FROM product_product ' \
                                'WHERE '+' and '.join(where) + (where and ' and ' or '')+
                                    'active')
                  

                        product_ids = [r[0] for r in cr.fetchall()]
                        #generate the line 
                        product_obj = self.pool.get("product.product").browse(cr,uid,product_ids)
                        for prod in product_obj:
                            vals ={
                                'min_quantity':line.qty or 1,
                                'base':1,
                                'price_surcharge':line.price or 1,
                                'product_id':prod.id,
                                'price_version_id':liste.version_pricelist.id,
                                
                            }
                            self.pool.get('product.pricelist.item').create(cr, uid, vals)

        return True     
    
pricelist_updater  

class pricelist_updater_line(osv.osv):
    _name ="pricelist.updater.line"
    _columns={
        'pricelist_updater_id': fields.many2one('pricelist.updater','Updater'), 
        'name':fields.char('Product', size=128),
        'lenght':fields.integer('Lenght'),
        'width':fields.integer('Width'),    
        'purcent_inking': fields.char('Inking %',size=64),
        'nbr_color': fields.selection([('0','0'), ('1','1'),('2','2'),('3','3'),('4','4'),('5','5'),('6','6'),('7','7'),('8','8'),],'Number of color'),   
        'qty':fields.integer('Quantity'),
        'price':fields.float('Price'),            
    }
    
pricelist_updater_line    
