from sqlalchemy import create_engine, Column, Integer, String, Float, Date, ForeignKey, func, text
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.exc import IntegrityError
from datetime import datetime

#  DATABASE SETUP
engine = create_engine("sqlite:///fintrack.db", echo=False)
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()

# ---------- MODELS 
class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)

class Expense(Base):
    __tablename__ = "expenses"
    id = Column(Integer, primary_key=True)
    title = Column(String)
    amount = Column(Float)
    date = Column(Date)
    category_id = Column(Integer, ForeignKey("categories.id"))

class Budget(Base):
    __tablename__ = "budgets"
    id = Column(Integer, primary_key=True)
    month = Column(String, unique=True)
    limit = Column(Float)

Base.metadata.create_all(engine)
def get_or_create_category(name):
    cat = session.query(Category).filter_by(name=name).first()
    if cat:
        return cat
    cat = Category(name=name)
    session.add(cat)
    try:
        session.commit()
        return cat
    except IntegrityError:
        session.rollback()
        return session.query(Category).filter_by(name=name).first()
def add_expense():
    title = input("Title: ")
    amount = float(input("Amount: "))
    date = datetime.strptime(input("Date YYYY-MM-DD: "), "%Y-%m-%d")
    cname = input("Category: ")
    cat = get_or_create_category(cname)
    exp = Expense(title=title, amount=amount, date=date, category_id=cat.id)
    session.add(exp)
    session.commit()
    print("Expense Added")
def update_expense():
    id = int(input("Expense ID: "))
    exp = session.get(Expense, id)
    if not exp:
        print("Not found")
        return
    exp.title = input("New Title: ")
    exp.amount = float(input("New Amount: "))
    session.commit()
    print("Updated")
def delete_expense():
    id = int(input("Expense ID: "))
    exp = session.get(Expense, id)
    if exp:
        session.delete(exp)
        session.commit()
        print("Deleted")
    else:
        print("Not found")
def show_all():
    print("\n All Expenses")
    for e in session.query(Expense).all():
        print(e.id, e.title, e.amount, e.date, e.category_id)


def category_report():
    print("\n Category Wise Spending")
    query = text("""
        SELECT c.name, SUM(e.amount)
        FROM categories c
        JOIN expenses e ON c.id = e.category_id
        GROUP BY c.name
    """)
    with engine.connect() as conn:
        for r in conn.execute(query):
            print(r[0], ":", float(r[1]))
def set_budget():
    month = input("Month YYYY-MM: ")
    limit = float(input("Limit: "))
    b = session.query(Budget).filter_by(month=month).first()

    if b:
        b.limit = limit
        print("Budget Updated")
    else:
        session.add(Budget(month=month, limit=limit))
        print("Budget Set")
    session.commit()
def check_budget():
    month = input("Month YYYY-MM: ")
    total = session.query(func.sum(Expense.amount))\
        .filter(func.strftime("%Y-%m", Expense.date) == month)\
        .scalar() or 0
    b = session.query(Budget).filter_by(month=month).first()
    print("Spent:", total)
    if not b:
        print("No budget set")
    elif total > b.limit:
        print("⚠️ Budget Exceeded!")
    else:
        print("Within Budget")
def search_by_date():
    date = input("Date YYYY-MM-DD: ")
    query = text("SELECT title, amount FROM expenses WHERE date = :d")
    print("\nResults")
    with engine.connect() as conn:
        rows = conn.execute(query, {"d": date})
        found = False
        for r in rows:
            found = True
            print(r[0], "-", r[1])
        if not found:
            print("No records")
# ---------- MENU 
while True:
    print("\n====== FINTRACK PRO ======")
    print("1 Add Expense")
    print("2 Update Expense")
    print("3 Delete Expense")
    print("4 Show All")
    print("5 Category Report")
    print("6 Set Budget")
    print("7 Check Budget")
    print("8 Search by Date")
    print("0 Exit")
    ch = input("Choice: ")
    if ch == "1": add_expense()
    elif ch == "2": update_expense()
    elif ch == "3": delete_expense()
    elif ch == "4": show_all()
    elif ch == "5": category_report()
    elif ch == "6": set_budget()
    elif ch == "7": check_budget()
    elif ch == "8": search_by_date()
    elif ch == "0": break
    else: print("Invalid")
