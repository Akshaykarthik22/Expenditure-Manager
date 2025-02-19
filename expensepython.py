import sys
import mysql.connector

# MySQL Connection
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="ExpenseManager"
)
cursor = conn.cursor()

# Ensure the table exists
cursor.execute("""
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
conn.commit()

class ExpenseManager:
    def add_expense(self, amount, date, category, person, is_recurring=False, recurrence=None):
        query = "INSERT INTO expenses (amount, date, category, person, is_recurring, recurrence) VALUES (%s, %s, %s, %s, %s, %s)"
        cursor.execute(query, (amount, date, category, person, is_recurring, recurrence))
        conn.commit()
        print("✅ Expense added successfully.")

    def view_expenses(self):
        cursor.execute("SELECT * FROM expenses")
        expenses = cursor.fetchall()

        if not expenses:
            print("⚠️ No expenses found.")
            return

        print("\n+------------------------------------------------------+")
        print("|                   View Expenses                     |")
        print("+------------------------------------------------------+")
        print("| ID | Amount  | Date       | Category    | Person   | Recurrence |")
        print("+------------------------------------------------------+")

        for row in expenses:
            recurrence_display = row[6] if row[5] else "N/A"  # Handling the recurrence column properly
            print(f"| {row[0]:<2} | {row[1]:<7} | {row[2]:<10} | {row[3]:<10} | {row[4]:<8} | {recurrence_display:<10} |")

        print("+------------------------------------------------------+\n")

    def delete_expense(self, expense_id):
        cursor.execute("DELETE FROM expenses WHERE id = %s", (expense_id,))
        conn.commit()
        print("✅ Expense deleted successfully.")

    def update_expense(self, expense_id):
        amount = float(input("Enter new amount: "))
        date = input("Enter new date (YYYY-MM-DD): ")
        category = input("Enter new category: ")
        person = input("Enter new person's name: ")
        recurrence = input("Enter recurrence (weekly/monthly or leave empty): ")
        is_recurring = bool(recurrence)

        query = "UPDATE expenses SET amount=%s, date=%s, category=%s, person=%s, is_recurring=%s, recurrence=%s WHERE id=%s"
        cursor.execute(query, (amount, date, category, person, is_recurring, recurrence, expense_id))
        conn.commit()
        print("✅ Expense updated successfully.")

    def view_total_expense_by_month(self, month):
        cursor.execute("SELECT amount, recurrence, is_recurring FROM expenses WHERE DATE_FORMAT(date, '%Y-%m') = %s", (month,))
        expenses = cursor.fetchall()
        total_expense = 0

        for amount, recurrence, is_recurring in expenses:
            if is_recurring and recurrence == "weekly":
                total_expense += amount * 4.33  # 4.33 weeks in a month
            else:
                total_expense += amount

        print(f"📊 Total expense for {month}: {total_expense}")

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
            print("| 6. Exit                                   |")
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
                print("👋 Exiting... Goodbye!")
                conn.close()
                sys.exit()
            else:
                print("⚠️ Invalid choice. Please try again.")

if __name__ == "__main__":
    manager = ExpenseManager()
    manager.menu()
