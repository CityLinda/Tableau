'''
Created on Mar 23, 2019

This script exports Tableau workbook view into csv format using Tableau API. It includes class Tableau_Exporter, Transformer_Column
Tableau_Exporter encapsulates session authentication, get resource_id(s) and export tableau view(s) methods
Transformer_Column encapsulates columns transformation.
This program depends upon a configuration file, the configuration has the workbook view name as key, customized column order as value.
a sample configuration file is attached

@author: Linda Li
'''

import argparse
import getpass
import logging
import tableauserverclient as TSC
from tableauserverclient.models import pagination_item
import csv
from configparser import ConfigParser
import sys
import os

#helper function

def export_csv(server, resource_id, fi_path, fi_name):
    
    	views = filter(lambda x: x.id == resource_id,
                   	TSC.Pager(server.views.get))
    	view = list(views).pop()
    	print(type(view))
  	 
    	(populate_func_name, option_factory_name, member_name, extension) = ('populate_csv','CSVRequestOptions','csv','csv')
    	populate = getattr(server.views, populate_func_name)
         	 
    	populate(view, None)
   	 
    	with open ((fi_path+'/'+fi_name), 'wb') as f:
        	if member_name == 'csv':
				f.writelines(getattr(view, member_name))
        	else:
				f.write(getattr(view, member_name))
   	 
class Tableau_Exporter():
    
	def __init__(self,server_url, user_name, password):
		
		self.server_url=server_url
    	self.user=user_name
    	self.password=password
   	 
    	self.server=TSC.Server(self.server_url, use_server_version=True)
  	 
   	 
	def get_session(self):

		tableau_auth = TSC.TableauAuth(self.user, self.password)
    	session=self.server.auth.sign_in(tableau_auth)
   	 
    	return session

	def get_resource_id(self, view_name):
		with self.get_session():
       	 
			for view in TSC.Pager(self.server.views):
				if view.name == view_name:
               	 
					print(view.name, view.id)
                	return view.id

	def export_view(self, view_name, fi_path, fi_name, new_columns, file_format='csv'):	 

		view_resource_id=self.get_resource_id(view_name)  # view_name is one value list
   	 
  	 
    	with self.get_session():
       	 
        	export_csv(self.server, view_resource_id, fi_path, fi_name+"tmp")
       	 
   	 
    	with open((fi_path+'/'+fi_name+"tmp"),'r') as infile, open((fi_path+'/'+fi_name),'w') as outfile:
       	 
        	writer=csv.DictWriter(outfile, fieldnames=new_columns, lineterminator='\n')
        	writer.writeheader()
        	for row in csv.DictReader(infile):
				writer.writerow(row)
           	 
    	os.remove(fi_path+'/'+fi_name+"tmp")
   	 
class Transformer_Column():

	def __init__(self):
		pass
    
	def get_csv_column(self, config_file, view_name):
   	 
   	 
		config=ConfigParser()
    	config.read(config_file)
    	get_view_string=config.get('section1',view_name)
    	column_list=get_view_string.split(',')
    	new_column_lst = []
   	 
    	for item in column_list:
       	 
        	item=item.strip()
        	new_column_lst.append(item)
       	 
	return new_column_lst
   	 
if __name__=="__main__":
    
    
	transformer=Transformer_Column()
 
	new_columns=transformer.get_csv_column(sys.argv[1],sys.argv[2]) #   
    
	tableau_exporter_to_csv=Tableau_Exporter(sys.argv[3],sys.argv[4],sys.argv[5])
    
	tableau_exporter_to_csv.export_view(sys.argv[6],sys.argv[7],sys.argv[8],new_columns)
    
	print('done')
	

