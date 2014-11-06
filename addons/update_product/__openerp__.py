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

{
    'name': 'Product Update',
    'version': '0.1',
    'category': 'Product',
    'sequence': 100,
    'description': """Update the product view to be similar to the customer old software""",
    'author': 'BHC',
    'website': 'http://www.bhc.be',
    'depends':['base','product','category_type','purchase','stock','product_packaging','mrp','sale','access_right_pacarbel','account','stock_account'],       
    'data': ['security/ir.model.access.csv','product_view.xml','product_data.xml','stock_view.xml','stock_data.xml','sale_view.xml','purchase_view.xml','mrp_view.xml'],
    'demo_xml': [],
    'test':[],
    'installable': True,
    'active': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
