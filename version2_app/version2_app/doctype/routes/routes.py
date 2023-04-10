# Copyright (c) 2023, caratred and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import cstr, encode
from cryptography.fernet import Fernet, InvalidToken
from frappe.model.document import Document

class Routes(Document):
	pass


@frappe.whitelist()
def user_by_roles_companies():
    values =frappe.db.sql('''select `tabHas Role`.role, `tabUser`.username,`tabUser`.email, `tabUser`.full_name,`tabUser`.enabled,`tabUser`.first_name,`tabUser`.full_name from `tabUser` inner join `tabHas Role` on `tabUser`.email=`tabHas Role`.parent where `tabUser`.username  not like 'adm%' and `tabHas Role`.role like 'ezy%' and `tabHas Role`.role not like 'EzyInvoicing%'  order by `tabUser`.email ''',as_dict=1)
    return values,


@frappe.whitelist()
def reset_initial_password(user,pwd):
    get_user_details = frappe.db.sql(''' select * from `tabUser` Where email = '{user}' '''.format(user=user),as_dict=1)
    for each in get_user_details:
        if each.last_active is not None:
            print("allow User to login")
        else:
            print("Users Initial Login")    

         
    





