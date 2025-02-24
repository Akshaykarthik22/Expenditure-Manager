import sys
import mysql.connector
import calendar
from datetime import datetime
from abc import ABC, abstractmethod

# Abstraction: Creating an abstract base class
class ExpenseManagerBase(ABC):
    @abstractmethod
    def add_expense(self, amount, date, category, person, is_recurring=False, recurrence=None):
        pass

    @abstractmethod
    def view_expenses(self):
        pass

    @abstractmethod
    def delete_expense(self, expense_id):
        pass

    @abstractmethod
    def update_expense(self, expense_id):
        pass

    @abstractmethod
    def view_total_expense_by_month(self, month):
        pass

    @abstractmethod
    def reset_all_expenses(self):
        pass

# Inheritance: ExpenseManager inherits from ExpenseManagerBase
class ExpenseManager(ExpenseManagerBase):
    def __init__(self):
        # Encapsulation: Using private attributes
        self.__conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="ExpenseManager"
        )
        self.__cursor = self.__conn.cursor()

        # Ensure the table exists
        self.__cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INT AUTO_INCREMENT PRIMARY KEY,
            amount FLOAT NOT NULL,
            date DATE NOT NULL,
            category VARCHAR(50) NOT NULL,
            person VARCHAR(50) NOT NULL,
            is_recurring BOOLEAN DEFAULT FALSE,
            recurrence VARCHAR(20) DEFAULT NULL
        )
        """)
        self.__conn.commit()

    def add_expense(self, amount, date, category, person, is_recurring=False, recurrence=None):
        query = "INSERT INTO expenses (amount, date, category, person, is_recurring, recurrence) VALUES (%s, %s, %s, %s, %s, %s)"
        self.__cursor.execute(query, (amount, date, category, person, is_recurring, recurrence))
        self.__conn.commit()
        print("✅ Expense added successfully.")

    def view_expenses(self):
        self.__cursor.execute("SELECT * FROM expenses")
        expenses = self.__cursor.fetchall()

        if not expenses:
            print("⚠️ No expenses found.")
            return

        print("\n+---------------------------------------------------------------------+")
        print("| ID | Amount     | Date        | Category      | Person     | Recurrence |")
        print("+---------------------------------------------------------------------+")

        for row in expenses:
            expense_id = row[0]
            amount = row[1]
            date = row[2].strftime("%Y-%m-%d")
            category = row[3]
            person = row[4]
            recurrence_display = row[6] if row[5] else "N/A"

            print(f"| {expense_id:<2} | {amount:<10} | {date:<12} | {category:<12} | {person:<10} | {recurrence_display:<10} |")

        print("+---------------------------------------------------------------------+\n")

    def delete_expense(self, expense_id):
        self.__cursor.execute("DELETE FROM expenses WHERE id = %s", (expense_id,))
        self.__conn.commit()
        print("✅ Expense deleted successfully.")

    def update_expense(self, expense_id):
        amount = float(input("Enter new amount: "))
        date = input("Enter new date (YYYY-MM-DD): ")
        category = input("Enter new category: ")
        person = input("Enter new person's name: ")
        recurrence = input("Enter recurrence (weekly/monthly or leave empty): ")
        is_recurring = bool(recurrence)

        query = "UPDATE expenses SET amount=%s, date=%s, category=%s, person=%s, is_recurring=%s, recurrence=%s WHERE id=%s"
        self.__cursor.execute(query, (amount, date, category, person, is_recurring, recurrence, expense_id))
        self.__conn.commit()
        print("✅ Expense updated successfully.")

    def view_total_expense_by_month(self, month):
        year, month_num = map(int, month.split("-"))
        _, days_in_month = calendar.monthrange(year, month_num)
        num_weeks = len([day for day in range(1, days_in_month + 1) if datetime(year, month_num, day).weekday() == 0])
        
        self.__cursor.execute("SELECT amount, recurrence, is_recurring FROM expenses WHERE DATE_FORMAT(date, '%Y-%m') = %s", (month,))
        expenses = self.__cursor.fetchall()
        total_expense = sum(amount * num_weeks if is_recurring and recurrence == "weekly" else amount for amount, recurrence, is_recurring in expenses)
        
        print(f"📊 Total expense for {month}: {total_expense}")

    def reset_all_expenses(self):
        confirm = input("⚠️ Are you sure you want to delete all expenses? (yes/no): ").strip().lower()
        if confirm == "yes":
            self.__cursor.execute("TRUNCATE TABLE expenses")
            self.__conn.commit()
            print("✅ All expenses deleted and ID reset to 1.")
        else:
            print("Operation cancelled.")

    # Polymorphism: This method can be overridden
    def menu(self):
        while True:
            print("\n+-------------------------------------------+")
            print("|           Family Expense Manager          |")
            print("+-------------------------------------------+")
            print("| 1. Add Expense                            |")
            print("| 2. View Expenses                          |")
            print("| 3. Delete Expense                         |")
            print("| 4. View Total Expense for a Month         |")
            print("| 5. Update Expense                         |")
            print("| 6. Reset All Expenses                     |")
            print("| 7. Exit                                   |")
            print("+-------------------------------------------+")
            choice = input("Enter your choice: ")

            if choice == '1':
                amount = float(input("Enter amount: "))
                date = input("Enter date (YYYY-MM-DD): ")
                category = input("Enter category: ")
                person = input("Enter family person's name: ")
                is_recurring = input("Is this a recurring expense? (yes/no): ").strip().lower() == "yes"
                recurrence = input("Enter recurrence (e.g., monthly, weekly): ") if is_recurring else None
                self.add_expense(amount, date, category, person, is_recurring, recurrence)
            elif choice == '2':
                self.view_expenses()
            elif choice == '3':
                expense_id = int(input("Enter expense ID to delete: "))
                self.delete_expense(expense_id)
            elif choice == '4':
                month = input("Enter month to view total expense (YYYY-MM): ")
                self.view_total_expense_by_month(month)
            elif choice == '5':
                expense_id = int(input("Enter expense ID to update: "))
                self.update_expense(expense_id)
            elif choice == '6':
                self.reset_all_expenses()
            elif choice == '7':
                print("👋 Exiting... Goodbye!")
                self.__conn.close()
                sys.exit()
            else:
                print("⚠️ Invalid choice. Please try again.")

# Polymorphism: Subclass that modifies `view_expenses()`
class AdvancedExpenseManager(ExpenseManager):
    def view_expenses(self):
        print("🔍 Fetching expenses with additional analytics...")
        super().view_expenses()

if __name__ == "__main__":
    manager = AdvancedExpenseManager()  # Using subclass for polymorphism
    manager.menu()
