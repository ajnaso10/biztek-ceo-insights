/**
 * Biztek workspace top bar for Insights SPA (no Desk / jQuery).
 * Injected into /insights and /insights_v2 by biztek_ceo_insights.branding.after_request.
 */
(function () {
	"use strict";

	if (window.__biztekCeoInsightsTopbar) {
		return;
	}
	window.__biztekCeoInsightsTopbar = true;

	const TOPBAR_HEIGHT = "48px";
	const BRAND_LOGO = "/assets/biztek_custom/images/biztek-topbar-logo.png?v=16";
	const BIZTEK_FAVICON = "/assets/biztek_custom/images/favicon.png?v=1";
	const INSIGHTS_LOGO_BIZTEK =
		"/assets/biztek_ceo_insights/images/insights-logo-biztek.svg?v=2";
	const API_METHOD = "biztek_custom.api.workspace.get_topbar_workspaces";
	const INSIGHTS_URL = "/insights/dashboards";
	const INSIGHTS_NAME = "Insights";

	function setBiztekFavicon() {
		const href = BIZTEK_FAVICON;
		document
			.querySelectorAll('link[rel="icon"], link[rel="shortcut icon"]')
			.forEach((el) => el.remove());
		["shortcut icon", "icon"].forEach((rel) => {
			const link = document.createElement("link");
			link.rel = rel;
			link.href = href;
			link.type = "image/png";
			link.setAttribute("data-biztek-ceo-insights-favicon", "1");
			(document.head || document.documentElement).appendChild(link);
		});
	}

	function isUpstreamInsightsLogo(src) {
		if (!src) {
			return false;
		}
		const s = String(src);
		if (s.indexOf("insights-logo-biztek") !== -1) {
			return false;
		}
		return /insights-logo/i.test(s);
	}

	function rebrandInsightsLogos(root) {
		const scope = root && root.querySelectorAll ? root : document;
		scope.querySelectorAll("img").forEach((img) => {
			if (img.dataset.biztekCeoInsightsLogo === "1") {
				return;
			}
			const src = img.getAttribute("src") || img.currentSrc || "";
			if (!isUpstreamInsightsLogo(src)) {
				return;
			}
			img.src = INSIGHTS_LOGO_BIZTEK;
			img.dataset.biztekCeoInsightsLogo = "1";
		});
	}

	function watchInsightsLogos() {
		rebrandInsightsLogos(document);
		if (window.__biztekCeoInsightsLogoObserver) {
			return;
		}
		const observer = new MutationObserver((mutations) => {
			for (const m of mutations) {
				if (m.type === "attributes" && m.target && m.target.tagName === "IMG") {
					rebrandInsightsLogos(m.target.parentNode || document);
				}
				if (m.type === "childList") {
					m.addedNodes.forEach((node) => {
						if (node.nodeType === 1) {
							rebrandInsightsLogos(node);
						}
					});
				}
			}
		});
		observer.observe(document.documentElement, {
			childList: true,
			subtree: true,
			attributes: true,
			attributeFilter: ["src"],
		});
		window.__biztekCeoInsightsLogoObserver = observer;
		[300, 1000, 2500].forEach((ms) => setTimeout(() => rebrandInsightsLogos(document), ms));
	}

	function csrfToken() {
		return (
			window.csrf_token ||
			(window.boot && window.boot.csrf_token) ||
			""
		);
	}

	function slug(name) {
		return String(name || "")
			.trim()
			.toLowerCase()
			.replace(/[/\s]+/g, "-");
	}

	function workspaceName(ws) {
		return (ws && (ws.name || ws.title)) || "";
	}

	function workspaceTitle(ws) {
		const name = workspaceName(ws);
		if (ws && ws.title === "Home") {
			return "Home";
		}
		if (/^Home-.+@.+$/.test(name)) {
			return "Home";
		}
		return (ws && ws.title) || name;
	}

	function isInsightsWorkspace(ws) {
		const name = workspaceName(ws);
		return name === INSIGHTS_NAME || (ws && ws.title === INSIGHTS_NAME);
	}

	function workspaceHref(ws) {
		if (ws && ws.external_link) {
			return ws.external_link;
		}
		if (ws && ws.type === "URL" && ws.link_to) {
			return ws.link_to;
		}
		if (isInsightsWorkspace(ws)) {
			return INSIGHTS_URL;
		}
		const name = workspaceName(ws);
		if (!name) {
			return "/app";
		}
		if (ws.public) {
			return "/app/" + encodeURIComponent(slug(name));
		}
		return "/app/private/" + encodeURIComponent(slug(name));
	}

	function ensureLayoutOffset() {
		document.documentElement.style.setProperty("--biztek-topbar-height", TOPBAR_HEIGHT);
		document.body.classList.add("biztek-has-workspace-topbar");
		document.body.classList.add("biztek-ceo-insights-has-topbar");
	}

	function createBrandLink(homeWs) {
		const a = document.createElement("a");
		a.className = "biztek-workspace-topbar__brand";
		a.href = homeWs ? workspaceHref(homeWs) : "/app";
		a.setAttribute("aria-label", "Biztek");
		const img = document.createElement("img");
		img.src = BRAND_LOGO;
		img.alt = "";
		img.decoding = "async";
		a.appendChild(img);
		a.addEventListener("click", (e) => {
			e.preventDefault();
			window.location.href = homeWs ? workspaceHref(homeWs) : "/app";
		});
		return a;
	}

	function createLink(ws) {
		const name = workspaceName(ws);
		const a = document.createElement("a");
		a.className = "biztek-workspace-link";
		if (isInsightsWorkspace(ws)) {
			a.classList.add("active");
		}
		a.href = workspaceHref(ws);
		a.textContent = workspaceTitle(ws);
		a.dataset.workspace = name;
		if (ws.external_link) {
			a.dataset.externalLink = ws.external_link;
		}
		a.addEventListener("click", (e) => {
			e.preventDefault();
			try {
				localStorage.current_page = name;
				localStorage.is_current_page_public = ws.public ? "true" : "false";
			} catch (err) {
				/* ignore */
			}
			window.location.href = workspaceHref(ws);
		});
		return a;
	}

	function pickHome(workspaces) {
		return (
			workspaces.find((ws) => !ws.public && workspaceTitle(ws) === "Home") ||
			workspaces.find((ws) => ws.public && (ws.title === "Home" || workspaceName(ws) === "Home")) ||
			null
		);
	}

	function ensureInsightsEntry(workspaces) {
		const list = Array.isArray(workspaces) ? workspaces.slice() : [];
		const hasInsights = list.some(isInsightsWorkspace);
		if (!hasInsights) {
			list.push({
				name: INSIGHTS_NAME,
				title: INSIGHTS_NAME,
				public: 1,
				type: "URL",
				external_link: INSIGHTS_URL,
				sequence_id: 5.5,
			});
		}
		return list;
	}

	function render(workspaces) {
		if (document.getElementById("biztek-workspace-topbar")) {
			return;
		}

		const list = ensureInsightsEntry(workspaces);
		const homeWs = pickHome(list);

		const bar = document.createElement("div");
		bar.id = "biztek-workspace-topbar";
		bar.className = "biztek-workspace-topbar";

		const wrap = document.createElement("div");
		wrap.className = "biztek-workspace-topbar__nav-wrap";

		const nav = document.createElement("nav");
		nav.id = "biztek-workspace-nav";
		nav.className = "biztek-workspace-topbar__nav";
		nav.setAttribute("aria-label", "Workspaces");

		list.forEach((ws) => {
			nav.appendChild(createLink(ws));
		});

		wrap.appendChild(nav);
		bar.appendChild(createBrandLink(homeWs));
		bar.appendChild(wrap);

		document.body.insertBefore(bar, document.body.firstChild);
		ensureLayoutOffset();
	}

	function fetchWorkspaces() {
		const headers = {
			Accept: "application/json",
			"X-Frappe-CSRF-Token": csrfToken(),
		};
		return fetch("/api/method/" + API_METHOD, {
			method: "GET",
			credentials: "same-origin",
			headers: headers,
		}).then((res) => {
			if (!res.ok) {
				throw new Error("topbar api " + res.status);
			}
			return res.json();
		}).then((data) => data.message || []);
	}

	function start() {
		if (!document.body) {
			return;
		}
		setBiztekFavicon();
		watchInsightsLogos();
		fetchWorkspaces()
			.then(render)
			.catch(() => {
				render([]);
			});
	}

	if (document.readyState === "loading") {
		document.addEventListener("DOMContentLoaded", start);
	} else {
		start();
	}
})();
