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
{
    'name': 'Sale Date',
    'version': '1.0',
    'category': 'Products',
    'sequence': 100,
    'summary': """Date in sale order""",
    'author': 'BHC',
    'website': 'www.bhc.be',
    'depends': ['base','base_setup',  'report', 'sale','sale_stock','mrp','sale_mrp','partner_order_amount','warning'],
    'data': ['sale_order_view.xml','sale_data.xml','security/ir.model.access.csv','views/sale_date_layouts_template.xml','views/report_saleorder.xml',],
    'installable': True,
}