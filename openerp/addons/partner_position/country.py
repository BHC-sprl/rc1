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

class partner(osv.osv):
    _inherit = 'res.partner'
    
    def onchange_country(self, cr, uid, ids, country, context=None):
        value = {}
        if country:
            fis=self.pool.get('res.country').browse(cr,uid,country).pos_fis.id
            if fis:
                value['property_account_position'] = fis
            else:
                value['property_account_position'] = False
        else:
            value['property_account_position'] = False
        return {'value': value}
    
partner()

class country(osv.osv):
    _inherit = 'res.country'
    _columns = {
        'pos_fis': fields.many2one('account.fiscal.position','Fiscal Position',),
    }
country()

class fiscal(osv.osv):
    _inherit = 'account.fiscal.position'
    _columns = {
        'country': fields.one2many('res.country','pos_fis','Country',),
    }
fiscal()