# Copyright (c) 2026, Savad Ibrahim and Contributors
# License: MIT

"""Accounts receivable KPI calculations."""

from __future__ import annotations

import frappe
from frappe import _
from frappe.utils import flt

from biztek_insights.kpi.filters import ensure_permission, ok_result, unavailable


def total_ar(filters) -> dict:
	"""Outstanding AR from Payment Ledger Entry (open Sales Invoices)."""
	if not frappe.db.exists("DocType", "Payment Ledger Entry"):
		return unavailable(_("Payment Ledger Entry is not available"))
	ensure_permission("Payment Ledger Entry")

	rows = _open_invoice_outstandings(
		company=filters.company,
		party_type="Customer",
		against_voucher_type="Sales Invoice",
	)
	total = sum(flt(r.outstanding) for r in rows)
	return ok_result(flt(total), currency=filters.currency, format="currency")


def ar_detail(filters) -> list[dict]:
	"""Open AR rows with ageing bucket."""
	ensure_permission("Payment Ledger Entry")
	ensure_permission("Sales Invoice")
	rows = _open_invoice_outstandings(
		company=filters.company,
		party_type="Customer",
		against_voucher_type="Sales Invoice",
	)
	return _enrich_with_invoice_dates(rows, "Sales Invoice", filters.as_on)


def _open_invoice_outstandings(
	*, company: str, party_type: str, against_voucher_type: str
) -> list[dict]:
	ple = frappe.qb.DocType("Payment Ledger Entry")
	aggregated = (
		frappe.qb.from_(ple)
		.select(
			ple.party,
			ple.against_voucher_no,
			frappe.query_builder.functions.Sum(ple.amount).as_("outstanding"),
		)
		.where(
			(ple.delinked == 0)
			& (ple.company == company)
			& (ple.party_type == party_type)
			& (ple.against_voucher_type == against_voucher_type)
		)
		.groupby(ple.party, ple.against_voucher_no)
	).run(as_dict=True)
	return [r for r in aggregated if flt(r.outstanding) > 0.5]


def _enrich_with_invoice_dates(rows: list[dict], doctype: str, as_on) -> list[dict]:
	if not rows:
		return []
	names = [r.against_voucher_no for r in rows]
	meta = frappe.get_meta(doctype)
	fields = ["name", "due_date", "posting_date"]
	if meta.has_field("customer"):
		fields.append("customer")
	if meta.has_field("supplier"):
		fields.append("supplier")
	if meta.has_field("customer_name"):
		fields.append("customer_name")
	if meta.has_field("supplier_name"):
		fields.append("supplier_name")
	invoices = {
		d.name: d
		for d in frappe.get_all(doctype, filters={"name": ["in", names]}, fields=fields)
	}
	for r in rows:
		inv = invoices.get(r.against_voucher_no) or frappe._dict()
		r.due_date = inv.get("due_date")
		r.posting_date = inv.get("posting_date")
		r.party_name = (
			inv.get("customer_name")
			or inv.get("supplier_name")
			or inv.get("customer")
			or inv.get("supplier")
		)
		if r.due_date:
			days = (as_on - r.due_date).days
			r.days_overdue = days
			r.overdue = days > 0
			r.bucket = _age_bucket(days)
		else:
			r.days_overdue = None
			r.overdue = False
			r.bucket = _("Unknown")
	return rows


def _age_bucket(days_overdue: int) -> str:
	if days_overdue <= 0:
		return _("Not Due")
	if days_overdue <= 30:
		return _("1-30 Days")
	if days_overdue <= 60:
		return _("31-60 Days")
	if days_overdue <= 90:
		return _("61-90 Days")
	return _("90+ Days")
