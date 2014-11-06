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
    'name': 'Sale Confirmation',
    'version': '1.0',
    'category': 'Sale',
    'sequence': 50,
    'summary': 'Sale status to confirm',
    'description': """ 
Add a new state in the SO     """,
    'author': 'BHC',
    'images': [],
    'website': 'www.bhc.be',
    'depends': ['base','sale','sale_crm','sale_stock','warning'],
    'data': ['security/security.xml','sale_view.xml',],
    'installable': True,
}