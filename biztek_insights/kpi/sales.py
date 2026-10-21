# Copyright (c) 2026, Savad Ibrahim and Contributors
# License: MIT

"""Sales Order KPI calculations."""

from __future__ import annotations

import frappe
from frappe import _
from frappe.utils import flt

from biztek_insights.kpi.constants import OPEN_SO_STATUSES, PENDING_SO_STATUSES
from biztek_insights.kpi.filters import ensure_permission, ok_result, unavailable


def pending_sales_orders_value(filters) -> dict:
	"""Total value of pending (open) sales orders.

	Formula: sum(base_grand_total - advance_paid) for submitted SOs whose status
	is in PENDING_SO_STATUSES (Biztek Financial Overview convention).
	"""
	if not frappe.db.exists("DocType", "Sales Order"):
		return unavailable(_("Sales Order is not available"))
	ensure_permission("Sales Order")

	so = frappe.qb.DocType("Sales Order")
	rows = (
		frappe.qb.from_(so)
		.select(so.base_grand_total, so.advance_paid)
		.where(
			(so.docstatus == 1)
			& (so.company == filters.company)
			& (so.status.isin(PENDING_SO_STATUSES))
		)
	).run(as_dict=True)

	total = sum(flt(r.base_grand_total) - flt(r.advance_paid) for r in rows)
	return ok_result(
		flt(total),
		secondary={"label": _("Open Orders"), "value": len(rows), "format": "number"},
		currency=filters.currency,
		format="currency",
	)


def total_sales_orders(filters) -> dict:
	"""Count of submitted sales orders in the selected period."""
	if not frappe.db.exists("DocType", "Sales Order"):
		return unavailable(_("Sales Order is not available"))
	ensure_permission("Sales Order")

	so = frappe.qb.DocType("Sales Order")
	rows = (
		frappe.qb.from_(so)
		.select(so.name, so.status)
		.where(
			(so.docstatus == 1)
			& (so.company == filters.company)
			& (so.transaction_date >= filters.from_date)
			& (so.transaction_date <= filters.to_date)
		)
	).run(as_dict=True)

	open_count = sum(1 for r in rows if r.status in OPEN_SO_STATUSES)
	completed = sum(1 for r in rows if r.status == "Completed")
	return ok_result(
		len(rows),
		secondary={
			"label": _("Open / Completed"),
			"value": f"{open_count} / {completed}",
			"format": "text",
			"open": open_count,
			"completed": completed,
		},
		currency=None,
		format="number",
	)


def pending_orders_detail(filters) -> list[dict]:
	"""Rows for pending SO detail (customer, age, status, delivery)."""
	ensure_permission("Sales Order")
	so = frappe.qb.DocType("Sales Order")
	rows = (
		frappe.qb.from_(so)
		.select(
			so.name,
			so.customer,
			so.customer_name,
			so.status,
			so.transaction_date,
			so.delivery_date,
			so.base_grand_total,
			so.advance_paid,
		)
		.where(
			(so.docstatus == 1)
			& (so.company == filters.company)
			& (so.status.isin(PENDING_SO_STATUSES))
		)
		.orderby(so.transaction_date)
	).run(as_dict=True)

	as_on = filters.as_on
	for r in rows:
		r.pending_value = flt(r.base_grand_total) - flt(r.advance_paid)
		r.order_age_days = (as_on - r.transaction_date).days if r.transaction_date else None
	return rows
