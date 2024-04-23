import csv
import os
import threading
import time
from collections import Counter, defaultdict
from datetime import datetime
from decimal import Decimal, InvalidOperation

transaction_history = []

class Transaction:
    def __init__(self, ID, counterparty, amount, fee, transaction_type, datetime_str):
        self.ID = ID
        self.counterparty = counterparty
        try:
            self.amount = Decimal(amount.replace(" IQD", "").strip()) if amount and amount.strip() else Decimal('0.0')
        except InvalidOperation:
            print(f"Warning: Invalid amount data '{amount}' - defaulting to 0.0")
            self.amount = Decimal('0.0')
        try:
            self.fee = Decimal(fee.replace(" IQD", "").strip()) if fee and fee.strip() else Decimal('0.0')
        except InvalidOperation:
            print(f"Warning: Invalid fee data '{fee}' - defaulting to 0.0")
            self.fee = Decimal('0.0')
        self.transaction_type = transaction_type
        self.timestamp = datetime.strptime(datetime_str, "%d/%m/%Y,%H:%M:%S")

    def __str__(self):
        return f"ID: {self.ID}, Counterparty: {self.counterparty}, Amount: {self.amount}, Fee: {self.fee}, Type: {self.transaction_type}, Timestamp: {self.timestamp}"


def read_transactions(file_path):
    transactions = []
    with open(file_path, 'r', encoding='utf-8') as file:
        csv_reader = csv.reader(file)
        next(csv_reader)  # Skip the header if there is one, or adjust accordingly
        for row in csv_reader:
            ID, counterparty, amount, fee, transaction_type, date, time = row
            datetime_str = f"{date},{time}"
            transaction = Transaction(ID, counterparty, amount, fee, transaction_type, datetime_str)
            transactions.append(transaction)
    return transactions


def background_load_data(filename):
    global transaction_history
    transaction_history = read_transactions(filename)
    print("Data loaded in background thread.")


def timer(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"{func.__name__} took {end_time - start_time:.2f} seconds to execute.")
        return result

    return wrapper


def analyze_transaction_types(transactions):
    type_count = Counter(t.transaction_type for t in transactions)
    # Sort by count in descending order
    sorted_types = sorted(type_count.items(), key=lambda item: item[1], reverse=True)
    print("Transaction types sorted by frequency:")
    for trans_type, count in sorted_types:
        print(f"{trans_type}: {count} transactions")

def most_common_transaction_types(transactions):
    type_count = Counter(t.transaction_type for t in transactions)
    top_five_types = type_count.most_common(5)  # Retrieve the top 5 transaction types
    print("Top 5 transaction types:")
    for trans_type, count in top_five_types:
        print(f"{trans_type}: {count} transactions")

def analyze_counterparties(transactions):
    counterparty_count = Counter(t.counterparty for t in transactions)
    # Sort by count in descending order
    sorted_counterparties = sorted(counterparty_count.items(), key=lambda item: item[1], reverse=True)
    print("Counterparties sorted by frequency:")
    for counterparty, count in sorted_counterparties:
        print(f"{counterparty}: {count} transactions")

def most_common_counterparties(transactions):
    counterparty_count = Counter(t.counterparty for t in transactions)
    top_five_counterparties = counterparty_count.most_common(5)  # Retrieve the top 5 counterparties
    print("Top 5 counterparties:")
    for counterparty, count in top_five_counterparties:
        print(f"{counterparty}: {count} transactions")

def calculate_total_revenue_and_expenditure(transactions):
    total_revenue = Decimal('0.0')
    total_expenditure = Decimal('0.0')
    for transaction in transactions:
        if transaction.transaction_type == 'MONEY_BOX_TRANSFER':  # Skip money box transfers because its not revenue or expenditure
            continue
        if transaction.amount >= 0:
            total_revenue += transaction.amount
        else:
            total_expenditure += transaction.amount  # Expenditure amounts are negative
    print(f"Total Revenue: {total_revenue} IQD")
    print(f"Total Expenditure: {total_expenditure} IQD")  # This will show a negative number, representing the total outflows


def calculate_average_transaction_size(transactions):
    if transactions:
        total_amount = sum(transaction.amount for transaction in transactions)
        average_size = total_amount / len(transactions)
        print(f"Average Transaction Size: {average_size} IQD")
    else:
        print("No transactions to calculate average size.")


def sort_transaction_types_by_total_amount(transactions):
    type_amounts = defaultdict(lambda: 0)
    for transaction in transactions:
        type_amounts[transaction.transaction_type] += transaction.amount
    sorted_types_by_amount = sorted(type_amounts.items(), key=lambda x: x[1], reverse=True)
    print("Transaction types sorted by total amount:")
    for trans_type, total in sorted_types_by_amount:
        print(f"{trans_type}: {total} IQD")

def analyze_spending_habits(transactions):
    # Dictionaries to hold total spending per day of the week and per month
    spending_by_day = defaultdict(Decimal)
    spending_by_month = defaultdict(Decimal)

    for transaction in transactions:
        if transaction.transaction_type == 'MONEY_BOX_TRANSFER':  # Skip money box transfers
            continue
        if transaction.amount < 0:  # Assuming negative amounts represent spending
            day_name = transaction.timestamp.strftime('%A')  # Get day name (e.g., Monday, Tuesday)
            month_name = transaction.timestamp.strftime('%B')  # Get month name (e.g., January, February)
            spending_by_day[day_name] += transaction.amount
            spending_by_month[month_name] += transaction.amount

    # Output results
    print("Spending by Day of the Week:")
    for day, total in spending_by_day.items():
        print(f"{day}: {total} IQD")

    print("Spending by Month:")
    for month, total in spending_by_month.items():
        print(f"{month}: {total} IQD")

def analyze_vendor_loyalty_by_total_amount(transactions):
    total_amount_by_vendor = defaultdict(Decimal)
    for transaction in transactions:
        if transaction.transaction_type == 'MONEY_BOX_TRANSFER':  # Skip money box transfers
            continue
        if transaction.amount < 0:  # Filter to spending transactions
            vendor = transaction.counterparty
            total_amount_by_vendor[vendor] += transaction.amount

    print("Vendor Loyalty by Total Spending:")
    for vendor, total in sorted(total_amount_by_vendor.items(), key=lambda item: item[1], reverse=True):
        print(f"{vendor}: {total} IQD")

def analyze_vendor_loyalty_by_frequency(transactions):
    frequency_by_vendor = defaultdict(int)

    for transaction in transactions:
        if transaction.transaction_type == 'MONEY_BOX_TRANSFER':  # Skip money box transfers
            continue
        if transaction.amount < 0:  # Filter to spending transactions
            vendor = transaction.counterparty
            frequency_by_vendor[vendor] += 1

    # Output results
    print("Vendor Loyalty by Frequency:")
    for vendor, count in sorted(frequency_by_vendor.items(), key=lambda item: item[1], reverse=True):
        print(f"{vendor}: {count} transactions")

def show_available_commands():
    print("Available commands:")
    print("1. Analyze transaction types")
    print("2. Most common transaction types")
    print("3. Analyze counterparties")
    print("4. Most common counterparties")
    print("5. Calculate total revenue and expenditure")
    print("6. Calculate average transaction size")
    print("7. Sort transaction types by total amount")
    print("8. Show all transactions")
    print("9. Analyze spending habits")
    print("10. Analyze vendor loyalty by total amount")
    print("11. Analyze vendor loyalty by frequency")
    print("0. Exit")


def main():
    print("**" * 30)


print("Welcome to the Transaction Analyzer!")
print("**" * 30)
print("please provide the path to the transaction data file.")
print("The data should be in CSV format with the following columns:")
print("ID, Counterparty, Amount, Fee, Type, Date, Time")
print("Example: 1,Company A,100.0,0.5,Deposit,01/01/2021,12:00:00")
print("Please make sure the file is in the same directory as this script.")
print("Enter the file name (e.g., transactions.csv):")
print("**" * 30)

filename = input("Enter the file name: ")
while not os.path.exists(filename):
    print("File not found")
    filename = input("Enter the file name: ")

script_dir = os.path.dirname(os.path.abspath(__file__))
filename = os.path.join(script_dir, filename)
thread = threading.Thread(target=background_load_data, args=(filename,))
thread.start()
thread.join()
print("transaction data loaded.")

if transaction_history:
    print(f"transactions loaded: {transaction_history.__len__()}")
else:
    print("No transaction data available.")

while True:
    print("**" * 30)
    print("Enter the number of the command you want to execute (e.g., 1) or 0 to exit:")
    show_available_commands()
    command = input()
    while command not in ['0', '1', '2', '3', '4', '5', '6', '7', '8','9', '10', '11']:
        print("Invalid command. Please enter a valid command number (1-11):")
        command = input()

    if command == '0':
        print("Exiting the Transaction Analyzer.")
        print("**" * 30)
        print("Thank you for using the Transaction Analyzer!")
        break

    if command == '1':
        analyze_transaction_types(transaction_history)
    elif command == '2':
        most_common_transaction_types(transaction_history)
    elif command == '3':
        analyze_counterparties(transaction_history)
    elif command == '4':
        most_common_counterparties(transaction_history)
    elif command == '5':
        calculate_total_revenue_and_expenditure(transaction_history)
    elif command == '6':
        calculate_average_transaction_size(transaction_history)
    elif command == '7':
        sort_transaction_types_by_total_amount(transaction_history)
    elif command == '8':
        print("All transactions:")
        print("ID, COUNTERPARTY, AMOUNT, FEE, TRANSACTION TYPE, DATE,TIME")
        for i in transaction_history:
            print(i)
    elif command == '9':
        analyze_spending_habits(transaction_history)
    elif command == '10':
        analyze_vendor_loyalty_by_total_amount(transaction_history)
    elif command == '11':
        analyze_vendor_loyalty_by_frequency(transaction_history)

    print("**" * 30)

if __name__ == "__main__":
    main()
