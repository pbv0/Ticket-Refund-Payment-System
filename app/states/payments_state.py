import reflex as rx
from typing import TypedDict
from app.db import fetch_all, fetch_one, execute
import uuid
import logging


class Payment(TypedDict):
    payment_id: str
    customer_id: str
    amount_cents: int
    currency: str
    payment_status: str
    payment_date: str


class PaymentsState(rx.State):
    payments: list[Payment] = []
    loading: bool = False
    sort_column: str = "payment_date"
    sort_order: str = "desc"
    status_filter: str = "all"
    search_query: str = ""
    is_open: bool = False
    is_edit_mode: bool = False
    current_payment: dict = {}
    delete_id: str = ""
    expanded_payment_id: str = ""
    related_refunds: list[dict] = []
    loading_related: bool = False
    page: int = 1
    page_size: int = 10
    total_count: int = 0

    @rx.var
    def total_pages(self) -> int:
        return (self.total_count + self.page_size - 1) // self.page_size

    @rx.var
    def has_next(self) -> bool:
        return self.page < self.total_pages

    @rx.var
    def has_prev(self) -> bool:
        return self.page > 1

    @rx.event(background=True)
    async def fetch_payments(self):
        async with self:
            self.loading = True
            if not self.search_query:
                param_search = self.router.url.query_parameters.get("search")
                if param_search:
                    self.search_query = param_search
        try:
            base_query = """
                FROM stripe_payments
                WHERE 1=1
            """
            params = {}
            if self.status_filter != "all":
                base_query += " AND payment_status = %(status)s"
                params["status"] = self.status_filter
            if self.search_query:
                base_query += (
                    " AND (payment_id ILIKE %(search)s OR customer_id ILIKE %(search)s)"
                )
                params["search"] = f"%{self.search_query}%"
            count_result = await fetch_one(f"SELECT COUNT(*) {base_query}", params)
            total = count_result[0] if count_result else 0
            sort_map = {
                "payment_date": "payment_date",
                "amount_cents": "amount_cents",
                "payment_status": "payment_status",
            }
            sort_col = sort_map.get(self.sort_column, "payment_date")
            order = "DESC" if self.sort_order == "desc" else "ASC"
            offset = (self.page - 1) * self.page_size
            query_str = f"SELECT payment_id, customer_id, amount_cents, currency, payment_status, payment_date {base_query} ORDER BY {sort_col} {order} LIMIT {self.page_size} OFFSET {offset}"
            rows = await fetch_all(query_str, params)
            formatted = []
            for row in rows:
                formatted.append(
                    {
                        "payment_id": row[0],
                        "customer_id": row[1] or "",
                        "amount_cents": row[2] or 0,
                        "currency": row[3] or "USD",
                        "payment_status": row[4] or "",
                        "payment_date": row[5].strftime("%Y-%m-%d %H:%M")
                        if row[5]
                        else "",
                    }
                )
            async with self:
                self.payments = formatted
                self.total_count = total
                self.loading = False
        except Exception as e:
            logging.exception(f"Error fetching payments: {e}")
            async with self:
                self.loading = False

    @rx.event
    def next_page(self):
        if self.has_next:
            self.page += 1
            return PaymentsState.fetch_payments

    @rx.event
    def prev_page(self):
        if self.has_prev:
            self.page -= 1
            return PaymentsState.fetch_payments

    @rx.event
    def set_page(self, page_num: int):
        self.page = page_num
        return PaymentsState.fetch_payments

    @rx.event(background=True)
    async def toggle_row(self, payment_id: str):
        async with self:
            if self.expanded_payment_id == payment_id:
                self.expanded_payment_id = ""
                self.related_refunds = []
                return
            else:
                self.expanded_payment_id = payment_id
                self.loading_related = True
        try:
            query = """
                SELECT refund_id, sku, approved, request_date
                FROM refund_requests
                WHERE payment_id = %(pid)s
                ORDER BY request_date DESC
            """
            rows = await fetch_all(query, {"pid": payment_id})
            refunds = []
            for row in rows:
                refunds.append(
                    {
                        "refund_id": row[0],
                        "sku": row[1],
                        "approved": row[2],
                        "date": row[3].strftime("%Y-%m-%d") if row[3] else "",
                    }
                )
            async with self:
                self.related_refunds = refunds
                self.loading_related = False
        except Exception as e:
            logging.exception(f"Error fetching related refunds: {e}")
            async with self:
                self.loading_related = False

    @rx.event
    def search_payments(self, query: str):
        self.search_query = query
        self.page = 1
        return PaymentsState.fetch_payments

    @rx.event
    def sort_by(self, column: str):
        if self.sort_column == column:
            self.sort_order = "asc" if self.sort_order == "desc" else "desc"
        else:
            self.sort_column = column
            self.sort_order = "asc"
        return PaymentsState.fetch_payments

    @rx.event
    def filter_status(self, status: str):
        self.status_filter = status
        self.page = 1
        return PaymentsState.fetch_payments

    @rx.event
    def open_create_modal(self):
        self.is_edit_mode = False
        self.current_payment = {"currency": "USD", "payment_status": "succeeded"}
        self.is_open = True

    @rx.event
    def open_edit_modal(self, payment: Payment):
        self.is_edit_mode = True
        self.current_payment = payment
        self.is_open = True

    @rx.event
    def close_modal(self):
        self.is_open = False

    @rx.event(background=True)
    async def save_payment(self, form_data: dict):
        try:
            customer_id = form_data.get("customer_id")
            amount_cents = int(form_data.get("amount_cents", 0))
            currency = form_data.get("currency")
            status = form_data.get("payment_status")
            if self.is_edit_mode:
                payment_id = form_data.get("payment_id")
                await execute(
                    "UPDATE stripe_payments SET customer_id=%(cid)s, amount_cents=%(amt)s, currency=%(curr)s, payment_status=%(stat)s WHERE payment_id=%(pid)s",
                    {
                        "cid": customer_id,
                        "amt": amount_cents,
                        "curr": currency,
                        "stat": status,
                        "pid": payment_id,
                    },
                )
                msg = "Payment updated"
            else:
                new_id = str(uuid.uuid4())
                await execute(
                    "INSERT INTO stripe_payments (payment_id, customer_id, amount_cents, currency, payment_status, payment_date) VALUES (%(pid)s, %(cid)s, %(amt)s, %(curr)s, %(stat)s, NOW())",
                    {
                        "pid": new_id,
                        "cid": customer_id,
                        "amt": amount_cents,
                        "curr": currency,
                        "stat": status,
                    },
                )
                msg = "Payment recorded"
            async with self:
                self.is_open = False
                yield rx.toast(msg)
                yield PaymentsState.fetch_payments
        except Exception as e:
            logging.exception(f"Error saving payment: {e}")
            async with self:
                yield rx.toast(f"Error: {str(e)}")

    @rx.event
    def prompt_delete(self, pid: str):
        self.delete_id = pid

    @rx.event
    def cancel_delete(self):
        self.delete_id = ""

    @rx.event(background=True)
    async def confirm_delete(self):
        if not self.delete_id:
            return
        try:
            await execute(
                "DELETE FROM stripe_payments WHERE payment_id=%(pid)s",
                {"pid": self.delete_id},
            )
            async with self:
                self.delete_id = ""
                yield rx.toast("Payment deleted")
                yield PaymentsState.fetch_payments
        except Exception as e:
            logging.exception(f"Error deleting payment: {e}")
            async with self:
                yield rx.toast(f"Error: {str(e)}")