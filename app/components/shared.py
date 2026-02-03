import reflex as rx
from typing import Callable, Any


def form_field(
    label: str,
    component: rx.Component,
    error: str | None = None,
    required: bool = False,
) -> rx.Component:
    return rx.el.div(
        rx.el.label(
            label,
            rx.cond(required, rx.el.span(" *", class_name="text-red-500")),
            class_name="block text-sm font-medium text-gray-700 mb-1",
        ),
        component,
        rx.cond(error, rx.el.p(error, class_name="mt-1 text-sm text-red-600")),
        class_name="mb-4",
    )


def empty_state(icon: str, title: str, description: str) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.icon(icon, class_name="w-12 h-12 text-gray-400"),
            class_name="w-24 h-24 bg-gray-50 rounded-full flex items-center justify-center mb-4",
        ),
        rx.el.h3(title, class_name="text-lg font-medium text-gray-900"),
        rx.el.p(
            description, class_name="text-sm text-gray-500 mt-1 max-w-sm text-center"
        ),
        class_name="flex flex-col items-center justify-center py-12 px-4 border-2 border-dashed border-gray-200 rounded-xl",
    )


def th(
    text: str,
    sort_key: str = "",
    current_sort: str = "",
    current_order: str = "asc",
    on_click: rx.event.EventType | None = None,
) -> rx.Component:
    """Sortable table header"""
    return rx.el.th(
        rx.el.div(
            text,
            rx.cond(
                sort_key != "",
                rx.el.button(
                    rx.cond(
                        current_sort == sort_key,
                        rx.icon(
                            rx.cond(current_order == "asc", "arrow-up", "arrow-down"),
                            class_name="w-4 h-4 ml-1",
                        ),
                        rx.icon(
                            "arrow-up-down", class_name="w-4 h-4 ml-1 text-gray-300"
                        ),
                    ),
                    on_click=on_click,
                    class_name="focus:outline-none",
                ),
            ),
            class_name="flex items-center space-x-1",
        ),
        class_name="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider",
    )


def status_badge(status: str, color_map: dict[str, str]) -> rx.Component:
    return rx.el.span(
        status,
        class_name=rx.match(
            status.lower(),
            *[
                (k, f"px-2 py-1 text-xs font-medium rounded-full {v}")
                for k, v in color_map.items()
            ],
            "px-2 py-1 text-xs font-medium rounded-full bg-gray-100 text-gray-800",
        ),
    )


def pagination_control(
    current_page: rx.Var[int],
    total_pages: rx.Var[int],
    prev_event: rx.event.EventType,
    next_event: rx.event.EventType,
    total_count: rx.Var[int],
    page_size: int = 10,
) -> rx.Component:
    start_idx = (current_page - 1) * page_size + 1
    end_idx = rx.cond(
        current_page * page_size > total_count, total_count, current_page * page_size
    )
    return rx.el.div(
        rx.el.div(
            rx.el.p(
                "Showing ",
                rx.el.span(start_idx.to_string(), class_name="font-semibold"),
                " to ",
                rx.el.span(end_idx.to_string(), class_name="font-semibold"),
                " of ",
                rx.el.span(total_count.to_string(), class_name="font-semibold"),
                " results",
                class_name="text-sm text-gray-700 font-medium",
            ),
            class_name="flex-1 flex items-center",
        ),
        rx.el.div(
            rx.el.button(
                rx.icon("chevron-left", class_name="w-4 h-4"),
                on_click=prev_event,
                disabled=current_page <= 1,
                class_name="p-2 border border-gray-200 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors",
            ),
            rx.el.div(
                rx.el.span(
                    "Page ",
                    current_page.to_string(),
                    " of ",
                    total_pages.to_string(),
                    class_name="text-sm font-medium text-gray-600",
                ),
                class_name="px-4 py-2 bg-gray-50 rounded-lg border border-gray-200",
            ),
            rx.el.button(
                rx.icon("chevron-right", class_name="w-4 h-4"),
                on_click=next_event,
                disabled=current_page >= total_pages,
                class_name="p-2 border border-gray-200 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors",
            ),
            class_name="flex items-center gap-2",
        ),
        class_name="flex items-center justify-between px-6 py-4 bg-white border-t border-gray-100",
    )