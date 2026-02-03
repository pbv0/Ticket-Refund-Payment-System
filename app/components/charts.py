import reflex as rx
from app.states.dashboard_state import DashboardState

TOOLTIP_PROPS = {
    "content_style": {
        "backgroundColor": "white",
        "borderRadius": "8px",
        "border": "1px solid #e5e7eb",
        "boxShadow": "0 4px 6px -1px rgb(0 0 0 / 0.1)",
        "padding": "8px 12px",
    },
    "item_style": {"color": "#374151", "fontSize": "12px", "fontWeight": "500"},
    "separator": "",
}


def tickets_pie_chart() -> rx.Component:
    return rx.el.div(
        rx.el.h3(
            "Tickets by Status", class_name="text-lg font-bold text-gray-900 mb-4"
        ),
        rx.el.div(
            rx.recharts.pie_chart(
                rx.recharts.graphing_tooltip(**TOOLTIP_PROPS),
                rx.recharts.pie(
                    data=DashboardState.ticket_status_data,
                    data_key="value",
                    name_key="name",
                    cx="50%",
                    cy="50%",
                    inner_radius=60,
                    outer_radius=85,
                    padding_angle=2,
                    label=True,
                    stroke="#ffffff",
                    stroke_width=2,
                ),
                height=300,
                width="100%",
            ),
            class_name="w-full h-[300px] flex items-center justify-center",
        ),
        rx.el.div(
            rx.foreach(
                DashboardState.ticket_status_data,
                lambda item: rx.el.div(
                    rx.el.div(
                        class_name="w-3 h-3 rounded-full",
                        style={"background_color": item["fill"]},
                    ),
                    rx.el.span(item["name"], class_name="text-sm text-gray-600"),
                    rx.el.span(
                        item["value"],
                        class_name="text-sm font-semibold text-gray-900 ml-auto",
                    ),
                    class_name="flex items-center gap-2",
                ),
            ),
            class_name="grid grid-cols-2 gap-4 mt-4 pt-4 border-t border-gray-100",
        ),
        class_name="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 flex flex-col",
    )


def refunds_area_chart() -> rx.Component:
    return rx.el.div(
        rx.el.h3(
            "Refund Requests Over Time",
            class_name="text-lg font-bold text-gray-900 mb-4",
        ),
        rx.el.div(
            rx.recharts.area_chart(
                rx.recharts.cartesian_grid(
                    stroke_dasharray="3 3", vertical=False, stroke="#E5E7EB"
                ),
                rx.recharts.graphing_tooltip(**TOOLTIP_PROPS),
                rx.recharts.x_axis(
                    data_key="date",
                    axis_line=False,
                    tick_line=False,
                    tick={"fill": "#6B7280", "font_size": 12},
                    dy=10,
                ),
                rx.recharts.y_axis(
                    axis_line=False,
                    tick_line=False,
                    tick={"fill": "#6B7280", "font_size": 12},
                ),
                rx.recharts.area(
                    type_="monotone",
                    data_key="count",
                    stroke="#F59E0B",
                    fill="#FDE68A",
                    stroke_width=2,
                ),
                data=DashboardState.refunds_over_time,
                height=300,
                width="100%",
            ),
            class_name="w-full h-[300px]",
        ),
        class_name="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 col-span-1 lg:col-span-2",
    )


def payments_bar_chart() -> rx.Component:
    return rx.el.div(
        rx.el.h3(
            "Payment Status Distribution",
            class_name="text-lg font-bold text-gray-900 mb-4",
        ),
        rx.el.div(
            rx.recharts.bar_chart(
                rx.recharts.cartesian_grid(
                    stroke_dasharray="3 3", vertical=False, stroke="#E5E7EB"
                ),
                rx.recharts.graphing_tooltip(**TOOLTIP_PROPS),
                rx.recharts.x_axis(
                    data_key="name",
                    axis_line=False,
                    tick_line=False,
                    tick={"fill": "#6B7280", "font_size": 12},
                    dy=10,
                ),
                rx.recharts.y_axis(
                    axis_line=False,
                    tick_line=False,
                    tick={"fill": "#6B7280", "font_size": 12},
                ),
                rx.recharts.bar(
                    data_key="count", fill="#8B5CF6", radius=[4, 4, 0, 0], bar_size=40
                ),
                data=DashboardState.payment_status_data,
                height=300,
                width="100%",
            ),
            class_name="w-full h-[300px]",
        ),
        class_name="bg-white p-6 rounded-2xl shadow-sm border border-gray-100",
    )