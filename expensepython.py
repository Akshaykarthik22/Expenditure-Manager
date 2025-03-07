import mysql.connector
import getpass

# Connect to the database
def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="corporateexpensemanager"
    )

# Ensure required tables exist
def setup_tables(conn):
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS companies (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255) UNIQUE NOT NULL,
        password TEXT NOT NULL
    )""")
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        company_id INT NOT NULL,
        FOREIGN KEY (company_id) REFERENCES companies(id)
    )""")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS categories (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        company_id INT NOT NULL,
        FOREIGN KEY (company_id) REFERENCES companies(id)
    )""")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS expenses (
        id INT AUTO_INCREMENT PRIMARY KEY,
        amount DECIMAL(10,2) NOT NULL,
        date DATE NOT NULL,
        category_id INT,
        description TEXT,
        company_id INT NOT NULL,
        FOREIGN KEY (category_id) REFERENCES categories(id),
        FOREIGN KEY (company_id) REFERENCES companies(id)
    )""")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS income (
        id INT AUTO_INCREMENT PRIMARY KEY,
        amount DECIMAL(10,2) NOT NULL,
        date DATE NOT NULL,
        source TEXT NOT NULL,
        company_id INT NOT NULL,
        FOREIGN KEY (company_id) REFERENCES companies(id)
    )""")

    conn.commit()
    cursor.close()

# Register a new company
def register_company(conn, name, password):
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO companies (name, password) VALUES (%s, %s)", (name, password))
        conn.commit()
        print(f"✅ Company '{name}' registered successfully!")
    except mysql.connector.IntegrityError:
        print("❌ Company already exists!")
    cursor.close()

# Expense Manager class
class ExpenseManager:
    def __init__(self, company_id):
        self._conn = connect_db()
        self._cursor = self._conn.cursor()
        self.company_id = company_id

    def add_expense(self, amount, date, category, description):
        self._cursor.execute("SELECT id FROM categories WHERE name = %s AND company_id = %s", (category, self.company_id))
        result = self._cursor.fetchone()
        if not result:
            self._cursor.execute("INSERT INTO categories (name, company_id) VALUES (%s, %s)", (category, self.company_id))
            self._conn.commit()
            category_id = self._cursor.lastrowid
        else:
            category_id = result[0]

        self._cursor.execute(
            "INSERT INTO expenses (amount, date, category_id, description, company_id) VALUES (%s, %s, %s, %s, %s)",
            (amount, date, category_id, description, self.company_id)
        )
        self._conn.commit()
        print("✅ Expense added successfully.")

    def view_expenses(self):
        self._cursor.execute("""
        SELECT e.id, e.amount, e.date, c.name, e.description
        FROM expenses e
        LEFT JOIN categories c ON e.category_id = c.id
        WHERE e.company_id = %s
        """, (self.company_id,))
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

    def add_income(self, amount, date, source):
        self._cursor.execute(
            "INSERT INTO income (amount, date, source, company_id) VALUES (%s, %s, %s, %s)",
            (amount, date, source, self.company_id)
        )
        self._conn.commit()
        print("✅ Income added successfully.")

    def view_income(self):
        self._cursor.execute("SELECT id, amount, date, source FROM income WHERE company_id = %s", (self.company_id,))
        income = self._cursor.fetchall()

        if not income:
            print("⚠️ No income records found.")
            return

        print("\n+-----------------------------------------------------------+")
        print("| ID | Amount  | Date       | Source                       |")
        print("+-----------------------------------------------------------+")
        for row in income:
            print(f"| {row[0]:<2} | {row[1]:<8} | {row[2]} | {row[3]:<30} |")
        print("+-----------------------------------------------------------+\n")

# Main program
def main():
    conn = connect_db()
    setup_tables(conn)

    while True:
        print("\n🚀 Corporate Expense Manager")
        print("1. Register Company")
        print("2. Login to Company")
        print("3. Exit")
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
                company_id = result[0]
                manager = ExpenseManager(company_id)

                while True:
                    print("\n❤️ Welcome 🤝")
                    print("1. Add Expense")
                    print("2. View Expenses")
                    print("3. Add Income")
                    print("4. View Income")
                    print("5. Logout")
                    action = input("Choose an action: ")

                    if action == "1":
                        manager.add_expense(
                            float(input("Amount: ")),
                            input("Date (YYYY-MM-DD): "),
                            input("Category: "),
                            input("Description: ")
                        )
                    elif action == "2":
                        manager.view_expenses()
                    elif action == "3":
                        manager.add_income(
                            float(input("Amount: ")),
                            input("Date (YYYY-MM-DD): "),
                            input("Source: ")
                        )
                    elif action == "4":
                        manager.view_income()
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

        else:
            print("❌ Invalid option. Try again!")

if __name__ == "__main__":
    main()
