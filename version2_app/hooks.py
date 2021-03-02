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
		"after_delete":"version2_app.events.invoice_deleted",
		# "on_update": "version2_app.events.invoiceUpdate",
		# "on_cancel": "method",
		# "on_trash": "method"
	},
	"File":{
		# 'after_save':"version2_app.events.fileCreated",
		'after_insert':"version2_app.events.fileCreated"
	},
	"Bench Manager Command":{
		'before_insert':"version2_app.events.emitsocket",
		# 'after_insert':"version2_app.events.updateManager"
		'on_update':"version2_app.events.updateManager"
	}

}

# Scheduled Tasks
# ---------------

scheduler_events = {
	"all": [
		"version2_app.doctype.invoices.invoices.login_gsp2"
	],
	"cron": {
        "0/1 * * *": [
            "version2_app.doctype.invoices.invoices.login_gsp2"
        ]}
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

