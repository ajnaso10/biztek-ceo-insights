/**
 * Hide Documentation / Telegram / Frappe Cloud (and related) links in Insights SPA.
 * Injected into /insights and /insights_v2 by biztek_ceo_insights.branding.after_request.
 */
(function () {
	"use strict";

	if (window.__biztekCeoInsightsHideLinks) {
		return;
	}
	window.__biztekCeoInsightsHideLinks = true;

	const HIDDEN_LABELS = new Set([
		"documentation",
		"join telegram group",
		"login to frappe cloud",
		"login to frappe cloud?",
	]);

	const BLOCKED_HOST_PATTERNS = [
		/^docs\.frappe\.io$/i,
		/^docs\.frappeinsights\.com$/i,
		/^t\.me$/i,
		/^frappecloud\.com$/i,
		/(^|\.)frappe\.cloud$/i,
		/^frappeframework\.com$/i,
		/^frappe\.io$/i,
	];

	const BLOCKED_PATH_HINTS = ["/insights", "/frappeinsights", "/marketplace/apps/insights"];

	function normalizeLabel(text) {
		return String(text || "")
			.replace(/\s+/g, " ")
			.trim()
			.toLowerCase();
	}

	function parseUrl(raw) {
		if (!raw || typeof raw !== "string") {
			return null;
		}
		try {
			return new URL(raw, window.location.origin);
		} catch (e) {
			return null;
		}
	}

	function isBlockedUrl(raw) {
		const url = parseUrl(raw);
		if (!url) {
			return false;
		}
		if (url.origin === window.location.origin) {
			return false;
		}
		const host = url.hostname;
		if (!BLOCKED_HOST_PATTERNS.some((re) => re.test(host))) {
			return false;
		}
		// t.me: only Insights Telegram; other hosts blocked entirely
		if (/^t\.me$/i.test(host)) {
			return /frappeinsights/i.test(url.pathname);
		}
		if (/^frappe\.io$/i.test(host) && !/^docs\./i.test(host)) {
			return BLOCKED_PATH_HINTS.some((hint) => url.pathname.indexOf(hint) !== -1);
		}
		return true;
	}

	function hideElement(el) {
		if (!el || el.dataset.biztekCeoInsightsKeep === "1") {
			return;
		}
		el.style.setProperty("display", "none", "important");
		el.setAttribute("aria-hidden", "true");
		el.dataset.biztekCeoInsightsHidden = "1";
	}

	function labelMatches(el) {
		const label = normalizeLabel(el.innerText || el.textContent || "");
		if (!label || label.length > 80) {
			return false;
		}
		if (HIDDEN_LABELS.has(label)) {
			return true;
		}
		// Dropdown rows sometimes include icon glyph text noise
		for (const hidden of HIDDEN_LABELS) {
			if (label === hidden || label.startsWith(hidden + " ") || label.endsWith(" " + hidden)) {
				return true;
			}
		}
		return false;
	}

	function hideLabeledItems(root) {
		const scope = root || document;
		scope
			.querySelectorAll("button, a, [role='menuitem'], [role='option'], li")
			.forEach((el) => {
				if (el.dataset.biztekCeoInsightsHidden === "1") {
					return;
				}
				if (!labelMatches(el)) {
					return;
				}
				// Prefer the clickable row, not a nested span/icon wrapper
				const row =
					el.closest("[role='menuitem'], [role='option'], a, button") || el;
				hideElement(row);
			});
	}

	function hideBlockedAnchors(root) {
		const scope = root || document;
		scope.querySelectorAll("a[href]").forEach((a) => {
			if (isBlockedUrl(a.getAttribute("href"))) {
				hideElement(a);
			}
		});
	}

	function hideDocsIconButton(root) {
		const scope = root || document;
		scope.querySelectorAll(".mt-auto").forEach((footer) => {
			footer.querySelectorAll("button").forEach((btn) => {
				if (/amber/i.test(btn.className)) {
					return;
				}
				if (btn.querySelector("img, [class*='avatar'], [class*='Avatar']")) {
					return;
				}
				const text = normalizeLabel(btn.innerText || btn.textContent || "");
				if (text) {
					return;
				}
				if (btn.querySelector("svg")) {
					hideElement(btn);
				}
			});
		});
	}

	function hideNeedHelpFrappeLinks(root) {
		const scope = root || document;
		scope.querySelectorAll("a[href]").forEach((a) => {
			if (!isBlockedUrl(a.getAttribute("href"))) {
				return;
			}
			hideElement(a);
			const section = a.closest("div");
			if (section && /need help/i.test(section.textContent || "")) {
				// Leave surrounding copy; only links are hidden above.
			}
		});
	}

	function hideErpnextLabels(root) {
		// Workbook Library groups templates by app_title — hide the "ERPNext" section header
		const scope = root || document;
		scope.querySelectorAll("div, span, p, h1, h2, h3, h4, label").forEach((el) => {
			if (el.dataset.biztekCeoInsightsHidden === "1") {
				return;
			}
			const label = normalizeLabel(el.innerText || el.textContent || "");
			if (label !== "erpnext") {
				return;
			}
			// Avoid hiding large containers that merely contain the word
			if ((el.innerText || "").trim().length > 20) {
				return;
			}
			if (el.querySelector("img, button, a, input, table")) {
				return;
			}
			hideElement(el);
		});
	}

	function hideWorkbookLibraryBlurb(root) {
		// Workbook Library dialog intro copy (upstream Insights marketing text)
		const BLURB_NEEDLE = "ready-made dashboards bundled with your installed apps";
		const scope = root || document;
		scope.querySelectorAll("p, div").forEach((el) => {
			if (el.dataset.biztekCeoInsightsHidden === "1") {
				return;
			}
			const label = normalizeLabel(el.innerText || el.textContent || "");
			if (!label || label.indexOf(BLURB_NEEDLE) === -1) {
				return;
			}
			// Prefer the paragraph itself, not a large parent that includes cards
			if (el.querySelector("img, button, input, table, [class*='grid']")) {
				return;
			}
			if (label.length > 400) {
				return;
			}
			hideElement(el);
		});
	}

	function sweep(root) {
		hideLabeledItems(root);
		hideBlockedAnchors(root);
		hideDocsIconButton(root);
		hideNeedHelpFrappeLinks(root);
		hideErpnextLabels(root);
		hideWorkbookLibraryBlurb(root);
	}

	function ensureStyles() {
		if (document.getElementById("biztek-ceo-insights-hide-links-style")) {
			return;
		}
		const style = document.createElement("style");
		style.id = "biztek-ceo-insights-hide-links-style";
		style.textContent = `
			[data-biztek-ceo-insights-hidden="1"] {
				display: none !important;
			}
		`;
		(document.head || document.documentElement).appendChild(style);
	}

	function patchWindowOpen() {
		if (window.open.__biztekCeoInsightsPatched) {
			return;
		}
		const original = window.open.bind(window);
		function patchedOpen(url) {
			if (isBlockedUrl(String(url || ""))) {
				return null;
			}
			return original.apply(window, arguments);
		}
		patchedOpen.__biztekCeoInsightsPatched = true;
		window.open = patchedOpen;
	}

	function start() {
		ensureStyles();
		patchWindowOpen();
		sweep(document);

		const observer = new MutationObserver((mutations) => {
			for (const m of mutations) {
				if (m.type === "childList") {
					m.addedNodes.forEach((node) => {
						if (node.nodeType === 1) {
							sweep(node);
						}
					});
				}
			}
		});
		observer.observe(document.documentElement, {
			childList: true,
			subtree: true,
		});

		// Vue dropdowns mount asynchronously
		[500, 1500, 3000].forEach((ms) => setTimeout(() => sweep(document), ms));
	}

	if (document.readyState === "loading") {
		document.addEventListener("DOMContentLoaded", start);
	} else {
		start();
	}
})();
