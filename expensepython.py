import mysql.connector
import getpass
import re
import hashlib
from datetime import datetime

# Base class for database handling (Encapsulation & Abstraction)
class Database:
    def __init__(self, company_name):
        self._company_name = re.sub(r'\W+', '_', company_name).lower()  # Private attribute with sanitized DB name
        self._category_table = f"{self._company_name}_categories"
        self._expense_table = f"{self._company_name}_expenses"

        # Private connection to corporate database
        self._conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="corporateexpensemanager"
        )
        self._cursor = self._conn.cursor()
        
        self._create_corporate_table()

    def _create_corporate_table(self):
        """Ensure corporate database has a 'companies' table with secure password storage."""
        self._cursor.execute("""
        CREATE TABLE IF NOT EXISTS companies (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL
        )""")
        self._conn.commit()

    def register_company(self, password):
        """Register a new company and store hashed password securely."""
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        self._cursor.execute("SELECT id FROM companies WHERE name = %s", (self._company_name,))
        if not self._cursor.fetchone():
            self._cursor.execute("INSERT INTO companies (name, password) VALUES (%s, %s)", 
                                 (self._company_name, hashed_password))
            self._conn.commit()
            print(f"✅ Company '{self._company_name}' registered successfully!")

            # Create separate database for the company
            self._create_company_database()
        else:
            print("❌ Company already exists. Please log in.")

    def login_company(self, password):
        """Authenticate company using hashed password verification."""
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        self._cursor.execute("SELECT id FROM companies WHERE name = %s AND password = %s", 
                             (self._company_name, hashed_password))
        return bool(self._cursor.fetchone())

    def _create_company_database(self):
        """Create a separate database for each company."""
        self._cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self._company_name}")
        self._conn.commit()
        print(f"✅ Database '{self._company_name}' is ready.")

    def switch_to_company_db(self):
        """Switch to the specific company's database and create tables."""
        self._conn.database = self._company_name
        self._create_company_tables()

    def _create_company_tables(self):
        """Create categories and expenses tables inside the company's database."""
        self._cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {self._category_table} (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) UNIQUE NOT NULL
        )""")
        
        self._cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {self._expense_table} (
            id INT AUTO_INCREMENT PRIMARY KEY,
            amount FLOAT NOT NULL,
            date DATE NOT NULL,
            category_id INT,
            description TEXT,
            recurring ENUM('none', 'daily', 'weekly', 'monthly', 'yearly') DEFAULT 'none',
            FOREIGN KEY (category_id) REFERENCES {self._category_table}(id)
        )""")
        self._conn.commit()

    def get_cursor(self):
        """Encapsulation: Prevent direct access to private cursor"""
        return self._cursor

    def get_conn(self):
        """Encapsulation: Prevent direct access to private connection"""
        return self._conn

    def get_category_table(self):
        return self._category_table

    def get_expense_table(self):
        return self._expense_table


# ExpenseManager class inherits from Database (Inheritance)
class ExpenseManager(Database):
    def __init__(self, db):
        super().__init__(db._company_name)  # Inheritance: Using parent class constructor
        self._cursor = db.get_cursor()
        self._conn = db.get_conn()
        self._category_table = db.get_category_table()
        self._expense_table = db.get_expense_table()

    def add_expense(self, amount, date, category, description, recurring):
        """Polymorphism: Overriding method with additional logic"""
        self._cursor.execute(f"SELECT id FROM {self._category_table} WHERE name = %s", (category,))
        result = self._cursor.fetchone()
        
        if not result:
            self._cursor.execute(f"INSERT INTO {self._category_table} (name) VALUES (%s)", (category,))
            self._conn.commit()
            category_id = self._cursor.lastrowid
        else:
            category_id = result[0]
        
        self._cursor.execute(f"""
        INSERT INTO {self._expense_table} (amount, date, category_id, description, recurring)
        VALUES (%s, %s, %s, %s, %s)
        """, (amount, date, category_id, description, recurring))
        self._conn.commit()
        print("✅ Expense added successfully.")

    def view_expenses(self, filter_type=None):
        """View expenses based on optional filters."""
        query = f"""
        SELECT e.id, e.amount, e.date, c.name, e.description, e.recurring
        FROM {self._expense_table} e
        LEFT JOIN {self._category_table} c ON e.category_id = c.id
        WHERE 1=1
        """
        if filter_type:
            query += f" AND e.recurring = '{filter_type}'"
        
        self._cursor.execute(query)
        expenses = self._cursor.fetchall()
        
        if not expenses:
            print("⚠️ No expenses found for the selected filter.")
            return
        
        print("\n+------------------------------------------------------------+")
        print("| ID | Amount  | Date       | Category    | Description      | Recurring |")
        print("+------------------------------------------------------------+")
        for row in expenses:
            print(f"| {row[0]:<2} | {row[1]:<8} | {row[2]} | {row[3]:<10} | {row[4]:<15} | {row[5]:<9} |")
        print("+------------------------------------------------------------+\n")


# Main function implementing User Interaction
if __name__ == "__main__":
    print("📊 Welcome to Corporate Expense Manager!")

    while True:
        print("\n1. Register\n2. Login\n3. Exit")
        choice = input("Choose an option: ")

        if choice == '1':  # Register a new company
            company_name = input("Enter company name: ")
            password = getpass.getpass("Enter a strong password: ")
            db = Database(company_name)
            db.register_company(password)

        elif choice == '2':  # Login to an existing company
            company_name = input("Enter company name: ")
            password = getpass.getpass("Enter your password: ")
            db = Database(company_name)

            if db.login_company(password):
                print("✅ Login successful!")
                db.switch_to_company_db()
                expense_manager = ExpenseManager(db)  # Polymorphism (ExpenseManager inherits Database)
                while True:
                    print("\n1. Add Expense\n2. View Expenses\n3. Logout")
                    option = input("Choose an option: ")
                    if option == '1':
                        expense_manager.add_expense(
                            float(input("Enter amount: ")),
                            input("Enter date (YYYY-MM-DD): "),
                            input("Enter category: "),
                            input("Enter description: "),
                            input("Enter recurring type: ")
                        )
                    elif option == '2':
                        expense_manager.view_expenses()
                    elif option == '3':
                        break
            else:
                print("❌ Incorrect password. Try again.")

        elif choice == '3':  # Exit
            break
