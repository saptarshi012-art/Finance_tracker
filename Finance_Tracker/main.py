from src.database import init_db
from src.expense_manager import add_expense, read_expenses
from src.visualization import category_wise_chart, monthly_expense_chart
from src.alerts import overspending_report
from src.prediction import predict_next_month_expense
from src.insights import generate_insights

def show_menu():
    print("\n====== Finance Tracker ======")
    print("1. Add Expense")
    print("2. View Expenses")
    print("3. Category Chart")
    print("4. Monthly Chart")
    print("5. Alerts")
    print("6. Prediction")
    print("7. Insights")
    print("8. Exit")

def main():
    init_db()

    while True:
        show_menu()
        choice = input("Enter choice: ")

        if choice == "1":
            amount = float(input("Amount: "))
            category = input("Category: ")
            desc = input("Description: ")
            add_expense(amount, category, desc)

        elif choice == "2":
            for exp in read_expenses():
                print(exp)

        elif choice == "3":
            category_wise_chart()

        elif choice == "4":
            monthly_expense_chart()

        elif choice == "5":
            print(overspending_report())

        elif choice == "6":
            print("Prediction:", predict_next_month_expense())

        elif choice == "7":
            print(generate_insights())

        elif choice == "8":
            break

        else:
            print("Invalid choice")

if __name__ == "__main__":
    main()