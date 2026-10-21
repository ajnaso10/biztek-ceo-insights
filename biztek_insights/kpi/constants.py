# Copyright (c) 2026, Savad Ibrahim and Contributors
# License: MIT

"""Shared KPI constants."""

PENDING_SO_STATUSES = (
	"To Deliver and Bill",
	"To Bill",
	"To Deliver",
	"To Pay",
)

OPEN_SO_STATUSES = PENDING_SO_STATUSES + ("On Hold",)

SECTION_SALES = "sales"
SECTION_INVENTORY = "inventory"
SECTION_FINANCE = "finance"
SECTION_CASH = "cash"
SECTION_HR = "hr"

SECTION_ORDER = (
	SECTION_SALES,
	SECTION_INVENTORY,
	SECTION_FINANCE,
	SECTION_CASH,
	SECTION_HR,
)

SECTION_LABELS = {
	SECTION_SALES: "Sales and Orders",
	SECTION_INVENTORY: "Inventory",
	SECTION_FINANCE: "Accounts Receivable and Payable",
	SECTION_CASH: "Cash and Bank",
	SECTION_HR: "HR and Payroll",
}
