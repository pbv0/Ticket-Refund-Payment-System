import reflex as rx
from app.states.dashboard_state import DashboardState


def stat_card(
    title: str,
    value: str,
    subtext: str,
    icon: str,
    trend: str,
    trend_up: bool,
    color_scheme: str = "indigo",
) -> rx.Component:
    colors = {
        "indigo": "bg-indigo-50 text-indigo-600",
        "emerald": "bg-emerald-50 text-emerald-600",
        "amber": "bg-amber-50 text-amber-600",
        "violet": "bg-violet-50 text-violet-600",
        "blue": "bg-blue-50 text-blue-600",
    }
    icon_style = colors.get(color_scheme, colors["indigo"])
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.icon(icon, class_name="w-6 h-6"),
                class_name=f"p-3 rounded-xl {icon_style} mb-4 w-fit",
            ),
            rx.el.div(
                rx.el.p(title, class_name="text-sm font-medium text-gray-500 mb-1"),
                rx.el.h3(value, class_name="text-2xl font-bold text-gray-900"),
                class_name="mb-4",
            ),
            rx.el.div(
                rx.el.span(
                    trend,
                    class_name=f"text-xs font-semibold px-2 py-1 rounded-full {rx.cond(trend_up, 'bg-green-100 text-green-700', 'bg-red-100 text-red-700')} mr-2",
                ),
                rx.el.span(subtext, class_name="text-xs text-gray-500 font-medium"),
                class_name="flex items-center",
            ),
            class_name="flex flex-col h-full justify-between",
        ),
        class_name="bg-white rounded-2xl p-6 shadow-sm border border-gray-100 hover:shadow-md transition-shadow duration-300",
    )


def stats_grid() -> rx.Component:
    return rx.el.div(
        stat_card(
            "Total Tickets",
            DashboardState.total_tickets.to_string(),
            "Tickets processed",
            "ticket",
            f"{DashboardState.tickets_open_count} Open",
            trend_up=False,
            color_scheme="blue",
        ),
        stat_card(
            "Pending Refunds",
            DashboardState.total_refunds_pending.to_string(),
            "Awaiting approval",
            "clock",
            f"{DashboardState.refund_approval_rate}% Appr.",
            trend_up=True,
            color_scheme="amber",
        ),
        stat_card(
            "Total Revenue",
            f"${DashboardState.total_payment_volume:,.2f}",
            "Processed volume",
            "dollar-sign",
            "+12.5%",
            trend_up=True,
            color_scheme="emerald",
        ),
        stat_card(
            "Payment Success",
            f"{DashboardState.payment_success_rate}%",
            "Transaction rate",
            "activity",
            "Stable",
            trend_up=True,
            color_scheme="violet",
        ),
        class_name="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-8",
    )