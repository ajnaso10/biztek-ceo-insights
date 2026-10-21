# Copyright (c) 2026, Savad Ibrahim and Contributors
# License: MIT

"""Cash and bank position KPIs (closing balances via get_balance_on)."""

from __future__ import annotations

import frappe
from frappe import _
from frappe.utils import flt
from erpnext.accounts.utils import get_balance_on

from biztek_insights.kpi.filters import ensure_permission, ok_result, unavailable


def get_pdc_accounts(company: str) -> set[str]:
	"""Company PDC receivable/payable accounts to exclude from cash/bank totals."""
	accounts: set[str] = set()
	meta = frappe.get_meta("Company")
	for field in ("custom_pdc_receivable_account", "custom_pdc_payable_account"):
		if meta.has_field(field):
			value = frappe.db.get_value("Company", company, field)
			if value:
				accounts.add(value)
	return accounts


def get_account_balance_rows(company: str, as_on, account_type: str) -> list[dict]:
	"""Leaf Cash/Bank accounts with closing balance as on date (excludes PDC accounts)."""
	ensure_permission("Account")
	exclude = get_pdc_accounts(company)
	accounts = frappe.get_all(
		"Account",
		filters={
			"company": company,
			"account_type": account_type,
			"is_group": 0,
			"disabled": 0,
		},
		fields=["name", "account_currency"],
		order_by="name",
	)
	rows = []
	for acc in accounts:
		if acc.name in exclude:
			continue
		balance = flt(get_balance_on(acc.name, date=as_on, company=company))
		if not balance:
			continue
		rows.append(
			{
				"account": acc.name,
				"account_type": account_type,
				"balance": balance,
				"currency": acc.account_currency,
			}
		)
	return rows


def sum_balances(rows: list[dict]) -> float:
	return flt(sum(flt(r.get("balance")) for r in rows))


def cash_in_hand(filters) -> dict:
	"""Closing balance of leaf Cash accounts as of as_on."""
	if not frappe.db.exists("DocType", "Account"):
		return unavailable(_("Account is not available"))
	rows = get_account_balance_rows(filters.company, filters.as_on, "Cash")
	return ok_result(sum_balances(rows), currency=filters.currency, format="currency")


def cash_in_bank(filters) -> dict:
	"""Closing balance of leaf Bank accounts as of as_on."""
	if not frappe.db.exists("DocType", "Account"):
		return unavailable(_("Account is not available"))
	rows = get_account_balance_rows(filters.company, filters.as_on, "Bank")
	return ok_result(sum_balances(rows), currency=filters.currency, format="currency")


def net_cash(filters) -> dict:
	"""Net cash position = Cash in Hand + Cash in Bank (closing balances)."""
	if not frappe.db.exists("DocType", "Account"):
		return unavailable(_("Account is not available"))
	cash = sum_balances(get_account_balance_rows(filters.company, filters.as_on, "Cash"))
	bank = sum_balances(get_account_balance_rows(filters.company, filters.as_on, "Bank"))
	return ok_result(
		flt(cash + bank),
		secondary={
			"label": _("Cash / Bank"),
			"value": f"{cash} / {bank}",
			"format": "text",
			"cash": cash,
			"bank": bank,
		},
		currency=filters.currency,
		format="currency",
		label=_("Net Cash (Cash + Bank)"),
	)


def cash_accounts_detail(filters, account_type: str | None = None) -> list[dict]:
	"""Cash and/or bank account balance rows for detail views."""
	types = [account_type] if account_type else ["Cash", "Bank"]
	rows: list[dict] = []
	for t in types:
		rows.extend(get_account_balance_rows(filters.company, filters.as_on, t))
	return rows
