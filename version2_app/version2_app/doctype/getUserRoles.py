import frappe
import json
import requests


@frappe.whitelist(allow_guest=True)
def getUserRoles():
	if frappe.local.request.method == "POST":
		data = json.loads(frappe.request.data)
		print(data,"etst")
		for i in data['role']:
			doc = frappe.get_doc({
				"docstatus": 0,
				"doctype": "Has Role",
				"modified_by": "Administrator",
				"owner": "Administrator",
				"parent": data['parent'],
				'parentfield': "roles",
				"parenttype": "User",
				"role": i,
				})
			doc.save()
			frappe.db.commit()
			
		return {"success":True}
	if frappe.local.request.method=="PUT":
		data = json.loads(frappe.request.data)
		par = frappe.db.delete('Has Role', {'parent': data['parent']})
		# frappe.db.commit()
		for i in data['role']:
			doc = frappe.get_doc({
				"docstatus": 0,
				"doctype": "Has Role",
				 # "idx": 1,
				"modified_by": "Administrator",
				"owner": "Administrator",
				"parent": data['parent'],
				'parentfield': "roles",
				"parenttype": "User",
				"role": i,
				})
			doc.save()
			frappe.db.commit()
		return {"success":True}
		