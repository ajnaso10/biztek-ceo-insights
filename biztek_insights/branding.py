"""Insights SPA overlays: hide Frappe links + Biztek workspace top bar."""

from __future__ import annotations

import re

import frappe

BIZTEK_FAVICON = "/assets/biztek_custom/images/favicon.png?v=1"

_HIDE_LINKS_SCRIPT = (
	'<script src="/assets/biztek_insights/js/hide_frappe_links.js?v=3" '
	'data-biztek-insights-hide-links="1"></script>'
)
_INTER_CSS = (
	'<link rel="stylesheet" '
	'href="/assets/frappe/css/fonts/inter/inter.css" '
	'data-biztek-insights-inter-font="1">'
)
_TOPBAR_CSS = (
	'<link rel="stylesheet" '
	'href="/assets/biztek_insights/css/insights_topbar.css?v=2" '
	'data-biztek-insights-topbar-css="1">'
)
_TOPBAR_SCRIPT = (
	'<script src="/assets/biztek_insights/js/insights_topbar.js?v=5" '
	'data-biztek-insights-topbar="1"></script>'
)
_FAVICON_LINKS = (
	f'<link rel="shortcut icon" href="{BIZTEK_FAVICON}" type="image/png" '
	f'data-biztek-insights-favicon="1">'
	f'<link rel="icon" href="{BIZTEK_FAVICON}" type="image/png" '
	f'data-biztek-insights-favicon="1">'
)


def after_request(response):
	"""Inject hide-links + top bar assets into /insights and /insights_v2 HTML."""
	try:
		if not _is_insights_html_response(response):
			return response

		data = response.get_data(as_text=True)
		if not data:
			return response

		data = _apply_biztek_favicon(data)

		head_bits = []
		if 'data-biztek-insights-inter-font="1"' not in data:
			head_bits.append(_INTER_CSS)
		if 'data-biztek-insights-topbar-css="1"' not in data:
			head_bits.append(_TOPBAR_CSS)

		body_bits = []
		if 'data-biztek-insights-hide-links="1"' not in data:
			body_bits.append(_HIDE_LINKS_SCRIPT)
		if 'data-biztek-insights-topbar="1"' not in data:
			body_bits.append(_TOPBAR_SCRIPT)

		if head_bits and "</head>" in data:
			data = data.replace("</head>", "".join(head_bits) + "</head>", 1)
		elif head_bits:
			body_bits = head_bits + body_bits

		if body_bits:
			if "</body>" in data:
				data = data.replace("</body>", "".join(body_bits) + "</body>", 1)
			elif "</head>" in data:
				data = data.replace("</head>", "".join(body_bits) + "</head>", 1)

		response.set_data(data)
	except Exception:
		frappe.log_error(title="Biztek Insights after_request overlay failed")

	return response


def _apply_biztek_favicon(data: str) -> str:
	"""Keep Desk Biztek favicon on Insights SPA (replace Insights app icon)."""
	if 'data-biztek-insights-favicon="1"' in data:
		return data

	# Drop existing icon links (Insights ships its own favicon.png)
	data = re.sub(
		r'<link[^>]+rel=["\'](?:shortcut )?icon["\'][^>]*>\s*',
		"",
		data,
		flags=re.IGNORECASE,
	)
	if "</head>" in data:
		data = data.replace("</head>", f"{_FAVICON_LINKS}</head>", 1)
	return data


def _is_insights_html_response(response) -> bool:
	request = getattr(frappe.local, "request", None)
	if request is None:
		return False

	path = (request.path or "").rstrip("/") or "/"
	if path not in ("/insights", "/insights_v2") and not path.startswith(
		("/insights/", "/insights_v2/")
	):
		return False

	try:
		status = int(getattr(response, "status_code", 200) or 200)
	except Exception:
		status = 200
	if status >= 400:
		return False

	content_type = (response.headers.get("Content-Type") or "").lower()
	if content_type and "html" not in content_type and "text/plain" not in content_type:
		return False

	return True
