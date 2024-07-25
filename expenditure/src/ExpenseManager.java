import java.util.ArrayList;
import java.util.List;
import java.util.Scanner;

// The ExpenseManager class represents the main application logic.
public class ExpenseManager {
    // The main method serves as the entry point of the program.
    public static void main(String[] args) {
        // Encapsulation: expenses list is hidden within the class.
        List<Expense> expenses = new ArrayList<>();
        Scanner scanner = new Scanner(System.in);

        while (true) {
            System.out.println("+-------------------------------------------+");
            System.out.println("|           Family Expense Manager          |");
            System.out.println("+-------------------------------------------+");
            System.out.println("| 1. Add Expense                            |");
            System.out.println("| 2. View Expenses                          |");
            System.out.println("| 3. Delete Expense                         |");
            System.out.println("| 4. View Total Expense for a Date          |");
            System.out.println("| 5. Exit                                   |");
            System.out.println("+-------------------------------------------+");
            System.out.print("Enter your choice: ");
            int choice = scanner.nextInt();

            // Polymorphism: using a switch-case to handle different user inputs.
            switch (choice) {
                case 1:
                    System.out.println("+-------------------------------------------+");
                    System.out.println("|               Add Expense                 |");
                    System.out.println("+-------------------------------------------+");
                    System.out.print("Enter amount: ");
                    double amount = scanner.nextDouble();
                    System.out.print("Enter date (YYYY-MM-DD): ");
                    String date = scanner.next();
                    System.out.print("Enter category: ");
                    String category = scanner.next();
                    System.out.print("Enter family person's name: ");
                    String person = scanner.next();
                    // Creating an instance of Expense using the constructor (Encapsulation).
                    expenses.add(new Expense(amount, date, category, person));
                    System.out.println("Expense added successfully.");
                    break;
                case 2:
                    System.out.println("+-------------------------------------------+");
                    System.out.println("|             View Expenses                 |");
                    System.out.println("+-------------------------------------------+");
                    if (expenses.isEmpty()) {
                        System.out.println("No expenses added yet.");
                    } else {
                        // Display table header
                        System.out.printf("%-5s %-10s %-10s %-10s %-10s%n", "Index", "Amount", "Date", "Category", "Person");
                        System.out.println("-------------------------------------------------");
                        // Encapsulation: accessing Expense properties through getter methods.
                        for (int i = 0; i < expenses.size(); i++) {
                            Expense expense = expenses.get(i);
                            System.out.printf("%-5d %-10.2f %-10s %-10s %-10s%n", i, expense.getAmount(), expense.getDate(), expense.getCategory(), expense.getPerson());
                        }
                    }
                    break;
                case 3:
                    System.out.println("+-------------------------------------------+");
                    System.out.println("|            Delete Expense                 |");
                    System.out.println("+-------------------------------------------+");
                    if (expenses.isEmpty()) {
                        System.out.println("No expenses to delete.");
                    } else {
                        System.out.print("Enter index of expense to delete: ");
                        int index = scanner.nextInt();
                        if (index >= 0 && index < expenses.size()) {
                            expenses.remove(index);
                            System.out.println("Expense deleted successfully.");
                        } else {
                            System.out.println("Invalid expense index.");
                        }
                    }
                    break;
                case 4:
                    System.out.println("+-------------------------------------------+");
                    System.out.println("| View Total Expense for a Date             |");
                    System.out.println("+-------------------------------------------+");
                    if (expenses.isEmpty()) {
                        System.out.println("No expenses added yet.");
                    } else {
                        System.out.print("Enter date to view total expense (YYYY-MM-DD): ");
                        String viewDate = scanner.next();
                        double totalExpenseForDate = getTotalExpenseForDate(expenses, viewDate);
                        System.out.println("Total expense for " + viewDate + " is: " + totalExpenseForDate);
                    }
                    break;
                case 5:
                    System.out.println("Exiting...");
                    // Exiting the program.
                    System.exit(0);
                default:
                    System.out.println("Invalid choice. Please try again.");
            }
        }
    }

    // Abstraction: hiding the implementation details of calculating total expenses.
    private static double getTotalExpenseForDate(List<Expense> expenses, String viewDate) {
        double totalExpense = 0;
        for (Expense expense : expenses) {
            if (expense.getDate().equals(viewDate)) {
                totalExpense += expense.getAmount();
            }
        }
        return totalExpense;
    }
}

// The Expense class represents an individual expense.
class Expense {
    // Encapsulation: private variables that cannot be accessed directly from outside the class.
    private double amount;
    private String date;
    private String category;
    private String person;

    // Constructor: Initializes the Expense object (Encapsulation).
    public Expense(double amount, String date, String category, String person) {
        this.amount = amount;
        this.date = date;
        this.category = category;
        this.person = person;
    }

    // Getter method for amount (Encapsulation).
    public double getAmount() {
        return amount;
    }

    // Setter method for amount (Encapsulation).
    public void setAmount(double amount) {
        this.amount = amount;
    }

    // Getter method for date (Encapsulation).
    public String getDate() {
        return date;
    }

    // Setter method for date (Encapsulation).
    public void setDate(String date) {
        this.date = date;
    }

    // Getter method for category (Encapsulation).1
    public String getCategory() {
        return category;
    }

    // Setter method for category (Encapsulation).
    public void setCategory(String category) {
        this.category = category;
    }

    // Getter method for person (Encapsulation).
    public String getPerson() {
        return person;
    }

    // Setter method for person (Encapsulation).
    public void setPerson(String person) {
        this.person = person;
    }
}
