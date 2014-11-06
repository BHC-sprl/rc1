# -*- encoding: utf-8 -*-
import xmlrpclib
import csv
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta 
import re
import sys, os
username = "admin"
pwd = "admin"
dbname = "trad"

sock_common = xmlrpclib.ServerProxy("http://localhost:8069/xmlrpc/common")
uid = sock_common.login(dbname, username, pwd)
sock = xmlrpclib.ServerProxy("http://localhost:8069/xmlrpc/object")
reader = csv.reader(open('product.product.csv','rb'),delimiter=';')
x = 1 	
for row in reader:
	if row[0] == 'Num':
		continue
	else:
		print x
		print "num", row[0]
		x+=1
		data={}
		datap={}
		datac={}
		tradfr={}
		tradnl={}
		#product_template
		'''
		if row[7]:
				if len(row[7])==11:
					ean= "00" + str(row[7])
				else:
					ean=row[7]
				datap['ean13'] = ean
	
		datap['so_minimal_qty'] = row[22]	
		datap['so_multi_qty'] = row[23]
		'''

		
		#product_product
		if row[0]:
			data['num_import'] = row[0]
		if row[1]:
			data['name'] = row[1].decode('latin-1')
		else:
			data['name'] = '??'			
		#recherche categ
		if row[2]:
			if row[2] =="sleeve":				
				args4 = [('name','=','SLEEVES')] 	
				print "r",row[2]	
				categ = sock.execute(dbname, uid,pwd, 'product.category','search',args4)
			else:
				args4 = [('code','=',row[2].decode('latin-1'))] 	
				print "rr",row[2]	
				categ = sock.execute(dbname, uid,pwd, 'product.category','search',args4)				
			data['categ_id'] = categ[0]	
		if row[3]=="1":
			data['sale_ok'] = True
		else:
			data['sale_ok'] = False
			
		if row[4] == "1":
			data['purchase_ok'] = True
		else:
			data['purchase_ok'] = False
		if row[5]:	
			data['type'] = row[5].decode('latin-1')
	
		#data['list_price'] = row[6].replace(',','.')
		#print "8",row[8]		
		#if row[8]:
	#		data['ean13'] = row[8].decode('latin-1')	
		if row[9] == "1":
			data['christmaes_product'] = True
		else:
			data['christmaes_product'] = False			
		if row[10]=="1":
			data['print_two_face'] = True
		else:
			data['print_two_face'] = False	

		if row[11]=="1":
			data['predecoupe'] = True
		else:
			data['predecoupe'] = False	

			
			
		if row[12]:
			data['developpement'] = row[12]
		if row[13]:
			data['relief'] = str(row[13]).lower()#Case()
#		if row[14]:
#			args5 = [('num_import','=',row[0])] 		
#			categ = sock.execute(dbname, uid,pwd, 'product.product','search',args5)
#			data['paletissation_id'] = categ[0]				
		if row[15]:
			data['pantone'] = row[15].decode('latin-1')
		if row[16]:
			data['print_schema'] = row[16].decode('latin-1')
		if row[18]:
			data['carton'] = row[18]
		if row[19]:
			data['palette'] = row[19]
		if row[20]:
			data['qty_to_invoice'] = row[20]	
		if row[21]:
			print "farde not implemented"		
		if row[22]:						
			data['description'] = row[22].decode('latin-1')
		if row[23]:
			data['remarque'] = row[23].decode('latin-1')
		if row[24]:
			data['quality'] = row[24].decode('latin-1')		
		if row[25]:
			if row[25] == 'make_to_order':
				procure_method='Make To Order'	
			args6 = [('name','=',procure_method)] 		
			route = sock.execute(dbname, uid,pwd, 'stock.location.route','search',args6)
			data['route_ids'] = [(6,0,route)]				
			
		if row[26]:
			if row[26] == 'produce':
				procure_method='Manufacture'
			elif row[26] =="buy":
				procure_method='Buy'					
			args7 = [('name','=',procure_method)] 		
			route = sock.execute(dbname, uid,pwd, 'stock.location.route','search',args7)
			data['route_ids'] = [(6,0,route)]				
		
		if row[27]:
			data['standard_price'] = row[27].replace(',','.')
		if row[28]:	
			data['produce_delay'] = row[28]
		

		#recherche uom
		if row[29]:
			print "29",row[29]			
			if row[29]=='RL':
				to_find = "Rouleau"
			elif row[29]=='P':
				to_find = "Unit(s)"		
			elif row[29] == 'KG':
				to_find = "kg"	
			elif row[29] == 'PT':
				to_find = "paquet"												
			args8 = [('name','=',to_find)] 		
			categ = sock.execute(dbname, uid,pwd, 'product.uom','search',args8)
			print "29_2", categ
			data['uom_po_id'] = categ[0]
			data['uom_id'] = categ[0]			
		if row[30]:
			data['description_purchase'] = row[30].decode('latin-1')
		if row[31]:	
			data['state'] = row[31]
				

		#data['volume'] = row[17].replace(',','.')	
		if row[32]:
			data['weight'] = row[32].replace(',','.')
		if row[33]:	
			data['weight_net'] = row[33].replace(',','.')
		if row[34]:
			data['largeur'] = row[34].replace(',','.')
		if row[35]:
			data['longueur'] = row[35].replace(',','.')	
		if row[36]:		
			data['grammage'] = row[36].replace(',','.')
		if row[37]=="1":
			data['recompute_grammage'] = True
		else:
			data['recompute_grammage'] = False	
		if row[38]:		
			data['type_crochet'] = str(row[38]).lower()					
		if row[39]:		
			data['print_step'] = row[39].replace(',','.')
		if row[40]:
			data['f_pliage_1'] = row[40].replace(',','.')
		if row[41]:
			data['f_pliage_2'] = row[41].replace(',','.')													
		#data['warranty'] = row[21].replace(',','.')
		if row[42]:	
			data['sale_delay'] = row[42].replace(',','.')	
		if row[43]:	
			data['produce_delay'] = row[43].replace(',','.')				
			
			
		#recherche uos
		if row[44]:
			if row[44]=='RL':
				to_find = "Rouleau"
			elif row[44]=='P':
				to_find = "Unit(s)"	
			elif row[44] == 'KG':
				to_find = "kg"								
			args9 = [('name','=',to_find)] 		
			categ = sock.execute(dbname, uid,pwd, 'product.uom','search',args9)		
			data['uos_id'] = categ[0]
		
		if row[45]:
			data['uos_coeff'] = row[45]	
		if row[46]:
			data['description_sale'] = row[46].decode('latin-1')
		if row[53]:
			print "date"
			#calcule sur les dates
			#date_old_call = datetime.strptime(row[53], "%d/%m/%Y")
			#date_old_call = date_old_call.strftime("%Y")+"-"+date_old_call.strftime("%m")+"-"+date_old_call.strftime("%d")	
			#data['date_obsolete'] = date_old_call
		'''
		#recherche income
		if row[28]:
			args4 = [('code','=',row[28])] 		
			account_parent = sock.execute(dbname, uid,pwd, 'account.account','search',args4)
			if not account_parent :
				fichieracc.write(str(x))
				fichieracc.write("\n")
			else:	 
				data['property_account_income'] = account_parent[0]	
		#recherche expense
		if row[29]:
			args5 = [('code','=',row[29])] 		
			account_parent = sock.execute(dbname, uid,pwd, 'account.account','search',args5)
			if not account_parent :
				fichieracc.write(str(x))
				fichieracc.write("\n")
			else:
				data['property_account_expense'] = account_parent[0]
		#recherche sales taxes
		if row[30]:
			args6 = [('description','=',row[30])] 		
			account_parent = sock.execute(dbname, uid,pwd, 'account.tax','search',args6)
			data['taxes_id'] = [(6,0,account_parent)]
		#recherche supplier taxes
		if row[31]:
			args7 = [('description','=',row[31])] 		
			account_parent = sock.execute(dbname, uid,pwd, 'account.tax','search',args7)
			data['supplier_taxes_id'] = [(6,0,account_parent)]
		#try:
		'''

		
							
		#comp = sock.execute(dbname, uid,pwd, 'product.template','create', data)
		#data['product_tmpl_id'] = comp
		if row[6]:	
			data['default_code'] = row[6].decode('latin-1')	
		print "d",data		
		comp3 = sock.execute(dbname, uid,pwd, 'product.product','create', data)	
		print "create"
		#create config for ean13/14
		if row[8] or row[17]:
			if len(row[8])==13:
				data_ean13 = {}
				data_ean13['name'] = row[8]
				data_ean13['product_id'] = comp3
				if row[17]:
					data_ean13['need_ean14'] = 1
					ean_c = sock.execute(dbname, uid,pwd, 'product.ean14','create', {'name':row[17],'product_id':comp3})
					comp5 = sock.execute(dbname, uid,pwd, 'product.product','write', [comp3],{'colis_ean13':ean_c})				
					data_ean13['ean14'] = ean_c
				ean13_create = sock.execute(dbname, uid,pwd, 'product.ean13','create', data_ean13)
				#write new value
				print "ean13_create",ean13_create
				print "comp3",comp3			
				comp4 = sock.execute(dbname, uid,pwd, 'product.product','write', [comp3],{'ean13':ean13_create})				
				print "comp4",comp4
		if row[51] and row[52]:
			args10 = [('ref','=',row[52].decode('latin-1'))] 		
			print "row[51",row[51]
			print "row[52",row[52]			
			categ = sock.execute(dbname, uid,pwd, 'res.partner','search',args10)		
			print "c", 	categ
			code_create = sock.execute(dbname, uid,pwd, 'customer.code','create', {'name':row[51],'partner_id':categ[0],'product_id':comp3})
		#except:
		#		print 'except:', row
		#		fichier.write(str(row).decode('latin-1'))
		#		fichier.write("\n")	
		#		continue
		
		if comp3:
			#traduction
			tradfr['lang'] = 'fr_BE'
			tradfr['src'] = row[1].decode('latin-1')
			tradfr['name'] = 'product.product,name'
			tradfr['res_id'] = comp3
			tradfr['value'] = row[1].decode('latin-1')
			tradfr['type'] = 'model'
			sock.execute(dbname, uid,pwd, 'ir.translation','create', tradfr)
	
		