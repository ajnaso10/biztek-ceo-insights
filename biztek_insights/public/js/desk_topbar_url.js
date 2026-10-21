/**
 * Desk: show Insights in the top bar (role-gated) and open the Insights SPA.
 * biztek_custom.topbar.filter_workspaces drops type=URL — patch that, then rewire clicks.
 * Do NOT inject Insights for users without workspace role access (e.g. Sales Manager).
 */
(function () {
	"use strict";

	const INSIGHTS_NAME = "Insights";
	const INSIGHTS_URL = "/insights/dashboards";
	const INSIGHTS_ROLES = ["System Manager", "Insights Admin", "Insights User"];

	function userCanSeeInsights() {
		if (!window.frappe) {
			return false;
		}
		if (frappe.session && frappe.session.user === "Administrator") {
			return true;
		}
		const roles = frappe.user_roles || [];
		if (roles.indexOf("Administrator") !== -1) {
			return true;
		}
		return INSIGHTS_ROLES.some(function (role) {
			return roles.indexOf(role) !== -1;
		});
	}

	function insightsUrl(ws) {
		if (ws && ws.external_link) {
			return String(ws.external_link).trim();
		}
		return INSIGHTS_URL;
	}

	function isInsightsWorkspace(ws) {
		if (!ws) {
			return false;
		}
		if (ws.type === "URL" && (ws.external_link || ws.link_to)) {
			const link = ws.external_link || ws.link_to;
			if (String(link).indexOf("/insights") === 0) {
				return true;
			}
		}
		const name = String(ws.name || ws.title || "").trim();
		return name === INSIGHTS_NAME;
	}

	function goInsights(ws) {
		window.location.href = insightsUrl(ws);
	}

	function removeUnauthorizedInsightsLink() {
		if (!window.jQuery || userCanSeeInsights()) {
			return;
		}
		$("#biztek-workspace-nav .biztek-workspace-link").filter(function () {
			const name = String($(this).attr("data-workspace") || $(this).text() || "").trim();
			return name === INSIGHTS_NAME;
		}).remove();
	}

	function patchFilterWorkspaces() {
		if (
			!window.biztek_custom ||
			!biztek_custom.topbar ||
			typeof biztek_custom.topbar.filter_workspaces !== "function"
		) {
			return false;
		}
		if (biztek_custom.topbar.filter_workspaces.__biztekInsightsPatched) {
			return true;
		}

		const original = biztek_custom.topbar.filter_workspaces.bind(biztek_custom.topbar);
		biztek_custom.topbar.filter_workspaces = function (pages) {
			const allowed = (pages || []).filter(function (ws) {
				if (!ws || ws.is_hidden || ws.title === "Welcome Workspace") {
					return false;
				}
				const name = biztek_custom.topbar.get_workspace_name(ws);
				if (!name) {
					return false;
				}
				const typeOk = !ws.type || ws.type === "Workspace" || ws.type === "URL";
				if (!typeOk) {
					return false;
				}
				if (isInsightsWorkspace(ws) && !userCanSeeInsights()) {
					return false;
				}
				return biztek_custom.topbar.user_can_see_workspace(ws);
			});
			return allowed.sort(function (a, b) {
				const a_home = a.title === "Home" ? 0 : 1;
				const b_home = b.title === "Home" ? 0 : 1;
				if (a_home !== b_home) {
					return a_home - b_home;
				}
				return (a.sequence_id || 0) - (b.sequence_id || 0);
			});
		};
		biztek_custom.topbar.filter_workspaces.__biztekInsightsPatched = true;
		biztek_custom.topbar._filter_workspaces_original = original;
		return true;
	}

	function ensureInsightsLinkInNav() {
		if (!window.jQuery) {
			return;
		}
		removeUnauthorizedInsightsLink();
		if (!userCanSeeInsights()) {
			return;
		}
		const $nav = $("#biztek-workspace-nav");
		if (!$nav.length) {
			return;
		}
		const exists = $nav.find('.biztek-workspace-link[data-workspace="' + INSIGHTS_NAME + '"]').length;
		if (exists) {
			rewireInsightsLinks();
			return;
		}
		// Insights is non-public so API omits it — inject only for permitted roles
		const $link = $('<a class="biztek-workspace-link" href="#"></a>')
			.text(INSIGHTS_NAME)
			.attr("data-workspace", INSIGHTS_NAME)
			.attr("href", INSIGHTS_URL);
		$nav.append($link);
		rewireInsightsLinks();
		if (biztek_custom.topbar.scroll_nav) {
			biztek_custom.topbar.scroll_nav();
		}
	}

	async function rebuildTopbarIfNeeded() {
		if (!window.biztek_custom || !biztek_custom.topbar) {
			return;
		}
		if (!window.jQuery) {
			return;
		}
		removeUnauthorizedInsightsLink();

		const $nav = $("#biztek-workspace-nav");
		const alreadyShown =
			$nav.length &&
			$nav.find('.biztek-workspace-link[data-workspace="' + INSIGHTS_NAME + '"]').length;

		if (alreadyShown) {
			if (!userCanSeeInsights()) {
				removeUnauthorizedInsightsLink();
			} else {
				rewireInsightsLinks();
			}
			return;
		}

		if (!userCanSeeInsights()) {
			return;
		}

		try {
			const workspaces = await biztek_custom.topbar.fetch_workspaces();
			const hasInsights = (workspaces || []).some(isInsightsWorkspace);
			if (!hasInsights) {
				ensureInsightsLinkInNav();
				return;
			}
			biztek_custom.topbar.initialized = false;
			$("#biztek-workspace-topbar").remove();
			$("body").removeClass("biztek-has-workspace-topbar");
			biztek_custom.topbar.render(workspaces);
			rewireInsightsLinks();
		} catch (e) {
			ensureInsightsLinkInNav();
		}
	}

	function patchOpenWorkspace() {
		if (
			!window.biztek_custom ||
			!biztek_custom.topbar ||
			typeof biztek_custom.topbar.open_workspace !== "function"
		) {
			return false;
		}
		if (biztek_custom.topbar.open_workspace.__biztekInsightsPatched) {
			return true;
		}

		const original = biztek_custom.topbar.open_workspace.bind(biztek_custom.topbar);

		biztek_custom.topbar.open_workspace = function (ws) {
			if (isInsightsWorkspace(ws) || (ws && ws.type === "URL" && ws.external_link)) {
				if (isInsightsWorkspace(ws) && !userCanSeeInsights()) {
					return;
				}
				const url = (ws && ws.external_link) || (ws && ws.type === "URL" && ws.link_to) || "";
				if (isInsightsWorkspace(ws) || (url && String(url).charAt(0) === "/")) {
					try {
						localStorage.current_page = (ws && (ws.name || ws.title)) || INSIGHTS_NAME;
						localStorage.is_current_page_public = "true";
					} catch (e) {
						/* ignore */
					}
					window.location.href =
						(url && String(url).charAt(0) === "/" ? url : null) || insightsUrl(ws);
					return;
				}
			}
			return original(ws);
		};
		biztek_custom.topbar.open_workspace.__biztekInsightsPatched = true;
		return true;
	}

	function rewireInsightsLinks() {
		if (!window.jQuery) {
			return;
		}
		if (!userCanSeeInsights()) {
			removeUnauthorizedInsightsLink();
			return;
		}
		$("#biztek-workspace-nav .biztek-workspace-link").each(function () {
			const $el = $(this);
			const name = String($el.attr("data-workspace") || $el.text() || "").trim();
			if (name !== INSIGHTS_NAME) {
				return;
			}
			$el.attr("href", INSIGHTS_URL);
			$el.off("click.biztekInsights").on("click.biztekInsights", function (e) {
				e.preventDefault();
				e.stopImmediatePropagation();
				goInsights({ name: INSIGHTS_NAME, external_link: INSIGHTS_URL, type: "URL" });
			});
		});
	}

	function patchRender() {
		if (!window.biztek_custom || !biztek_custom.topbar || typeof biztek_custom.topbar.render !== "function") {
			return false;
		}
		if (biztek_custom.topbar.render.__biztekInsightsPatched) {
			rewireInsightsLinks();
			return true;
		}
		const original = biztek_custom.topbar.render.bind(biztek_custom.topbar);
		biztek_custom.topbar.render = function (workspaces) {
			const result = original(workspaces);
			rewireInsightsLinks();
			ensureInsightsLinkInNav();
			return result;
		};
		biztek_custom.topbar.render.__biztekInsightsPatched = true;
		rewireInsightsLinks();
		return true;
	}

	function patchRouterRedirect() {
		if (!window.frappe || !frappe.router || frappe.router.__biztekInsightsRedirect) {
			return !!window.frappe;
		}
		frappe.router.__biztekInsightsRedirect = true;

		function maybeRedirect() {
			try {
				if (!userCanSeeInsights()) {
					return;
				}
				const route = frappe.get_route ? frappe.get_route() : [];
				if (!route || !route.length) {
					return;
				}
				const parts = route.map(function (p) {
					return String(p || "");
				});
				const first = parts[0];
				const leaf = parts[parts.length - 1];

				const isInsightsSlug = first.toLowerCase() === "insights";
				const isWorkspaceInsights =
					(first === "Workspaces" || first.toLowerCase() === "workspaces") &&
					leaf === INSIGHTS_NAME;

				if (isInsightsSlug || isWorkspaceInsights) {
					window.location.replace(INSIGHTS_URL);
				}
			} catch (e) {
				/* ignore */
			}
		}

		$(document).on("page-change", maybeRedirect);
		frappe.after_ajax && frappe.after_ajax(maybeRedirect);
		setTimeout(maybeRedirect, 0);
		setTimeout(maybeRedirect, 400);
		return true;
	}

	function tryPatch() {
		const filterOk = patchFilterWorkspaces();
		const a = patchOpenWorkspace();
		const b = patchRender();
		patchRouterRedirect();
		removeUnauthorizedInsightsLink();
		rewireInsightsLinks();
		if (filterOk) {
			rebuildTopbarIfNeeded();
		}
		if (a && b && filterOk) {
			return;
		}
		setTimeout(tryPatch, 300);
	}

	if (window.jQuery) {
		$(document).on("app_ready", tryPatch);
		$(document).on("page-change", function () {
			removeUnauthorizedInsightsLink();
			rewireInsightsLinks();
		});
	}
	if (window.frappe && frappe.ready) {
		frappe.ready(tryPatch);
	}
	tryPatch();
	[500, 1500, 3000].forEach(function (ms) {
		setTimeout(function () {
			tryPatch();
			removeUnauthorizedInsightsLink();
			rewireInsightsLinks();
			if (userCanSeeInsights()) {
				ensureInsightsLinkInNav();
			}
		}, ms);
	});
})();
