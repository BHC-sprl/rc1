from xmlrpclib import ServerProxy
import csv
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta 
import re
import sys, os
username = "admin"
pwd = "admin"
dbname = "trad"

sock_common = ServerProxy("http://localhost:8069/xmlrpc/common")
uid = sock_common.login(dbname, username, pwd)

sock = ServerProxy("http://localhost:8069/xmlrpc/object")
reader = csv.reader(open('product.category.csv','rb'),delimiter=';')
x = 1 
for row in reader:
	print x
	x+=1
	if row[0] == 'name':
		continue
	else:
		data= {}
		data['name'] = row[0].decode('latin-1')
		if row[1]:
			parent=row[1].decode('latin-1')
			args2 = [('name','=', parent.decode('latin-1'))] 	
			account_parent = sock.execute(dbname, uid,pwd, 'product.category','search',args2)
			data['parent_id'] = account_parent[0]
			
		if row[2]:
			if row[2]=='normal':
				data['type'] = 'normal'
			else:
				data['type'] = 'view'
		if row[3]:
			parent2=row[3].decode('latin-1')
			print "p",parent2			
			args3 = [('name','=', parent2.decode('latin-1'))] 
			print "a",args3			
			account_parent2 = sock.execute(dbname, uid,pwd, 'product.category.type','search',args3)	
			print "aa",account_parent2[0]			
			data['prod_categ_type_id'] = account_parent2[0]

		if row[4]:
			data['code'] = row[4]


        print "data",data
        comp = sock.execute(dbname, uid,pwd, 'product.category','create', data)	

