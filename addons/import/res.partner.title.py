# -*- coding: utf-8 -*-
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
reader = csv.reader(open('/usr/local/lib/python2.7/dist-packages/openerp-8.0rc1-py2.7.egg/openerp/addons/import/res.partner.title.csv','rb'),delimiter=';')  
x = 1 
chemin = 'erreur.csv'	
fichier = open(chemin, "wb")
for row in reader:
	print x
	x+=1
	if row[0] == 'name':
		continue
	else:
		data= {}
		data['name'] = row[0].decode('utf-8')
		data['shortcut'] = row[1].decode('utf-8')
		if row[2]:
			if row[2]=='True':
				print "if"
				data['domain']= 'partner'
			elif row[2]=='1':
				print "elid"
				data['domain']= 'partner'				
			else:
				print "else"
				data['domain'] = 'contact'
		try:
			print "d",data
			comp = sock.execute(dbname, uid,pwd, 'res.partner.title','create', data)	
		except:
			print 'except:', row
			fichier.write(str(row).decode('utf-8'))
			fichier.write("\n")	
			continue
				