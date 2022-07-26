frappe.query_reports["Missing Checks"] = 
{
    "filters": [
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
        // {
        //     "fieldname": "sync",
        //     "label": __("Sync"),
        //     "fieldtype": "Select",
        //     "width": "80",
        //     "options":["Yes","No"],
        //     "default": 'Yes'
        // },
    ]
};

// select pos_cheks.name,pos_cheks.check_no,pos_cheks.sync,items.check_number,pos_cheks.check_date from `tabPOS Checks` as pos_cheks LEFT JOIN `tabItems` as items on pos_cheks.check_no = items.check_number where DATE(pos_cheks.check_date) between DATE("2022-05-01") and DATE("2022-05-30") and pos_cheks.sync="Yes";
// Query for selecting pos check dates sync YES or NO