# Copyright (c) 2026, Savad Ibrahim and Contributors
# License: MIT

"""Post-dated cheque (PDC) pending payable KPI."""

from __future__ import annotations

import frappe
from frappe import _
from frappe.utils import flt

from biztek_insights.kpi.filters import ensure_permission, meta_has_field, ok_result, unavailable


def pdc_fields_available() -> bool:
	return meta_has_field("Payment Entry", "custom_pdc_payment") and meta_has_field(
		"Payment Entry", "custom_pdc_status"
	)


def pdc_pending_payable(filters) -> dict:
	"""Total value of pending payable PDCs (Payment Entry workflow)."""
	if not pdc_fields_available():
		return unavailable(_("PDC fields are not installed (pdc_cheques app)"))
	ensure_permission("Payment Entry")

	total = frappe.db.sql(
		"""
		SELECT COALESCE(SUM(COALESCE(base_paid_amount, paid_amount)), 0)
		FROM `tabPayment Entry`
		WHERE docstatus = 1
			AND company = %s
			AND custom_pdc_payment = 1
			AND custom_pdc_status = 'Pending'
			AND payment_type = 'Pay'
		""",
		(filters.company,),
	)[0][0]
	return ok_result(flt(total), currency=filters.currency, format="currency")


def pdc_pending_detail(filters) -> list[dict]:
	"""Pending payable PDC rows for the detail dashboard."""
	if not pdc_fields_available():
		return []
	ensure_permission("Payment Entry")
	return frappe.get_all(
		"Payment Entry",
		filters={
			"docstatus": 1,
			"company": filters.company,
			"custom_pdc_payment": 1,
			"custom_pdc_status": "Pending",
			"payment_type": "Pay",
		},
		fields=[
			"name",
			"party",
			"party_name",
			"reference_no",
			"reference_date",
			"posting_date",
			"paid_amount",
			"base_paid_amount",
			"custom_pdc_status",
			"currency",
		],
		order_by="reference_date asc, name asc",
	)
