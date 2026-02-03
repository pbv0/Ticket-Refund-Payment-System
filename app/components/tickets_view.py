import reflex as rx
from app.states.tickets_state import TicketsState, Ticket
from app.components.shared import (
    form_field,
    th,
    status_badge,
    empty_state,
    pagination_control,
)


def ticket_modal() -> rx.Component:
    return rx.radix.primitives.dialog.root(
        rx.radix.primitives.dialog.portal(
            rx.radix.primitives.dialog.overlay(
                class_name="fixed inset-0 bg-black/50 backdrop-blur-sm z-40"
            ),
            rx.radix.primitives.dialog.content(
                rx.radix.primitives.dialog.title(
                    rx.cond(TicketsState.is_edit_mode, "Edit Ticket", "New Ticket"),
                    class_name="text-xl font-semibold text-gray-900 mb-4",
                ),
                rx.el.form(
                    rx.cond(
                        TicketsState.is_edit_mode,
                        rx.el.input(
                            type="hidden",
                            name="ticket_id",
                            value=TicketsState.current_ticket["ticket_id"],
                        ),
                    ),
                    form_field(
                        "Customer ID",
                        rx.el.input(
                            name="customer_id",
                            default_value=TicketsState.current_ticket["customer_id"],
                            class_name="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none transition-all",
                            placeholder="CUST-001",
                        ),
                        required=True,
                    ),
                    form_field(
                        "Subject",
                        rx.el.input(
                            name="subject",
                            default_value=TicketsState.current_ticket["subject"],
                            class_name="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none transition-all",
                            placeholder="Login issue...",
                        ),
                        required=True,
                    ),
                    form_field(
                        "Status",
                        rx.el.div(
                            rx.el.select(
                                rx.el.option("Open", value="open"),
                                rx.el.option("Pending", value="pending"),
                                rx.el.option("Resolved", value="resolved"),
                                rx.el.option("Closed", value="closed"),
                                name="status",
                                default_value=TicketsState.current_ticket["status"],
                                class_name="w-full px-3 py-2 border border-gray-300 rounded-lg appearance-none bg-white focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none transition-all",
                            ),
                            rx.icon(
                                "chevron-down",
                                class_name="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500 pointer-events-none",
                            ),
                            class_name="relative",
                        ),
                        required=True,
                    ),
                    rx.el.div(
                        rx.el.button(
                            "Cancel",
                            type="button",
                            on_click=TicketsState.close_modal,
                            class_name="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500",
                        ),
                        rx.el.button(
                            "Save Ticket",
                            type="submit",
                            class_name="px-4 py-2 text-sm font-medium text-white bg-indigo-600 rounded-lg hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500",
                        ),
                        class_name="flex justify-end gap-3 mt-6 pt-6 border-t border-gray-100",
                    ),
                    on_submit=TicketsState.save_ticket,
                ),
                class_name="fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 bg-white rounded-2xl shadow-xl p-6 w-full max-w-md z-50 focus:outline-none",
            ),
        ),
        open=TicketsState.is_open,
        on_open_change=TicketsState.close_modal,
    )


def tickets_view() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.h1("Help Tickets", class_name="text-2xl font-bold text-gray-900"),
            rx.el.button(
                rx.icon("plus", class_name="w-4 h-4 mr-2"),
                "New Ticket",
                on_click=TicketsState.open_create_modal,
                class_name="flex items-center px-4 py-2 bg-indigo-600 text-white rounded-xl hover:bg-indigo-700 transition-colors text-sm font-medium",
            ),
            class_name="flex justify-between items-center mb-6",
        ),
        rx.el.div(
            rx.el.div(
                rx.el.input(
                    placeholder="Search tickets...",
                    on_change=TicketsState.search_tickets.debounce(300),
                    class_name="w-full pl-10 pr-4 py-2 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent",
                ),
                rx.icon(
                    "search",
                    class_name="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400",
                ),
                class_name="relative flex-1 max-w-md",
            ),
            rx.el.div(
                rx.el.select(
                    rx.el.option("All Statuses", value="all"),
                    rx.el.option("Open", value="open"),
                    rx.el.option("Pending", value="pending"),
                    rx.el.option("Resolved", value="resolved"),
                    rx.el.option("Closed", value="closed"),
                    on_change=TicketsState.filter_status,
                    class_name="pl-3 pr-8 py-2 border border-gray-200 rounded-xl appearance-none bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500",
                ),
                rx.icon(
                    "filter",
                    class_name="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none",
                ),
                class_name="relative",
            ),
            class_name="flex gap-4 mb-6",
        ),
        rx.cond(
            TicketsState.loading,
            rx.el.div(rx.spinner(), class_name="flex justify-center py-12"),
            rx.cond(
                TicketsState.tickets.length() > 0,
                rx.el.div(
                    rx.el.table(
                        rx.el.thead(
                            rx.el.tr(
                                th(
                                    "Ticket ID",
                                    "ticket_id",
                                    TicketsState.sort_column,
                                    TicketsState.sort_order,
                                    TicketsState.sort_by("ticket_id"),
                                ),
                                th(
                                    "Customer",
                                    "customer_id",
                                    TicketsState.sort_column,
                                    TicketsState.sort_order,
                                    TicketsState.sort_by("customer_id"),
                                ),
                                th(
                                    "Subject",
                                    "subject",
                                    TicketsState.sort_column,
                                    TicketsState.sort_order,
                                    TicketsState.sort_by("subject"),
                                ),
                                th(
                                    "Status",
                                    "status",
                                    TicketsState.sort_column,
                                    TicketsState.sort_order,
                                    TicketsState.sort_by("status"),
                                ),
                                th(
                                    "Created",
                                    "created_at",
                                    TicketsState.sort_column,
                                    TicketsState.sort_order,
                                    TicketsState.sort_by("created_at"),
                                ),
                                rx.el.th("", class_name="px-6 py-3"),
                            ),
                            class_name="bg-gray-50 border-b border-gray-100",
                        ),
                        rx.foreach(
                            TicketsState.tickets,
                            lambda t: rx.el.tbody(
                                rx.el.tr(
                                    rx.el.td(
                                        rx.el.div(
                                            rx.el.button(
                                                rx.icon(
                                                    rx.cond(
                                                        TicketsState.expanded_ticket_id
                                                        == t["ticket_id"],
                                                        "chevron-down",
                                                        "chevron-right",
                                                    ),
                                                    class_name="w-4 h-4 text-gray-400",
                                                ),
                                                on_click=TicketsState.toggle_row(
                                                    t["ticket_id"]
                                                ),
                                                class_name="mr-2 p-1 hover:bg-gray-100 rounded-md transition-colors",
                                            ),
                                            rx.el.span(
                                                t["ticket_id"],
                                                class_name="font-mono text-xs text-gray-400",
                                            ),
                                            class_name="flex items-center",
                                        ),
                                        class_name="px-6 py-4",
                                    ),
                                    rx.el.td(
                                        t["customer_id"],
                                        class_name="px-6 py-4 text-sm font-medium text-gray-900",
                                    ),
                                    rx.el.td(
                                        t["subject"],
                                        class_name="px-6 py-4 text-sm text-gray-500",
                                    ),
                                    rx.el.td(
                                        status_badge(
                                            t["status"],
                                            {
                                                "open": "bg-green-100 text-green-700",
                                                "pending": "bg-yellow-100 text-yellow-700",
                                                "resolved": "bg-blue-100 text-blue-700",
                                                "closed": "bg-gray-100 text-gray-600",
                                            },
                                        ),
                                        class_name="px-6 py-4",
                                    ),
                                    rx.el.td(
                                        t["created_at"],
                                        class_name="px-6 py-4 text-sm text-gray-500 whitespace-nowrap",
                                    ),
                                    rx.el.td(
                                        rx.el.div(
                                            rx.el.button(
                                                rx.icon("pencil", class_name="w-4 h-4"),
                                                on_click=TicketsState.open_edit_modal(
                                                    t
                                                ),
                                                class_name="p-2 text-gray-400 hover:text-indigo-600 hover:bg-indigo-50 rounded-lg transition-colors",
                                            ),
                                            rx.el.button(
                                                rx.icon(
                                                    "trash-2", class_name="w-4 h-4"
                                                ),
                                                on_click=TicketsState.prompt_delete(
                                                    t["ticket_id"]
                                                ),
                                                class_name="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors",
                                            ),
                                            class_name="flex items-center justify-end gap-2",
                                        ),
                                        class_name="px-6 py-4",
                                    ),
                                    class_name=rx.cond(
                                        TicketsState.expanded_ticket_id
                                        == t["ticket_id"],
                                        "bg-indigo-50/50 border-b border-gray-100",
                                        "hover:bg-gray-50 transition-colors border-b border-gray-100 last:border-0",
                                    ),
                                ),
                                rx.cond(
                                    TicketsState.expanded_ticket_id == t["ticket_id"],
                                    rx.el.tr(
                                        rx.el.td(
                                            rx.el.div(
                                                rx.el.h4(
                                                    "Related Refunds",
                                                    class_name="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3",
                                                ),
                                                rx.cond(
                                                    TicketsState.loading_related,
                                                    rx.el.div(
                                                        rx.spinner(size="1"),
                                                        class_name="py-2",
                                                    ),
                                                    rx.cond(
                                                        TicketsState.related_refunds.length()
                                                        > 0,
                                                        rx.el.div(
                                                            rx.foreach(
                                                                TicketsState.related_refunds,
                                                                lambda r: rx.el.div(
                                                                    rx.el.div(
                                                                        rx.el.span(
                                                                            r["date"],
                                                                            class_name="text-gray-500 w-24",
                                                                        ),
                                                                        rx.el.span(
                                                                            f"${r['amount']}",
                                                                            class_name="font-medium text-gray-900",
                                                                        ),
                                                                        rx.cond(
                                                                            r[
                                                                                "approved"
                                                                            ],
                                                                            rx.el.span(
                                                                                "Approved",
                                                                                class_name="text-xs bg-green-100 text-green-700 px-2 py-0.5 rounded-full ml-2",
                                                                            ),
                                                                            rx.cond(
                                                                                r[
                                                                                    "approved"
                                                                                ]
                                                                                == None,
                                                                                rx.el.span(
                                                                                    "Pending",
                                                                                    class_name="text-xs bg-yellow-100 text-yellow-700 px-2 py-0.5 rounded-full ml-2",
                                                                                ),
                                                                                rx.el.span(
                                                                                    "Denied",
                                                                                    class_name="text-xs bg-red-100 text-red-700 px-2 py-0.5 rounded-full ml-2",
                                                                                ),
                                                                            ),
                                                                        ),
                                                                        class_name="flex items-center text-sm",
                                                                    ),
                                                                    rx.el.button(
                                                                        "View Refund",
                                                                        rx.icon(
                                                                            "arrow-right",
                                                                            class_name="w-3 h-3 ml-1",
                                                                        ),
                                                                        class_name="text-xs text-indigo-600 hover:text-indigo-800 flex items-center font-medium",
                                                                        on_click=rx.redirect(
                                                                            f"/refunds?search={r['refund_id']}"
                                                                        ),
                                                                    ),
                                                                    class_name="flex items-center justify-between py-2 border-b border-gray-100 last:border-0",
                                                                ),
                                                            ),
                                                            class_name="bg-white rounded-lg border border-gray-200 px-4 py-2",
                                                        ),
                                                        rx.el.p(
                                                            "No refunds found for this ticket.",
                                                            class_name="text-sm text-gray-400 italic",
                                                        ),
                                                    ),
                                                ),
                                                class_name="p-6 bg-gray-50/80",
                                            ),
                                            col_span=5,
                                            class_name="p-0",
                                        )
                                    ),
                                ),
                                class_name="divide-y divide-gray-100",
                            ),
                        ),
                        class_name="w-full text-left",
                    ),
                    pagination_control(
                        TicketsState.page,
                        TicketsState.total_pages,
                        TicketsState.prev_page,
                        TicketsState.next_page,
                        TicketsState.total_count,
                        TicketsState.page_size,
                    ),
                    class_name="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden",
                ),
                empty_state(
                    "ticket",
                    "No tickets found",
                    "Get started by creating a new support ticket.",
                ),
            ),
        ),
        ticket_modal(),
        rx.radix.primitives.dialog.root(
            rx.radix.primitives.dialog.portal(
                rx.radix.primitives.dialog.overlay(
                    class_name="fixed inset-0 bg-black/50 backdrop-blur-sm z-50"
                ),
                rx.radix.primitives.dialog.content(
                    rx.radix.primitives.dialog.title(
                        "Confirm Delete",
                        class_name="text-lg font-bold text-gray-900 mb-2",
                    ),
                    rx.el.p(
                        "Are you sure you want to delete this ticket? This action cannot be undone.",
                        class_name="text-gray-500 mb-6",
                    ),
                    rx.el.div(
                        rx.el.button(
                            "Cancel",
                            on_click=TicketsState.cancel_delete,
                            class_name="px-4 py-2 text-gray-700 font-medium hover:bg-gray-100 rounded-lg",
                        ),
                        rx.el.button(
                            "Delete",
                            on_click=TicketsState.confirm_delete,
                            class_name="px-4 py-2 bg-red-600 text-white font-medium hover:bg-red-700 rounded-lg",
                        ),
                        class_name="flex justify-end gap-3",
                    ),
                    class_name="fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 bg-white rounded-xl shadow-xl p-6 w-full max-w-sm z-50",
                ),
            ),
            open=TicketsState.delete_id != "",
        ),
        class_name="flex-1 md:ml-72 p-8 bg-gray-50/50 min-h-screen",
    )