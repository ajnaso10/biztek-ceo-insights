# Copyright (c) 2026, Savad Ibrahim and Contributors
# License: MIT

"""KPI registry — single place to add future cards."""

from __future__ import annotations

from typing import Any, Callable

from biztek_ceo_insights.kpi import cash, hr, payables, pdc, receivables, sales, stock
from biztek_ceo_insights.kpi.constants import (
	SECTION_CASH,
	SECTION_FINANCE,
	SECTION_HR,
	SECTION_INVENTORY,
	SECTION_LABELS,
	SECTION_ORDER,
	SECTION_SALES,
)

KPIFn = Callable[[Any], dict]


class KPIDefinition:
	__slots__ = (
		"id",
		"section",
		"label",
		"formula_doc",
		"value_fn",
		"detail_dashboard_key",
		"detail_fn",
		"snapshot",
	)

	def __init__(
		self,
		*,
		id: str,
		section: str,
		label: str,
		formula_doc: str,
		value_fn: KPIFn,
		detail_dashboard_key: str,
		detail_fn: Callable | None = None,
		snapshot: bool = True,
	):
		self.id = id
		self.section = section
		self.label = label
		self.formula_doc = formula_doc
		self.value_fn = value_fn
		self.detail_dashboard_key = detail_dashboard_key
		self.detail_fn = detail_fn
		self.snapshot = snapshot


KPI_REGISTRY: list[KPIDefinition] = [
	KPIDefinition(
		id="pending_so_value",
		section=SECTION_SALES,
		label="Pending Sales Orders Value",
		formula_doc=(
			"Submitted Sales Orders in statuses To Deliver and Bill / To Bill / "
			"To Deliver / To Pay; sum(base_grand_total - advance_paid)."
		),
		value_fn=sales.pending_sales_orders_value,
		detail_dashboard_key="td-pending-so",
		detail_fn=sales.pending_orders_detail,
		snapshot=True,
	),
	KPIDefinition(
		id="total_sales_orders",
		section=SECTION_SALES,
		label="Total Sales Orders",
		formula_doc=(
			"Count of submitted Sales Orders with transaction_date in the selected period. "
			"Secondary: open vs completed."
		),
		value_fn=sales.total_sales_orders,
		detail_dashboard_key="td-total-so",
		snapshot=False,
	),
	KPIDefinition(
		id="total_stock",
		section=SECTION_INVENTORY,
		label="Total Stock",
		formula_doc="sum(Bin.stock_value) for company; secondary sum(actual_qty).",
		value_fn=stock.total_stock,
		detail_dashboard_key="td-total-stock",
		detail_fn=stock.stock_by_warehouse,
		snapshot=True,
	),
	KPIDefinition(
		id="total_ar",
		section=SECTION_FINANCE,
		label="Total A/R",
		formula_doc=(
			"Payment Ledger Entry outstanding for Customer × Sales Invoice "
			"(delinked=0, outstanding > 0.5)."
		),
		value_fn=receivables.total_ar,
		detail_dashboard_key="td-total-ar",
		detail_fn=receivables.ar_detail,
		snapshot=True,
	),
	KPIDefinition(
		id="total_ap",
		section=SECTION_FINANCE,
		label="Total A/P",
		formula_doc=(
			"Payment Ledger Entry outstanding for Supplier × Purchase Invoice "
			"(delinked=0, outstanding > 0.5)."
		),
		value_fn=payables.total_ap,
		detail_dashboard_key="td-total-ap",
		detail_fn=payables.ap_detail,
		snapshot=True,
	),
	KPIDefinition(
		id="pdc_pending_payable",
		section=SECTION_FINANCE,
		label="PDC Pending Payable",
		formula_doc=(
			"Submitted Payment Entry with custom_pdc_payment=1, custom_pdc_status=Pending, "
			"payment_type=Pay; sum(base_paid_amount)."
		),
		value_fn=pdc.pdc_pending_payable,
		detail_dashboard_key="td-pdc-payable",
		detail_fn=pdc.pdc_pending_detail,
		snapshot=True,
	),
	KPIDefinition(
		id="cash_in_hand",
		section=SECTION_CASH,
		label="Cash in Hand",
		formula_doc=(
			"Closing balance of leaf Cash accounts via get_balance_on(as_on); "
			"excludes Company PDC accounts."
		),
		value_fn=cash.cash_in_hand,
		detail_dashboard_key="td-cash-hand",
		detail_fn=lambda f: cash.cash_accounts_detail(f, "Cash"),
		snapshot=True,
	),
	KPIDefinition(
		id="net_cash",
		section=SECTION_CASH,
		label="Net Cash",
		formula_doc="Cash in Hand + Cash in Bank (closing balances as of as_on).",
		value_fn=cash.net_cash,
		detail_dashboard_key="td-net-cash",
		detail_fn=lambda f: cash.cash_accounts_detail(f, None),
		snapshot=True,
	),
	KPIDefinition(
		id="cash_in_bank",
		section=SECTION_CASH,
		label="Cash in Bank",
		formula_doc=(
			"Closing balance of leaf Bank accounts via get_balance_on(as_on); "
			"excludes Company PDC accounts."
		),
		value_fn=cash.cash_in_bank,
		detail_dashboard_key="td-cash-bank",
		detail_fn=lambda f: cash.cash_accounts_detail(f, "Bank"),
		snapshot=True,
	),
	KPIDefinition(
		id="total_head_count",
		section=SECTION_HR,
		label="Total Head Count",
		formula_doc="Count of Employee where status=Active and company matches.",
		value_fn=hr.total_head_count,
		detail_dashboard_key="td-headcount",
		detail_fn=lambda f: hr.headcount_by_dimension(f, "department"),
		snapshot=True,
	),
	KPIDefinition(
		id="salary_total",
		section=SECTION_HR,
		label="Salary Total",
		formula_doc=(
			"Submitted Salary Slip in period (end_date in range); sum(base_gross_pay). "
			"Labeled Payroll Cost (Gross). Does not include salary Journal Entries."
		),
		value_fn=hr.salary_total,
		detail_dashboard_key="td-salary",
		snapshot=False,
	),
	KPIDefinition(
		id="hr_kpi",
		section=SECTION_HR,
		label="HR KPI",
		formula_doc=(
			"Summary mosaic: primary = Active Headcount; supporting = New Hires "
			"(date_of_joining in range) and Exits (relieving_date in range). "
			"No weighted score."
		),
		value_fn=hr.hr_kpi_summary,
		detail_dashboard_key="td-hr-kpi",
		detail_fn=hr.hr_detail_metrics,
		snapshot=False,
	),
]


def get_kpi(kpi_id: str) -> KPIDefinition | None:
	for kpi in KPI_REGISTRY:
		if kpi.id == kpi_id:
			return kpi
	return None


def list_kpi_ids() -> list[str]:
	return [k.id for k in KPI_REGISTRY]


def section_label(section: str) -> str:
	return SECTION_LABELS.get(section, section)


def ordered_sections() -> list[str]:
	return list(SECTION_ORDER)
