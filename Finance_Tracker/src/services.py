from src.expense_manager import add_expense
from src.ml_model import predict_category


def add_expense_service(amount, description):
    category = predict_category(description)
    add_expense(amount, category, description)
    return category