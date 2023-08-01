# Copyright (c) 2023, caratred and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class PermissionList(Document):
    pass


@frappe.whitelist()
def migrate_user_role_per():
    get_role = frappe.db.get_list('Role','name')
    if not frappe.db.exists('Role',{"role_name":"ezy-admin"}, cache=True):
        doc = frappe.get_doc({'doctype': 'Role',"role_name":"ezy-admin"})
        doc.insert()
        frappe.db.commit()
        parent_role = frappe.db.get_list('Roles Permission',{'select_role':'ezy-admin'},['select_role'])
        for i in parent_role:
            perm_list = frappe.db.get_list('Permission List',{'parent':i.select_role,'module':'Master Data','select_route':('in',('User Management-Details','Permissions','Role Management','User Management'))},['name','module','select_route','route_link','read','write','create','delete_perm','export']) 
            print(perm_list)
            for each in perm_list:
                if frappe.db.exists({"doctype": "Permission List",'parent':i.select_role,"parentfield":"permission_list", "route_link": each.route_link, "module": each.module,"select_route":each.select_route,"parenttype":"Roles Permission"}):
                    child_doc= frappe.db.set_value('Permission List',each.name,{'read':1,'export':1,'write':1,'create':1,'delete_perm':1})
                    frappe.db.commit()


from frappe.sessions import delete_session
from frappe.core.doctype.session_default_settings.session_default_settings import clear_session_defaults
# from frappe.sessions import clear_sessions
# from frappe.auth import clear_cookies	
# # from  auth import logout

# # from frappe.frappe.auth import LoginManager
# # from frappe.auth import LoginManager

from frappe.auth import LoginManager
Auth = LoginManager()


@frappe.whitelist()
def logout_user():
    user = frappe.session.user
    resp = Auth.logout(user=user)
    clear_sessions= clear_session_defaults
    if user == frappe.session.user:
        delete_session(frappe.session.sid, user=user, reason="User Manually Logged Out")
    return {"Success":True,"message":"User logged out succuessfully"}


