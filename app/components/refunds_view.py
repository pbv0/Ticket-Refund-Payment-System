import reflex as rx
from app.states.refunds_state import RefundsState
from app.components.shared import (
    form_field,
    th,
    status_badge,
    empty_state,
    pagination_control,
)


def refund_modal() -> rx.Component:
    return rx.radix.primitives.dialog.root(
        rx.radix.primitives.dialog.portal(
            rx.radix.primitives.dialog.overlay(
                class_name="fixed inset-0 bg-black/50 backdrop-blur-sm z-40"
            ),
            rx.radix.primitives.dialog.content(
                rx.radix.primitives.dialog.title(
                    rx.cond(
                        RefundsState.is_edit_mode,
                        "Edit Refund Request",
                        "New Refund Request",
                    ),
                    class_name="text-xl font-semibold text-gray-900 mb-4",
                ),
                rx.el.form(
                    rx.cond(
                        RefundsState.is_edit_mode,
                        rx.el.input(
                            type="hidden",
                            name="refund_id",
                            value=RefundsState.current_refund["refund_id"],
                        ),
                    ),
                    form_field(
                        "Ticket ID",
                        rx.el.input(
                            name="ticket_id",
                            default_value=RefundsState.current_refund["ticket_id"],
                            class_name="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 outline-none",
                        ),
                    ),
                    form_field(
                        "Payment ID",
                        rx.el.input(
                            name="payment_id",
                            default_value=RefundsState.current_refund["payment_id"],
                            class_name="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 outline-none",
                        ),
                    ),
                    form_field(
                        "SKU",
                        rx.el.input(
                            name="sku",
                            default_value=RefundsState.current_refund["sku"],
                            class_name="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 outline-none",
                        ),
                    ),
                    form_field(
                        "Approval Status",
                        rx.el.div(
                            rx.el.select(
                                rx.el.option("Pending Review", value="pending"),
                                rx.el.option("Approved", value="true"),
                                rx.el.option("Denied", value="false"),
                                name="approval_status",
                                default_value=rx.cond(
                                    RefundsState.current_refund["approved"] == None,
                                    "pending",
                                    rx.cond(
                                        RefundsState.current_refund["approved"],
                                        "true",
                                        "false",
                                    ),
                                ),
                                class_name="w-full px-3 py-2 border border-gray-300 rounded-lg appearance-none bg-white",
                            ),
                            rx.icon(
                                "chevron-down",
                                class_name="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500 pointer-events-none",
                            ),
                            class_name="relative",
                        ),
                    ),
                    rx.el.div(
                        rx.el.button(
                            "Cancel",
                            type="button",
                            on_click=RefundsState.close_modal,
                            class_name="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50",
                        ),
                        rx.el.button(
                            "Save Request",
                            type="submit",
                            class_name="px-4 py-2 text-sm font-medium text-white bg-indigo-600 rounded-lg hover:bg-indigo-700",
                        ),
                        class_name="flex justify-end gap-3 mt-6 pt-6 border-t border-gray-100",
                    ),
                    on_submit=RefundsState.save_refund,
                ),
                class_name="fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 bg-white rounded-2xl shadow-xl p-6 w-full max-w-md z-50",
            ),
        ),
        open=RefundsState.is_open,
        on_open_change=RefundsState.close_modal,
    )


def refunds_view() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.h1("Refund Requests", class_name="text-2xl font-bold text-gray-900"),
            rx.el.button(
                rx.icon("plus", class_name="w-4 h-4 mr-2"),
                "New Refund",
                on_click=RefundsState.open_create_modal,
                class_name="flex items-center px-4 py-2 bg-indigo-600 text-white rounded-xl hover:bg-indigo-700 transition-colors text-sm font-medium",
            ),
            class_name="flex justify-between items-center mb-6",
        ),
        rx.el.div(
            rx.el.div(
                rx.el.select(
                    rx.el.option("All Requests", value="all"),
                    rx.el.option("Pending", value="pending"),
                    rx.el.option("Approved", value="approved"),
                    rx.el.option("Denied", value="denied"),
                    on_change=RefundsState.filter_approval,
                    class_name="pl-3 pr-8 py-2 border border-gray-200 rounded-xl appearance-none bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500",
                ),
                rx.icon(
                    "filter",
                    class_name="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none",
                ),
                class_name="relative",
            ),
            rx.el.div(
                rx.el.input(
                    placeholder="Search ticket or payment ID...",
                    on_change=RefundsState.search_refunds.debounce(300),
                    class_name="w-full pl-10 pr-4 py-2 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent",
                ),
                rx.icon(
                    "search",
                    class_name="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400",
                ),
                class_name="relative w-64",
            ),
            class_name="flex gap-4 mb-6",
        ),
        rx.cond(
            RefundsState.loading,
            rx.el.div(rx.spinner(), class_name="flex justify-center py-12"),
            rx.cond(
                RefundsState.refunds.length() > 0,
                rx.el.div(
                    rx.el.table(
                        rx.el.thead(
                            rx.el.tr(
                                th(
                                    "Date",
                                    "request_date",
                                    RefundsState.sort_column,
                                    RefundsState.sort_order,
                                    RefundsState.sort_by("request_date"),
                                ),
                                th("Ticket ID", "ticket_id", "", "", None),
                                th(
                                    "SKU",
                                    "sku",
                                    RefundsState.sort_column,
                                    RefundsState.sort_order,
                                    RefundsState.sort_by("sku"),
                                ),
                                th("Status", "approved", "", "", None),
                                rx.el.th("", class_name="px-6 py-3"),
                            ),
                            class_name="bg-gray-50 border-b border-gray-100",
                        ),
                        rx.foreach(
                            RefundsState.refunds,
                            lambda r: rx.el.tbody(
                                rx.el.tr(
                                    rx.el.td(
                                        rx.el.div(
                                            rx.el.button(
                                                rx.icon(
                                                    rx.cond(
                                                        RefundsState.expanded_refund_id
                                                        == r["refund_id"],
                                                        "chevron-down",
                                                        "chevron-right",
                                                    ),
                                                    class_name="w-4 h-4 text-gray-400",
                                                ),
                                                on_click=RefundsState.toggle_row(
                                                    r["refund_id"],
                                                    r["ticket_id"],
                                                    r["payment_id"],
                                                ),
                                                class_name="mr-2 p-1 hover:bg-gray-100 rounded-md transition-colors",
                                            ),
                                            r["request_date"],
                                            class_name="flex items-center",
                                        ),
                                        class_name="px-6 py-4 text-sm text-gray-900",
                                    ),
                                    rx.el.td(
                                        rx.el.a(
                                            r["ticket_id"],
                                            href=f"/tickets?search={r['ticket_id']}",
                                            class_name="text-indigo-600 hover:text-indigo-900 hover:underline font-mono",
                                        ),
                                        class_name="px-6 py-4 text-sm",
                                    ),
                                    rx.el.td(
                                        r["sku"],
                                        class_name="px-6 py-4 text-sm text-gray-500",
                                    ),
                                    rx.el.td(
                                        rx.cond(
                                            r["approved"] == None,
                                            rx.el.span(
                                                "Pending",
                                                class_name="px-2 py-1 bg-yellow-100 text-yellow-700 text-xs rounded-full font-medium",
                                            ),
                                            rx.cond(
                                                r["approved"],
                                                rx.el.span(
                                                    "Approved",
                                                    class_name="px-2 py-1 bg-green-100 text-green-700 text-xs rounded-full font-medium",
                                                ),
                                                rx.el.span(
                                                    "Denied",
                                                    class_name="px-2 py-1 bg-red-100 text-red-700 text-xs rounded-full font-medium",
                                                ),
                                            ),
                                        ),
                                        class_name="px-6 py-4",
                                    ),
                                    rx.el.td(
                                        rx.el.div(
                                            rx.el.button(
                                                rx.icon("pencil", class_name="w-4 h-4"),
                                                on_click=RefundsState.open_edit_modal(
                                                    r
                                                ),
                                                class_name="p-2 text-gray-400 hover:text-indigo-600 hover:bg-indigo-50 rounded-lg",
                                            ),
                                            rx.el.button(
                                                rx.icon(
                                                    "trash-2", class_name="w-4 h-4"
                                                ),
                                                on_click=RefundsState.prompt_delete(
                                                    r["refund_id"]
                                                ),
                                                class_name="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg",
                                            ),
                                            class_name="flex items-center justify-end gap-2",
                                        ),
                                        class_name="px-6 py-4",
                                    ),
                                    class_name=rx.cond(
                                        RefundsState.expanded_refund_id
                                        == r["refund_id"],
                                        "bg-indigo-50/50 border-b border-gray-100",
                                        "hover:bg-gray-50 transition-colors border-b border-gray-100 last:border-0",
                                    ),
                                ),
                                rx.cond(
                                    RefundsState.expanded_refund_id == r["refund_id"],
                                    rx.el.tr(
                                        rx.el.td(
                                            rx.el.div(
                                                rx.cond(
                                                    RefundsState.loading_related,
                                                    rx.el.div(
                                                        rx.spinner(size="1"),
                                                        class_name="py-4 flex justify-center",
                                                    ),
                                                    rx.el.div(
                                                        rx.el.div(
                                                            rx.el.h4(
                                                                "Related Ticket",
                                                                class_name="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2",
                                                            ),
                                                            rx.el.div(
                                                                rx.el.div(
                                                                    rx.el.span(
                                                                        "Subject:",
                                                                        class_name="text-sm text-gray-500 w-20",
                                                                    ),
                                                                    rx.el.span(
                                                                        RefundsState.related_ticket[
                                                                            "subject"
                                                                        ],
                                                                        class_name="text-sm font-medium text-gray-900",
                                                                    ),
                                                                    class_name="flex mb-1",
                                                                ),
                                                                rx.el.div(
                                                                    rx.el.span(
                                                                        "Customer:",
                                                                        class_name="text-sm text-gray-500 w-20",
                                                                    ),
                                                                    rx.el.span(
                                                                        RefundsState.related_ticket[
                                                                            "customer_id"
                                                                        ],
                                                                        class_name="text-sm font-mono text-gray-700",
                                                                    ),
                                                                    class_name="flex mb-1",
                                                                ),
                                                                rx.el.div(
                                                                    rx.el.span(
                                                                        "Status:",
                                                                        class_name="text-sm text-gray-500 w-20",
                                                                    ),
                                                                    rx.el.span(
                                                                        RefundsState.related_ticket[
                                                                            "status"
                                                                        ],
                                                                        class_name="text-sm capitalize text-gray-900",
                                                                    ),
                                                                    class_name="flex",
                                                                ),
                                                                class_name="bg-white p-3 rounded-lg border border-gray-200",
                                                            ),
                                                            class_name="flex-1",
                                                        ),
                                                        rx.el.div(
                                                            rx.el.h4(
                                                                "Related Payment",
                                                                class_name="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2",
                                                            ),
                                                            rx.el.div(
                                                                rx.el.div(
                                                                    rx.el.span(
                                                                        "Amount:",
                                                                        class_name="text-sm text-gray-500 w-20",
                                                                    ),
                                                                    rx.el.span(
                                                                        f"${RefundsState.related_payment['amount']}",
                                                                        class_name="text-sm font-medium text-gray-900",
                                                                    ),
                                                                    class_name="flex mb-1",
                                                                ),
                                                                rx.el.div(
                                                                    rx.el.span(
                                                                        "Status:",
                                                                        class_name="text-sm text-gray-500 w-20",
                                                                    ),
                                                                    rx.el.span(
                                                                        RefundsState.related_payment[
                                                                            "status"
                                                                        ],
                                                                        class_name="text-sm capitalize text-gray-900",
                                                                    ),
                                                                    class_name="flex mb-1",
                                                                ),
                                                                rx.el.div(
                                                                    rx.el.span(
                                                                        "ID:",
                                                                        class_name="text-sm text-gray-500 w-20",
                                                                    ),
                                                                    rx.el.a(
                                                                        r["payment_id"],
                                                                        href=f"/payments?search={r['payment_id']}",
                                                                        class_name="text-sm text-indigo-600 hover:underline font-mono truncate",
                                                                    ),
                                                                    class_name="flex",
                                                                ),
                                                                class_name="bg-white p-3 rounded-lg border border-gray-200",
                                                            ),
                                                            class_name="flex-1",
                                                        ),
                                                        class_name="grid grid-cols-1 md:grid-cols-2 gap-4",
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
                        RefundsState.page,
                        RefundsState.total_pages,
                        RefundsState.prev_page,
                        RefundsState.next_page,
                        RefundsState.total_count,
                        RefundsState.page_size,
                    ),
                    class_name="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden",
                ),
                empty_state(
                    "history",
                    "No refund requests",
                    "There are no refund requests matching your criteria.",
                ),
            ),
        ),
        refund_modal(),
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
                        "Are you sure you want to delete this refund request?",
                        class_name="text-gray-500 mb-6",
                    ),
                    rx.el.div(
                        rx.el.button(
                            "Cancel",
                            on_click=RefundsState.cancel_delete,
                            class_name="px-4 py-2 text-gray-700 font-medium hover:bg-gray-100 rounded-lg",
                        ),
                        rx.el.button(
                            "Delete",
                            on_click=RefundsState.confirm_delete,
                            class_name="px-4 py-2 bg-red-600 text-white font-medium hover:bg-red-700 rounded-lg",
                        ),
                        class_name="flex justify-end gap-3",
                    ),
                    class_name="fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 bg-white rounded-xl shadow-xl p-6 w-full max-w-sm z-50",
                ),
            ),
            open=RefundsState.delete_id != "",
        ),
        class_name="flex-1 md:ml-72 p-8 bg-gray-50/50 min-h-screen",
    )