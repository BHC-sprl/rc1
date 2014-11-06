# -*- coding: utf-8 -*-
import xmlrpclib
import csv
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta 
import re
import sys, os
username = "admin"
#pwd = "admin"
#dbname = "phase2_V4"

#sock_common = xmlrpclib.ServerProxy("http://localhost:8069/xmlrpc/common")
#uid = sock_common.login(dbname, username, pwd)
#sock = xmlrpclib.ServerProxy("http://localhost:8069/xmlrpc/object")
#reader = csv.reader(open('/usr/lib/pymodules/python2.7/openerp/addons/import/res.partner.csv','rb'),delimiter=';')

pwd = "ljpFUBtn"
dbname = "trad"

sock_common = xmlrpclib.ServerProxy("http://localhost:8069/xmlrpc/common")
uid = sock_common.login(dbname, username, pwd)
sock = xmlrpclib.ServerProxy("http://localhost:8069/xmlrpc/object")
reader = csv.reader(open('/usr/local/lib/python2.7/dist-packages/openerp-8.0rc1-py2.7.egg/openerp/addons/import/res.bank.csv','rb'),delimiter=';')   
x = 1 
for row in reader:
    if row[0] == 'type':
        continue
    if not row[0]:
        continue
    print x
    print "r",row
    x+=1
 
    
    data={}

    if row[0] == "IBAN":
        data['state'] = "iban"
    else:
        data['state'] = "bank"        
    data['acc_number'] = row[1]#.decode('latin-1')
    #data['partner_id'] = row[2]

    #recherche partner
    if row[2]:
        args = [('ref','=',row[2].decode('latin-1'))]         
        partner = sock.execute(dbname, uid,pwd, 'res.partner','search',args)
        if partner:
            data['partner_id'] = partner[0]
    data['street'] = row[3].decode('latin-1')
    data['zip'] = row[4]
    data['city'] = row[5].decode('latin-1')
    if row[6]:
        args = [('code','=',row[6])]         
        categ = sock.execute(dbname, uid,pwd, 'res.country','search',args)
        if categ:
            data['country_id']=categ[0]
        else:
            data['country_id']=False   
            
    if row[9]:
        args = [('bic','=',row[9])]         
        categ = sock.execute(dbname, uid,pwd, 'res.bank','search',args)
        if categ:
            data['bank']=categ[0]
            data['bank_name']=row[8].decode('latin-1')   
            data['bank_bic']=row[9]               
        else:
            data['bank_name']=row[8].decode('latin-1')   
            data['bank_bic']=row[9]                     

    print "d",data
    comp = sock.execute(dbname, uid,pwd, 'res.partner.bank','create', data)
    print "create",comp
