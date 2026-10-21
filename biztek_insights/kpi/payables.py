# Copyright (c) 2026, Savad Ibrahim and Contributors
# License: MIT

"""Accounts payable KPI calculations."""

from __future__ import annotations

import frappe
from frappe import _
from frappe.utils import flt

from biztek_insights.kpi.filters import ensure_permission, ok_result, unavailable
from biztek_insights.kpi.receivables import _enrich_with_invoice_dates, _open_invoice_outstandings


def total_ap(filters) -> dict:
	"""Outstanding AP from Payment Ledger Entry (open Purchase Invoices)."""
	if not frappe.db.exists("DocType", "Payment Ledger Entry"):
		return unavailable(_("Payment Ledger Entry is not available"))
	ensure_permission("Payment Ledger Entry")

	rows = _open_invoice_outstandings(
		company=filters.company,
		party_type="Supplier",
		against_voucher_type="Purchase Invoice",
	)
	total = sum(flt(r.outstanding) for r in rows)
	return ok_result(flt(total), currency=filters.currency, format="currency")


def ap_detail(filters) -> list[dict]:
	"""Open AP rows with ageing bucket."""
	ensure_permission("Payment Ledger Entry")
	ensure_permission("Purchase Invoice")
	rows = _open_invoice_outstandings(
		company=filters.company,
		party_type="Supplier",
		against_voucher_type="Purchase Invoice",
	)
	return _enrich_with_invoice_dates(rows, "Purchase Invoice", filters.as_on)
