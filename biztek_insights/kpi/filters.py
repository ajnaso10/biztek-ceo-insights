# Copyright (c) 2026, Savad Ibrahim and Contributors
# License: MIT

"""Normalize and validate KPI filter inputs."""

from __future__ import annotations

from typing import Any

import frappe
from frappe import _
from frappe.utils import getdate


def parse_filters(
	company: str | None = None,
	from_date: str | None = None,
	to_date: str | None = None,
	as_on: str | None = None,
) -> frappe._dict:
	"""Return a validated filter dict for KPI calculators."""
	company = (company or "").strip() or frappe.defaults.get_user_default("Company")
	if not company:
		frappe.throw(_("Company is required"))
	if not frappe.db.exists("Company", company):
		frappe.throw(_("Company {0} does not exist").format(company))

	today = getdate()
	to_dt = getdate(to_date) if to_date else today
	from_dt = getdate(from_date) if from_date else to_dt.replace(day=1)
	as_on_dt = getdate(as_on) if as_on else to_dt

	if from_dt > to_dt:
		frappe.throw(_("From Date cannot be after To Date"))

	currency = frappe.get_cached_value("Company", company, "default_currency")
	return frappe._dict(
		company=company,
		from_date=from_dt,
		to_date=to_dt,
		as_on=as_on_dt,
		currency=currency,
	)


def ensure_permission(doctype: str, ptype: str = "read") -> None:
	"""Raise if the current user cannot read the DocType."""
	frappe.has_permission(doctype, ptype, throw=True)


def doctype_exists(doctype: str) -> bool:
	return bool(frappe.db.exists("DocType", doctype))


def meta_has_field(doctype: str, fieldname: str) -> bool:
	if not doctype_exists(doctype):
		return False
	return frappe.get_meta(doctype).has_field(fieldname)


def unavailable(reason: str) -> dict[str, Any]:
	return {
		"available": False,
		"value": None,
		"secondary": None,
		"reason": reason,
	}


def ok_result(
	value: float | int | None,
	*,
	secondary: dict | None = None,
	currency: str | None = None,
	format: str = "currency",
	label: str | None = None,
) -> dict[str, Any]:
	return {
		"available": True,
		"value": value,
		"secondary": secondary,
		"currency": currency,
		"format": format,
		"label": label,
		"reason": None,
	}
