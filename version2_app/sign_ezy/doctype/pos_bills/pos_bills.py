# -*- coding: utf-8 -*-
# Copyright (c) 2021, caratred and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from datetime import datetime, date
import re
from frappe.utils import logger
import sys, os, traceback
frappe.utils.logger.set_log_level("DEBUG")

class PosBills(Document):
	pass

@frappe.whitelist(allow_guest=True)
def create_pos_bills(bills):
    try:
        # print(bills['transaction_date'])
        if 'transaction_date' not in bills:
            bills['check_date'] = date.today()
        else:
            inDate = bills['transaction_date']
            o_date = inDate[0:2]
            o_hh = inDate.split(',')[1].split(':')[0]
            o_mm = inDate.split(',')[1].split(':')[1]
            o_year = inDate.split(',')[0][-2:]
            o_month = inDate.split(',')[0][2:-3]
            convert_date = o_date + '-'+o_month+'-20'+o_year+'-'+o_hh+':'+o_mm+':00'
            bills['check_date'] = datetime.strptime(
                convert_date, "%d-%b-%Y-%H:%M:%S")
            # print(bills['transaction_date'])
        if 'check_no' not in bills:
            bills['check_no'] = 'No Check Number'
        if 'tabel_no' not in bills:
            bills['tabel_no'] = 'No Table Number'
        if 'guest_no' not in bills:
            bills['guest_no'] = 'No Guest Count'
        if 'billed_by' not in bills:
            bills['billed_by'] = 'No billed By'
        if 'work_station_name' not in bills:
            bills['work_station_name'] = 'No Work Station'
        if 'ce' not in bills:
            bills['ce'] = 'No CE'
        if 'cc' not in bills:
            bills['cc'] = 'No CC'
        if 'tc' not in bills:
            bills['tc'] = 'No TC'
        # bill_exist = frappe.db.exists({'doctype': 'Pos Bills', 'check_number': bills['check_no']})
        bill_exist = frappe.db.get_value(
            'Pos Bills', {'check_number': bills['check_no']}, ['name'])
        print(bill_exist,bills['check_no'],"^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^66")
        if bill_exist is None:
            print("If&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
            doc = frappe.get_doc({
                'doctype': 'Pos Bills',
                'check_number': bills['check_no'],
                'table_no': bills['tabel_no'],
                'check_date': bills['check_date'],
                'billed_by': bills['billed_by'],
                'guest_count': bills['guest_no'],
                'work_station': bills['work_station_name'],
                'transaction_no': bills['Trn'],
                'ce': bills['ce'],
                'cc': bills['cc'],
                'tc': bills['tc'],
                'invoice_type': 'B2C',
                'raw_text': bills['raw_text'],
                "company": bills["company"]
            })
            doc.insert()
            frappe.db.commit()
        else:
            print("else &&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
            doc = frappe.get_doc('Pos Bills', bill_exist)
            new_text = re.sub('================================', bills['items_raw_text'], doc.raw_text)
            # removed_double_slash_text = re.sub('/n/n', bills['items_raw_text'], doc.raw_text)
            # doc = frappe.get_doc('Pos Bills', bill_exist)
            # print(new_text,"*********************88")
            doc.raw_text = new_text
            doc.save()
            frappe.db.commit()

        return True
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("SignEzy passport_address","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
        return {"success":False, "error":str(e)}
