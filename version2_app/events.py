import base64
import glob
from heapq import merge
import importlib.util
import itertools
import json
import os
from version2_app.parsers import *
import re
import shlex
import shutil
import sys
import time
import fitz
import traceback
from datetime import date, datetime, timedelta
from email.mime import image
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from io import BytesIO
from version2_app.clbs.doctype.summary_breakups.summary_breakups import convert_image_to_base64
from frappe.utils.background_jobs import enqueue
from subprocess import PIPE, STDOUT, Popen
from version2_app.pos_bills.doctype.pos_checks.pos_checks import extract_data, get_outlet_from_check
# from requests.sessions import _Data
import frappe
import pdfplumber
import PIL
import pyshorteners as ps
import requests
from frappe.core.doctype.communication.email import make
from frappe.utils import cstr, get_site_name, logger, random_string
from frappe.utils.data import money_in_words
from PIL import Image
from weasyprint import HTML
from version2_app.passport_scanner.doctype.dropbox.dropbox import merge_guest_to_guest_details, extract_text
import datetime
frappe.utils.logger.set_log_level("DEBUG")
logger = frappe.logger("api")

# from version2_app.passport_scanner.doctype.dropbox.dropbox import create_scanned_doc
# user_name = frappe.session.user


@frappe.whitelist(allow_guest=True)
def num_to_words(num):
    try:
        given_num = abs(float((num)))
        num_in_word = money_in_words(given_num)
        text = str(num_in_word).strip("INR")
        return {"success": True, "data": text.strip()}
    except:
        frappe.log_error(frappe.get_traceback(), "num_to_words Error")
        return {"success": False}


def invoice_update(doc, method=None):
    try:
        company = frappe.get_last_doc("company")
        if company.create_etax_invoices_in_separate_folder == 1 and doc.etax_invoice_created == 0 and doc.irn_generated == "Success":
            print("//////////////////////////")
            etax = html_to_pdf(doc.name)
            if etax["success"]:
                doc.etax_invoice_created
        if doc.sales_amount_after_tax:
            print("...........................")
            total_amount_in_words = num_to_words(doc.sales_amount_after_tax)
            if total_amount_in_words["success"] == True:
                doc.amount_in_word = total_amount_in_words["data"]
                # doc.save(ignore_permissions=True,ignore_version=True)
        # frappe.db.commit()
    except:
        frappe.log_error(frappe.get_traceback(), "invoice_update Error")


def invoice_created(doc, method=None):
    try:
        print("/.................../........///////////.")
        company = frappe.get_last_doc("company")
        if company.create_etax_invoices_in_separate_folder == 1 and doc.etax_invoice_created == 0 and doc.irn_generated == "Success":
            etax = html_to_pdf(doc.name)
            if etax["success"]:
                frappe.db.set_value("Invoices",doc.name,"etax_invoice_created",1)
                frappe.db.commit()
        if doc.sales_amount_after_tax:
            total_amount_in_words = num_to_words(doc.sales_amount_after_tax)
            if total_amount_in_words["success"] == True:
                doc.amount_in_word = total_amount_in_words["data"]
                # print(doc.amount_in_word,"===============")
                # doc.save(ignore_permissions=True)
                # frappe.db.commit()
        if frappe.db.exists('Invoice Reconciliations', doc.name):
            reconciliations_doc = frappe.get_doc(
                'Invoice Reconciliations', doc.name)
            reconciliations_doc.invoice_found = "Yes"
            reconciliations_doc.save(ignore_permissions=True, ignore_version=True)
        if doc.invoice_from == "Pms":
            if frappe.db.exists(
                {"doctype": "Document Bin", "invoice_file": doc.invoice_file}
            ):
                bin_name = frappe.db.get_value(
                    "Document Bin", {"invoice_file": doc.invoice_file}
                )
                bin_doc = frappe.get_doc("Document Bin", bin_name)
                bin_doc.print_by = doc.print_by
                bin_doc.document_type = doc.invoice_category
                bin_doc.invoice_number = doc.name
                # bin_doc.error_log = error_log
                bin_doc.document_printed = "Yes"
                bin_doc.save(ignore_permissions=True, ignore_version=True)
        if not frappe.db.exists("Documents", doc.confirmation_number):
            data = {
                "doctype": "Documents",
                "tax_invoice_file": doc.invoice_file,
                "confirmation_number": doc.confirmation_number,
                "module_name": "Sign Ezy",
                "user": doc.owner,
            }
            get_doc = frappe.get_doc(data)
            get_doc.insert()
            frappe.db.commit()
        get_doc = frappe.db.set_value(
            "Documents", doc.confirmation_number, {"tax_invoice_file": doc.invoice_file}
        )
        frappe.db.commit()
        company = frappe.get_doc("company", doc.company)
        if company.direct_print_without_push_to_tab == 1:
            if doc.invoice_file.count("@-") == 2:
                get_values = {}
                if doc.confirmation_number != "":
                    if frappe.db.exists("Arrival Information", doc.confirmation_number):
                        get_values = frappe.db.get_value(
                            "Arrival Information",
                            doc.confirmation_number,
                            ["guest_email_address", "guest_phone_no"],
                            as_dict=1,
                        )
                workstation = re.search("@-(.*)@-", doc.invoice_file)
                workstation = workstation.group(1)
                if frappe.db.exists(
                    {
                        "doctype": "Tablet Config",
                        "work_station": workstation,
                        "mode": "Active",
                    }
                ):
                    # tabletconfig = frappe.get_doc({"doctype":"Tablet Config","work_station":workstation,"mode":"Active"})
                    tabletconfig = frappe.db.get_value(
                        "Tablet Config",
                        {"work_station": workstation, "mode": "Active"},
                        [
                            "work_station",
                            "tablet",
                            "username",
                            "work_station_socket_id",
                            "tablet_socket_id",
                            "mode",
                            "device_name",
                        ],
                        as_dict=1,
                    )
                    data = {
                        "tablet_config": tabletconfig,
                        "doc_data": doc.__dict__,
                        "uuid": tabletconfig.tablet,
                        "guest_details": get_values,
                    }
                    data["uuid"] = tabletconfig.tablet
                    frappe.publish_realtime(
                        "custom_socket", {"message": "Push To Tab", "data": data}
                    )
                    return {"success": True, "data": data}
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error(
            "Ezy-invoicing invoice created Event",
            "line No:{}\n{}".format(exc_tb.tb_lineno, traceback.format_exc()),
        )
        return {"success": False, "message": str(e)}


def company_created(doc, method=None):
    try:
        if frappe.db.exists("company", doc.name):
            pass
            doc = frappe.db.get_list(
                "company",
                filters={"docstatus": 0},
                fields=[
                    "name",
                    "company_name",
                    "company_code",
                    "phone_number",
                    "gst_number",
                    "provider",
                    "licensing_host",
                ],
            )
            api = doc[0]["licensing_host"] + "/api/resource/Properties"
            adequare_doc = frappe.get_doc("GSP APIS", doc[0]["provider"])
            insert_dict = {
                "doctype": "Properties",
                "property_name": doc[0]["company_name"],
                "property_code": doc[0]["company_code"],
                "contact_number": doc[0]["phone_number"],
                "gst_number": doc[0]["gst_number"],
                "gsp_provider": doc[0]["provider"],
                "api_key": adequare_doc.gsp_prod_app_secret,
                "api_secret": adequare_doc.gsp_prod_app_id,
                "gsp_test_app_id": adequare_doc.gsp_test_app_id,
                "gsp_test_app_secret": adequare_doc.gsp_test_app_secret,
            }
            headers = {"content-type": "application/json"}
            requests.post(api, headers=headers, json=insert_dict, verify=False)
            # folder_path = frappe.utils.get_bench_path()
            # if doc.pms_property_logo != "":
            #     file_path = folder_path+'/sites/'+doc.site_name+doc.pms_property_logo
            #     status = upload_propery_logo_pms({"file_path":file_path,"company":doc.name})
            #     if status["success"] == False:
            #         return status
            #     frappe.db.set_value('company', doc.name, {"pms_property_url":status["data"]})
            #     frappe.db.commit()
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error(
            "Ezy-invoicing company_created Event",
            "line No:{}\n{}".format(exc_tb.tb_lineno, traceback.format_exc()),
        )
        return {"success": False, "message": str(e)}


def invoice_deleted(doc, method=None):
    try:
        frappe.publish_realtime(
            "custom_socket",
            {
                "message": "Invoice deleted",
                "type": "Delete invoice",
                "invoice_number": doc.name,
                "company": doc.company,
            },
        )
        soc_doc = frappe.new_doc("Socket Notification")
        soc_doc.invoice_number = doc.name
        soc_doc.guest_name = doc.guest_name
        soc_doc.document_type = doc.invoice_category
        soc_doc.room_number = doc.room_number
        soc_doc.confirmation_number = doc.confirmation_number
        soc_doc.print_by = doc.print_by
        soc_doc.invoice_category = doc.invoice_category
        soc_doc.record_type = "Delete"
        soc_doc.insert(ignore_permissions=True)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error(
            "Ezy-invoicing invoice_deleted Event",
            "line No:{}\n{}".format(exc_tb.tb_lineno, traceback.format_exc()),
        )
        return {"success": False, "message": str(e)}


def precheckinsdocuments(doc, method=None):
    try:
        user_name = frappe.session.user
        date_time = datetime.datetime.now()
        confirmation_number = str(doc.confirmation_number)
        if "-" in confirmation_number:
            confirmation_number = confirmation_number.split("-")[0]

        date_time = date_time.strftime("%Y-%m-%d %H:%M:%S")
        # activity_data = {"doctype":"Activity Logs","datetime":date_time,"confirmation_number":confirmation_number,"module":"ezycheckins","event":"PreCheckins","user":user_name,"activity":"Precheckin done by "+doc.guest_first_name,"status":""}
        if not frappe.db.exists("Documents", confirmation_number):
            # event_doc=frappe.get_doc(activity_data)
            # event_doc.insert()
            # frappe.db.commit()
            user_name = frappe.session.user
            data = {
                "doctype": "Documents",
                "guest_details": [{"image1": doc.image_1, "image2": doc.image_2}],
                "confirmation_number": confirmation_number,
                "module_name": "Ezycheckins",
                "user": user_name,
            }
            get_doc = frappe.get_doc(data)
            get_doc.insert()
            frappe.db.commit()
        else:
            update_doc = frappe.get_doc("Documents", confirmation_number)
            update_doc.append(
                "guest_details", {"image1": doc.image_1, "image2": doc.image_2}
            )
            update_doc.save()
            frappe.db.commit()
    except Exception as e:
        print(str(e), "Process Checkin event")
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error(
            "Ezy-precheckins",
            "line No:{}\n{}".format(exc_tb.tb_lineno, traceback.format_exc()),
        )
        print(traceback.print_exc())
        return {"success": False, "message": str(e)}


def invoiceCreated(doc):
    try:
        # frappe.publish_realtime("invoice_created", "message")
        frappe.publish_realtime(
            "custom_socket",
            {
                "message": "Invoices Created",
                "data": doc.__dict__,
                "company": doc.company,
            },
        )
        soc_doc = frappe.new_doc("Socket Notification")
        soc_doc.invoice_number = doc.name
        soc_doc.guest_name = doc.guest_name
        soc_doc.document_type = doc.invoice_category
        soc_doc.room_number = doc.room_number
        soc_doc.confirmation_number = doc.confirmation_number
        soc_doc.print_by = doc.print_by
        soc_doc.invoice_category = doc.invoice_category
        soc_doc.record_type = "Create"
        soc_doc.insert(ignore_permissions=True)

        filename = doc.invoice_file
        bin_name = frappe.db.get_value("Document Bin", {"invoice_file": filename})
        if frappe.db.exists({"doctype": "Document Bin", "name": bin_name}):
            bin_doc = frappe.get_doc("Document Bin", bin_name)
            bin_doc.print_by = doc.print_by
            bin_doc.document_printed = "Yes"
            bin_doc.document_type = doc.invoice_category
            bin_doc.invoice_number = doc.invoice_number
            bin_doc.save(ignore_permissions=True, ignore_version=True)
    except Exception as e:
        print(str(e), "Invoice Created Socket Method")
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error(
            "Ezy-invoicing invoiceCreated Event",
            "line No:{}\n{}".format(exc_tb.tb_lineno, traceback.format_exc()),
        )
        print(traceback.print_exc())
        return {"success": False, "message": str(e)}


def update_documentbin(filepath, error_log):
    try:
        bin_data = frappe.db.get_list(
            "Document Bin", filters={"invoice_file": ["=", filepath]}
        )
        print(bin_data)
        if len(bin_data) > 0:
            pass
        else:
            systemName = "NA"
            if filepath.count("@") == 2:
                if "@" in filepath:
                    systemName = re.search("@(.*)@", filepath)
                    systemName = systemName.group(1)
            bin_doc = frappe.new_doc("Document Bin")
            bin_doc.system_name = systemName
            bin_doc.invoice_file = filepath
            bin_doc.error_log = error_log
            bin_doc.insert(ignore_permissions=True)
            frappe.db.commit()
    except Exception as e:
        print(str(e), "update_documentbin")
        print(traceback.print_exc())
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error(
            "Ezy-invoicing update_documentbin Event",
            "line No:{}\n{}".format(exc_tb.tb_lineno, traceback.format_exc()),
        )
        return {"success": False, "message": str(e)}


def insert_folios(company, file_path):
    try:
        print(file_path)
        site_folder_path = company.site_name
        folder_path = frappe.utils.get_bench_path()
        if "private" in file_path:
            file_path = folder_path + "/sites/" + site_folder_path + file_path
        else:
            file_path = (
                folder_path + "/sites/" + site_folder_path + "/public" + file_path
            )
        content = []
        with pdfplumber.open(file_path) as pdf:
            count = len(pdf.pages)
            for index in range(count):
                first_page = pdf.pages[index]
                content.append(first_page.extract_text())
        raw_data = []
        for i in content:
            for j in i.splitlines():
                raw_data.append(j)
        document_type = []
        # document_names = {"reg_card_identification_text": "Redg Card", "paid_out_receipts": "Paidout Receipts", "advance_deposits_identification": "Advance Deposits",
        #                   "payment_receipts_identification": "Payment Receipts", "encashment_certificates_identification": "Encashment Certificates"}
        get_values = frappe.db.get_value(
            "company",
            company.name,
            [
                "reg_card_identification_text",
                "paid_out_receipts",
                "advance_deposits_identification",
                "payment_receipts_identification",
                "encashment_certificates_identification",
            ],
            as_dict=1,
        )
        for key, value in get_values.items():
            for i in raw_data:
                if value:
                    if value in i:
                        document_type.append(key)
        for i in raw_data:
            if "advance_deposits_identification" in document_type:
                pattern = re.compile(company.advance_deposits_confirmation_no_regex)
                check_confirmation = re.findall(pattern, i)
                if len(check_confirmation) > 0:
                    confirmation = list(itertools.chain(*tuple))
                    print(confirmation)
        return {"success": True}
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error(
            "Ezy-Insert Folios",
            "line No:{}\n{}".format(exc_tb.tb_lineno, traceback.format_exc()),
        )
        return {"success": False, "message": str(e)}


def fileCreated(doc, method=None):
    try:
        if "job-" in doc.file_name:
            if not frappe.db.exists(
                {"doctype": "Document Bin", "invoice_file": doc.file_url}
            ):
                update_documentbin(doc.file_url, "")
                abs_path = os.path.dirname(os.getcwd())
                company = frappe.db.get_value("company",doc.attached_to_name)
                if company:
                    company_doc = frappe.get_doc("company",doc.attached_to_name)
                    new_parsers = company_doc.new_parsers
                    if company_doc.block_print == "True":
                        return {"success":False,"message":"Print has been Blocked"}
                    if new_parsers == 0:
                        file_path = abs_path + '/apps/version2_app/version2_app/parsers/'+doc.attached_to_name+'/invoice_parser.py'
                    else:
                        file_path = abs_path + '/apps/version2_app/version2_app/parsers_invoice/invoice_parsers/'+doc.attached_to_name+'/invoice_parser.py'
                    module_name = 'file_parsing'
                    spec = importlib.util.spec_from_file_location(module_name, file_path)
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    module.file_parsing(doc.file_url)
                    frappe.log_error(traceback.print_exc())
                    logger.error(f"fileCreated,   {traceback.print_exc()}")
        elif "POS-" in doc.file_name or "pos-" in doc.file_name:
            if not frappe.db.exists("POS Checks",{"pos_bill": doc.file_url}):
                enqueue(
                    extract_data_from_pos_check,
                    queue="default",
                    timeout=800000,
                    event="data_extraction",
                    now=False,
                    data={
                        "pos_bill": doc.file_url,
                        "file_name": doc.file_name 
                    },
                    is_async=True,
                )
                return True
        else:
            if "company" not in doc.file_name and "GSP_API" not in doc.file_name:
                company = frappe.get_last_doc("company")
                if company.block_print == "True":
                    return {"success": False, "message": "Print has been Blocked"}
                if ".pdf" in doc.file_url and "with-qr" not in doc.file_url:
                    update_documentbin(doc.file_url, "")
        return True
        logger.error(f"fileCreated,   {traceback.print_exc()}")
    except Exception as e:
        logger.error(f"fileCreated,   {traceback.print_exc()}")
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error(
            "Ezy-invoicing fileCreated Event",
            "line No:{}\n{}".format(exc_tb.tb_lineno, traceback.format_exc()),
        )
        update_documentbin(doc.file_url, str(e))
        return {"success": False, "message": str(e)}


def Updateemitsocket(doc, method=None):
    try:
        if doc.status == "Success":
            company = frappe.get_last_doc("company")
            frappe.log_error(
                "trigger socket bench update",
                " {'message':'bench  update started','type':'bench update'}",
            )
            frappe.publish_realtime(
                "custom_socket",
                {
                    "message": "bench  update started",
                    "type": "bench update",
                    "company": company.name,
                },
            )
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error(
            "Ezy-invoicing Updateemitsocket Event",
            "line No:{}\n{}".format(exc_tb.tb_lineno, traceback.format_exc()),
        )
        return {"success": False, "message": str(e)}


def DocumentBinSocket(doc, method=None):
    try:
        company = frappe.get_last_doc("company")
        frappe.log_error("Document Bin Insert", " {'message':'Docuemnt Bin Insert'}")
        frappe.publish_realtime(
            "custom_socket",
            {
                "message": "Document Bin Insert",
                "type": "document_bin_insert",
                "data": doc.__dict__,
                "company": company.name,
            },
        )
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error(
            "Ezy-invoicing DocumentBinSocket Event",
            "line No:{}\n{}".format(exc_tb.tb_lineno, traceback.format_exc()),
        )
        return {"success": False, "message": str(e)}


def updateManager(doc, method=None):
    try:
        if doc.status != "Ongoing":
            commands = [
                "git pull origin updates",
                "systemctl nginx reload",
                "systemctl nginx restart",
            ]
            console_dump = ""
            company = frappe.get_last_doc("company")
            cwd = company.angular_project_production_path
            for command in commands:
                terminal = Popen(
                    shlex.split(command),
                    stdin=PIPE,
                    stdout=PIPE,
                    stderr=STDOUT,
                    cwd=cwd,
                )
                # frappe.log_error("log error", terminal.stdout.read(1))
                for c in iter(lambda: safe_decode(terminal.stdout.read(1)), ""):
                    console_dump += c
            # logged_command = " && ".join(commands)
            frappe.publish_realtime(
                "custom_socket",
                {
                    "message": "bench update completed",
                    "type": "bench completed",
                    "company": company.name,
                },
            )
            frappe.log_error("Angular project pull data", "update manager")
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error(
            "Ezy-invoicing updateManager Event",
            "line No:{}\n{}".format(exc_tb.tb_lineno, traceback.format_exc()),
        )
        print(str(e), "    updateManager")


def safe_decode(string, encoding="utf-8"):
    try:
        string = string.decode(encoding)
    except Exception:
        pass
    return string


def information_folio_created(doc, method=None):
    try:
        user_name = frappe.session.user
        frappe.publish_realtime(
            "custom_socket",
            {"message": "information Invoices Created", "data": doc.__dict__},
        )
        if not frappe.db.exists("Documents", doc.confirmation_number):
            data = {
                "doctype": "Documents",
                "invoice_file": doc.invoice_file,
                "confirmation_number": doc.confirmation_number,
                "module_name": "Sign Ezy",
                "user": user_name,
            }
            get_doc = frappe.get_doc(data)
            get_doc.insert()
            frappe.db.commit()
        get_doc = frappe.db.set_value(
            "Documents", doc.confirmation_number, {"invoice_file": doc.invoice_file}
        )
        frappe.db.commit()
        company = frappe.get_doc("company", doc.company)
        if company.direct_print_without_push_to_tab == 1:
            if doc.invoice_file.count("@-") >= 2:
                get_values = {}
                if doc.confirmation_number != "":
                    if frappe.db.exists("Arrival Information", doc.confirmation_number):
                        get_values = frappe.db.get_value(
                            "Arrival Information",
                            doc.confirmation_number,
                            ["guest_email_address", "guest_phone_no"],
                            as_dict=1,
                        )
                workstation = re.search("@-(.*)@-", doc.invoice_file)
                workstation = workstation.group(1)
                if frappe.db.exists(
                    {
                        "doctype": "Tablet Config",
                        "work_station": workstation,
                        "mode": "Active",
                    }
                ):
                    tabletconfig = frappe.db.get_value(
                        "Tablet Config",
                        {"work_station": workstation, "mode": "Active"},
                        [
                            "work_station",
                            "tablet",
                            "username",
                            "work_station_socket_id",
                            "tablet_socket_id",
                            "mode",
                            "device_name",
                        ],
                        as_dict=1,
                    )
                    data = {
                        "tablet_config": tabletconfig,
                        "doc_data": doc.__dict__,
                        "uuid": tabletconfig.tablet,
                        "guest_details": get_values,
                    }
                    data["uuid"] = tabletconfig.tablet
                    frappe.publish_realtime(
                        "custom_socket", {"message": "Push To Tab", "data": data}
                    )
                    return {"success": True, "data": data}
        # frappe.publish_realtime("custom_socket", {'message':'information Folio','type':"bench completed"})
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error(
            "Ezy-information folio created Event",
            "line No:{}\n{}".format(exc_tb.tb_lineno, traceback.format_exc()),
        )
        return {"success": False, "message": str(e)}


def tablet_mapping(doc, method=None):
    try:
        workstation = frappe.get_doc("Active Work Stations", doc.work_station)
        workstation.username = doc.username
        workstation.save(ignore_permissions=True, ignore_version=True)
        tablet_doc = frappe.get_doc("Active Tablets", doc.tablet)
        doc.device_name = tablet_doc.device_name
        doc.uuid = doc.tablet
        doc.workstation_status = workstation.status
        workstation.save(ignore_permissions=True, ignore_version=True)
        frappe.publish_realtime(
            "custom_socket", {"message": "Tablet Mapped", "data": doc.__dict__}
        )
        # frappe.publish_realtime("custom_socket", {'message':'information Folio','type':"bench completed"})
    except Exception as e:
        print(e)


def remove_mapping(doc, method=None):
    try:
        tablet = frappe.db.get_value("Active Tablets", doc.tablet, "tablet")
        frappe.publish_realtime(
            "custom_socket", {"message": "Remove Tablet config", "data": doc.__dict__}
        )
        frappe.publish_realtime(
            "custom_socket",
            {
                "message": "Tablet Config Disconnected",
                "data": doc.__dict__,
                "tablet": tablet,
            },
        )
        # frappe.publish_realtime("custom_socket", {'message':'information Folio','type':"bench completed"})
    except Exception as e:
        print(e)


def tablet_connected(doc, method=None):
    try:
        frappe.publish_realtime(
            "custom_socket", {"message": "Tablet Connected", "data": doc.__dict__}
        )
        # frappe.publish_realtime("custom_socket", {'message':'information Folio','type':"bench completed"})
    except Exception as e:
        print(e)


def tablet_disconnected(doc, method=None):
    try:
        frappe.publish_realtime(
            "custom_socket",
            {"message": "Tablet Config Disconnected", "data": doc.__dict__},
        )
        frappe.publish_realtime(
            "custom_socket", {"message": "Tablet Disconnected", "data": doc.__dict__}
        )
    except Exception as e:
        print(e)


# def workstation_disconnected(doc, method=None):
#     try:
#         print(doc.name, "hello hiee")
#         frappe.publish_realtime(
#             "custom_socket", {'message': 'station_disconnected', 'data': doc.__dict__})
#     except Exception as e:
#         print(e)


def update_tablet_status(doc, method=None):
    try:
        table_config = frappe.db.get_value(
            "Tablet Config", {"tablet": doc.name}, ["name"]
        )
        if table_config:
            table_config_doc = frappe.get_doc("Tablet Config", table_config)
            table_config_doc.tablet_socket_id = doc.socket_id
            table_config_doc.save(ignore_permissions=True, ignore_version=True)
            frappe.publish_realtime(
                "custom_socket",
                {"message": "Tablet Status Updated", "data": doc.__dict__},
            )
    except Exception as e:
        print(e)


@frappe.whitelist(allow_guest=True)
def update_workstations_status():
    try:
        data = json.loads(frappe.request.data)
        data = data["data"]
        workstation = data["workstation"]
        del data["workstation"]
        frappe.db.set_value("Active Work Stations", workstation, data)
        frappe.db.commit()
        table_config = frappe.db.get_value(
            "Tablet Config", {"work_station": workstation}, ["name"]
        )
        if table_config:
            table_config_doc = frappe.get_doc("Tablet Config", table_config)
            table_config_doc.work_station_socket_id = data["socket_id"]
            table_config_doc.save(ignore_permissions=True, ignore_version=True)
            frappe.db.commit()
        return {"success": True, "message": "Tablet updated"}
    except Exception as e:
        return {"success": False, "message": str(e)}


def before_update_ws(doc, method=None):
    try:
        doc.update_modified = False
        return doc
    except Exception as e:
        print(e)


def create_redg_card(doc, method=None):
    try:
        frappe.publish_realtime(
            "custom_socket", {"message": "Redg Created", "data": doc.__dict__}
        )
        user_name = frappe.session.user
        date_time = datetime.datetime.now()
        date_time = date_time.strftime("%Y-%m-%d %H:%M:%S")
        activity_data = {
            "doctype": "Activity Logs",
            "datetime": date_time,
            "confirmation_number": doc.confirmation_number,
            "module": "Sign Ezy",
            "event": "PreArrivals",
            "user": user_name,
            "activity": "Redg card added successfully",
        }
        event_doc = frappe.get_doc(activity_data)
        event_doc.insert()
        frappe.db.commit()
        if not frappe.db.exists("Documents", doc.confirmation_number):
            user_name = frappe.session.user
            data = {
                "doctype": "Documents",
                "redg_file": doc.redg_file,
                "confirmation_number": doc.confirmation_number,
                "module_name": "Sign Ezy",
                "user": doc.owner,
            }
            get_doc = frappe.get_doc(data)
            get_doc.insert()
            frappe.db.commit()
        user_name = frappe.session.user
        data = {"redg_file": doc.redg_file}
        get_doc = frappe.db.set_value("Documents", doc.confirmation_number, data)
        frappe.db.commit()
    except Exception as e:
        print(e, "=================================================")


def create_paidout_receipt(doc, method=None):
    try:
        frappe.publish_realtime(
            "custom_socket",
            {"message": "Paidout Receipt Created", "data": doc.__dict__},
        )
    except Exception as e:
        print(e)


def create_advance_deposits(doc, method=None):
    try:
        frappe.publish_realtime(
            "custom_socket",
            {"message": "Advance Deposits Created", "data": doc.__dict__},
        )
        user_name = frappe.session.user
        get_data = frappe.db.get_list(
            doctype="Documents", filters={"confirmation_number": doc.conformation_no}
        )
        date_time = datetime.datetime.now()
        date_time = date_time.strftime("%Y-%m-%d %H:%M:%S")
        activity_data = {
            "doctype": "Activity Logs",
            "datetime": date_time,
            "confirmation_number": doc.conformation_no,
            "module": "Sign Ezy",
            "event": "PreArrivals",
            "user": user_name,
            "activity": "Advance Deposits Created successfully",
        }
        event_doc = frappe.get_doc(activity_data)
        event_doc.insert()
        frappe.db.commit()
        if len(get_data) == 0:
            user_name = frappe.session.user
            data = {
                "doctype": "Documents",
                "advance_deposits_file": doc.file_path,
                "confirmation_number": doc.conformation_no,
                "module_name": "Sign Ezy",
                "user": user_name,
            }
            get_doc = frappe.get_doc(data)
            get_doc.insert()
            frappe.db.commit()
        user_name = frappe.session.user
        data = {
            "advance_deposits_file": doc.file_path,
            "confirmation_number": doc.conformation_no,
            "module_name": "Sign Ezy",
            "user": user_name,
        }
        get_doc = frappe.db.set_value("Documents", get_data[0]["name"], data)
        frappe.db.commit()
    except Exception as e:
        print(e)


def create_encashment_certificates(doc, method=None):
    try:
        frappe.publish_realtime(
            "custom_socket",
            {"message": "Encashment Certifcates Created", "data": doc.__dict__},
        )
    except Exception as e:
        print(e)


def create_payment_receipts(doc, method=None):
    try:
        frappe.publish_realtime(
            "custom_socket",
            {"message": "Payment Receipts Created", "data": doc.__dict__},
        )
    except Exception as e:
        print(e)


def create_pos_bill(doc, method=None):
    try:
        frappe.publish_realtime(
            "custom_socket", {"message": "Pos Bills Created", "data": doc.__dict__}
        )
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("create_pos_bill","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
        return {"success":False,"message":str(e)}


# def create_pos_checks(doc, method=None):
#     try:
#         if doc.pos_bill:
#             enqueue(
#                 extract_data_from_pos_check,
#                 queue="default",
#                 timeout=800000,
#                 event="data_extraction",
#                 now=True,
#                 data={
#                     "pos_bill": doc.pos_bill
#                 },
#                 is_async=True,
#             )
#         frappe.publish_realtime(
#             "custom_socket", {"message": "Pos Bills Created", "data": doc.__dict__}
#         )
#     except Exception as e:
#         exc_type, exc_obj, exc_tb = sys.exc_info()
#         frappe.log_error("create_pos_checks","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
#         return {"success":False,"message":str(e)}

@frappe.whitelist(allow_guest=True)
def extract_data_from_pos_check(data={}):
    try:
        pos_date = ""
        if data["pos_bill"].count("@") == 2:
            date_extract = re.search("@(.*)@", data["file_name"])
            if date_extract:
                pos_date = date_extract.group(1)
        if isinstance(data,str):
            data = json.loads(data)
        company = frappe.get_last_doc("company")
        image_to_base = convert_image_to_base64(data["pos_bill"])
        if not image_to_base["success"]:
            return image_to_base
        # with open('/home/caratred/Music/readme.txt', 'w') as f:
        #     f.write(image_to_base["data"])
        post_data = {
            "base": image_to_base["data"]
        }
        # image_response = requests.post(company.pos_bill_domain,
        #     json=post_data,
        # )
        total_data = {}
        if company.skip_pos_check_data_extraction == 0:
            if company.proxy == 1:
                proxyhost = company.proxy_url
                proxyhost = proxyhost.replace("http://","@")
                proxies = {'https':'https://'+company.proxy_username+":"+company.proxy_password+proxyhost}
            if company.proxy == 0:
                if company.skip_ssl_verify == 0:
                    image_response = requests.post(
                        company.pos_bill_domain,
                        json=post_data,verify=False)
                else:
                    image_response = requests.post(
                        company.pos_bill_domain,
                        json=post_data,verify=False)
            else:
                image_response = requests.post(
                    company.pos_bill_domain,
                    json=post_data,
                    proxies=proxies,verify=False)
            if image_response.status_code == 200:
                image_response = image_response.json()
                extract = extract_data(image_response["data"],company)
                extract_outlet = get_outlet_from_check(image_response["data"])
                total_data["payload"] = image_response["data"]
                # outlet_short_cut = None
                if extract_outlet["success"]:
                    total_data["outlet"] = extract_outlet["outlet"]
                    # outlet_short_cut = extract_outlet["outlet_short_name"]
                if extract["success"]:
                    if "check_date" in extract["data"]:
                        total_data["detected_check_date"] = extract["data"]["check_date"]
                        del extract["data"]["check_date"] # delete check Date
                    if pos_date != "":
                        total_data["check_date"] = pos_date
                    total_data.update(extract["data"])
                    # pos_date = datetime.datetime.strptime(extract["data"]["check_date"],'%Y-%m-%d').strftime('%d-%m-%Y')
                    if "check_date" in extract["data"] and "check_no" in extract["data"]:
                        total_data["pos_check_reference_number"] = extract["data"]["check_date"]+"-"+extract["data"]["check_no"]
                        # if outlet_short_cut:
                        #     total_data["pos_check_reference"] = extract["data"]["check_date"]+"-"+outlet_short_cut+"-"+extract["data"]["check_no"]
                        # else:
                        #     frappe.log_error("outlet_short_name","Please provide the outlet short name")
                        if frappe.db.exists("POS Checks",{"pos_check_reference_number": total_data["pos_check_reference_number"]}):
                            cwd = os.getcwd()
                            site_name = cstr(frappe.local.site)
                            get_files = frappe.db.get_list("POS Checks", filters ={"pos_check_reference_number": total_data["pos_check_reference_number"]}, pluck="pos_bill")
                            if data["pos_bill"] in get_files:
                                frappe.db.sql("""update `tabPOS Checks` set pos_bill='{}' where pos_check_reference_number = '{}'""".format(data["pos_bill"],total_data["pos_check_reference_number"]))
                                frappe.db.commit()
                                return True
                            get_files.append(data["pos_bill"])
                            result = fitz.open()
                            for each in get_files:
                                file_path = cwd + "/" + site_name + each
                                with fitz.open(file_path) as mfile:
                                    result.insertPDF(mfile)
                            file_path = cwd + "/" + site_name + "/public/files/" + total_data["pos_check_reference_number"] + '.pdf'
                            result.save(file_path)
                            files_new = {"file": open(file_path, 'rb')}
                            payload_new = {'is_private': 1, 'folder': 'Home'}
                            file_response = requests.post(company.host+"api/method/upload_file", files=files_new,
                                                        data=payload_new, verify=False).json()
                            if "file_url" in file_response["message"].keys():
                                os.remove(file_path)
                            else:
                                return False
                            frappe.db.sql("""update `tabPOS Checks` set pos_bill='{}' where pos_check_reference_number = '{}'""".format(file_response["message"]["file_url"],total_data["pos_check_reference_number"]))
                            frappe.db.commit()
                            return True
                        invoice_number = frappe.db.get_value('Items', {'reference_check_number': total_data["pos_check_reference_number"]}, ["parent"])
                        if invoice_number:
                            total_data["sync"] = "Yes"
                            total_data["attached_to"] = invoice_number
        else:
            if pos_date != "":
                total_data["check_date"] = pos_date
        total_data["pos_bill"] = data["pos_bill"]
        total_data["company"] = company.name
        total_data["doctype"] = "POS Checks"
        if "check_no" in total_data:
            total_data["detected_check_number"] = total_data["check_no"]
            # del total_data["check_no"] # delete check Number
        total_data["check_type"] = "Check Closed"
        get_doc = frappe.get_doc(total_data)
        get_doc.insert()
        frappe.db.commit()
        if "pos_check_reference_number" in total_data:
            frappe.db.sql("""update `tabItems` set pos_check='{}' where reference_check_number='{}'""".format(get_doc.name, total_data["pos_check_reference_number"]))
            frappe.db.commit()
        frappe.publish_realtime("custom_socket", {"message": "POS Checks", "data": get_doc.as_dict()})
        return True
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("extract_data_from_pos_check","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
        return {"success":False,"message":str(e)}

# @frappe.whitelist(allow_guest=True)
# def extract_data_from_invoice(data={}):
#     try:
#         check_num = frappe.db.get_value('POS Checks',{'pos_check_reference_number': "reference_check_number"}, ["parent"])
#         print(check_num,";;;;;;;;;;;;")
#     except Exception as e:
#         exc_type, exc_obj, exc_tb = sys.exc_info()
#         frappe.log_error("extract_data_from_invoice","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
#         return {"success":False,"message":str(e)}

def deleteemailfilesdaily():
    try:
        lastdate = date.today() - timedelta(days=1)
        emaildata = frappe.db.get_list(
            "Email Queue",
            filters={"creation": [">", lastdate], "status": "Sent"},
            fields=["name", "attachments"],
        )
        filelist = []
        if len(emaildata) > 0:
            for each in emaildata:
                value = json.loads(each.attachments)
                filelist.append(value[0]["fid"])
                delete = frappe.delete_doc("File", value[0]["fid"])
                print(delete)
        lastdate = date.today() - timedelta(days=6)
        frappe.db.sql("""DELETE FROM `tabDocument Bin` WHERE creation < %s""", lastdate)
        frappe.db.commit()
        return {"success": True}
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("Ezy-invoicing deletemailfilesdaily Event","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
        return {"success":False,"message":str(e)}

@frappe.whitelist(allow_guest=True)
def delete_error_logs():
    lastdate = date.today() - timedelta(days=7)
    print(lastdate)
    get_list=frappe.db.get_all("Error Log",filters={"creation":["<",lastdate]},pluck="name")
    print(get_list)
    # data = frappe.db.sql("""DELETE FROM `Error Log` WHERE creation < %s""",lastdate)
    # print(data)
    # frappe.db.commit()
    # return {"success":True}

def gspmeteringhook(doc, method=None):
    try:
        company = frappe.get_last_doc("company")
        inputData = {
            "data": {
                "doctype": "Gsp Metering",
                "property_code": company.name,
                "tax_payer_details": doc.tax_payer_details,
                "login": doc.login,
                "generate_irn": doc.generate_irn,
                "get_irn_details_by_doc": doc.get_irn_details_by_doc,
                "cancel_irn": doc.cancel_irn,
                "invoice_by_irn": doc.invoice_by_irn,
                "create_qr_image": doc.create_qr_image,
                "status": doc.status,
            }
        }
        headers = {"Content-Type": "application/json"}
        if company.mode == "Production":
            if company.proxy == 1:
                proxyhost = company.proxy_url
                proxyhost = proxyhost.replace("http://", "@")
                proxies = {
                    "http": "http://"
                    + company.proxy_username
                    + ":"
                    + company.proxy_password
                    + proxyhost,
                    "https": "https://"
                    + company.proxy_username
                    + ":"
                    + company.proxy_password
                    + proxyhost,
                }
                json_response = requests.post(
                    company.licensing_host
                    + "/api/method/ezylicensing.ezylicensing.getcount.gspmetering_post",
                    headers=headers,
                    json=inputData,
                    proxies=proxies,
                    verify=False,
                )
            else:
                if company.skip_ssl_verify == 1:
                    json_response = requests.post(
                        company.licensing_host
                        + "/api/method/ezylicensing.ezylicensing.getcount.gspmetering_post",
                        headers=headers,
                        json=inputData,
                        verify=False,
                    )
                else:
                    json_response = requests.post(
                        company.licensing_host
                        + "/api/method/ezylicensing.ezylicensing.getcount.gspmetering_post",
                        headers=headers,
                        json=inputData,
                        verify=False,
                    )
            return json_response
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error(
            "Ezy-invoicing gspmeteringhook Event",
            "line No:{}\n{}".format(exc_tb.tb_lineno, traceback.format_exc()),
        )
        print(str(e))


def taxpayerhook(doc, method=None):
    try:
        company = frappe.get_doc("company", doc.company)
        headers = {"Content-Type": "application/json"}

        inputData = {
            "doctype": "TaxPayerDetail",
            "gst_number": doc.gst_number,
            "legal_name": doc.legal_name,
            "email": doc.email,
            "address_1": doc.address_1,
            "address_2": doc.address_2,
            "location": doc.location,
            "pincode": doc.pincode,
            "gst_status": doc.gst_status,
            "tax_type": doc.tax_type,
            "trade_name": doc.trade_name,
            "phone_number": doc.phone_number,
            "state_code": doc.state_code,
            "address_floor_number": doc.address_floor_number,
            "address_street": doc.address_street,
            "status": doc.status,
            "block_status": doc.block_status,
        }
        if company.mode == "Production":
            if company.proxy == 1:
                proxyhost = company.proxy_url
                proxyhost = proxyhost.replace("http://", "@")
                proxies = {
                    "http": "http://"
                    + company.proxy_username
                    + ":"
                    + company.proxy_password
                    + proxyhost,
                    "https": "https://"
                    + company.proxy_username
                    + ":"
                    + company.proxy_password
                    + proxyhost,
                }
                insertTaxpayer = requests.post(
                    company.licensing_host + "/api/resource/TaxPayerDetail",
                    headers=headers,
                    json=inputData,
                    proxies=proxies,
                    verify=False,
                )
            else:
                if company.skip_ssl_verify == 1:
                    insertTaxpayer = requests.post(
                        company.licensing_host + "/api/resource/TaxPayerDetail",
                        headers=headers,
                        json=inputData,
                        verify=False,
                    )
                else:
                    insertTaxpayer = requests.post(
                        company.licensing_host + "/api/resource/TaxPayerDetail",
                        headers=headers,
                        json=inputData,
                        verify=False,
                    )
            if insertTaxpayer.status_code == 200:
                print("--------- Taxpayer hook")
            return insertTaxpayer
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error(
            "Ezy-invoicing taxpayerhook Event",
            "line No:{}\n{}".format(exc_tb.tb_lineno, traceback.format_exc()),
        )
        print(str(e))


def InvoiceDataTolicensing():
    try:
        company = frappe.get_last_doc("company")
        if company.mode == "Production":
            today = date.today()  # - timedelta(days=43)
            Invoice_count = frappe.db.get_list(
                "Invoices",
                filters={"creation": ["Between", [today, today]], "mode": "Testing"},
                fields=["count(name) as count", "invoice_category", "mode"],
                group_by="invoice_category",
            )
            Invoice_count2 = frappe.db.get_list(
                "Invoices",
                filters={"creation": ["Between", [today, today]], "mode": "Production"},
                fields=["count(name) as count", "invoice_category", "mode"],
                group_by="invoice_category",
            )
            headers = {"Content-Type": "application/json"}

            if len(Invoice_count) > 0:
                inputData = {
                    "data": {
                        "date": str(today),
                        "property_code": company.name,
                        "mode": "Testing",
                    }
                }
                for each in Invoice_count:
                    if each["invoice_category"] == "Tax Invoice":
                        inputData["data"]["taxinvoices"] = each["count"]
                    if each["invoice_category"] == "Debit Invoice":
                        inputData["data"]["debitinvoices"] = each["count"]
                    if each["invoice_category"] == "Credit Invoice":
                        inputData["data"]["creditinvoices"] = each["count"]
                requests.post(
                    company.licensing_host
                    + "/api/method/ezylicensing.ezylicensing.getcount.invoice_post",
                    headers=headers,
                    json=inputData,
                    verify=False,
                )

            if len(Invoice_count2) > 0:
                inputData = {
                    "data": {
                        "date": str(today),
                        "property_code": company.name,
                        "mode": "Production",
                    }
                }
                for each in Invoice_count2:
                    if each["invoice_category"] == "Tax Invoice":
                        inputData["data"]["taxinvoices"] = each["count"]
                    if each["invoice_category"] == "Debit Invoice":
                        inputData["data"]["debitinvoices"] = each["count"]
                    if each["invoice_category"] == "Credit Invoice":
                        inputData["data"]["creditinvoices"] = each["count"]
                requests.post(
                    company.licensing_host
                    + "/api/method/ezylicensing.ezylicensing.getcount.invoice_post",
                    headers=headers,
                    json=inputData,
                    verify=False,
                )
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error(
            "Ezy-invoicing InvoiceDataToLicensing Event",
            "line No:{}\n{}".format(exc_tb.tb_lineno, traceback.format_exc()),
        )
        return {"success": True, "message": str(e)}


def dailyDeletedocumentBin():
    try:
        lastdate = date.today() - timedelta(days=6)
        frappe.db.sql("""DELETE FROM `tabDocument Bin` WHERE creation < %s""", lastdate)
        frappe.db.commit()
        return {"success": True}
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error(
            "Ezy-invoicing dailyDeletedocumentBin Event",
            "line No:{}\n{}".format(exc_tb.tb_lineno, traceback.format_exc()),
        )
        return {"success": False, "message": str(e)}


def dailyIppprinterFiles():
    try:
        company = frappe.get_last_doc("company")
        shutil.rmtree(company.ipp_printer_file_path)
        os.mkdir(company.ipp_printer_file_path)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error(
            "Ezy-invoicing dailyIppprinterFiles Event",
            "line No:{}\n{}".format(exc_tb.tb_lineno, traceback.format_exc()),
        )
        print(str(e))


@frappe.whitelist(allow_guest=True)
def updatepropertiesdetails():
    try:
        gspdetails = frappe.get_last_doc("GSP APIS")
        company = frappe.get_last_doc("company")
        inputData = {
            "data": {
                "doctype": "Properties",
                "company_code": company.name,
                "api_key": gspdetails.gsp_prod_app_id,
                "api_secret": gspdetails.gsp_prod_app_secret,
                "gst_prod_username": gspdetails.gst__prod_username,
                "gst_prod_password": gspdetails.gst_prod_password,
                "gsp_test_app_id": gspdetails.gsp_test_app_id,
                "gsp_test_app_secret": gspdetails.gsp_test_app_secret,
                "gst_test_username": gspdetails.gst__test_username,
                "gst_test_password": gspdetails.gst_test_password,
                "groups": company.property_group,
                "mode": company.mode,
            }
        }
        headers = {"Content-Type": "application/json"}
        if company.mode == "Production":
            if company.proxy == 1:
                proxyhost = company.proxy_url
                proxyhost = proxyhost.replace("http://", "@")
                proxies = {
                    "http": "http://"
                    + company.proxy_username
                    + ":"
                    + company.proxy_password
                    + proxyhost,
                    "https": "https://"
                    + company.proxy_username
                    + ":"
                    + company.proxy_password
                    + proxyhost,
                }
                json_response = requests.post(
                    company.licensing_host
                    + "/api/method/ezylicensing.ezylicensing.doctype.properties.properties.update_property_status",
                    headers=headers,
                    json=inputData,
                    proxies=proxies,
                    verify=False,
                )
            else:
                if company.skip_ssl_verify == 1:
                    json_response = requests.post(
                        company.licensing_host
                        + "/api/method/ezylicensing.ezylicensing.doctype.properties.properties.update_property_status",
                        headers=headers,
                        json=inputData,
                        verify=False,
                    )
                else:
                    json_response = requests.post(
                        company.licensing_host
                        + "/api/method/ezylicensing.ezylicensing.doctype.properties.properties.update_property_status",
                        headers=headers,
                        json=inputData,
                        verify=False,
                    )
            return json_response.json()
        return {"success": True, "message": "Property is in Testing Mode"}
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error(
            "Ezy-updatepropertiesdetails",
            "line No:{}\n{}".format(exc_tb.tb_lineno, traceback.format_exc()),
        )
        return {"success": False, "message": str(e)}


def promotionsSocket(doc, method=None):
    try:
        frappe.publish_realtime(
            "custom_socket", {"message": "Promotions Created", "data": doc.__dict__}
        )
    except Exception as e:
        print(str(e))


def deletePromotionsSocket(doc, method=None):
    try:
        frappe.publish_realtime(
            "custom_socket", {"message": "Promotions Deleted", "data": doc.__dict__}
        )
    except Exception as e:
        print(str(e))


@frappe.whitelist(allow_guest=True)
def block_irn():
    try:
        company = frappe.get_last_doc("company")
        url_property = requests.get(
            company.licensing_host + "/api/resource/Properties/" + company.company_code
        )
        json_property = url_property.json()
        if url_property.status_code == 200:
            company.block_irn = json_property["data"]["block_irn"]
            company.block_print = json_property["data"]["block_print"]
            company.sign_ezy_module = json_property["data"]["signezy"]
            company.scan_ezy_module = json_property["data"]["scanezy"]
            company.ezy_checkins_module = json_property["data"]["ezycheckins"]
            company.pos_bills_module = (
                "Enable"
                if json_property["data"]["pos_bills"] == 1
                else "Disable"
            )
            company.save(ignore_permissions=True)
            frappe.db.commit()
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error(
            "Ezy-block-IRN",
            "line No:{}\n{}".format(exc_tb.tb_lineno, traceback.format_exc()),
        )
        return {"success": False, "message": str(e)}


@frappe.whitelist(allow_guest=True)
def backup_file_perticulerdoctypes(data):
    try:
        get_company=frappe.db.get_value("company",{"name":data["company_code"]},["host","site_name"])
        if get_company:
            site_name = cstr(frappe.local.site)
            run_command=os.system('bench --site {} backup --only "company,SAC HSN CODES,Payment Types,GSP APIS"'.format(site_name))
            cwd= os.getcwd() 
            # site_name = cstr(frappe.local.site)
            mypath = cwd+"/"+site_name+"/private/backups/*.gz"
            filename=max(glob.glob(mypath), key=os.path.getmtime)
            shutil.move(filename,cwd+"/"+site_name+"/public/files")
            return "/files/{}".format(os.path.basename(filename))
        return {"success":False,"message": "something went wrong"}
    except Exception as e:
        frappe.log_error("backupfile:" + str(e))


@frappe.whitelist(allow_guest=True)
def arrival_information(doc, method=None):
    try:
        user_name = frappe.session.user
        date_time = datetime.datetime.now()
        date_time = date_time.strftime("%Y-%m-%d %H:%M:%S")
        get_dropbox_details = frappe.db.get_list(
            "Dropbox",
            filters={"reservation_no": doc.name, "merged": "Not merged"}, fields=["name"]
        )
        if len(get_dropbox_details) > 0:
            for each in get_dropbox_details:
                frappe.db.set_value(
                        "Dropbox",
                        each["name"],
                        {
                            "merged_to": doc.name,
                            "merged": "Merged",
                            "reservation_found": 1,
                            "merged_on": date_time,
                        },
                    )
                frappe.db.commit()
                merge_guest_details = merge_guest_to_guest_details(each["name"])
                if not merge_guest_details["success"]:
                    frappe.log_error(
                        "Ezy-merge_guest_details", merge_guest_details["message"]
                    )    
        data = {
            "doctype": "Activity Logs",
            "datetime": date_time,
            "confirmation_number": doc.confirmation_number,
            "module": "Sign Ezy",
            "event": "PreArrivals",
            "user": user_name,
            "activity": "Reservation Created",
        }
        get_doc = frappe.get_doc(data)
        get_data = frappe.db.get_list(
            doctype="Documents",
            filters={"confirmation_number": doc.confirmation_number},
        )
        get_doc.insert()
        frappe.db.commit()
        data_get = {
            "doctype": "Documents",
            "number_of_guests": doc.number_of_guests,
            "confirmation_number": doc.confirmation_number,
        }
        if len(get_data) == 0:
            get_doc = frappe.get_doc(data_get)
            get_doc.insert()
            frappe.db.commit()
        else:
            frappe.db.set_value(
                "Documents",
                get_data[0]["name"],
                {"number_of_guests": doc.number_of_guests},
            )
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error(
            "Ezy-arrival_information",
            "line No:{}\n{}".format(exc_tb.tb_lineno, traceback.format_exc()),
        )
        return {"success": False, "message": str(e)}


@frappe.whitelist(allow_guest=True)
def send_invoice_mail_scheduler():
    try:
        get_arrivals = frappe.db.get_list(
            "Arrival Information",
            filters={
                "guest_eamil2": ["!=", ""],
                "send_invoice_mail": ["=", 1],
                "invoice_send_mail_send": ["=", 0],
            },
        )
        if len(get_arrivals) > 0:
            for each in get_arrivals:
                get_arrivals = frappe.get_doc("Arrival Information", each["name"])
                if frappe.db.exists(
                    {"doctype": "Invoices", "confirmation_number": each["name"]}
                ):
                    get_doc = frappe.db.get_value(
                        "Invoices",
                        {"confirmation_number": each["name"]},
                        ["invoice_file", "name"],
                        as_dict=True,
                    )
                    b2csuccess = frappe.get_doc("Email Template", "Scan Ezy")
                    files = frappe.db.get_list(
                        "File",
                        filters={"file_url": ["=", get_doc["invoice_file"]]},
                        fields=["name"],
                    )
                    attachments = [files[0]["name"]]
                    get_email_sender = frappe.db.get_list(
                        "Email Account",
                        filters=[["default_outgoing", "=", 1]],
                        fields=["email_id"],
                    )
                    if len(get_email_sender) == 0:
                        return {
                            "success": False,
                            "message": "Make one smtp as a defalut outgoing",
                        }
                    get_email_sender = get_email_sender[0]
                    make(
                        recipients=get_arrivals.guest_eamil2,
                        # cc = '',
                        sender=get_email_sender["email_id"],
                        subject=b2csuccess.subject,
                        content=b2csuccess.response,
                        doctype="Invoices",
                        name=get_doc["name"],
                        attachments=attachments,
                        send_email=1,
                    )
                    get_arrivals.invoice_send_mail_send = 1
                    get_arrivals.save(ignore_permissions=True, ignore_version=True)
                    frappe.db.commit()
                    return {"success": True, "message": "Mail Send"}
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error(
            "Ezy-send_invoice_mail",
            "line No:{}\n{}".format(exc_tb.tb_lineno, traceback.format_exc()),
        )
        return {"success": False, "message": str(e)}


# @frappe.whitelist(allow_guest=True)
def guest_attachments(doc, method=None):
    try:
        # print("/////////////////")
        user_name = frappe.session.user
        date_time = datetime.datetime.now()
        date_time = date_time.strftime("%Y-%m-%d %H:%M:%S")
        activity_data = {
            "doctype": "Activity Logs",
            "datetime": date_time,
            "confirmation_number": doc.confirmation_number,
            "module": "Passport Scanner",
            "event": "PreArrivals",
            "user": user_name,
            "activity": "guest details added successfully",
            "status": doc.status,
        }
        event_doc = frappe.get_doc(activity_data)
        event_doc.insert()
        frappe.db.commit()
        get_data = frappe.db.get_list(
            doctype="Documents",
            filters={"confirmation_number": doc.confirmation_number},
        )
        if len(get_data) == 0:
            user_name = frappe.session.user
            data = {
                "doctype": "Documents",
                "guest_details": [
                    {
                        "image1": doc.id_image1,
                        "image2": doc.id_image2,
                        "image3": doc.id_image3,
                        "face_image": doc.face_image,
                    }
                ],
                "confirmation_number": doc.confirmation_number,
                "module_name": "Scan Ezy",
                "user": user_name,
            }
            get_doc = frappe.get_doc(data)
            get_doc.insert()
            frappe.db.commit()
        else:
            user_name = frappe.session.user
            data = {
                "confirmation_number": doc.confirmation_number,
                "module_name": "Scan Ezy",
                "user": user_name,
            }
            get_doc = frappe.db.set_value("Documents", get_data[0]["name"], data)
            frappe.db.commit()
            update_doc = frappe.get_doc("Documents", get_data[0]["name"])
            update_doc.append(
                "guest_details",
                {
                    "image1": doc.id_image1,
                    "image2": doc.id_image2,
                    "image3": doc.id_image3,
                    "face_image": doc.face_image,
                },
            )
            update_doc.save()
            frappe.db.commit()
        if frappe.db.exists("Arrival Information", doc.confirmation_number):
            arrival_doc = frappe.get_doc("Arrival Information", doc.confirmation_number)
            guest_count = arrival_doc.no_of_adults
            now = datetime.datetime.now()
            doc.no_of_nights = arrival_doc.no_of_nights
            doc.checkin_time = now.strftime("%H:%M:%S")
            added_guest_count = frappe.db.count(
                "Guest Details", {"confirmation_number": doc.confirmation_number}
            )
            if guest_count != 0:
                arrival_doc.booking_status = "CHECKED IN"
                if added_guest_count > guest_count:
                    arrival_doc.no_of_adults = guest_count + 1
            else:
                arrival_doc.no_of_adults = guest_count + 1
                arrival_doc.booking_status = "CHECKED IN"
            arrival_doc.save(ignore_permissions=True, ignore_version=True)
            # if arrival_doc.room_number:
            #     doc.room_number = arrival_doc.room_number
            if arrival_doc.checkin_time:
                doc.checkin_time = arrival_doc.checkin_time
            if arrival_doc.checkout_time:
                doc.checkout_time = arrival_doc.checkout_time
            doc.checkout_date = (
                frappe.utils.formatdate(arrival_doc.departure_date, "yyyy-mm-dd")
                if arrival_doc.departure_date
                else None
            )
            doc.checkin_date = (
                frappe.utils.formatdate(arrival_doc.arrival_date, "yyyy-mm-dd")
                if arrival_doc.arrival_date
                else None
            )
            if doc.main_guest == 1:
                doc.no_of_adults = 1
            else:
                guest_doc = frappe.get_doc("Guest Details", doc.name)
                guest_doc.no_of_adults = arrival_doc.no_of_adults
                guest_doc.save(ignore_permissions=True, ignore_version=True)
                frappe.db.commit()
            doc.no_of_children = arrival_doc.no_of_children
        given_name = doc.guest_first_name if doc.guest_first_name else ""
        surname = doc.guest_last_name if doc.guest_last_name else ""
        if doc.guest_id_type == "Foreigner":
            if frappe.db.exists(
                {
                    "doctype": "Precheckins",
                    "confirmation_number": data["confirmation_number"],
                }
            ):
                pre_checkins = frappe.db.get_value(
                    "Precheckins",
                    {"confirmation_number": data["confirmation_number"]},
                    ["address1", "guest_city", "guest_country"],
                    as_dict=1,
                )
                doc.address = pre_checkins["address1"]
                doc.city = pre_checkins["guest_city"]
                doc.country = pre_checkins["guest_country"]
        if doc.guest_dob is not None:
            today = datetime.datetime.today()
            birthDate = datetime.datetime.strptime(str(doc.guest_dob), '%Y-%m-%d')
            doc.guest_age= (
                today.year
                - birthDate.year
                - ((today.month, today.day) < (birthDate.month, birthDate.day))
            )
        doc.guest_full_name = given_name + " " + surname
        # doc.save(ignore_permissions=True, ignore_version=True)
        # frappe.db.commit()
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error(
            "Ezy-Guest Attachments",
            "line No:{}\n{}".format(exc_tb.tb_lineno, traceback.format_exc()),
        )
        return {"success": False, "message": str(e)}


@frappe.whitelist(allow_guest=True)
def guest_update_attachment_logs(doc, method=None):
    try:
        data = {}
        if frappe.db.exists("Arrival Information", doc.confirmation_number):
            arrival_doc = frappe.get_doc("Arrival Information", doc.confirmation_number)
            guest_count = arrival_doc.no_of_adults
            now = datetime.datetime.now()
            data["no_of_nights"] = arrival_doc.no_of_nights
            data["checkin_time"] = now.strftime("%H:%M:%S")
            added_guest_count = frappe.db.count(
                "Guest Details", {"confirmation_number": doc.confirmation_number}
            )
            if guest_count != 0:
                arrival_doc.booking_status = "CHECKED IN"
                if added_guest_count > guest_count:
                    arrival_doc.no_of_adults = guest_count + 1
            else:
                arrival_doc.no_of_adults = guest_count + 1
                arrival_doc.booking_status = "CHECKED IN"
            arrival_doc.save(ignore_permissions=True, ignore_version=True)
            # if arrival_doc.room_number != None:
            #     data["room_number"] = arrival_doc.room_number
            if arrival_doc.checkin_time:
                data["checkin_time"] = arrival_doc.checkin_time
            if arrival_doc.checkout_time:
                data["checkout_time"] = arrival_doc.checkout_time
            data["checkout_date"] = (
                frappe.utils.formatdate(arrival_doc.departure_date, "yyyy-mm-dd")
                if arrival_doc.departure_date
                else None
            )
            data["checkin_date"] = (
                frappe.utils.formatdate(arrival_doc.arrival_date, "yyyy-mm-dd")
                if arrival_doc.arrival_date
                else None
            )
            if doc.main_guest == 1:
                data["no_of_adults"] = 1
            else:
                data["no_of_adults"] = arrival_doc.no_of_adults
            data["no_of_children"] = arrival_doc.no_of_children
        given_name = doc.guest_first_name if doc.guest_first_name else ""
        surname = doc.guest_last_name if doc.guest_last_name else ""
        if doc.guest_id_type == "Foreigner":
            if frappe.db.exists(
                {
                    "doctype": "Precheckins",
                    "confirmation_number": doc.confirmation_number,
                }
            ):
                pre_checkins = frappe.db.get_value(
                    "Precheckins",
                    {"confirmation_number": doc.confirmation_number},
                    ["address1", "guest_city", "guest_country"],
                    as_dict=1,
                )
                data["address"] = pre_checkins["address1"]
                data["city"] = pre_checkins["guest_city"]
                data["country"] = pre_checkins["guest_country"]
        if doc.guest_dob is not None:
            today = datetime.datetime.today()
            birthDate = datetime.datetime.strptime(str(doc.guest_dob), '%Y-%m-%d')
            data["guest_age"] = (
                today.year
                - birthDate.year
                - ((today.month, today.day) < (birthDate.month, birthDate.day))
            )
        data["guest_full_name"] = given_name + " " + surname
        frappe.db.set_value(
            "Guest Details", doc.name, data
        )
        frappe.db.commit()
        user_name = frappe.session.user
        date_time = datetime.datetime.now()
        date_time = date_time.strftime("%Y-%m-%d %H:%M:%S")
        activity_data = {
            "doctype": "Activity Logs",
            "datetime": date_time,
            "confirmation_number": doc.confirmation_number,
            "module": "Passport Scanner",
            "event": "PreArrivals",
            "user": user_name,
            "activity": "guest details changed successfully",
            "status": doc.status,
        }
        event_doc = frappe.get_doc(activity_data)
        event_doc.insert(ignore_permissions=True)
        frappe.db.commit()
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error(
            "Ezy-invoicing guest update attachment logs",
            "line No:{}\n{}".format(exc_tb.tb_lineno, traceback.format_exc()),
        )
        return {"success": False, "message": str(e)}


@frappe.whitelist(allow_guest=True)
def send_email(confirmation_number, company):
    user_name = frappe.session.user
    company_doc = frappe.get_doc("company", company)
    folder_path = frappe.utils.get_bench_path()
    site_folder_path = company_doc.site_name
    file_path = (
        folder_path
        + "/sites/"
        + site_folder_path
        + company_doc.pre_checkin_mail_content
    )
    arrival_doc = frappe.get_doc("Arrival Information", confirmation_number)
    date_time = datetime.datetime.now()
    f = open(file_path, "r")
    data = f.read()
    company_doc.save()
    frappe.db.commit()
    f.close
    data = data.replace("{{name}}", arrival_doc.guest_first_name)
    data = data.replace("{{lastName}}", arrival_doc.guest_last_name)
    data = data.replace("{{hotelName}}", company_doc.company_name)
    logopath = folder_path + "/sites/" + site_folder_path + company_doc.company_logo
    logofilename, logofile_extension = os.path.splitext(logopath)
    baneer_image = folder_path + "/sites/" + site_folder_path + company_doc.email_banner
    bannerfilename, bannerfile_extension = os.path.splitext(baneer_image)
    with open(baneer_image, "rb") as f:
        filecontent = f.read()
    # final_banner_string = "cid:{}".format(filecontent)
    with open(logopath, "rb") as f:
        logofilecontent = f.read()
    # data = data.replace('headerBG',final_banner_string)
    # data = data.replace('logoImg',final_logo_string)
    data = data.replace("{{email}}", company_doc.email)
    data = data.replace("{{phone}}", company_doc.phone_number)
    url = (
        "https://so.ezycheckins.com/v2/?hotelId={}&confirmation={}&source=email".format(
            company_doc.name, confirmation_number
        )
    )
    data = data.replace("{{url}}", url)
    frappe.sendmail(
        recipients="kiran@caratred.com",
        subject=company_doc.pre_checkin_mail_subject,
        message=data,
        now=True,
    )
    activity_data = {
        "doctype": "Activity Logs",
        "datetime": date_time,
        "confirmation_number": arrival_doc.confirmation_number,
        "module": "Ezycheckins",
        "event": "PreArrivals",
        "user": user_name,
        "activity": "Email Sent successfully",
    }
    event_doc = frappe.get_doc(activity_data)
    event_doc.insert()
    frappe.db.commit()


@frappe.whitelist(allow_guest=True)
def pre_mail():
    try:
        user_name = frappe.session.user
        company = frappe.get_last_doc("company")
        if not company.site_domain:
            return {
                "success": False,
                "message": "Please add site domain in property setting",
            }
        if company.mail_schedule == "True":
            convert_days = int(company.no_of_days)
            date_time = datetime.datetime.now()
            future_date = date_time + timedelta(days=convert_days)
            future_date = future_date.strftime("%Y-%m-%d")
            get_arrival_data = frappe.db.get_list(
                "Arrival Information",
                filters={
                    "booking_status": ["in", ["RESERVED", "DUE IN"]],
                    "arrival_date": ["=", future_date],
                    "guest_email_address": ["is", "set"],
                },
                fields=[
                    "arrival_date",
                    "name",
                    "guest_email_address",
                    "mail_sent",
                    "mail_via",
                    "guest_first_name",
                    "guest_last_name",
                    "confirmation_number",
                ],
            )
            now = datetime.datetime.now()
            current_time = now.strftime("%H:%M")
            time_company = str(company.mail_schedule_time)[:-3:]
            str_date = str(company.mail_schedule_time + timedelta(minutes=1))[:-3:]
            folder_path = frappe.utils.get_bench_path()
            site_folder_path = company.site_name
            file_path = (
                folder_path
                + "/sites/"
                + site_folder_path
                + company.pre_checkin_mail_content
            )
            if current_time >= time_company and current_time < str_date:
                time.sleep(60)
                if company.mail_frequency == "Once":
                    for x in get_arrival_data:
                        guest_first_name = str(x["guest_first_name"])
                        email_address = str(x["guest_email_address"])
                        guest_last_name = str(x["guest_last_name"])
                        conf_number = str(x["confirmation_number"])
                        f = open(file_path, "r")
                        data = f.read()
                        data = data.replace("{{name}}", guest_first_name)
                        data = data.replace("{{lastName}}", guest_last_name)
                        data = data.replace("{{hotelName}}", company.company_name)
                        data = data.replace("{{email}}", company.email)
                        data = data.replace("{{phone}}", company.phone_number)
                        company_logo = (company.site_domain).rstrip(
                            "/"
                        ) + company.company_logo
                        data = data.replace("logoImg", company_logo)
                        bg_logo = (company.site_domain).rstrip(
                            "/"
                        ) + company.email_banner
                        data = data.replace("headerBG", bg_logo)
                        url = (
                            "{}?company={}&confirmation_number={}&source=email".format(
                                company.ezycheckins_socket_host,
                                company.name,
                                conf_number,
                            )
                        )
                        tiny_url = ps.Shortener().tinyurl.short(url)
                        data = data.replace("{{url}}", tiny_url)
                        if x["mail_sent"] == "No":
                            frappe.sendmail(
                                recipients=email_address,
                                subject=company.pre_checkin_mail_subject,
                                message=data,
                                now=True,
                            )
                            frappe.db.set_value(
                                "Arrival Information", x["name"], "mail_sent", "Yes"
                            )
                            frappe.db.set_value(
                                "Arrival Information",
                                x["name"],
                                "mail_via",
                                "Automatic",
                            )
                            activity_data = {
                                "doctype": "Activity Logs",
                                "datetime": date_time,
                                "confirmation_number": conf_number,
                                "module": "Ezycheckins",
                                "event": "PreArrivals",
                                "user": user_name,
                                "activity": "Email Sent successfully by System",
                            }
                            event_doc = frappe.get_doc(activity_data)
                            event_doc.insert()
                            frappe.db.commit()
                    return {"success": False, "message": "Invitation Sent"}
                elif company.mail_frequency == "Daily":
                    for x in get_arrival_data:
                        email_address = str(x["guest_email_address"])
                        guest_first_name = str(x["guest_first_name"])
                        guest_last_name = str(x["guest_last_name"])
                        conf_number = str(x["confirmation_number"])
                        f = open(file_path, "r")
                        data = f.read()
                        data = data.replace("{{name}}", guest_first_name)
                        data = data.replace("{{lastName}}", guest_last_name)
                        data = data.replace("{{hotelName}}", company.company_name)
                        data = data.replace("{{email}}", company.email)
                        data = data.replace("{{phone}}", company.phone_number)
                        company_logo = (company.site_domain).rstrip(
                            "/"
                        ) + company.company_logo
                        data = data.replace("logoImg", company_logo)
                        bg_logo = (company.site_domain).rstrip(
                            "/"
                        ) + company.email_banner
                        data = data.replace("headerBG", bg_logo)
                        url = (
                            "{}?company={}&confirmation_number={}&source=email".format(
                                company.ezycheckins_socket_host,
                                company.name,
                                conf_number,
                            )
                        )
                        tiny_url = ps.Shortener().tinyurl.short(url)
                        data = data.replace("{{url}}", tiny_url)
                        frappe.sendmail(
                            recipients=email_address,
                            subject=company.pre_checkin_mail_subject,
                            message=data,
                            now=True,
                        )
                        frappe.db.set_value(
                            "Arrival Information", x["name"], "mail_sent", "Yes"
                        )
                        frappe.db.set_value(
                            "Arrival Information", x["name"], "mail_via", "Automatic"
                        )
                        activity_data = {
                            "doctype": "Activity Logs",
                            "datetime": date_time,
                            "confirmation_number": conf_number,
                            "module": "Ezycheckins",
                            "event": "PreArrivals",
                            "user": user_name,
                            "activity": "Email Sent successfully by System",
                        }
                        event_doc = frappe.get_doc(activity_data)
                        event_doc.insert()
                        frappe.db.commit()
                    return {"success": True, "message": "Invitation Sent"}
            if company.cancellation_email == 1:
                get_arrival_data = frappe.db.get_list(
                    "Arrival Information",
                    filters={"booking_status": ["=", "CANCELLED"]},
                    fields=[
                        "arrival_date",
                        "name",
                        "guest_email_address",
                        "mail_sent",
                        "mail_via",
                    ],
                )
                for x in get_arrival_data:
                    dt_convert = str(x["arrival_date"])
                    name = str(x["name"])
                    cancel_email_address = str(x["guest_email_address"])
                    arrival_date = datetime.datetime.strptime(
                        dt_convert, "%Y-%m-%d"
                    ).date()
                    folder_path = frappe.utils.get_bench_path()
                    site_folder_path = company.site_name
                    file_path = (
                        folder_path
                        + "/sites/"
                        + site_folder_path
                        + company.cancellation_email_mail_content
                    )
                    if x["mail_sent"] == "No":
                        f = open(file_path, "r")
                        data = f.read()
                        data = data.replace("{{name}}", x["guest_first_name"])
                        # data = data.replace('{{lastName}}',arrival_doc.guest_last_name)
                        data = data.replace("{{hotelName}}", company.company_name)
                        data = data.replace("{{email}}", company.email)
                        data = data.replace("{{phone}}", company.phone_number)
                        frappe.sendmail(
                            recipients=cancel_email_address,
                            subject=company.cancellation_email_mail_content,
                            message=data,
                            now=True,
                        )
                        frappe.db.set_value(
                            "Arrival Information", x["name"], "mail_sent", "Yes"
                        )
                        frappe.db.set_value(
                            "Arrival Information", x["name"], "mail_via", "Automatic"
                        )
                        activity_data = {
                            "doctype": "Activity Logs",
                            "datetime": date_time,
                            "confirmation_number": x["confirmation_number"],
                            "module": "Ezycheckins",
                            "event": "PreArrivals",
                            "user": user_name,
                            "activity": "Cancellation Mail Sent successfully",
                        }
                        event_doc = frappe.get_doc(activity_data)
                        event_doc.insert()
                        frappe.db.commit()
                    else:
                        return {"success": False, "message": "Invitation Sent"}
        else:
            print("schedular is false")
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error(
            "Ezy-pre_mail",
            "line No:{}\n{}".format(exc_tb.tb_lineno, traceback.format_exc()),
        )
        return {"success": False, "message": str(e)}


@frappe.whitelist(allow_guest=True)
def manual_mail(data):
    user_name = frappe.session.user
    date_time = datetime.datetime.now()
    conf_number = data["confirmation_number"]
    email_address = data["guest_email_address"]
    arrival_doc = frappe.get_doc("Arrival Information", conf_number)
    count = arrival_doc.mail_count
    company = frappe.get_last_doc("company")
    if not company.site_domain:
        return {
            "success": False,
            "message": "Please add site domain in property setting",
        }
    folder_path = frappe.utils.get_bench_path()
    site_folder_path = company.site_name
    file_path = (
        folder_path + "/sites/" + site_folder_path + company.pre_checkin_mail_content
    )
    if (
        arrival_doc.booking_status == "RESERVED"
        or arrival_doc.booking_status == "DUE IN"
    ):
        f = open(file_path, "r")
        data = f.read()
        data = data.replace(
            "{{name}}",
            arrival_doc.guest_first_name if arrival_doc.guest_first_name else "",
        )
        data = data.replace(
            "{{lastName}}",
            arrival_doc.guest_last_name if arrival_doc.guest_last_name else "",
        )
        data = data.replace("{{hotelName}}", company.company_name)
        data = data.replace("{{email}}", company.email)
        data = data.replace("{{phone}}", company.phone_number)
        company_logo = (company.site_domain).rstrip("/") + company.company_logo
        frappe.log_error("Ezy-Manual email", company_logo)
        data = data.replace("logoImg", company_logo)
        bg_logo = (company.site_domain).rstrip("/") + company.email_banner
        data = data.replace("headerBG", bg_logo)
        url = "{}?company={}&confirmation_number={}&source=email".format(
            company.ezycheckins_socket_host, company.name, conf_number
        )
        u = ps.Shortener().tinyurl.short(url)
        data = data.replace("{{url}}", u)
        frappe.sendmail(
            recipients=email_address,
            subject=company.pre_checkin_mail_subject,
            message=data,
            now=True,
        )
        frappe.db.set_value(
            "Arrival Information", conf_number, "guest_email_address", email_address
        )
        frappe.db.set_value("Arrival Information", conf_number, "mail_via", "Manual")
        frappe.db.set_value("Arrival Information", conf_number, "mail_sent", "Yes")
        count = count + 1
        frappe.db.set_value("Arrival Information", conf_number, "mail_count", count)
        activity_data = {
            "doctype": "Activity Logs",
            "datetime": date_time,
            "confirmation_number": conf_number,
            "module": "Ezycheckins",
            "event": "PreArrivals",
            "user": user_name,
            "activity": "Mail Sentout",
        }
        event_doc = frappe.get_doc(activity_data)
        event_doc.insert()
        frappe.db.commit()
        return {"success": True}

    elif arrival_doc.booking_status == "CHECKED-IN":
        file_path = (
            folder_path
            + "/sites/"
            + site_folder_path
            + company.thank_you_email_mail_content
        )
        f = open(file_path, "r")
        data = f.read()
        data = data.replace("{{name}}", arrival_doc.guest_first_name)
        data = data.replace("{{hotelName}}", company.company_name)
        data = data.replace("{{email}}", company.email)
        data = data.replace("{{phone}}", company.phone_number)
        frappe.sendmail(
            recipients=arrival_doc.guest_email_address,
            subject=company.thank_you_mail_subject,
            message=data,
            now=True,
        )
        frappe.db.set_value("Arrival Information", conf_number, "mail_via", "Manual")
        frappe.db.set_value("Arrival Information", conf_number, "mail_sent", "Yes")
        count = count + 1
        frappe.db.set_value("Arrival Information", conf_number, "mail_count", count)
        activity_data = {
            "doctype": "Activity Logs",
            "datetime": date_time,
            "confirmation_number": conf_number,
            "module": "Ezycheckins",
            "event": "PreArrivals",
            "user": user_name,
            "activity": "Mail Sent successfully",
        }
        event_doc = frappe.get_doc(activity_data)
        event_doc.insert()
        frappe.db.commit()
        return {"success": True}
    else:
        {"success": False, "message": "Email Failure"}


@frappe.whitelist(allow_guest=True)
def check_hotelId(data):
    confirmation_number = data["confirmation_number"]
    company = data["company"]
    company_doc = frappe.db.get_value(
        "company",
        company,
        [
            "name",
            "company_name",
            "trade_name",
            "gst_number",
            "b2c_qr_url",
            "company_logo",
            "terms_and_conditions",
            "ezycheckin_signature",
            "welcome_message",
        ],
        as_dict=True,
    )
    arrival_doc = frappe.db.get_value(
        "Arrival Information",
        confirmation_number,
        [
            "guest_title",
            "guest_last_name",
            "guest_first_name",
            "room_type",
            "guest_email_address",
            "guest_phone_no",
            "travel_agent_name",
            "no_of_adults",
            "no_of_children",
            "no_of_nights",
            "billing_instructions",
            "no_of_rooms",
            "confirmation_number",
            "reservation_clerk",
            "room_rate",
            "print_rate",
            "csr_id",
            "membership_no",
            "membership_type",
            "checkin_date",
            "total_visits",
            "checkout_date",
            "cc_number",
            "booking_status",
            "company_name",
            "cc_exp_date",
            "company",
            "virtual_checkin_status",
            "arrival_date",
            "is_group_code",
            "departure_date",
            "number_of_guests",
            "mail_sent",
            "mail_via",
            "confirmation_number",
        ],
        as_dict=True,
    )
    if company == company_doc["name"]:
        if confirmation_number == arrival_doc["confirmation_number"]:
            if arrival_doc["virtual_checkin_status"] == "No":
                arrival_doc["company_settings"] = company_doc
                return {"success": True, "data": arrival_doc}
            else:
                return {
                    "success": True,
                    "message": "You Already Checked-In",
                    "data": arrival_doc,
                }
        else:
            {"success": False, "message": "confirmation Number not found"}
    else:
        {"success": False, "message": "Company Code not found"}


@frappe.whitelist(allow_guest=True)
def check_hotelCode(data):
    company = data["company"]
    company_doc = frappe.db.get_value(
        "company",
        company,
        [
            "name",
            "company_name",
            "trade_name",
            "gst_number",
            "b2c_qr_url",
            "company_logo",
            "terms_and_conditions",
            "welcome_message",
            "ezycheckin_signature",
        ],
        as_dict=True,
    )
    if company == company_doc["name"]:
        return {"success": True, "data": company_doc}
    else:
        return {"success": False, "message": "Company Code not found"}


@frappe.whitelist(allow_guest=True)
def precheckins():
    user_name = frappe.session.user
    data = json.loads(frappe.request.data)
    company = frappe.get_last_doc("company")
    date_time = datetime.datetime.now()
    for i in data["data"]:
        cwd = os.getcwd()
        site_name = cstr(frappe.local.site)
        signature_binary = base64.b64decode(i["signature"])
        try:
            image1_binary = base64.b64decode(i["image_1"])
            image2_binary = base64.b64decode(i["image_2"])
            im1 = Image.open(BytesIO(image1_binary))
            im1.save(
                cwd
                + "/"
                + site_name
                + "/private/files/image1"
                + i["confirmation_number"]
                + ".png",
                "PNG",
            )
            im2 = Image.open(BytesIO(image2_binary))
            im2.save(
                cwd
                + "/"
                + site_name
                + "/private/files/image2"
                + i["confirmation_number"]
                + ".png",
                "PNG",
            )
            im = Image.open(BytesIO(signature_binary))
            im.save(
                cwd
                + "/"
                + site_name
                + "/private/files/signature"
                + i["confirmation_number"]
                + ".png",
                "PNG",
            )
        except PIL.UnidentifiedImageError:
            pass
        if company.ezycheckin_signature == "0":
            i["signature"] = "/files/signature" + i["confirmation_number"] + ".png"
        i["image_1"] = "/files/image1" + i["confirmation_number"] + ".png"
        i["image_2"] = "/files/image2" + i["confirmation_number"] + ".png"
        i.update({"doctype": "Precheckins"})
        get_arrival_data = frappe.db.count(
            "Precheckins", filters={"confirmation_number": i["confirmation_number"]}
        )
        if get_arrival_data != 0:
            if get_arrival_data == 1:
                nam = (i["confirmation_number"] + "-") + str(get_arrival_data)
            else:
                nam = (i["confirmation_number"] + "-") + str(get_arrival_data - 1)
            i["confirmation_number"] = nam
        precheckins_doc = frappe.get_doc(i)
        frappe.db.set_value(
            "Arrival Information",
            i["confirmation_number"],
            "virtual_checkin_status",
            "Yes",
        )
        activity_data = {
            "doctype": "Activity Logs",
            "datetime": date_time,
            "confirmation_number": i["confirmation_number"],
            "module": "Ezycheckins",
            "event": "PreArrivals",
            "user": user_name,
            "activity": "Precheckin Done",
        }
        event_doc = frappe.get_doc(activity_data)
        event_doc.insert()
        precheckins_doc.insert()
        frappe.db.commit()
        if company.thank_you_email == "1":
            cancel_email_address = i["guest_email_address"]
            folder_path = frappe.utils.get_bench_path()
            site_folder_path = company.site_name
            file_path = (
                folder_path
                + "/sites/"
                + site_folder_path
                + company.thank_you_email_mail_content
            )
            if i["mail_sent"] == "No":
                f = open(file_path, "r")
                data = f.read()
                data = data.replace("{{name}}", i["guest_first_name"])
                # data = data.replace('{{lastName}}',arrival_doc.guest_last_name)
                data = data.replace("{{hotelName}}", company.company_name)
                data = data.replace("{{email}}", company.email)
                data = data.replace("{{phone}}", company.phone_number)
                frappe.sendmail(
                    recipients=cancel_email_address,
                    subject=company.cancellation_email_mail_content,
                    message=data,
                    now=True,
                )
                frappe.db.set_value(
                    "Arrival Information", i["name"], "mail_sent", "Yes"
                )
                frappe.db.set_value(
                    "Arrival Information", i["name"], "mail_via", "Automatic"
                )
                activity_data = {
                    "doctype": "Activity Logs",
                    "datetime": date_time,
                    "confirmation_number": i["confirmation_number"],
                    "module": "Ezycheckins",
                    "event": "PreArrivals",
                    "user": user_name,
                    "activity": "Thankyou Mail Sent-out",
                }
                event_doc = frappe.get_doc(activity_data)
                event_doc.insert()
                frappe.db.commit()
            else:
                return {"success": False, "message": "Invitation Sent"}
    return {"success": True}


def upload_propery_logo_pms(data):
    try:
        # headers = {'Content-Type': 'application/json'}
        company = frappe.get_doc("company", data["company"])
        if company.proxy == 1:
            proxyhost = company.proxy_url
            proxyhost = proxyhost.replace("http://", "@")
            proxies = {
                "https": "https://"
                + company.proxy_username
                + ":"
                + company.proxy_password
                + proxyhost
            }
        files = {"file": open(data["file_path"], "rb")}
        file_name, file_extension = os.path.splitext(data["file_path"])
        if company.proxy == 0:
            if company.skip_ssl_verify == 0:
                json_response = requests.post(
                    "https://gst.caratred.in/ezy/api/addCompanyLogo",
                    data={"company": company.name, "file_extension": file_extension},
                    files=files,
                    verify=False,
                )
            else:
                json_response = requests.post(
                    "https://gst.caratred.in/ezy/api/addCompanyLogo",
                    data={"company": company.name, "file_extension": file_extension},
                    files=files,
                    verify=False,
                )
            response = json_response.json()
            if response["success"] is False:
                return {"success": False, "message": response["message"]}
            return response
        else:
            json_response = requests.post(
                "https://gst.caratred.in/ezy/api/addCompanyLogo",
                data={"company": company.name, "file_extension": file_extension},
                files=files,
                proxies=proxies,
                verify=False,
            )
            response = json_response.json()
            if response["success"] is False:
                return {"success": False, "message": response["message"]}
            return response
    except Exception as e:
        frappe.log_error("upload_propery_logo_pms:" + str(e))
        return {"success": False, "message": str(e)}


def update_company(doc, method=None):
    try:
        folder_path = frappe.utils.get_bench_path()
        if doc.pms_property_logo:
            file_path = folder_path + "/sites/" + doc.site_name + doc.pms_property_logo
            status = upload_propery_logo_pms(
                {"file_path": file_path, "company": doc.name}
            )
            if status["success"] is False:
                return status
            frappe.db.set_value(
                "company", doc.name, {"pms_property_url": status["data"]}
            )
            frappe.db.commit()
    except Exception as e:
        frappe.log_error("update_company:" + str(e))
        return {"success": False, "message": str(e)}


def delete_arrival_activity():
    try:
        last_week = datetime.datetime.now() - datetime.timedelta(days=2)
        arrival_activity = frappe.db.get_all(
            "Arrival Activities",
            filters={"creation": ["<", last_week]},
            fields=["name", "file_path"],
        )
        frappe.db.sql(
            """DELETE FROM `tabArrival Activities` WHERE creation < %s""", last_week
        )
        frappe.db.commit()
        for each in arrival_activity:
            frappe.db.delete("File", {"file_url": each["file_path"]})
            frappe.db.commit()
        return {"success": True}
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error(
            "Ezy-Delete Arrival Activity",
            "line No:{}\n{}".format(exc_tb.tb_lineno, traceback.format_exc()),
        )
        return {"success": False, "message": str(e)}


@frappe.whitelist(allow_guest=True)
def get_apikey(user):
    try:
        if frappe.db.exists("User", user):
            user_api = frappe.get_doc("User", user)
            secret = user_api.get_password(fieldname="api_secret", raise_exception=True)
            api_key = user_api.api_key
            # generate = generate_keys(user)
            return {"success": True, "api_key": api_key, "api_secret": secret}
        else:
            return {"success": False, "message": "No user found"}
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error(
            "Ezy-get_apikey",
            "line No:{}\n{}".format(exc_tb.tb_lineno, traceback.format_exc()),
        )
        return {"success": False, "message": str(e)}


@frappe.whitelist(allow_guest=True)
def update_mail_send_confirmation(confirmation_number):
    try:
        if frappe.db.exists("Arrival Information", confirmation_number):
            arrival_doc = frappe.get_doc("Arrival Information", confirmation_number)
            arrival_doc.invoice_send_mail_send = 1
            arrival_doc.save(ignore_permissions=True, ignore_version=True)
            frappe.db.commit()
            return {"success": True, "message": "Arrival updated"}
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error(
            "Ezy-update_mail_send_confirmation",
            "line No:{}\n{}".format(exc_tb.tb_lineno, traceback.format_exc()),
        )
        return {"success": False, "message": str(e)}


# @frappe.whitelist(allow_guest=True)


def delete_error_logs():
    try:
        frappe.log_error("Ezy-delete_error_logs", "test")
        days_before = (date.today() - timedelta(days=30)).isoformat()
        frappe.db.delete("Error Log", {"creation": ["<=", str(days_before)]})
        frappe.db.commit()
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error(
            "Ezy-delete_error_logs",
            "line No:{}\n{}".format(exc_tb.tb_lineno, traceback.format_exc()),
        )
        return {"success": False, "message": str(e)}


# @frappe.whitelist(allow_guest=True)


def delete_email_queue():
    try:
        days_before = (date.today() - timedelta(days=30)).isoformat()
        frappe.db.delete("Email Queue", {"creation": ["<=", str(days_before)]})
        frappe.db.commit()
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error(
            "Ezy-delete_email_queue",
            "line No:{}\n{}".format(exc_tb.tb_lineno, traceback.format_exc()),
        )
        return {"success": False, "message": str(e)}


@frappe.whitelist(allow_guest=True)
def ezy_suite_dashboard(from_date, to_date):
    try:
        total_reservations = frappe.db.sql(
            """select count(name) as total_reservations from `tabArrival Information` where DATE(arrival_date) between '{}' and '{}'""".format(
                from_date, to_date
            ),
            as_dict=1,
        )
        pre_checkins_count = frappe.db.sql(
            """select count(name) as pre_checkins from tabPrecheckins where DATE(creation) between '{}' and '{}'""".format(
                from_date, to_date
            ),
            as_dict=1,
        )
        reservations_scanned = frappe.db.sql(
            """select count(name) as scanned_reservations from `tabArrival Information` where DATE(arrival_date) between '{}' and '{}' and status='Scanned'""".format(
                from_date, to_date
            ),
            as_dict=1,
        )
        reservations_pending = frappe.db.sql(
            """select count(name) as pending_reservations from `tabArrival Information` where DATE(arrival_date) between '{}' and '{}' and status='Pending' and virtual_checkin_status='No'""".format(
                from_date, to_date
            ),
            as_dict=1,
        )
        pending_reviews = frappe.db.sql(
            """select count(name) as pending_reviews from `tabGuest Details` where uploaded_to_frro=0 and guest_id_type='Foreigner'""",
            as_dict=1,
        )
        uploaded_cform_count = frappe.db.sql(
            """select count(name) as uploaded_cfrom_count from `tabGuest Details` where uploaded_to_frro=1 and guest_id_type='Foreigner'""",
            as_dict=1,
        )
        pathik_pending = frappe.db.sql(
            """select count(name) as pending_pathik from `tabGuest Details` where pending_pathik=0 and guest_id_type='Foreigner' and main_guest=1""",
            as_dict=1,
        )
        uploaded_pathik = frappe.db.sql(
            """select count(name) as uploaded_pathik from `tabGuest Details` where pending_pathik=1 and guest_id_type='Foreigner' and main_guest=1""",
            as_dict=1,
        )
        return {
            "success": True,
            "data": {
                "total_reservations": total_reservations[0]["total_reservations"],
                "pre_checkins_count": pre_checkins_count[0]["pre_checkins"],
                "reservations_scanned": reservations_scanned[0]["scanned_reservations"],
                "reservations_pending": reservations_pending[0]["pending_reservations"],
                "pending_reviews": pending_reviews[0]["pending_reviews"],
                "uploaded_cform_count": uploaded_cform_count[0]["uploaded_cfrom_count"],
                "total_foreign_ids": pending_reviews[0]["pending_reviews"]
                + uploaded_cform_count[0]["uploaded_cfrom_count"],
                "pathik_pending": pathik_pending[0]["pending_pathik"],
                "uploaded_pathik": uploaded_pathik[0]["uploaded_pathik"],
                "total_foreign_ids_pathik": pathik_pending[0]["pending_pathik"]
                + uploaded_pathik[0]["uploaded_pathik"],
            },
        }
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error(
            "Ezy-suite dashboard",
            "line No:{}\n{}".format(exc_tb.tb_lineno, traceback.format_exc()),
        )
        return {"success": False, "message": str(e)}


@frappe.whitelist(allow_guest=True)
def fetch_invoice_details(filters=[]):
    try:
        if len(filters) > 0:
            filters = json.loads(filters)
            company = frappe.get_last_doc("company")
            # if filters["company_code"] == company.name:
            filters.extend([["invoice_type", "=", "B2B"], [
                           "irn_generated", "=", "Success"]])
            # ['igst_amount','sgst_amount','cgst_amount','total_gst_amount','invoice_number','invoice_date','guest_name','room_number','confirmation_number','total_invoice_amount','irn_number','qr_code_image','irn_generated_time','ack_no','invoice_file','gst_number'])
            fetch_invoice = frappe.db.get_list(
                'Invoices', filters=filters, fields=["*"])
            for x in fetch_invoice:
                items_fields = ['parent', 'sac_code', 'item_value', 'item_value_after_gst', 'gst_rate', 'igst_amount',
                                'cgst_amount', 'sgst_amount', 'state_cess_amount', 'cess_amount', 'date', 'item_type', 'sac_code', 'item_name']
                items_doc = frappe.db.get_list(
                    'Items', filters={'parent': ['in', x["invoice_number"]]}, fields=["*"])
                x['items'] = items_doc
                # print(x['items'])
            return fetch_invoice
        else:
            return {"success": False, "message": "filters not be empty"}
    except Exception as e:
        return {"Success":False,"message":str(e)}


def summaries_insert(doc, method=None):
    try:
        start_date = datetime.datetime.strptime(doc.from_date,"%Y/%m/%d").strftime("%d %B %Y")
        end_date = datetime.datetime.strptime(doc.to_date,"%Y/%m/%d").strftime("%d %B %Y")
        doc.between_dates = start_date+" to "+end_date
        today_date = datetime.datetime.today().strftime('%Y%m%d')
        reference = frappe.db.get_list('Summaries',filters=[["name",'!=',doc.name],["tax_payer_details","=",doc.tax_payer_details]],order_by='creation desc',pluck='reference')
        if len(reference) > 0:
            if reference[0]:
                reference_number = int(reference[0].split("-")[-1])
                doc.reference = doc.tax_payer_details+"-"+today_date
            else:
                doc.reference = doc.tax_payer_details+"-"+today_date
        else:
            doc.reference = doc.tax_payer_details+"-"+today_date
        if method == "after_insert":
            doc.save(ignore_permissions=True, ignore_version=True)
    except Exception as e:
        frappe.log_error(str(e), "summaries_insert")
        return {"Success":False,"message":str(e)}


@frappe.whitelist(allow_guest=True)
def convert_image_to_base64(image):
    try:
        company = frappe.get_last_doc("company")
        folder_path = frappe.utils.get_bench_path()
        file_path1 = (
            folder_path
            + "/sites/"
            + company.site_name
            + image
        )
        with open(file_path1, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read())
        encoded_str = encoded_string.decode("utf-8")
        return {"success": True, "data": encoded_str}
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("convert_image_to_base64",
                         "line No:{}\n{}".format(exc_tb.tb_lineno, str(e)))
        return {"success": False, "message": str(e)}


@frappe.whitelist(allow_guest=True)
def html_to_pdf(invoice_number=None,month=None,year=None):
    try:
        print(invoice_number,month)
        if invoice_number:
            doc = frappe.get_doc("Invoices",invoice_number)
            create_pdf_each_invoice(doc)
        elif month:
            print("""SELECT name from  `tabInvoices` WHERE month(invoice_date)={0};""".format(month))
            docs = frappe.db.sql("""SELECT name from  `tabInvoices` WHERE month(invoice_date)={} and year(invoice_date)={};""".format(month,year),as_dict=1)
            for invoice_number in docs:
                doc = frappe.get_doc("Invoices",invoice_number['name'])
                create_pdf_each_invoice(doc)   
        # elif year:
        #     print("""SELECT name from  `tabInvoices` WHERE year(invoice_date)={0};""".format(year))
        #     year_doc = frappe.db.sql("""SELECT name from  `tabInvoices` WHERE year(invoice_date)={0};""".format(year),as_dict=1)
        #     for invoice_number in year_doc:
        #         docs = frappe.get_doc("Invoices",invoice_number['name'])
        #         create_pdf_each_invoice(docs)        
        else:
            return {"message":"Please check the filter","success":False}
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("html_to_pdf",
                         "line No:{}\n{}".format(exc_tb.tb_lineno, str(e)))
        return {"success": False, "message": str(e)}




def create_pdf_each_invoice(doc):
    try:
        site_name = cstr(frappe.local.site)
        company = frappe.get_last_doc('company')
        if not company.host:
            return {'success': False, 'message': "please specify host in company"}
        cwd = os.getcwd()
        templates = frappe.db.get_value("Print Format", "Manual E-Tax Invoice","html")
        if company.company_logo:
            convimgtobase = convert_image_to_base64(company.company_logo)
            if not convimgtobase["success"]:
                return convimgtobase
            base = "data:image/png;base64,"+convimgtobase["data"]
        else:
            base= ""
        qr_image_base = ""
        if doc.qr_code_image or doc.credit_qr_code_image:
            convimgtobase = convert_image_to_base64(doc.qr_code_image if doc.invoice_category != "Credit Invoice" else doc.credit_qr_code_image)
            if not convimgtobase["success"]:
                return convimgtobase
            qr_image_base = "data:image/png;base64," + \
                convimgtobase["data"]
        invoice_doc = doc.as_dict()
        invoice_doc["base"] = base
        invoice_doc["qr_image_base"] = qr_image_base           
        html_data = frappe.render_template(templates,invoice_doc)
        site_name = cstr(frappe.local.site)
        htmldoc = HTML(string=html_data, base_url="")
        folder=company.save_etax_invoice_folder
        get_inv_date=doc.invoice_date
        create_month_year_folder = get_inv_date.strftime("%Y_%m")
        path=os.path.join(folder,create_month_year_folder)
        file_path=path +"/"+  doc.name  + '.pdf'
        try:
            os.makedirs(path,exist_ok=True)
            print("directory '%s' created successfully" %create_month_year_folder)
        except OSError as error:
                print("directory '%s' cant be created " %create_month_year_folder)       
        htmldoc.write_pdf(file_path)
        return {"success": True}
    except Exception as e:
        pass




