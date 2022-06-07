// Copyright (c) 2022, caratred and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Event Food"] = {
	"filters": [
		{
            "fieldname": "invoice_number",
            "label": __("Invoice Number"),
            "fieldtype": "Link",
			"options": "Invoices",
            "width": "80"
        },
		{
            "fieldname": "from_date",
            "label": __("From Date"),
            "fieldtype": "Date",
            "width": "80",
            "default": frappe.datetime.month_start()
        },
        {
            "fieldname": "to_date",
            "label": __("To Date"),
            "fieldtype": "Date",
            "width": "80",
            "default": frappe.datetime.month_end()
        }

	]
};
