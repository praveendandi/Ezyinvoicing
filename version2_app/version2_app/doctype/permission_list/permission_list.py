# Copyright (c) 2023, caratred and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class PermissionList(Document):
	pass


@frappe.whitelist(allow_guest=True)
def migrate_user_role_per():
	print(",.,,,,,,,,,,,,,,,,,,,,,,,,,,,,,")
	get_role = frappe.db.get_list('Role','name')
	# if not frappe.db.exists("Role", {'role':'ezy-admin'}, cache=True):
	if not frappe.db.exists('Role',{"role_name":"ezy-admin"}):
		doc = frappe.get_doc({'doctype': 'Role',"role_name":"ezy-admin"})
		doc.insert()
		frappe.db.commit()
		parent_role = frappe.db.get_list('Roles Permission',{'select_role':'ezy-admin'},['select_role'])
		for i in parent_role:
			perm_list = frappe.db.get_list('Permission List',{'parent':i.select_role,'module':'Master Data','select_route':'User Management-Details','route_link':"home/users-details?"},['module','select_route','route_link','read','write','create','delete_perm','export']) 
			for each in perm_list:
				if frappe.db.exists({"doctype": "Permission List",'parent':i.select_role,"parentfield":"permission_list", "route_link": each.route_link, "module": each.module,"select_route":each.select_route,"parenttype":"Roles Permission"}):
				# if not frappe.db.exists({"doctype": "Permission List",'parent':i.select_role}):
					child_doc = frappe.get_doc({"doctype": "Permission List",'parent':i.select_role,"parentfield":"permission_list", "route_link": each.route_link, "module": each.module,"select_route":each.select_route,'read':1,'export':1,'write':1,'create':1,'delete_perm':1,"parenttype":"Roles Permission"})
					child_doc.insert()
					frappe.db.commit()
			
				
	
	



@frappe.whitelist(allow_guest=True)
def add_permission_to_role():
	if not frappe.db.exists("Permission List",{"select_role": "ezy-admin", "parent": "Roles Permission","select":1,"create":1,"read":1,"write":1,"export":1,"delete":1}):
		print(("Permission List",{"select_role": "ezy-admin", "parent": "Roles Permission","select":1,"create":1,"read":1,"write":1,"export":1,"delete":1}))
		doc = frappe.get_doc({'doctype': 'Permission List',"parent":"Roles Permission","parenttype":"Roles Permission","select_role":"ezy-admin","select":1,"create":1,"import":1,"read":1,"write":1,"export":1})
		doc = frappe.get_doc({'doctype': 'Permission List',"parent":"Roles Permission","parenttype":"Roles Permission","select_role":"ezy-admin","select":1,"create":1,"import":1,"read":1,"write":1,"export":1})
		print(doc)
		doc.insert()
		frappe.db.commit()

		

