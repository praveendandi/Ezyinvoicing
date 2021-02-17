# -*- coding: utf-8 -*-
# Copyright (c) 2020, Caratred and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import get_site_name
import shutil
import os
import pdfplumber
from datetime import date, datetime
import requests
import pandas as pd
import random, string
import re
import json
import sys
import frappe
import os
# from version2_app.version2_app.doctype.invoices.reinitiate_parser import reinitiateInvoice


class company(Document):
    # pass
    def on_update(self):
        if self.name:
            folder_path = frappe.utils.get_bench_path()
            site_folder_path = self.site_name
            folder_path = frappe.utils.get_bench_path()
            path = folder_path + '/sites/' + site_folder_path
            if self.invoice_reinitiate_parsing_file:
                reinitatefilepath = path + self.invoice_reinitiate_parsing_file
                destination_path = folder_path + self.reinitiate_file_path
                try:
                    print(self.name, "$$$$$$$$$$$$$$$$$$$$$$$")
                    shutil.copy(reinitatefilepath, destination_path)
                except Exception as e:
                    print(str(e), "************on_update company")
                    frappe.throw("file updated Failed")
            if self.invoice_parser_file:
                # invoice_parser_file_path
                invoicefilepath = path + self.invoice_parser_file
                destination_path2 = folder_path + self.invoice_parser_file_path
                try:
                    print(self.name, "$$$$$$$$$$$$$$$$$$$$$$$")
                    shutil.copy(invoicefilepath, destination_path2)
                except Exception as e:
                    print(str(e), "************on_update company")
                    frappe.throw("file updated Failed")


@frappe.whitelist(allow_guest=True)
def getUserRoles():
    if frappe.local.request.method == "GET":
        #data = json.loads(frappe.request.data)
        doc = frappe.get_roles(frappe.session.user)
        # perm = frappe.get_permissions(frappe.session.user)
        # print(doc)
        # frappe.db.commit()
        return {"success": True, "data": doc}
    else:
        return {
            "success": False,
            "message": "User doesn't exists! please Register"
        }


@frappe.whitelist(allow_guest=True)
def createError(title, error):
    frappe.log_error(error)


@frappe.whitelist(allow_guest=True)
def getPrinters():
    raw_printers = os.popen("lpstat -p -d")
    print(raw_printers.__dict__)
    printers = []
    for index, i in enumerate(raw_printers):
        print(index, i)
        if 'system default destination' not in i and 'ezy' not in i and 'EZY' not in i and "reason unknown" not in i:
            printers.append(i.split('is')[0].split('printer')[1].strip())

    return {
        'success': True,
        "data": printers,
        "message": "list of avaliable printers"
    }


@frappe.whitelist(allow_guest=True)
def givePrint(invoiceNumber, printer):

    # get invoice details
    invoice = frappe.get_doc('Invoices', invoiceNumber)

    invoice_file = invoice.invoice_file
    if invoice.invoice_type == 'B2B':
        if invoice.irn_generated == 'Success':
            invoice_file = invoice.invoice_with_gst_details
        else:
            invoice_file = invoice.invoice_file
    else:
        invoice_file = invoice.invoice_file

    # get invoice file path
    folder_path = frappe.utils.get_bench_path()
    company = frappe.get_last_doc('company')
    site_folder_path = company.site_name
    path = folder_path + '/sites/' + site_folder_path + invoice_file

    # invoicefile = invoice.invoice_file
    os.system("lpr -P " + printer + " " + path)
    return {
        "success": "True",
        "Data": {},
        "message": "Job Issued to Printer " + printer
    }


@frappe.whitelist(allow_guest=True)
def gitCurrentBranchCommit():
    try:
        folder_path = frappe.utils.get_bench_path()
        b = os.popen("git --git-dir=" + folder_path +
                     "/apps/version2_app/.git rev-parse HEAD")
        return {"success": True, "message": b}
    except Exception as e:
        print("git branch commit id:  ", str(e))
        return {"success": False, "message": str(e)}


@frappe.whitelist(allow_guest=True)
def b2cstatusupdate():
    try:
        data = frappe.db.get_list('Invoices',
                                  filters={'invoice_type': 'B2C'},
                                  fields=[
                                      "name", "invoice_number", "qr_generated",
                                      "irn_generated", "b2c_qrimage"
                                  ])
        for each in data:
            print(each)
            if each["irn_generated"] == "NA" and each[
                    "qr_generated"] == "Pending":
                doc = frappe.get_doc("Invoices", each["name"])
                doc.qr_generated = "Success"
            elif each["irn_generated"] == "Zero Invoice" and each[
                    "qr_generated"] == "Pending":
                doc = frappe.get_doc("Invoices", each["name"])
                doc.qr_generated = "Zero Invoice"
                doc.irn_generated = "NA"
                # update = "Update tabInvoices set qr_generated = 'Zero Invoice', irn_generated = 'NA' where name = '"+each[0]+"';"
            elif each["irn_generated"] == "Error" and each[
                    "qr_generated"] == "Pending":
                doc = frappe.get_doc("Invoices", each["name"])
                doc.qr_generated = "Error"
                doc.irn_generated = "NA"
                # update = "Update tabInvoices set qr_generated = 'Error', irn_generated = 'NA' where name = '"+each[0]+"';"
            elif each["irn_generated"] == "Error" and each[
                    "qr_generated"] == "Success":
                doc = frappe.get_doc("Invoices", each["name"])
                doc.irn_generated = "NA"
                # update = "Update tabInvoices set irn_generated = 'NA' where name = '"+each[0]+"';"
            elif each["irn_generated"] == "Zero Invoice" and each[
                    "qr_generated"] == "Success":
                doc = frappe.get_doc("Invoices", each["name"])
                doc.qr_generated = "Zero Invoice"
                doc.irn_generated = "NA"
                # update = "Update tabInvoices set qr_generated = 'Zero Invoice', irn_generated = 'NA' where name = '"+each[0]+"';"
            else:
                doc = None
            if doc == None:
                continue
            doc.save()
            frappe.db.commit()
        return True
    except Exception as e:
        print("b2cstatusupdate", str(e))
        return {"success": False, "message": str(e)}


@frappe.whitelist(allow_guest=True)
def addsacindex():
    try:
        data = frappe.db.get_all('SAC HSN CODES',
                                 fields=["name", "sac_index"],
                                 order_by='modified')
        if len(data) > 0:
            for index, j in enumerate(data):
                if j["sac_index"] == None:
                    doc = frappe.get_doc("SAC HSN CODES", j["name"])
                    doc.sac_index = ''.join(
                        random.choice(string.digits) for _ in range(7))
                    doc.save()
                    frappe.db.commit()
            return {"success": True}
        else:
            return {"success": False, "message": "no data found"}
    except Exception as e:
        print("addsacindex", str(e))
        return {"success": False, "message": str(e)}


@frappe.whitelist(allow_guest=True)
def qr_generatedtoirn_generated():
    try:
        data = frappe.db.get_list('Invoices',
                                  filters={'invoice_type': 'B2C'},
                                  fields=[
                                      "name", "invoice_number", "qr_generated",
                                      "irn_generated", "b2c_qrimage"
                                  ])
        if len(data) > 0:
            for each in data:
                doc = frappe.get_doc("Invoices", each["name"])
                doc.irn_generated = each["qr_generated"]
                doc.save()
                frappe.db.commit()
            return {"success": True}
        else:
            return {"success": False, "message": "no data found"}
    except Exception as e:
        print("addsacindex", str(e))
        return {"success": False, "message": str(e)}


# @frappe.whitelist(allow_guest=True)
# def reprocess_error_inoices():
# 	try:
# 		data = frappe.db.get_list('Invoices',filters={'irn_generated': 'Error'},fields=["name","invoice_number","invoice_file"])
# 		print(data)
# 		if len(data)>0:
# 			for each in data:
# 				obj = {"filepath":each["invoice_file"],"invoice_number":each["name"]}
# 				reinitiate = reinitiateInvoice(obj)
# 			return {"success":True}
# 		else:
# 			return {"success":False, "message":"no data found"}
# 	except Exception as e:
# 		print("reprocess_error_inoices", str(e))
# 		return {"success":False,"message":str(e)}

# @frappe.whitelist(allow_guest=True)
# def reprocess_pending_inoices():
# 	try:
# 		data = frappe.db.get_list('Invoices',filters={'irn_generated': 'Pending'},fields=["name","invoice_number","invoice_file"])
# 		if len(data)>0:
# 			for each in data:
# 				obj = {"filepath":each["invoice_file"],"invoice_number":each["name"]}
# 				reinitiate = reinitiateInvoice(obj)
# 			return {"success":True}
# 		else:
# 			return {"success":False, "message":"no data found"}
# 	except Exception as e:
# 		print("reprocess_pending_inoices", str(e))
# 		return {"success":False,"message":str(e)}


@frappe.whitelist(allow_guest=True)
def manual_to_pms():
    try:
        data = frappe.db.get_list('Invoices',
                                  filters={'invoice_from': 'Manual'},
                                  fields=["name", "invoice_number"])
        if len(data) > 0:
            updatePms = frappe.db.sql(
                """update tabInvoices set invoice_from='Pms' where invoice_from='Manual'"""
            )
        updatecategory = frappe.db.sql(
            """update tabInvoices set invoice_category='Tax Invoice' where invoice_category is NULL"""
        )
        frappe.db.commit()
        return True
    except Exception as e:
        return {"success": False}


@frappe.whitelist(allow_guest=True)
def manulaTax_credit_to_debit():
    try:
        data = frappe.db.get_list('Items',
                                  filters={
                                      'item_mode': 'Credit',
                                      'is_credit_item': 'Yes'
                                  },
                                  fields=["name", "parent"])
        if len(data) > 0:
            updatetax = frappe.db.sql(
                """update tabItems set item_mode='Debit' where item_mode='credit' and is_credit_item='No'"""
            )
            frappe.db.commit()
        # print(data)
        return True
    except Exception as e:
        return {"success": False, "message": str(e)}


import time
from bench_manager.bench_manager.utils import run_command


@frappe.whitelist(allow_guest=True)
def console_command(key=None,
                    caller='bench_update_pull',
                    app_name=None,
                    branch_name=None):
    commands = {
        "bench_update": ["bench update"],
        "switch_branch": [""],
        "get-app": ["bench get-app {app_name}".format(app_name=app_name)],
        "bench_update_pull": ["bench update"]
    }
    print(str(time.time()))
    run_command(commands=commands[caller],
                doctype='Bench Settings',
                key=str(time.time()),
                docname='Bench Settings')
    return True


# -*- coding: utf-8 -*-
# Copyright (c) 2017, Frappe and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import json, os, shlex, time
from subprocess import check_output, Popen, PIPE
from bench_manager.bench_manager.utils import verify_whitelisted_call, safe_decode


class BenchSettings(Document):
    site_config_fields = [
        "background_workers", "shallow_clone", "admin_password",
        "auto_email_id", "auto_update", "frappe_user", "global_help_setup",
        "dropbox_access_key", "dropbox_secret_key", "gunicorn_workers",
        "github_username", "github_password", "mail_login", "mail_password",
        "mail_port", "mail_server", "use_tls", "rebase_on_pull", "redis_cache",
        "redis_queue", "redis_socketio", "restart_supervisor_on_update",
        "root_password", "serve_default_site", "socketio_port",
        "update_bench_on_update", "webserver_port", "file_watcher_port"
    ]

    def set_attr(self, varname, varval):
        return setattr(self, varname, varval)

    def validate(self):
        self.sync_site_config()
        self.update_git_details()
        current_time = frappe.utils.time.time()
        if current_time - self.last_sync_timestamp > 10 * 60:
            sync_all(in_background=True)

    def sync_site_config(self):
        common_site_config_path = 'common_site_config.json'
        with open(common_site_config_path, 'r') as f:
            common_site_config_data = json.load(f)
            for site_config_field in self.site_config_fields:
                try:
                    self.set_attr(site_config_field,
                                  common_site_config_data[site_config_field])
                except:
                    pass

    def update_git_details(self):
        self.frappe_git_branch = safe_decode(
            check_output("git rev-parse --abbrev-ref HEAD".split(),
                         cwd=os.path.join('..', 'apps', 'frappe'))).strip('\n')

    def console_command(self, key, caller, app_name=None, branch_name=None):
        commands = {
            "bench_update": ["bench update"],
            "switch_branch": [""],
            "get-app": ["bench get-app {app_name}".format(app_name=app_name)]
        }
        frappe.enqueue('bench_manager.bench_manager.utils.run_command',
                       commands=commands[caller],
                       doctype=self.doctype,
                       key=key,
                       docname=self.name)


@frappe.whitelist()
def sync_sites():
    verify_whitelisted_call()
    site_dirs = update_site_list()
    site_entries = [x['name'] for x in frappe.get_all('Site')]
    create_sites = list(set(site_dirs) - set(site_entries))
    delete_sites = list(set(site_entries) - set(site_dirs))

    for site in create_sites:
        doc = frappe.get_doc({
            'doctype': 'Site',
            'site_name': site,
            'developer_flag': 1
        })
        doc.insert()
        frappe.db.commit()

    for site in delete_sites:
        doc = frappe.get_doc('Site', site)
        doc.developer_flag = 1
        doc.save()
        doc.delete()
        frappe.db.commit()
    # frappe.msgprint('Sync sites completed')


@frappe.whitelist()
def sync_apps():
    verify_whitelisted_call()
    app_dirs = update_app_list()
    app_entries = [x['name'] for x in frappe.get_all('App')]
    create_apps = list(set(app_dirs) - set(app_entries))
    delete_apps = list(set(app_entries) - set(app_dirs))
    create_apps = [app for app in create_apps if app != '']
    delete_apps = [app for app in delete_apps if app != '']

    for app in create_apps:
        doc = frappe.get_doc({
            'doctype': 'App',
            'app_name': app,
            'app_description': 'lorem ipsum',
            'app_publisher': 'lorem ipsum',
            'app_email': 'lorem ipsum',
            'developer_flag': 1
        })
        doc.insert()
        frappe.db.commit()

    for app in delete_apps:
        doc = frappe.get_doc('App', app)
        doc.developer_flag = 1
        doc.save()
        doc.delete()
        frappe.db.commit()
    # frappe.msgprint('Sync apps completed')


def update_app_list():
    app_list_file = 'apps.txt'
    with open(app_list_file, "r") as f:
        apps = f.read().split('\n')
    return apps


def update_site_list():
    site_list = []
    for root, dirs, files in os.walk(".", topdown=True):
        for name in files:
            if name == 'site_config.json':
                site_list.append(str(root).strip('./'))
                break
    if '' in site_list:
        site_list.remove('')
    return site_list


@frappe.whitelist()
def sync_backups():
    verify_whitelisted_call()
    backup_dirs_data = update_backup_list()
    backup_entries = [x['name'] for x in frappe.get_all('Site Backup')]
    backup_dirs = [
        x['date'] + ' ' + x['time'] + ' ' + x['site_name'] + ' ' +
        x['stored_location'] for x in backup_dirs_data
    ]
    create_backups = list(set(backup_dirs) - set(backup_entries))
    delete_backups = list(set(backup_entries) - set(backup_dirs))

    for date_time_sitename_loc in create_backups:
        date_time_sitename_loc = date_time_sitename_loc.split(' ')
        backup = {}
        for x in backup_dirs_data:
            if (x['date'] == date_time_sitename_loc[0]
                    and x['time'] == date_time_sitename_loc[1]
                    and x['site_name'] == date_time_sitename_loc[2]
                    and x['stored_location'] == date_time_sitename_loc[3]):
                backup = x
                break
        doc = frappe.get_doc({
            'doctype':
            'Site Backup',
            'site_name':
            backup['site_name'],
            'date':
            backup['date'],
            'time':
            backup['time'],
            'stored_location':
            backup['stored_location'],
            'public_file_backup':
            backup['public_file_backup'],
            'private_file_backup':
            backup['private_file_backup'],
            'hash':
            backup['hash'],
            'file_path':
            backup['file_path'],
            'developer_flag':
            1
        })
        doc.insert()
        frappe.db.commit()

    for backup in delete_backups:
        doc = frappe.get_doc('Site Backup', backup)
        doc.developer_flag = 1
        doc.save()
        frappe.db.commit()
        doc.delete()
        frappe.db.commit()
    # frappe.msgprint('Sync backups completed')


def update_backup_list():
    all_sites = []
    archived_sites = []
    sites = []
    for root, dirs, files in os.walk("../archived_sites/", topdown=True):
        archived_sites.extend(dirs)
        break
    archived_sites = ["../archived_sites/" + x for x in archived_sites]
    all_sites.extend(archived_sites)
    for root, dirs, files in os.walk("../sites/", topdown=True):
        for site in dirs:
            if os.path.isfile("../sites/{}/site_config.json".format(site)):
                sites.append(site)
        break
    sites = ["../sites/" + x for x in sites]
    all_sites.extend(sites)

    response = []

    backups = []
    for site in all_sites:
        backup_path = os.path.join(site, "private", "backups")
        try:
            backup_files = safe_decode(
                check_output(
                    shlex.split("ls ./{backup_path}".format(
                        backup_path=backup_path)))).strip('\n').split('\n')
            backup_files = [
                file for file in backup_files if "database.sql" in file
            ]
            for backup_file in backup_files:
                inner_response = {}
                date_time_hash = backup_file.rsplit('_', 1)[0]
                file_path = backup_path + '/' + date_time_hash
                inner_response['site_name'] = site.split('/')[2]
                inner_response['date'] = get_date(date_time_hash)
                inner_response['time'] = get_time(date_time_hash)
                inner_response['stored_location'] = site.split('/')[1]
                inner_response['private_file_backup'] = os.path.isfile(backup_path+\
                 '/'+date_time_hash+"_private_files.tar")
                inner_response['public_file_backup'] = os.path.isfile(backup_path+\
                 '/'+date_time_hash+"_files.tar")
                inner_response['hash'] = get_hash(date_time_hash)
                inner_response['file_path'] = file_path[3:]
                response.append(inner_response)
        except:
            pass
            # frappe.msgprint('There are no backups to sync!')
    return response


def get_date(date_time_hash):
    return date_time_hash[:4] + "-" + date_time_hash[
        4:6] + "-" + date_time_hash[6:8]


def get_time(date_time_hash):
    time = date_time_hash.split('_')[1]
    return time[0:2] + ':' + time[2:4] + ':' + time[4:6]


def get_hash(date_time_hash):
    return date_time_hash.split('_')[2]


@frappe.whitelist()
def sync_all(in_background=False):
    if not in_background:
        frappe.msgprint('Sync has started and will run in the background...')
    verify_whitelisted_call()
    frappe.enqueue(
        'bench_manager.bench_manager.doctype.bench_settings.bench_settings.sync_sites'
    )
    frappe.enqueue(
        'bench_manager.bench_manager.doctype.bench_settings.bench_settings.sync_apps'
    )
    frappe.enqueue(
        'bench_manager.bench_manager.doctype.bench_settings.bench_settings.sync_backups'
    )
    frappe.set_value('Bench Settings', None, 'last_sync_timestamp',
                     frappe.utils.time.time())
