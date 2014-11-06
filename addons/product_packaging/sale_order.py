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
import time
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare
import openerp.addons.decimal_precision as dp
from openerp import workflow
import math

    
class sale_order_line(osv.osv):
    _inherit = 'sale.order.line'
    _columns={
        'nbr_def_carton': fields.integer('Package in box by default'),
        'nbr_def_palette': fields.integer('Box on palette by default'),                
        'carton': fields.integer('Number of package'),
        'palette': fields.integer('Number of pallet'),     
        'qty_in_stock': fields.float('Qty in stock'),
        'pds_ttl': fields.float('Total Weight'),
        'pds_delivery':fields.float('Delivery Weight'),  
        'code':fields.char("Code",size=64),                 
              }
        
    def product_id_change_with_wh(self, cr, uid, ids, pricelist, product, qty=0,
            uom=False, qty_uos=0, uos=False, name='', partner_id=False,
            lang=False, update_tax=True, date_order=False, packaging=False, fiscal_position=False, flag=False, warehouse_id=False, context=None):

        context = context or {}
        product_obj=self.pool.get('product.product')
        res=super(sale_order_line, self).product_id_change_with_wh(cr, uid, ids, pricelist, product, qty,uom, qty_uos, uos, name, partner_id,
            lang, update_tax, date_order, packaging, fiscal_position, flag, warehouse_id,context)
        data=product_obj.browse(cr,uid,product)
#        print "prod_packa",data.carton
#        print "prod_packa",qty        
#        if data and qty and data.carton>0:
#            tmp=data.carton%qty
#            print "t",tmp
#            if tmp!=0:
#                if res['warning']:
#                    res['warning']['message']+=_('The quantity must be a multiple of product per package.')
#                else:
#                    res['warning'].update({
#                        'title': _('Error!'),
#                        'message' : _('The quantity must be a multiple of product per package.')
#                    })
#        if res['value']['product_uos_qty']:
#            qty_tot=res['value']['product_uos_qty']
#        else:
#            qty_tot=qty
#        if data.carton>0:
#            carton=math.ceil(float(qty_tot)/float(data.carton))
#        else:
#            carton=0
#        if data.palette>0:
#            palette=math.ceil(float(carton)/float(data.palette))
#        else:
#            palette=0
#        res['value'].update({'carton': carton,'palette': palette})
        if qty and data.carton > 0 and data.palette > 0:
            tmp_carton = math.ceil(float(qty)/float(data.carton))
            res['value']['carton'] = tmp_carton
            res['value']['palette'] = math.ceil(float(tmp_carton)/float(data.palette))             
        res['value']['nbr_def_carton'] = data.carton or 0
        res['value']['nbr_def_palette'] = data.palette or 0      
        res['value']['code'] = data.default_code or ''    
        res['value']['qty_in_stock'] = data.qty_available or 0
        res['value']['pds_ttl'] = (qty * data.weight_net) or 0
        if data.qty_available > qty:
            res['value']['pds_delivery'] =  (qty * data.weight_net) or 0
        else:
            res['value']['pds_delivery'] =  (data.weight_net * data.qty_available) or 0 
        res['value']['name'] = str(data.name.encode("utf-8")) or ''          
        if data.customer_code_ids:
            for line_code in data.customer_code_ids:
                if line_code.partner_id.id == partner_id:
                    res['value']['name']+= "\n Ref : " + str(line_code.name.encode("utf-8"))   
        if data.description_sale:
            res['value']['name']+= "\n" + str(data.description_sale.encode("utf-8"))     
        return res
     
    def onchange_carton(self, cr, uid, ids, carton, product,context):
        res={}
        context = context or {}
        product_obj=self.pool.get('product.product')
        #if palette:
        #    data=product_obj.browse(cr,uid,product)
        #    data=product_obj.browse(cr,uid,product)
#            tmp_carton = 0
#            if data.carton > 0: 
#                tmp_carton = palette * data.palette 
#                res['carton'] =  tmp_carton    
#            else:
#                res['carton'] =  tmp_carton                   
#            res['product_uom_qty'] = (data.carton * tmp_carton)
#            res['product_uos_qty'] = (data.carton * tmp_carton)               
        if carton:
            data=product_obj.browse(cr,uid,product)
            if data.carton > 0:          
                res['product_uom_qty'] = (data.carton * carton)
                res['product_uos_qty'] = (data.carton * carton)            
        
            if data.palette>0:
                res['palette']=math.ceil(float(carton)/float(data.palette))    
        return {'value': res}    
    
    def onchange_palette(self, cr, uid, ids, palette, product,context):
        res={}        
        context = context or {}
        product_obj=self.pool.get('product.product')
        if palette:
            data=product_obj.browse(cr,uid,product)
            tmp_carton = 0
            if data.carton > 0: 
                tmp_carton = palette * data.palette  
                res['carton'] =  tmp_carton    
            else:
                res['carton'] =  tmp_carton                   
            res['product_uom_qty'] = (data.carton * tmp_carton)
            res['product_uos_qty'] = (data.carton * tmp_carton)            
    
        return {'value': res}      
               
sale_order_line()