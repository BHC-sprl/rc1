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
from openerp import tools
from openerp.tools.translate import _
class invoice(osv.osv):
    _inherit = 'account.invoice'
    
    def _commission(self,cr,uid,ids,field,arg,context=None):
        uid=1
        res={}
        for invoice_id in self.browse(cr,uid,ids,context=context):
            amount=0
            #customer invoice
            pricelist_commission= invoice_id.partner_id and invoice_id.partner_id.pricelist_com_id and invoice_id.partner_id.pricelist_com_id.id or ''
            if not pricelist_commission:
                res[invoice_id.id]=amount            
            if invoice_id.type=='out_invoice' and invoice_id.representant_id:
                for i in invoice_id.invoice_line:
                    product=i.product_id and i.product_id.id or False
                    price = self.pool.get('product.pricelist').price_get(cr, uid, [pricelist_commission],product, i.quantity, invoice_id.representant_id.id, {
                        'uom': i.uos_id.id ,
                        'date': invoice_id.date_invoice,
                        'subtotal': i.price_subtotal,
                        })[pricelist_commission]
                    amount+=price
            #customer refund
            elif invoice_id.type=='out_refund' and invoice_id.representant_id:
                for i in invoice_id.invoice_line:
                    product=i.product_id and i.product_id.id or False
                    price = self.pool.get('product.pricelist').price_get(cr, uid, [pricelist_commission],product, i.quantity, invoice_id.representant_id.id, {
                        'uom': i.uos_id.id ,
                        'date': invoice_id.date_invoice,
                        'subtotal': i.price_subtotal,
                        })[pricelist_commission]
                    amount-=price
            #supplier invoice
            elif invoice_id.type=='in_invoice' and invoice_id.com==1:
                amount-=invoice_id.amount_total
            res[invoice_id.id]=amount
        return res
    
    _columns = {
        'representant_id': fields.related('partner_id', 'representant', type='many2one', relation='res.partner', string='Representative', store=True, readonly=True),
        'com': fields.boolean('Commissioning Supplier Invoice', help="If checked, the amount of this invoice will be subtract to the partner commissioning"),
        'amount_com': fields.function(_commission,store=True,type='float',string='Commission',readonly=True,method=True,help="Amount for this invoice or refunds"),

        }
invoice()

class product_pricelist(osv.osv):
    _inherit = "product.pricelist"

    def price_get_multi(self, cr, uid, ids, products_by_qty_by_partner, context=None):
        """multi products 'price_get'.
           @param ids:
           @param products_by_qty:
           @param partner:
           @param context: {
             'date': Date of the pricelist (%Y-%m-%d),}
           @return: a dict of dict with product_id as key and a dict 'price by pricelist' as value
        """
        if not ids:
            ids = self.pool.get('product.pricelist').search(cr, uid, [], context=context)
        results = {}
        for pricelist in self.browse(cr, uid, ids, context=context):
            subres = self._price_get_multi(cr, uid, pricelist, products_by_qty_by_partner, context=context)
            for product_id,price in subres.items():
                results.setdefault(product_id, {}) 
                results[product_id][pricelist.id] = price
        return results


    def _price_get_multi(self, cr, uid, pricelist, products_by_qty_by_partner, context=None):
        context = context or {}
        date = context.get('date') or time.strftime('%Y-%m-%d')

        products = map(lambda x: x[0], products_by_qty_by_partner)
        currency_obj = self.pool.get('res.currency')
        product_obj = self.pool.get('product.template')
        product_uom_obj = self.pool.get('product.uom')
        price_type_obj = self.pool.get('product.price.type')

        if not products:
            return {}

        version = False
        for v in pricelist.version_id:
            if ((v.date_start is False) or (v.date_start <= date)) and ((v.date_end is False) or (v.date_end >= date)):
                version = v
                break
        if not version:
            raise osv.except_osv(_('Warning!'), _("At least one pricelist has no active version !\nPlease create or activate one."))
        categ_ids = {}
        for p in products:
            categ = p.categ_id
            while categ:
                categ_ids[categ.id] = True
                categ = categ.parent_id
        categ_ids = categ_ids.keys()

        is_product_template = products[0]._name == "product.template"
        if is_product_template:
            prod_tmpl_ids = [tmpl.id for tmpl in products]
            prod_ids = [product.id for product in tmpl.product_variant_ids for tmpl in products]
        else:
            prod_ids = [product.id for product in products]
            prod_tmpl_ids = [product.product_tmpl_id.id for product in products]

        # Load all rules  
        cr.execute(
            'SELECT i.id '
            'FROM product_pricelist_item AS i '
            'WHERE (product_tmpl_id IS NULL OR product_tmpl_id = any(%s)) '
                'AND (product_id IS NULL OR (product_id = any(%s))) '
                'AND ((categ_id IS NULL) OR (categ_id = any(%s))) '
                'AND (price_version_id = %s) '
            'ORDER BY sequence, min_quantity desc',
            (prod_tmpl_ids, prod_ids, categ_ids, version.id))
        
        item_ids = [x[0] for x in cr.fetchall()]
        items = self.pool.get('product.pricelist.item').browse(cr, uid, item_ids, context=context)

        price_types = {}

        results = {}
        for product, qty, partner in products_by_qty_by_partner:
            uom_price_already_computed = False
            results[product.id] = 0.0
            price = False
            for rule in items:
                if rule.min_quantity and qty<rule.min_quantity:
                    continue
                if is_product_template:
                    if rule.product_tmpl_id and product.id != rule.product_tmpl_id.id:
                        continue
                    if rule.product_id:
                        continue
                else:
                    if rule.product_tmpl_id and product.product_tmpl_id.id != rule.product_tmpl_id.id:
                        continue
                    if rule.product_id and product.id != rule.product_id.id:
                        continue

                if rule.categ_id:
                    cat = product.categ_id    
                    while cat:
                        if cat.id == rule.categ_id.id:
                            break
                        cat = cat.parent_id
                    if not cat:
                        continue
                if pricelist.type == 'com':
                    price=context.get('subtotal')
                elif rule.base == -1:
                    if rule.base_pricelist_id:
                        price_tmp = self._price_get_multi(cr, uid,
                                rule.base_pricelist_id, [(product,
                                qty, False)], context=context)[product.id]
                        ptype_src = rule.base_pricelist_id.currency_id.id
                        uom_price_already_computed = True
                        price = currency_obj.compute(cr, uid,
                                ptype_src, pricelist.currency_id.id,
                                price_tmp, round=False,
                                context=context)
                elif rule.base == -2:
                    for seller in product.seller_ids:
                        if (not partner) or (seller.name.id != partner):
                            continue
                        qty_in_seller_uom = qty
                        from_uom = context.get('uom') or product.uom_id.id
                        seller_uom = seller.product_uom and seller.product_uom.id or False
                        if seller_uom and from_uom and from_uom != seller_uom:
                            qty_in_seller_uom = product_uom_obj._compute_qty(cr, uid, from_uom, qty, to_uom_id=seller_uom)
                        else:
                            uom_price_already_computed = True
                        for line in seller.pricelist_ids:
                            if line.min_quantity <= qty_in_seller_uom:
                                price = line.price
                else:
                    if rule.base not in price_types:
                        price_types[rule.base] = price_type_obj.browse(cr, uid, int(rule.base))
                    price_type = price_types[rule.base]

                    uom_price_already_computed = True
                    price = currency_obj.compute(cr, uid,
                            price_type.currency_id.id, pricelist.currency_id.id,
                            product_obj._price_get(cr, uid, [product],
                            price_type.field, context=context)[product.id], round=False, context=context)

                if price is not False:
                    price_limit = price
                    price = price * (1.0+(rule.price_discount or 0.0))
                    if rule.price_round:
                        price = tools.float_round(price, precision_rounding=rule.price_round)
                    price += (rule.price_surcharge or 0.0)
                    if rule.price_min_margin:
                        price = max(price, price_limit+rule.price_min_margin)
                    if rule.price_max_margin:
                        price = min(price, price_limit+rule.price_max_margin)
                break

            if price:
                if 'uom' in context and not uom_price_already_computed:
                    uom = product.uos_id or product.uom_id
                    price = product_uom_obj._compute_price(cr, uid, uom.id, price, context['uom'])

            results[product.id] = price
        return results
                            
    def price_get(self, cr, uid, ids, prod_id, qty, partner=None, context=None):
        product = self.pool.get('product.product').browse(cr, uid, prod_id, context=context)
        res_multi = self.price_get_multi(cr, uid, ids, products_by_qty_by_partner=[(product, qty, partner)], context=context)
        res = res_multi[prod_id]
        return res


product_pricelist()

class res_partner(osv.osv):
    _inherit = 'res.partner'
    
    def _moy_invoice(self,cr,uid,ids,field,arg,context=None):
        res={}
        sum=nb=moy=0
        for partner in self.browse(cr,uid,ids,context=context):
            for inv in partner.invoice_ids2:
                if inv.ttl_evaluation > 0:
                    sum=inv.ttl_evaluation
                    nb+=1
            if nb>0:
                moy=sum/nb
            res[partner.id]=moy
        return res

    def _commission(self,cr,uid,ids,field,arg,context=None):
        uid=1
        res={}
        for partner in self.browse(cr,uid,ids,context=context):
            amount=0
            #customer
            invoice_ids= self.pool.get('account.invoice').search(cr,uid,[('type','in',('out_invoice','out_refund')),('state','=','paid'),('representant_id','=',partner.id)])
            for i in self.pool.get('account.invoice').browse(cr,uid,invoice_ids):
                amount+=i.amount_com
            #supplier
            invoice_ids= self.pool.get('account.invoice').search(cr,uid,[('type','=','in_invoice'),('state','=','paid'),('partner_id','=',partner.id),('com','=',1)])
            for i in self.pool.get('account.invoice').browse(cr,uid,invoice_ids):
                amount+=i.amount_com
            res[partner.id]=amount
        return res
    
    def _commission_prev(self,cr,uid,ids,field,arg,context=None):
        uid=1
        res={}
        for partner in self.browse(cr,uid,ids,context=context):
            amount=0
            #customer invoice
            invoice_ids= self.pool.get('account.invoice').search(cr,uid,[('type','in',('out_invoice','out_refund')),('state','=','open'),('representant_id','=',partner.id)])
            for i in self.pool.get('account.invoice').browse(cr,uid,invoice_ids):
                amount+=i.amount_com
            res[partner.id]=amount
        return res
    
    def _get_id_so_line(self, cr, uid, ids, field_name, arg, context):
        res = {}
        lines_obj = self.pool.get('sale.order.line')
        so_obj = self.pool.get('sale.order')
        for i in ids:
            so_ids = so_obj.search(cr,uid,[('partner_id','=',i),('state','not in',('draft','cancel'))])
            if so_ids:
                line_ids = lines_obj.search(cr,uid,[('order_id','in',so_ids)])
                res[i]=line_ids
        return res

    
    _columns = {
        'is_representant': fields.boolean('Representative'),
        'closing':fields.text('Closing'),
        'invoicing_address':fields.many2one('res.partner','Invoicing Address'),
        'representant':fields.many2one('res.partner','Representative'),
        'activity_type':fields.char('Activity Type', size=256),
        'blocage':fields.boolean('Block',help="If checked, the supplier will not be took in the automatic payement"),
        'fsc':fields.boolean('FSC'),   
        'ref': fields.char('Contact Reference',size=64, select=1),
        'invoice_ids2': fields.one2many('account.invoice','partner_id','Invoices'),
        'invoice_rep_ids': fields.one2many('account.invoice','representant_id','Invoices',readonly=True),
        'moy_invoice_ids2': fields.function(_moy_invoice,type='float',string='Moyenne',method=True),
        'amount_com': fields.function(_commission,type='float',string='Commission',readonly=True,method=True,help="Base on the Commissioning Pricelist for the invoices and refunds in status 'Paid'.\nCalcul = ((customer invoices - customer refunds)base on the pricelist calcul) - Supplier commissioning invoices"),
        'amount_com_prev': fields.function(_commission_prev,type='float',string='Commission previsionnelle',readonly=True,method=True,help="Base on the Commissioning Pricelist for the invoices and refunds in status 'Open'.\nCalcul = (customer invoices - customer refunds)base on the pricelist calcul"),
        'partner_ids':fields.one2many('res.partner','representant','Customers',readonly=True),
        'pricelist_com_id': fields.many2one('product.pricelist', 'Commissioning Pricelist',),
        'so_lines':fields.function(_get_id_so_line,method=True,string="Sale Order Lines", type='many2many',relation='sale.order.line'),
        'remarque_transport': fields.text('Rem. Delivery'),
        'deliver_id': fields.many2one('res.partner', 'Deliver'),

    }
    
    _defaults={
        'opt_out':True,
        'notify_email':'none',       
#        'ref': lambda self, cr, uid, context: self.pool.get('ir.sequence').get(cr, uid, 'res.partner'),    
   
    }
    
    
    def _check_ref_key(self, cr, uid, ids, context=None):
        prod_obj = self.browse(cr, uid, ids)
        prod_ids = self.search(cr, uid, [('ref','=',prod_obj.ref)])   
        res = True
        if prod_ids:
            if ids == prod_ids:
                res = True
            elif ids not in prod_ids:
                res = False

        return res    
        
    _constraints = [(_check_ref_key, 'The partner ref must be unique', ['ref']) ]    
  #  _sql_constraints = [('ref_uniq1','unique(ref)', _('La reference doit etre unique!'))]

    def is_representant_change(self, cr, uid, ids, is_representant, context=None):
        context = context or {}
        warning = {}           
        if is_representant:
            value = {
                'is_representant': is_representant,
                'supplier':True,
            }           
  
        else:
            value = {
                'is_representant': is_representant,
            }             
            if ids:
                repre = self.search(cr,uid,[('representant','=',ids[0])])
                if repre:
                    value = {
                        'is_representant': True,
                    }                           
                    warning = {
                        'title': _('Warning !'),
                        'message' : _("Don't forget to unlink all the partner to this representant.\n") 
                    }
      
        return {'value': value, 'warning': warning}


    def copy(self, cr, uid, id, default=None, context=None):
        default['ref'] = ''
        return super(res_partner, self).copy(cr, uid, id, default=default, context=context)
    
res_partner()