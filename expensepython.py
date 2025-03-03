import mysql.connector
import getpass


# Connect to the main database
def connect_main_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="corporateexpensemanager"
    )


# Register a new company and create its own database
def register_company(conn, name, password):
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS companies (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255) UNIQUE NOT NULL,
        password TEXT NOT NULL
    )""")
    try:
        cursor.execute("INSERT INTO companies (name, password) VALUES (%s, %s)", (name, password))
        conn.commit()
        print(f"✅ Company '{name}' registered successfully!")

        company_db_name = f"{name.lower()}_db"
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{company_db_name}`")
        print(f"✅ Database '{company_db_name}' created!")

        company_conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database=company_db_name
        )
        company_cursor = company_conn.cursor()
        company_cursor.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) UNIQUE NOT NULL
        )""")
        company_cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INT AUTO_INCREMENT PRIMARY KEY,
            amount DECIMAL(10,2) NOT NULL,
            date DATE NOT NULL,
            category_id INT,
            description TEXT,
            FOREIGN KEY (category_id) REFERENCES categories(id)
        )""")
        company_conn.commit()
        company_cursor.close()
        company_conn.close()

    except mysql.connector.IntegrityError:
        print("❌ Company already exists!")
    cursor.close()


# Reset the companies table and IDs
def reset_companies_table(conn):
    cursor = conn.cursor()
    confirm = input("⚠️ Are you sure you want to reset the companies table? This will delete ALL companies! (yes/no): ")
    if confirm.lower() == "yes":
        cursor.execute("DELETE FROM companies")
        cursor.execute("ALTER TABLE companies AUTO_INCREMENT = 1")
        conn.commit()
        print("✅ Companies table reset successfully. All records deleted, IDs start from 1.")
    else:
        print("❌ Reset cancelled.")
    cursor.close()


# Expense Manager class
class ExpenseManager:
    def __init__(self, company_name):
        company_db = f"{company_name.lower()}_db"
        self._conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database=company_db
        )
        self._cursor = self._conn.cursor()

    def add_expense(self, amount, date, category, description):
        self._cursor.execute("SELECT id FROM categories WHERE name = %s", (category,))
        result = self._cursor.fetchone()
        if not result:
            self._cursor.execute("INSERT INTO categories (name) VALUES (%s)", (category,))
            self._conn.commit()
            category_id = self._cursor.lastrowid
        else:
            category_id = result[0]

        self._cursor.execute(
            "INSERT INTO expenses (amount, date, category_id, description) VALUES (%s, %s, %s, %s)",
            (amount, date, category_id, description)
        )
        self._conn.commit()
        print("✅ Expense added successfully.")

    def delete_expense(self, expense_id):
        self._cursor.execute("DELETE FROM expenses WHERE id = %s", (expense_id,))
        self._conn.commit()

        # Reset IDs after deletion
        self._cursor.execute("SET @count = 0;")
        self._cursor.execute("UPDATE expenses SET id = (@count := @count + 1);")
        self._cursor.execute("ALTER TABLE expenses AUTO_INCREMENT = 1;")
        self._conn.commit()

        print("✅ Expense deleted and IDs reset.")

    def modify_expense(self, expense_id, amount, date, category, description):
        self._cursor.execute("SELECT id FROM categories WHERE name = %s", (category,))
        result = self._cursor.fetchone()
        if not result:
            self._cursor.execute("INSERT INTO categories (name) VALUES (%s)", (category,))
            self._conn.commit()
            category_id = self._cursor.lastrowid
        else:
            category_id = result[0]

        self._cursor.execute("""
        UPDATE expenses
        SET amount = %s, date = %s, category_id = %s, description = %s
        WHERE id = %s
        """, (amount, date, category_id, description, expense_id))
        self._conn.commit()
        print("✅ Expense modified successfully.")

    def view_expenses(self):
        self._cursor.execute("""
        SELECT e.id, e.amount, e.date, c.name, e.description
        FROM expenses e
        LEFT JOIN categories c ON e.category_id = c.id
        """)
        expenses = self._cursor.fetchall()

        if not expenses:
            print("⚠️ No expenses found.")
            return

        print("\n+---------------------------------------------------------------------+")
        print("| ID | Amount  | Date       | Category    | Description              |")
        print("+---------------------------------------------------------------------+")
        for row in expenses:
            print(f"| {row[0]:<2} | {row[1]:<8} | {row[2]} | {row[3]:<10} | {row[4]:<20} |")
        print("+---------------------------------------------------------------------+\n")


# Main program
def main():
    conn = connect_main_db()

    while True:
        print("\n🚀 Corporate Expense Manager")
        print("1. Register Company")
        print("2. Login to Company")
        print("3. Exit")
        print("4. Reset Companies Table")
        choice = input("Choose an option: ")

        if choice == "1":
            name = input("Enter company name: ")
            password = getpass.getpass("Enter password: ")
            register_company(conn, name, password)

        elif choice == "2":
            name = input("Company name: ")
            password = getpass.getpass("Password: ")
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM companies WHERE name = %s AND password = %s", (name, password))
            result = cursor.fetchone()

            if result:
                manager = ExpenseManager(name)
                while True:
                    print("\n❤️ Welcome🤝\n1. Add Expense\n2. Delete Expense\n3. Modify Expense\n4. View Expenses\n5. Logout")
                    action = input("Choose an action: ")

                    if action == "1":
                        manager.add_expense(
                            float(input("Amount: ")),
                            input("Date (YYYY-MM-DD): "),
                            input("Category: "),
                            input("Description: ")
                        )
                    elif action == "2":
                        manager.delete_expense(int(input("Expense ID: ")))
                    elif action == "3":
                        manager.modify_expense(
                            int(input("Expense ID: ")),
                            float(input("New Amount: ")),
                            input("New Date (YYYY-MM-DD): "),
                            input("New Category: "),
                            input("New Description: ")
                        )
                    elif action == "4":
                        manager.view_expenses()
                    elif action == "5":
                        print("👋 Logged out.")
                        break
                    else:
                        print("❌ Invalid choice.")
            else:
                print("❌ Invalid credentials.")
            cursor.close()

        elif choice == "3":
            print("👋 Exiting... Have a great day!")
            conn.close()
            break

        elif choice == "4":
            reset_companies_table(conn)

        else:
            print("❌ Invalid option. Try again!")


if __name__ == "__main__":
    main()
