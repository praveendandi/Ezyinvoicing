# -*- coding: utf-8 -*-
# Copyright (c) 2020, Caratred and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class Items(Document):
	pass
	# def on_update(self):
	# 	if self.name:
	# 		print(self.name,"$$$$$$$$$$$$$$$$$$$$$$$")

	# 		frappe.throw('Age must be less than 60')




@frappe.whitelist(allow_guest=True)
def calulate_items(data):
	#items, invoice_number,company_code
	try:
		total_items = []
		for item in data['items']:
			final_item = {}
			calulationType = frappe.get_doc(
						'company', data['company_code'])
					
			if calulationType.calculation_by == "Description":
				sac_code_based_gst_rates = frappe.get_doc(
					'SAC HSN CODES', item['name'])
				SAC_CODE = sac_code_based_gst_rates.code 	
				# if sac_code_based_gst_rates.taxble == "Yes":
				if item['sac_code']== "No Sac" and SAC_CODE.isdigit():
					item['sac_code'] = sac_code_based_gst_rates.code	
				if "-" in str(item['item_value']):
					final_item['sort_order'] = item['sort_order']
					final_item['cgst'] = item['cgst']
					final_item['cgst_amount'] = round(item['cgstAmount'], 2)
					final_item['sgst'] = item['sgst']
					final_item['sgst_amount'] = round(item['sgstAmount'], 2)
					final_item['igst'] = item['igst']
					final_item['igst_amount'] = round(item['igstAmount'], 2)
					final_item[
						'gst_rate'] = item['cgst'] + item['sgst'] + item['igst']
					final_item['item_value_after_gst'] = item['item_value'] + item[
						'cgstAmount'] + item['sgstAmount'] + item['igstAmount']
					final_item['item_value'] = item['item_value']
					if item['sac_code'].isdigit():
						final_item['sac_code_found'] = 'Yes' 
					else:
						final_item['sac_code_found'] = 'No'	
					final_item['other_charges'] = 0	 
					final_item['taxable'] = sac_code_based_gst_rates.taxble

				elif item['sac_code'] == '996311':
					final_item['sort_order'] = item['sort_order']
					final_item['cgst'] = item['cgst']
					final_item['cgst_amount'] = round(item['cgstAmount'], 2)
					final_item['sgst'] = item['sgst']
					final_item['sgst_amount'] = round(item['sgstAmount'], 2)
					final_item['igst'] = item['igst']
					final_item['igst_amount'] = round(item['igstAmount'], 2)
					final_item[
						'gst_rate'] = item['cgst'] + item['sgst'] + item['igst']
					final_item['item_value_after_gst'] = item['item_value'] + item[
						'cgstAmount'] + item['sgstAmount'] + item['igstAmount']
					final_item['item_value'] = item['item_value']
					final_item['sac_code_found'] = 'Yes'  
					final_item['other_charges'] = 0
					final_item['taxable'] = sac_code_based_gst_rates.taxble
				elif item['sac_code'] == '998599':	
					final_item['sort_order'] = item['sort_order']
					final_item['cgst'] = item['cgst']
					final_item['cgst_amount'] = round(item['cgstAmount'], 2)
					final_item['sgst'] = item['sgst']
					final_item['sgst_amount'] = round(item['sgstAmount'], 2)
					final_item['igst'] = item['igst']
					final_item['igst_amount'] = round(item['igstAmount'], 2)
					final_item[
						'gst_rate'] = item['cgst'] + item['sgst'] + item['igst']
					final_item['item_value_after_gst'] = item['item_value'] + item[
						'cgstAmount'] + item['sgstAmount'] + item['igstAmount']
					final_item['item_value'] = item['item_value']
					final_item['sac_code_found'] = 'Yes'  
					final_item['other_charges'] = 0 
					final_item['taxable'] = sac_code_based_gst_rates.taxble 
				elif sac_code_based_gst_rates.description == item['name'] and sac_code_based_gst_rates.taxble == "Yes":
					final_item['sort_order'] = item['sort_order']
					final_item['cgst'] = int(sac_code_based_gst_rates.cgst)
					final_item['sgst'] = int(sac_code_based_gst_rates.sgst)
					gst_percentage = (int(sac_code_based_gst_rates.cgst) +
										int(sac_code_based_gst_rates.sgst))
					base_value = item['item_value'] * (100 /
														(gst_percentage + 100))
					gst_value = item['item_value'] - base_value
					final_item['cgst_amount'] = gst_value / 2
					final_item['sgst_amount'] = gst_value / 2
					final_item['other_charges'] = 0
					final_item['igst'] = int(sac_code_based_gst_rates.igst)

					if int(sac_code_based_gst_rates.igst) <= 0:
						final_item['igst_amount'] = 0
					else:
						gst_percentage = (int(sac_code_based_gst_rates.cgst) +
											int(sac_code_based_gst_rates.sgst))
						base_value = item['item_value'] * (
							100 / (gst_percentage + 100))
						final_item[
							'igst_amount'] = item['item_value'] - base_value
						final_item['other_charges'] = 0
					final_item['gst_rate'] = int(
						sac_code_based_gst_rates.cgst) + int(
							sac_code_based_gst_rates.sgst) + int(
								sac_code_based_gst_rates.igst)
					final_item['item_value'] = round(
						item['item_value'] - final_item['cgst_amount'] -
						final_item['sgst_amount'] - final_item['igst_amount'],
						2)
					final_item['item_value_after_gst'] = item['item_value']
					final_item['sac_code_found'] = 'Yes'
					final_item['taxable'] = sac_code_based_gst_rates.taxble

				else:
					final_item['sort_order'] = item['sort_order']
					item['sac_code'] = 'No Sac'
					final_item['sac_code_found'] = 'No'
					final_item['cgst'] = 0
					final_item['other_charges'] = 0
					final_item['cgst_amount'] = 0
					final_item['sgst'] = 0
					final_item['sgst_amount'] = 0
					final_item['igst'] = 0
					final_item['igst_amount'] = 0
					final_item['gst_rate'] = 0
					final_item['item_value_after_gst'] = item['item_value']
					final_item['item_value'] = item['item_value']
					final_item['taxable'] = sac_code_based_gst_rates.taxble
			else:
				sac_code_based_gst_rates = frappe.get_doc(
					'SAC HSN CODES', item['sac_code'])
				if item['sac_code'] == '996311':
					final_item['sort_order'] = item['sort_order']
					final_item['cgst'] = item['cgst']
					final_item['cgst_amount'] = round(item['cgstAmount'], 2)
					final_item['sgst'] = item['sgst']
					final_item['sgst_amount'] = round(item['sgstAmount'], 2)
					final_item['igst'] = item['igst']
					final_item['igst_amount'] = round(item['igstAmount'], 2)
					final_item[
						'gst_rate'] = item['cgst'] + item['sgst'] + item['igst']
					final_item['item_value_after_gst'] = item['item_value'] + item[
						'cgstAmount'] + item['sgstAmount'] + item['igstAmount']
					final_item['item_value'] = item['item_value']
					final_item['sac_code_found'] = 'Yes'
					final_item['other_charges'] = 0
					final_item['taxable'] = sac_code_based_gst_rates.taxble
				elif item['sac_code'] == '998599':
					final_item['sort_order'] = item['sort_order']	
					final_item['cgst'] = item['cgst']
					final_item['cgst_amount'] = round(item['cgstAmount'], 2)
					final_item['sgst'] = item['sgst']
					final_item['sgst_amount'] = round(item['sgstAmount'], 2)
					final_item['igst'] = item['igst']
					final_item['igst_amount'] = round(item['igstAmount'], 2)
					final_item[
						'gst_rate'] = item['cgst'] + item['sgst'] + item['igst']
					final_item['item_value_after_gst'] = item['item_value'] + item[
						'cgstAmount'] + item['sgstAmount'] + item['igstAmount']
					final_item['item_value'] = item['item_value']
					final_item['sac_code_found'] = 'Yes'  
					final_item['other_charges'] = 0	
					final_item['taxable'] = sac_code_based_gst_rates.taxble
				else:
					if item['sac_code'].isdigit():
						sac_code_based_gst_rates = frappe.get_doc(
							'SAC HSN CODES', item['sac_code'])
						final_item['cgst'] = int(sac_code_based_gst_rates.cgst)
						final_item['sgst'] = int(sac_code_based_gst_rates.sgst)
						gst_percentage = (int(sac_code_based_gst_rates.cgst) +
										int(sac_code_based_gst_rates.sgst))
						# gst_value = (item['item_value']*100) /(gst_percentage+100)
						# print(gst_percentage,"gst percentage")
						base_value = item['item_value'] * (100 /
														(gst_percentage + 100))
						gst_value = item['item_value'] - base_value
						final_item['cgst_amount'] = gst_value / 2
						final_item['sgst_amount'] = gst_value / 2
						final_item['other_charges'] = 0
						final_item['igst'] = int(sac_code_based_gst_rates.igst)
						final_item['sort_order'] = item['sort_order']

						if int(sac_code_based_gst_rates.igst) <= 0:
							final_item['igst_amount'] = 0
						else:
							gst_percentage = (int(sac_code_based_gst_rates.cgst) +
											int(sac_code_based_gst_rates.sgst))
							base_value = item['item_value'] * (
								100 / (gst_percentage + 100))
							final_item[
								'igst_amount'] = item['item_value'] - base_value

						final_item['gst_rate'] = int(
							sac_code_based_gst_rates.cgst) + int(
								sac_code_based_gst_rates.sgst) + int(
									sac_code_based_gst_rates.igst)
						final_item['item_value'] = round(
							item['item_value'] - final_item['cgst_amount'] -
							final_item['sgst_amount'] - final_item['igst_amount'],
							2)
						final_item['item_value_after_gst'] = item['item_value']
						final_item['sac_code_found'] = 'Yes'
						final_item['other_charges'] = 0
						final_item['taxable'] = sac_code_based_gst_rates.taxble
					else:
						final_item['sort_order'] = item['sort_order']
						item['sac_code'] = 'No Sac'
						final_item['sac_code_found'] = 'No'
						final_item['cgst'] = 0
						final_item['cgst_amount'] = 0
						final_item['sgst'] = 0
						final_item['sgst_amount'] = 0
						final_item['igst'] = 0
						final_item['igst_amount'] = 0
						final_item['gst_rate'] = 0
						final_item['item_value_after_gst'] = item['item_value']
						final_item['item_value'] = item['item_value']
						final_item['other_charges'] = 0
						final_item['taxable'] = sac_code_based_gst_rates.taxble
			total_items.append({
				'doctype':
				'Items',
				'sac_code':
				item['sac_code'],
				'item_name':
				item['name'],
				'sort_order':final_item['sort_order'],
				'date':
				datetime.datetime.strptime(item['date'], '%Y-%m-%d'),
				'cgst':
				final_item['cgst'],
				'cgst_amount':
				round(final_item['cgst_amount'], 2),
				'sgst':
				final_item['sgst'],
				'sgst_amount':
				round(final_item['sgst_amount'], 2),
				'igst':
				final_item['igst'],
				'igst_amount':
				round(final_item['igst_amount'], 2),
				'item_value':
				final_item['item_value'],
				'description':
				item['name'],
				'item_taxable_value':
				final_item['item_value'],
				'gst_rate':
				final_item['gst_rate'],
				'item_value_after_gst':
				round(final_item['item_value_after_gst'], 2),
				'parent':
				data['invoice_number'],
				'parentfield':
				'items',
				'parenttype':
				"invoices",
				'sac_code_found':
				final_item['sac_code_found'],
				'other_charges': final_item['other_charges'],
				'taxable':final_item['taxable']
			})
		return {"success":True,"data":total_items}
	except Exception as e:
		print(e, "calculation api")
		return {"success":False,"message":e}
		