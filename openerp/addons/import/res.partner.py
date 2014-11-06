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

pwd = "admin"
dbname = "trad"

sock_common = xmlrpclib.ServerProxy("http://localhost:8069/xmlrpc/common")
uid = sock_common.login(dbname, username, pwd)
sock = xmlrpclib.ServerProxy("http://localhost:8069/xmlrpc/object")
reader = csv.reader(open('res.partner.csv','rb'),delimiter=';')   
x = 1 
for row in reader:
	if row[0] == 'num':
		continue
	if not row[0]:
		continue
	print x
	print "row",row
	x+=1
#	if row[19]:
#		args = [('ref','=',row[19].decode('latin-1'))] 		
#		parent = sock.execute(dbname, uid,pwd, 'res.partner','search',args)
#		if parent:
#			continue	
	
	data={}
#	datac={}
	data['num_import'] = row[0]
	data['name'] = row[1].decode('latin-1')
	if row[2] =="1":
		print "c", row[2]
		data['is_company'] = True
	else:
		data['is_company'] = False
	#recherche parent
	if row[3]:
		args = [('ref','=',row[18].decode('latin-1'))] 		
		parent = sock.execute(dbname, uid,pwd, 'res.partner','search',args)
		if parent:
			data['parent_id'] = parent[0]
	#category
	
#	if row[4]:
#		categ_ids=[]
#		row[4]=row[4].replace('[','')
#		row[4]=row[4].replace(']','')
#		row[4]=row[4].split(',')
#		for i in row[4]:
#			args = [('name','=',i.decode('latin-1'))] 		
#			categ = sock.execute(dbname, uid,pwd, 'res.partner.category','search',args)
#			if categ:
#				categ_ids.append(categ[0])
#		data['category_id'] = [(6,0,categ_ids)]
		
	#adres_type
	if row[4]:
		data['type'] = row[4].lower() 		
	data['street'] = row[5].decode('latin-1')	
	data['street2'] = row[6].decode('latin-1')
	data['zip'] = row[7]
	data['city'] = row[8].decode('latin-1')

	if row[9]:
		args = [('code','=',row[9])] 		
		categ = sock.execute(dbname, uid,pwd, 'res.country','search',args)
		if categ:
			data['country_id']=categ[0]
		else:
			data['country_id']=False
	

	data['website'] = row[10].decode('latin-1')
	data['function'] = row[11].decode('latin-1')
	data['phone'] = row[12]
	data['mobile'] = row[13]
	data['fax'] = row[14].decode('latin-1')
	data['email'] = row[15]
	
	#pour le title
	if row[16]:
		print "row[16]",row[16]
		args = [('shortcut','=',row[16].decode('latin-1'))]
		print "args",args 		
		parent = sock.execute(dbname, uid,pwd, 'res.partner.title','search',args)
		print "p",parent
		if parent:
			print "if"
			data['title'] = parent[0]
			

	data['comment'] = row[17].decode('latin-1')
	data['ref'] = row[18].decode('latin-1')

	
	if row[19]:
		if row[19]=="FR" or 'fr_FR':
			data['lang'] = "fr_BE"
		elif row[19]=="NL" or "nl_BE":
			data['lang'] = "nl_BE"
		elif row[19]=="EN" or "en_US":
			data['lang'] = "en_US"
		elif row[19]=="DE" or "de":
			data['lang'] = "de"			
		else:
			data['lang'] = False
				
	#recherche pricelist sale
	if row[20]:
		args = [('name','=',row[20].decode('latin-1'))] 		
		parent = sock.execute(dbname, uid,pwd, 'product.pricelist','search',args)
		if parent:
			data['property_product_pricelist'] = parent[0]
	
	#recherche pricelist purchase
	if row[21]:
		args = [('name','=',row[21].decode('latin-1'))] 		
		parent = sock.execute(dbname, uid,pwd, 'product.pricelist','search',args)
		if parent:
			data['property_product_pricelist_purchase'] = parent[0]
		
	if row[22] =="1":
		data['customer'] = True
	else:
		data['customer'] = False		
	data['customer'] = row[22]
	
	if row[23] =="1":
		data['supplier'] = True
	else:
		data['supplier'] = False		


	data['opt_out'] = 1
	data['notify_email'] = 'none'
	#
	#recherche responsible payement
	if row[26]:
		args = [('name','=',row[26].decode('latin-1'))] 		
		parent = sock.execute(dbname, uid,pwd, 'res.users','search',args)
		data['payment_responsible_id'] = parent[0]

	if row[27]:
		if row[27]=='0':
			data['property_account_position'] = 1
		elif row[27]=='2':
			data['property_account_position'] = 2
		elif row[27]=='3':
			data['property_account_position'] = 3
	
	#verification sur la tva	
	if row[28]:
		print "rrrr",row[28]
		print "rrrr",row[29]		
		f= row[28]
		tmp = row[28][0:3]
		print "ss",tmp
		if tmp == "CHE":
			print "suisse", len(row[28])
			if len(row[28]) == 9:
				f="CH TVA "+str(row[28][3:9])
				print "f",f
			if len(row[28]) == 12:
				
				f="CHE-"+str(row[28][3:6])+"."+str(row[28][6:9])+"."+str(row[28][9:12])+" TVA"

		#CHE 501 174
		#CHE 108 072 920
		#CHE-123.456.788 TVA or CH TVA 123456:

		print "f",f
		data['vat'] = f#row[28]
	

	data['vat_subjected'] = row[29]

	#recherche receivable
#	if row[30]:
#		args = [('code','=',row[30].decode('latin-1'))] 		
#		parent = sock.execute(dbname, uid,pwd, 'account.account','search',args)
#		data['property_account_receivable'] = parent[0]
	#recherche payable
#	if row[31]:
#		args = [('code','=',row[31].decode('latin-1'))] 		
#		parent = sock.execute(dbname, uid,pwd, 'account.account','search',args)
#		data['property_account_payable'] = parent[0]
	
	#En attente 
#	if row[32]:
#		args = [('name','=',row[32].decode('latin-1'))] 		
#		parent = sock.execute(dbname, uid,pwd, 'account.payment.term','search',args)
#		data['property_payment_term'] = parent[0]
		
#	if row[33]:
#		args = [('name','=',row[33].decode('latin-1'))] 		
#		parent = sock.execute(dbname, uid,pwd, 'account.payment.term','search',args)
#		data['property_supplier_payment_term'] = parent[0]


	data['closing'] = row[34].decode('latin-1')
	if row[35]:
		data['sale_warn'] = "warning"
		data['sale_warn_msg'] = row[35].decode('latin-1')	
	if row[36]:
		data['invoice_warn'] = "warning"
		data['invoice_warn_msg'] = row[36].decode('latin-1')		
		

	data['activity_type']= row[38].decode('latin-1')
	if row[39]:
		data['blocage']= row[39]
	if row[40]:
		data['fsc'] = row[40]	
	if row[41]:
		data['is_representant'] = row[41]	
	
		

	
	#
	data['remarque_transport'] =row[43].decode('latin-1')	

	comp = sock.execute(dbname, uid,pwd, 'res.partner','create', data)
	print "create",comp
	#write necessaire si le partenaire est son propre representant	
	data2={}
	if row[37]:		
		args = [('num_import','=',int(row[37]))] 	
		parent = sock.execute(dbname, uid,pwd, 'res.partner','search',args)
		data2['invoicing_address'] = parent[0]	
	
	if row[42]:
		args = [('num_import','=',row[42])] 			
		parent = sock.execute(dbname, uid,pwd, 'res.partner','search',args)
		if parent:
			data2['representant'] = parent[0]	
		
	comp_write = sock.execute(dbname, uid,pwd, 'res.partner','write',comp, data2)