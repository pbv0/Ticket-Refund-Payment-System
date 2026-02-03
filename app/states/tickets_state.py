import reflex as rx
from typing import TypedDict, Optional
from app.db import fetch_all, fetch_one, execute
import uuid
import datetime
import logging


class Ticket(TypedDict):
    ticket_id: str
    customer_id: str
    subject: str
    status: str
    created_at: str
    resolved_at: Optional[str]


class TicketsState(rx.State):
    tickets: list[Ticket] = []
    loading: bool = False
    search_query: str = ""
    sort_column: str = "created_at"
    sort_order: str = "desc"
    status_filter: str = "all"
    is_open: bool = False
    is_edit_mode: bool = False
    current_ticket: dict = {}
    delete_id: str = ""
    expanded_ticket_id: str = ""
    related_refunds: list[dict] = []
    loading_related: bool = False
    has_checked_query_params: bool = False
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
    async def fetch_tickets(self):
        async with self:
            self.loading = True
            if not self.has_checked_query_params:
                param_search = self.router.url.query_parameters.get("search")
                if param_search:
                    self.search_query = param_search
                is_new = self.router.url.query_parameters.get("new") == "true"
                if is_new:
                    self.is_edit_mode = False
                    self.current_ticket = {"status": "open"}
                    self.is_open = True
                self.has_checked_query_params = True
        try:
            base_query = """
                FROM help_ticket
                WHERE 1=1
            """
            params = {}
            if self.status_filter != "all":
                base_query += " AND status = %(status)s"
                params["status"] = self.status_filter
            if self.search_query:
                base_query += " AND (customer_id ILIKE %(search)s OR subject ILIKE %(search)s OR ticket_id ILIKE %(search)s)"
                params["search"] = f"%{self.search_query}%"
            count_result = await fetch_one(f"SELECT COUNT(*) {base_query}", params)
            total = count_result[0] if count_result else 0
            sort_map = {
                "ticket_id": "ticket_id",
                "created_at": "created_at",
                "status": "status",
                "customer_id": "customer_id",
                "subject": "subject",
            }
            sort_col = sort_map.get(self.sort_column, "created_at")
            order = "DESC" if self.sort_order == "desc" else "ASC"
            offset = (self.page - 1) * self.page_size
            query_str = f"SELECT ticket_id, customer_id, subject, status, created_at, resolved_at {base_query} ORDER BY {sort_col} {order} LIMIT {self.page_size} OFFSET {offset}"
            rows = await fetch_all(query_str, params)
            formatted_tickets = []
            for row in rows:
                formatted_tickets.append(
                    {
                        "ticket_id": row[0],
                        "customer_id": row[1] or "",
                        "subject": row[2] or "",
                        "status": row[3] or "",
                        "created_at": row[4].strftime("%Y-%m-%d %H:%M")
                        if row[4]
                        else "",
                        "resolved_at": row[5].strftime("%Y-%m-%d %H:%M")
                        if row[5]
                        else None,
                    }
                )
            async with self:
                self.tickets = formatted_tickets
                self.total_count = total
                self.loading = False
        except Exception as e:
            logging.exception(f"Error fetching tickets: {e}")
            async with self:
                self.loading = False

    @rx.event
    def next_page(self):
        if self.has_next:
            self.page += 1
            return TicketsState.fetch_tickets

    @rx.event
    def prev_page(self):
        if self.has_prev:
            self.page -= 1
            return TicketsState.fetch_tickets

    @rx.event
    def set_page(self, page_num: int):
        self.page = page_num
        return TicketsState.fetch_tickets

    @rx.event(background=True)
    async def toggle_row(self, ticket_id: str):
        async with self:
            if self.expanded_ticket_id == ticket_id:
                self.expanded_ticket_id = ""
                self.related_refunds = []
                return
            else:
                self.expanded_ticket_id = ticket_id
                self.loading_related = True
        try:
            query = """
                SELECT refund_id, amount_cents, approved, request_date
                FROM refund_requests 
                LEFT JOIN stripe_payments ON refund_requests.payment_id = stripe_payments.payment_id
                WHERE ticket_id = %(tid)s
                ORDER BY request_date DESC
            """
            rows = await fetch_all(query, {"tid": ticket_id})
            refunds = []
            for row in rows:
                refunds.append(
                    {
                        "refund_id": row[0],
                        "amount": row[1] / 100.0 if row[1] else 0.0,
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
    def sort_by(self, column: str):
        if self.sort_column == column:
            self.sort_order = "asc" if self.sort_order == "desc" else "desc"
        else:
            self.sort_column = column
            self.sort_order = "asc"
        return TicketsState.fetch_tickets

    @rx.event
    def filter_status(self, status: str):
        self.status_filter = status
        self.page = 1
        return TicketsState.fetch_tickets

    @rx.event
    def search_tickets(self, query: str):
        self.search_query = query
        self.page = 1
        return TicketsState.fetch_tickets

    @rx.event
    def open_create_modal(self):
        self.is_edit_mode = False
        self.current_ticket = {"status": "open"}
        self.is_open = True

    @rx.event
    def open_edit_modal(self, ticket: Ticket):
        self.is_edit_mode = True
        self.current_ticket = ticket
        self.is_open = True

    @rx.event
    def close_modal(self):
        self.is_open = False

    @rx.event(background=True)
    async def save_ticket(self, form_data: dict):
        try:
            customer_id = form_data.get("customer_id")
            subject = form_data.get("subject")
            status = form_data.get("status")
            if self.is_edit_mode:
                ticket_id = form_data.get("ticket_id")
                resolved_at_clause = ""
                if status in ["resolved", "closed"]:
                    resolved_at_clause = ", resolved_at = NOW()"
                await execute(
                    f"UPDATE help_ticket SET customer_id = %(cid)s, subject = %(subj)s, status = %(stat)s {resolved_at_clause} WHERE ticket_id = %(tid)s",
                    {
                        "cid": customer_id,
                        "subj": subject,
                        "stat": status,
                        "tid": ticket_id,
                    },
                )
                msg = "Ticket updated successfully"
            else:
                new_id = str(uuid.uuid4())
                await execute(
                    "INSERT INTO help_ticket (ticket_id, customer_id, subject, status, created_at) VALUES (%(tid)s, %(cid)s, %(subj)s, %(stat)s, NOW())",
                    {
                        "tid": new_id,
                        "cid": customer_id,
                        "subj": subject,
                        "stat": status,
                    },
                )
                msg = "Ticket created successfully"
            async with self:
                self.is_open = False
                yield rx.toast(msg)
                yield TicketsState.fetch_tickets
        except Exception as e:
            logging.exception(f"Error saving ticket: {e}")
            async with self:
                yield rx.toast(f"Error: {str(e)}")

    @rx.event
    def prompt_delete(self, ticket_id: str):
        self.delete_id = ticket_id

    @rx.event
    def cancel_delete(self):
        self.delete_id = ""

    @rx.event(background=True)
    async def confirm_delete(self):
        if not self.delete_id:
            return
        try:
            await execute(
                "DELETE FROM help_ticket WHERE ticket_id = %(tid)s",
                {"tid": self.delete_id},
            )
            async with self:
                self.delete_id = ""
                yield rx.toast("Ticket deleted")
                yield TicketsState.fetch_tickets
        except Exception as e:
            logging.exception(f"Error deleting ticket: {e}")
            async with self:
                yield rx.toast(f"Error deleting: {str(e)}")