# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import __version__ as app_version


app_name = "version2_app"
app_title = "Version2 App"
app_publisher = "caratred"
app_description = "version 2 features"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "info@caratred.com"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/version2_app/css/version2_app.css"
# app_include_js = "/assets/version2_app/js/version2_app.js"

# include js, css files in header of web template
# web_include_css = "/assets/version2_app/css/version2_app.css"
# web_include_js = "/assets/version2_app/js/version2_app.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "version2_app/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "version2_app.install.before_install"
# after_install = "version2_app.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "version2_app.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
#	}
# }
doc_events = {
	"Invoices": {
        "after_insert":"version2_app.events.invoice_created",
        "on_update":"version2_app.events.invoice_update",
		"after_delete":"version2_app.events.invoice_deleted",
		# "on_update": "version2_app.events.invoiceUpdate",
		# "on_cancel": "method",
		# "on_trash": "method"
	},
    "Arrival Information": {
        "after_insert": "version2_app.events.arrival_information",
        # "on_update": "version2_app.events.send_invoice_mail"
    },
    "Guest Details": {
        "after_insert": "version2_app.events.guest_attachments",
        "on_update": "version2_app.events.guest_update_attachment_logs"
    },
    "Tablet Config": {
        "after_insert": "version2_app.events.tablet_mapping",
        # "on_trash": "version2_app.events.remove_mapping",
    },
    "Redg Card": {
        "after_insert": "version2_app.events.create_redg_card",
        "on_trash": "version2_app.events.create_redg_card",
    },
    "Paidout Receipts": {
        "after_insert": "version2_app.events.create_paidout_receipt",
        "on_trash": "version2_app.events.create_paidout_receipt",
    },
    "Advance Deposits": {
        "after_insert": "version2_app.events.create_advance_deposits",
        "on_trash": "version2_app.events.create_advance_deposits",
    },
    "Payment Receipts": {
        "after_insert": "version2_app.events.create_payment_receipts",
        "on_trash": "version2_app.events.create_payment_receipts",
    },
    "Encashment Certificates": {
        "after_insert": "version2_app.events.create_encashment_certificates",
        "on_trash": "version2_app.events.create_encashment_certificates",
    },
    "Pos Bills": {
        "after_insert": "version2_app.events.create_pos_bill",
        # "on_trash": "version2_app.events.create_encashment_certificates",
    },
    "Active Tablets": {
        "after_insert": "version2_app.events.tablet_connected",
        # "on_trash": "version2_app.events.tablet_disconnected",
        "on_update": "version2_app.events.update_tablet_status",
    },
    "Active Work Stations": {
        "on_trash": "version2_app.events.workstation_disconnected",
        "before_save": "version2_app.events.before_update_ws",
        # "on_update": "version2_app.events.update_workstations_status",
    },
    "Information Folio": {
        "after_insert": "version2_app.events.information_folio_created",
    },
	"File":{
		# 'after_save':"version2_app.events.fileCreated",
		'after_insert':"version2_app.events.fileCreated"
	},
	"Update Logs":{
		'before_insert':"version2_app.events.Updateemitsocket"
	},
	"Document Bin":{
		'on_update':"version2_app.events.DocumentBinSocket"
	},
	"company":{
		"after_insert":"version2_app.events.company_created",
        'on_update':"version2_app.events.update_company"
	},
	"Gsp Metering":{
		'after_insert':"version2_app.events.gspmeteringhook"
	},
	"TaxPayerDetail":{
		'after_insert':"version2_app.events.taxpayerhook"
	},
    "Promotions":{
        'after_insert':"version2_app.events.promotionsSocket",
        "on_trash": "version2_app.events.deletePromotionsSocket",       
    },
    'Precheckins':{
        'after_insert':"version2_app.events.precheckinsdocuments",
        # 'on_update':'version2_app.passport_scanner.doctype.temp_doc_details.temp_doc_details.update_document_details'
    },
    "Summaries": {
        "after_insert":"version2_app.events.summaries_insert",
        # "on_update": "version2_app.events.summaries_insert"
    },
    "Dropbox":{
        # 'on_update':'version2_app.passport_scanner.doctype.dropbox.dropbox.merge_guest_to_guest_details'
    }
}

# Scheduled Tasks/home/caratred/frappe_projects/Einvoice_Bench/apps/version2_app/version2_app/version2_app/doctype/emailTemplat.py
# ---------------
# scheduler_events = {
	

# 	# "daily":[
# 	# 	"version2_app.events.deleteemailfilesdaily"
# 	# ],
# 	"corn":{"0 1 * * *":["version2_app.events.dailyDeletedocumentBin"],
# 			"10 1 * * * ":["version2_app.events.deleteemailfilesdaily"],
# 			"20 1 * * *":["version2_app.events.dailyIppprinterFiles"],
# 			"0 12 * * *":["version2_app.events.block_irn"],
#             "* * * * *":["version2_app.events.pre_mail"]}	
# }	


scheduler_events = {
    # "all": [
    #     "version2_app.version2_app.doctype.emailTemplat.sampleFun"
    # ],
    "cron": {
        # "1-59 * * * *": ["version2_app.version2_app.doctype.emailTemplat.sampleFun"],
        "0 1 * * *":["version2_app.events.dailyDeletedocumentBin"],
        "10 1 * * * ":["version2_app.events.deleteemailfilesdaily"],
        # "20 1 * * *":["version2_app.events.dailyIppprinterFiles"],
        "0 12 * * *":["version2_app.events.block_irn"],
        "0 2 * * *":["version2_app.events.delete_arrival_activity"],
        "* * * * *":["version2_app.events.pre_mail"],
        # "09 11 * * * *": ["version2_app.version2_app.doctype.emailTemplat.sampleFun"],
        "*/2 * * * *":["version2_app.events.send_invoice_mail_scheduler"],
        "10 00 * * *":["version2_app.events.delete_error_logs"],
        "20 00 * * *":["version2_app.events.delete_email_queue"]},
        
    "daily": [
        "version2_app.version2_app.doctype.document_bin.document_bin.dailyDeletedocumentBin",
        "version2_app.events.deleteemailfilesdaily",
        "version2_app.events.delete_arrival_activity"
    ]
}
# scheduler_events = {

# 	"all": [
# 		"version2_app.tasks.all"
# 	],
# 	"daily": [
# 		"version2_app.tasks.daily"
# 	],
# 	"hourly": [
# 		"version2_app.tasks.hourly"
# 	],
# 	"weekly": [
# 		"version2_app.tasks.weekly"
# 	]
# 	"monthly": [
# 		"version2_app.tasks.monthly"
# 	]
# }

# Testing
# -------

# before_tests = "version2_app.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "version2_app.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "version2_app.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]
