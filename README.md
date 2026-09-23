# spartanspend
## SpartanSpend

A simple expense tracker for college students. CMPE 165 Project 1: Software Product from Idea to Execution.

## Team Members
- Chelsea Pham
- Arielah Arana

## Project Description
Many college students run out of money before the end of the month because they don't track where it goes. SpartanSpend is a simple web app where a student records expenses, sees them by category, and gets a warning when they go over their monthly budget.

## Major Features
1. **Add an expense:** date, description, category, and amount. Empty descriptions and amounts of $0 or less are rejected.
2. **Expense list:** view all expenses, filter by category, see the total, and delete an expense.
3. **Dashboard:** total spent this month, budget remaining, a bar chart of spending by category, and a warning when you are over (or close to) your monthly budget. The budget is saved in the database.

## Required Packages
- Python 3.9 or newer
- streamlit
- pandas

SQLite is built into Python, so it does not need to be installed.

## How to Run
git clone https://github.com/chelseamaipham/spartanspend.git
cd spartanspend
pip install -r requirements.txt
python load_sample.py
streamlit run app.py
The app opens in your browser at http://localhost:8501.

`python load_sample.py` is optional. It loads sample data so the app is not empty.

## Sample Data
`sample_expenses.csv` contains 30 realistic student expenses (rent, groceries, gas, textbooks, etc.). `load_sample.py` loads them into the database with dates in the current month so they appear on the dashboard. The database file (`spartanspend.db`) is created automatically and is not committed to GitHub.

## AI-Assisted Development

**AI tools used:** Claude

**What AI helped build:**
- The Streamlit app: the Add Expense, Expense List, and Dashboard pages, and the SQLite database functions
- The sample data (`sample_expenses.csv`) and the script that loads it (`load_sample.py`)
- This README
- Outside the code, AI also helped draft sections of our written report, ran the project calculations (weighted scoring, NPV, decision tree, and a 10,000-trial Monte Carlo simulation), and created the charts and presentation slides. The financial numbers are estimates for our fictional company, SpartanSpend Labs, and the report explains the assumptions behind each one.

**Where AI-generated code did not work correctly:** The first dashboard version formatted negative remaining budget incorrectly (displayed "$-693.90" instead of "-$693.90"); this was fixed manually.

**A decision the human team made, not the AI:**  After some setbacks, we chose an expense tracker because it was the simplest of the suggested project ideas, so we could finish a working version on time. We also decided to keep the scope small (no bank syncing, logins, or per-category budgets) and to focus on features that work reliably. We reviewed and tested the app ourselves, and the reflection in our report is written from our own experience.
