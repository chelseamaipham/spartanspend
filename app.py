"""
SpartanSpend - a simple expense tracker for college students.
CMPE 165 Project 1

Run with:  streamlit run app.py
"""

import sqlite3
from datetime import date

import pandas as pd
import streamlit as st

DB_PATH = "spartanspend.db"
CATEGORIES = ["Food", "Rent", "Transportation", "School", "Entertainment", "Other"]


# ------------------------------------------------------------------ database
def get_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.execute(
        """CREATE TABLE IF NOT EXISTS expenses (
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               date TEXT NOT NULL,
               description TEXT NOT NULL,
               category TEXT NOT NULL,
               amount REAL NOT NULL
           )"""
    )
    conn.execute(
        """CREATE TABLE IF NOT EXISTS settings (
               key TEXT PRIMARY KEY,
               value REAL NOT NULL
           )"""
    )
    conn.commit()
    return conn


def add_expense(conn, expense_date, description, category, amount):
    conn.execute(
        "INSERT INTO expenses (date, description, category, amount) VALUES (?, ?, ?, ?)",
        (expense_date.isoformat(), description.strip(), category, float(amount)),
    )
    conn.commit()


def delete_expense(conn, expense_id):
    conn.execute("DELETE FROM expenses WHERE id = ?", (int(expense_id),))
    conn.commit()


def load_expenses(conn):
    df = pd.read_sql_query(
        "SELECT id, date, description, category, amount FROM expenses "
        "ORDER BY date DESC, id DESC",
        conn,
    )
    df["date"] = pd.to_datetime(df["date"])
    return df


def get_budget(conn):
    row = conn.execute("SELECT value FROM settings WHERE key = 'monthly_budget'").fetchone()
    return row[0] if row else 0.0


def set_budget(conn, value):
    conn.execute(
        "INSERT INTO settings (key, value) VALUES ('monthly_budget', ?) "
        "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
        (float(value),),
    )
    conn.commit()


# ------------------------------------------------------------------ app
st.set_page_config(page_title="SpartanSpend", page_icon="💸")
conn = get_connection()

st.title("SpartanSpend")
st.caption("Track your spending, set a monthly budget, and see where your money goes.")

page = st.sidebar.radio("Go to", ["Add Expense", "Expense List", "Dashboard"])

# ---------- Page 1: Add Expense
if page == "Add Expense":
    st.header("Add an expense")
    with st.form("add_form", clear_on_submit=True):
        expense_date = st.date_input("Date", value=date.today())
        description = st.text_input("Description", placeholder="e.g. Chipotle lunch")
        category = st.selectbox("Category", CATEGORIES)
        amount = st.number_input("Amount ($)", min_value=0.0, step=1.0, format="%.2f")
        submitted = st.form_submit_button("Add expense")

    if submitted:
        if not description.strip():
            st.error("Please enter a description.")
        elif amount <= 0:
            st.error("Amount must be greater than $0.")
        else:
            add_expense(conn, expense_date, description, category, amount)
            st.success(f"Added ${amount:,.2f} for '{description.strip()}' ({category}).")

# ---------- Page 2: Expense List
elif page == "Expense List":
    st.header("Your expenses")
    df = load_expenses(conn)

    if df.empty:
        st.info("No expenses yet. Add one on the Add Expense page.")
    else:
        selected = st.multiselect("Filter by category", CATEGORIES, default=CATEGORIES)
        shown = df[df["category"].isin(selected)]

        table = shown.copy()
        table["date"] = table["date"].dt.date
        table["amount"] = table["amount"].map(lambda x: f"${x:,.2f}")
        st.dataframe(table.drop(columns=["id"]), hide_index=True)
        st.write(f"{len(shown)} expenses, total ${shown['amount'].sum():,.2f}")

        st.subheader("Delete an expense")
        labels = {
            row.id: f"{row.date.date()} - {row.description} (${row.amount:,.2f})"
            for row in df.itertuples()
        }
        to_delete = st.selectbox("Choose an expense", list(labels.keys()),
                                 format_func=lambda i: labels[i])
        if st.button("Delete"):
            delete_expense(conn, to_delete)
            st.success("Expense deleted.")
            st.rerun()

# ---------- Page 3: Dashboard
elif page == "Dashboard":
    st.header("This month / day")

    # Budget input (keeps existing behavior)
    budget = st.number_input("Monthly budget ($)", min_value=0.0, step=50.0,
                             value=float(get_budget(conn)), format="%.2f")
    if budget != get_budget(conn):
        set_budget(conn, budget)

    # Let the user choose whether to view by month or by a specific day
    view_mode = st.radio("View by", ["Month", "Day"], index=0)

    df = load_expenses(conn)

    if view_mode == "Month":
        # Month picker: choose any date and interpret its year+month
        today = date.today()
        default_month = date(today.year, today.month, 1)
        view_date = st.date_input("View month (pick any day in the month)", value=default_month)
        st.write(f"Showing: {view_date.strftime('%B %Y')}")

        # Filter for the selected month
        month = df[(df["date"].dt.year == view_date.year) & (df["date"].dt.month == view_date.month)]

        if month.empty:
            st.info("No expenses for that month yet. Add one on the Add Expense page.")
        else:
            total = month["amount"].sum()
            col1, col2 = st.columns(2)
            col1.metric("Spent this month", f"${total:,.2f}")
            if budget > 0:
                remaining = budget - total
                col2.metric("Budget remaining",
                            f"${remaining:,.2f}" if remaining >= 0 else f"-${-remaining:,.2f}")
                if total > budget:
                    st.error(f"You are over your monthly budget by ${total - budget:,.2f}.")
                elif total >= 0.8 * budget:
                    st.warning(f"You have used {total / budget:.0%} of your monthly budget.")
            else:
                col2.metric("Budget remaining", "No budget set")

            st.subheader("Spending by category")
            by_category = month.groupby("category")["amount"].sum().sort_values(ascending=False)
            st.bar_chart(by_category)

    else:  # Day view
        # Day picker: choose a specific day
        chosen_day = st.date_input("Pick a day", value=date.today())
        st.write(f"Showing: {chosen_day.strftime('%B %d, %Y')}")

        day_df = df[df["date"].dt.date == chosen_day]

        if day_df.empty:
            st.info("No expenses for that day. Add one on the Add Expense page.")
        else:
            total_day = day_df["amount"].sum()
            st.metric("Spent that day", f"${total_day:,.2f}")

            # Show table of that day's expenses
            table = day_df.copy()
            table["date"] = table["date"].dt.date
            table["amount"] = table["amount"].map(lambda x: f"${x:,.2f}")
            st.dataframe(table.drop(columns=["id"]), hide_index=True)

            # Category breakdown for the day
            st.subheader("Spending by category (day)")
            by_cat_day = day_df.groupby("category")["amount"].sum().sort_values(ascending=False)
            st.bar_chart(by_cat_day)