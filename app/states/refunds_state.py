import reflex as rx
from typing import TypedDict, Optional
from app.db import fetch_all, fetch_one, execute
import uuid
import logging


class Refund(TypedDict):
    refund_id: str
    ticket_id: str
    payment_id: str
    sku: str
    request_date: str
    approved: bool
    approval_date: Optional[str]


class RefundsState(rx.State):
    refunds: list[Refund] = []
    loading: bool = False
    sort_column: str = "request_date"
    sort_order: str = "desc"
    approval_filter: str = "all"
    search_query: str = ""
    is_open: bool = False
    is_edit_mode: bool = False
    current_refund: dict = {}
    delete_id: str = ""
    expanded_refund_id: str = ""
    related_ticket: dict = {}
    related_payment: dict = {}
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
    async def fetch_refunds(self):
        async with self:
            self.loading = True
            if not self.search_query:
                param_search = self.router.url.query_parameters.get("search")
                if param_search:
                    self.search_query = param_search
        try:
            base_query = """
                FROM refund_requests
                WHERE 1=1
            """
            params = {}
            if self.approval_filter == "approved":
                base_query += " AND approved = TRUE"
            elif self.approval_filter == "denied":
                base_query += " AND approved = FALSE"
            elif self.approval_filter == "pending":
                base_query += " AND approved IS NULL"
            if self.search_query:
                base_query += " AND (ticket_id ILIKE %(search)s OR payment_id ILIKE %(search)s OR refund_id ILIKE %(search)s)"
                params["search"] = f"%{self.search_query}%"
            count_result = await fetch_one(f"SELECT COUNT(*) {base_query}", params)
            total = count_result[0] if count_result else 0
            sort_map = {
                "request_date": "request_date",
                "approval_date": "approval_date",
                "sku": "sku",
            }
            sort_col = sort_map.get(self.sort_column, "request_date")
            order = "DESC" if self.sort_order == "desc" else "ASC"
            offset = (self.page - 1) * self.page_size
            query_str = f"SELECT refund_id, ticket_id, payment_id, sku, request_date, approved, approval_date {base_query} ORDER BY {sort_col} {order} LIMIT {self.page_size} OFFSET {offset}"
            rows = await fetch_all(query_str, params)
            formatted = []
            for row in rows:
                formatted.append(
                    {
                        "refund_id": row[0],
                        "ticket_id": row[1] or "",
                        "payment_id": row[2] or "",
                        "sku": row[3] or "",
                        "request_date": row[4].strftime("%Y-%m-%d") if row[4] else "",
                        "approved": row[5],
                        "approval_date": row[6].strftime("%Y-%m-%d")
                        if row[6]
                        else None,
                    }
                )
            async with self:
                self.refunds = formatted
                self.total_count = total
                self.loading = False
        except Exception as e:
            logging.exception(f"Error fetching refunds: {e}")
            async with self:
                self.loading = False

    @rx.event
    def next_page(self):
        if self.has_next:
            self.page += 1
            return RefundsState.fetch_refunds

    @rx.event
    def prev_page(self):
        if self.has_prev:
            self.page -= 1
            return RefundsState.fetch_refunds

    @rx.event
    def set_page(self, page_num: int):
        self.page = page_num
        return RefundsState.fetch_refunds

    @rx.event(background=True)
    async def toggle_row(self, refund_id: str, ticket_id: str, payment_id: str):
        async with self:
            if self.expanded_refund_id == refund_id:
                self.expanded_refund_id = ""
                self.related_ticket = {}
                self.related_payment = {}
                return
            else:
                self.expanded_refund_id = refund_id
                self.loading_related = True
        try:
            t_row = await fetch_one(
                "SELECT subject, status, customer_id FROM help_ticket WHERE ticket_id = %(tid)s",
                {"tid": ticket_id},
            )
            ticket_data = {}
            if t_row:
                ticket_data = {
                    "subject": t_row[0],
                    "status": t_row[1],
                    "customer_id": t_row[2],
                }
            p_row = await fetch_one(
                "SELECT amount_cents, currency, payment_status, payment_date FROM stripe_payments WHERE payment_id = %(pid)s",
                {"pid": payment_id},
            )
            payment_data = {}
            if p_row:
                payment_data = {
                    "amount": p_row[0] / 100.0 if p_row[0] else 0.0,
                    "currency": p_row[1],
                    "status": p_row[2],
                    "date": p_row[3].strftime("%Y-%m-%d") if p_row[3] else "",
                }
            async with self:
                self.related_ticket = ticket_data
                self.related_payment = payment_data
                self.loading_related = False
        except Exception as e:
            logging.exception(f"Error fetching related data: {e}")
            async with self:
                self.loading_related = False

    @rx.event
    def search_refunds(self, query: str):
        self.search_query = query
        self.page = 1
        return RefundsState.fetch_refunds

    @rx.event
    def sort_by(self, column: str):
        if self.sort_column == column:
            self.sort_order = "asc" if self.sort_order == "desc" else "desc"
        else:
            self.sort_column = column
            self.sort_order = "asc"
        return RefundsState.fetch_refunds

    @rx.event
    def filter_approval(self, status: str):
        self.approval_filter = status
        self.page = 1
        return RefundsState.fetch_refunds

    @rx.event
    def open_create_modal(self):
        self.is_edit_mode = False
        self.current_refund = {}
        self.is_open = True

    @rx.event
    def open_edit_modal(self, refund: Refund):
        self.is_edit_mode = True
        self.current_refund = refund
        self.is_open = True

    @rx.event
    def close_modal(self):
        self.is_open = False

    @rx.event(background=True)
    async def save_refund(self, form_data: dict):
        try:
            ticket_id = form_data.get("ticket_id")
            payment_id = form_data.get("payment_id")
            sku = form_data.get("sku")
            approval_status = form_data.get("approval_status")
            approved = None
            approval_date_clause = ""
            if approval_status == "true":
                approved = True
                approval_date_clause = ", approval_date = NOW()"
            elif approval_status == "false":
                approved = False
                approval_date_clause = ", approval_date = NOW()"
            else:
                approved = None
                approval_date_clause = ", approval_date = NULL"
            if self.is_edit_mode:
                refund_id = form_data.get("refund_id")
                await execute(
                    f"UPDATE refund_requests SET ticket_id=%(tid)s, payment_id=%(pid)s, sku=%(sku)s, approved=%(app)s {approval_date_clause} WHERE refund_id=%(rid)s",
                    {
                        "tid": ticket_id,
                        "pid": payment_id,
                        "sku": sku,
                        "app": approved,
                        "rid": refund_id,
                    },
                )
                msg = "Refund updated"
            else:
                new_id = str(uuid.uuid4())
                app_date_val = "NOW()" if approved is not None else "NULL"
                await execute(
                    f"INSERT INTO refund_requests (refund_id, ticket_id, payment_id, sku, request_date, approved, approval_date) VALUES (%(rid)s, %(tid)s, %(pid)s, %(sku)s, NOW(), %(app)s, {app_date_val})",
                    {
                        "rid": new_id,
                        "tid": ticket_id,
                        "pid": payment_id,
                        "sku": sku,
                        "app": approved,
                    },
                )
                msg = "Refund request created"
            async with self:
                self.is_open = False
                yield rx.toast(msg)
                yield RefundsState.fetch_refunds
        except Exception as e:
            logging.exception(f"Error saving refund: {e}")
            async with self:
                yield rx.toast(f"Error: {str(e)}")

    @rx.event
    def prompt_delete(self, rid: str):
        self.delete_id = rid

    @rx.event
    def cancel_delete(self):
        self.delete_id = ""

    @rx.event(background=True)
    async def confirm_delete(self):
        if not self.delete_id:
            return
        try:
            await execute(
                "DELETE FROM refund_requests WHERE refund_id = %(rid)s",
                {"rid": self.delete_id},
            )
            async with self:
                self.delete_id = ""
                yield rx.toast("Refund deleted")
                yield RefundsState.fetch_refunds
        except Exception as e:
            logging.exception(f"Error deleting refund: {e}")
            async with self:
                yield rx.toast(f"Error: {str(e)}")