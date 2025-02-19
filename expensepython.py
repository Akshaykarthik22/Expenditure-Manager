import sys

# Encapsulation: Expense class contains private attributes and public getter/setter methods.
class Expense:
    def __init__(self, amount, date, category, person):
        self.__amount = amount  # Private attribute
        self.__date = date      # Private attribute
        self.__category = category  # Private attribute
        self.__person = person  # Private attribute
    
    # Getter methods (Encapsulation)
    def get_amount(self):
        return self.__amount
    
    def get_date(self):
        return self.__date
    
    def get_category(self):
        return self.__category
    
    def get_person(self):
        return self.__person
    
    # Setter methods (Encapsulation)
    def set_amount(self, amount):
        self.__amount = amount
    
    def set_date(self, date):
        self.__date = date
    
    def set_category(self, category):
        self.__category = category
    
    def set_person(self, person):
        self.__person = person

# Inheritance: RecurringExpense is a subclass of Expense
class RecurringExpense(Expense):
    def __init__(self, amount, date, category, person, recurrence):
        super().__init__(amount, date, category, person)
        self.__recurrence = recurrence  # Additional attribute specific to recurring expenses
    
    # Polymorphism: Overriding get_amount to apply a discount for recurring expenses
    def get_amount(self):
        return super().get_amount() * 0.9  # 10% discount on recurring expenses
    
    def get_recurrence(self):
        return self.__recurrence

    def set_recurrence(self, recurrence):
        self.__recurrence = recurrence

# ExpenseManager class to handle the operations (Encapsulation & Abstraction)
class ExpenseManager:
    def __init__(self):
        self.expenses = []  # List to store expenses (Encapsulation)
    
    # Polymorphism: Using methods to handle different functionalities
    def add_expense(self, amount, date, category, person, is_recurring=False, recurrence=None):
        if is_recurring:
            expense = RecurringExpense(amount, date, category, person, recurrence)
        else:
            expense = Expense(amount, date, category, person)
        self.expenses.append(expense)
        print("Expense added successfully.")
    
    def view_expenses(self):
        if not self.expenses:
            print("No expenses added yet.")
        else:
            print("+------------------------------------------------+")
            print("|               View Expenses                    |")
            print("+------------------------------------------------+")
            print("Index  Amount  Date        Category  Person   Recurrence")
            print("--------------------------------------------------")
            for i, expense in enumerate(self.expenses):
                recurrence = expense.get_recurrence() if isinstance(expense, RecurringExpense) else "N/A"
                print(f"{i:<6} {expense.get_amount():<7} {expense.get_date():<10} {expense.get_category():<10} {expense.get_person():<10} {recurrence:<10}")
    
    def delete_expense(self, index):
        if 0 <= index < len(self.expenses):
            del self.expenses[index]
            print("Expense deleted successfully.")
        else:
            print("Invalid index.")
    
    def update_expense(self, index):
        if 0 <= index < len(self.expenses):
            expense = self.expenses[index]
            amount = float(input("Enter new amount: "))
            date = input("Enter new date (YYYY-MM-DD): ")
            category = input("Enter new category: ")
            person = input("Enter new family person's name: ")
            
            expense.set_amount(amount)
            expense.set_date(date)
            expense.set_category(category)
            expense.set_person(person)
            
            if isinstance(expense, RecurringExpense):
                recurrence = input("Enter new recurrence (e.g., monthly, weekly): ")
                expense.set_recurrence(recurrence)
            
            print("Expense updated successfully.")
        else:
            print("Invalid index.")
    
    def view_total_expense_by_month(self, month):
        total_expense = 0
        for expense in self.expenses:
            if expense.get_date().startswith(month):
                if isinstance(expense, RecurringExpense):
                    if expense.get_recurrence() == "weekly":
                        total_expense += expense.get_amount() * 4.33  # Approximate weeks in a month
                    elif expense.get_recurrence() == "monthly":
                        total_expense += expense.get_amount()
                else:
                    total_expense += expense.get_amount()
        print(f"Total expense for {month}: {total_expense}")
    
    def menu(self):
        while True:
            print("+-------------------------------------------+")
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
                index = int(input("Enter index of expense to delete: "))
                self.delete_expense(index)
            elif choice == '4':
                month = input("Enter month to view total expense (YYYY-MM): ")
                self.view_total_expense_by_month(month)
            elif choice == '5':
                index = int(input("Enter index of expense to update: "))
                self.update_expense(index)
            elif choice == '6':
                print("Exiting...")
                sys.exit()
            else:
                print("Invalid choice. Please try again.")

if __name__ == "__main__":
    manager = ExpenseManager()
    manager.menu()
