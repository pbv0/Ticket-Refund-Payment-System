import reflex as rx
from app.states.chat_state import ChatState


def message_bubble(message: dict) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.markdown(
                    message["content"],
                    class_name=rx.cond(
                        message["role"] == "user",
                        "prose prose-sm prose-invert max-w-none text-white",
                        "prose prose-sm prose-slate max-w-none text-gray-800",
                    ),
                ),
                class_name=rx.cond(
                    message["role"] == "user",
                    "bg-indigo-600 rounded-2xl rounded-tr-none px-4 py-3 shadow-sm",
                    "bg-white border border-gray-200 rounded-2xl rounded-tl-none px-4 py-3 shadow-sm",
                ),
            ),
            class_name=rx.cond(
                message["role"] == "user",
                "flex justify-end ml-16",
                "flex justify-start mr-16",
            ),
        ),
        class_name="mb-6",
    )


def chat_view() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.el.h1(
                        "AI Assistant", class_name="text-2xl font-bold text-gray-900"
                    ),
                    rx.el.p(
                        "Ask questions about your business data",
                        class_name="text-sm text-gray-500",
                    ),
                ),
                rx.el.div(
                    rx.el.div(
                        rx.el.select(
                            rx.el.option("All Data", value="all"),
                            rx.el.option("Help Tickets", value="tickets"),
                            rx.el.option("Refund Requests", value="refunds"),
                            rx.el.option("Payments", value="payments"),
                            value=ChatState.context_selector,
                            on_change=ChatState.set_context,
                            class_name="text-sm border-gray-200 rounded-xl shadow-sm focus:border-indigo-500 focus:ring-indigo-500 bg-white py-2 pl-3 pr-10 border appearance-none",
                        ),
                        rx.icon(
                            "chevron-down",
                            class_name="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none",
                        ),
                        class_name="relative",
                    ),
                    rx.el.button(
                        rx.icon("trash-2", class_name="w-4 h-4 mr-2"),
                        "Clear Chat",
                        on_click=ChatState.clear_chat,
                        class_name="flex items-center text-sm text-gray-500 hover:text-red-600 px-4 py-2 hover:bg-red-50 rounded-xl transition-colors border border-gray-200",
                    ),
                    class_name="flex gap-3 items-center",
                ),
                class_name="flex justify-between items-end mb-8 px-4 md:px-0",
            ),
            rx.el.div(
                rx.scroll_area(
                    rx.el.div(
                        rx.foreach(ChatState.messages, message_bubble),
                        rx.cond(
                            ChatState.loading,
                            rx.el.div(
                                rx.el.div(
                                    rx.el.div(
                                        class_name="w-2 h-2 bg-indigo-400 rounded-full animate-bounce"
                                    ),
                                    rx.el.div(
                                        class_name="w-2 h-2 bg-indigo-400 rounded-full animate-bounce delay-75"
                                    ),
                                    rx.el.div(
                                        class_name="w-2 h-2 bg-indigo-400 rounded-full animate-bounce delay-150"
                                    ),
                                    class_name="flex gap-1.5 items-center bg-white border border-gray-100 rounded-2xl rounded-tl-none px-5 py-4 w-fit shadow-sm",
                                ),
                                class_name="flex justify-start mr-16 mb-6",
                            ),
                        ),
                        class_name="flex flex-col p-6",
                    ),
                    type="always",
                    scrollbars="vertical",
                    class_name="h-[calc(100vh-22rem)] min-h-[400px]",
                ),
                rx.el.div(
                    rx.el.form(
                        rx.el.div(
                            rx.el.input(
                                name="message_input",
                                placeholder="How many open tickets do we have this week?",
                                class_name="flex-1 border-0 bg-transparent py-4 px-6 focus:ring-0 placeholder:text-gray-400 text-sm outline-none",
                            ),
                            rx.el.button(
                                rx.icon("send", class_name="h-4 w-4"),
                                type="submit",
                                disabled=ChatState.loading,
                                class_name="rounded-xl bg-indigo-600 px-4 py-2 text-white hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed m-2 transition-all flex items-center justify-center shadow-sm",
                            ),
                            class_name="flex items-center rounded-2xl bg-white border border-gray-200 shadow-sm focus-within:border-indigo-500 focus-within:ring-1 focus-within:ring-indigo-500 transition-all",
                        ),
                        on_submit=ChatState.send_message,
                        reset_on_submit=True,
                        class_name="w-full",
                    ),
                    class_name="p-6 bg-white border-t border-gray-100 rounded-b-3xl",
                ),
                class_name="flex flex-col flex-1 bg-gray-50/80 rounded-3xl border border-gray-200 shadow-sm overflow-hidden",
            ),
            class_name="max-w-4xl mx-auto w-full flex flex-col h-full",
        ),
        class_name="flex-1 md:ml-72 p-4 md:p-8 h-screen bg-white",
    )