from langchain_core.tools import tool
from typing import List
from app.db.models import save_loan

@tool
def get_loan_requirements(loan_type: str) -> List[str]:
    """Returns required fields for a 'new' or 'refinance' loan."""
    base_fields = [
        "full_name",
        "employment_type",
        "annual_income",
        "annual_expense",
        "property_value",
        "zip_code",
        "requested_amount"
    ]

    if "new" in loan_type.lower():
        return base_fields + ["employer_name"]

    return base_fields + ["existing_loan_id"]

@tool
def check_loan_eligibility(
    full_name: str,
    annual_income: str,
    annual_expense: str,
    property_value: str,
    requested_amount: str
) -> str:
    """
    Checks loan eligibility based on disposable income
    (annual income - annual expense) and calculates
    maximum eligible loan amount.
    """
    try:
        # Clean inputs (remove commas, currency symbols, spaces)
        clean_income = "".join(filter(str.isdigit, str(annual_income)))
        clean_expense = "".join(filter(str.isdigit, str(annual_expense)))
        clean_value = "".join(filter(str.isdigit, str(property_value)))
        clean_rqst_amount = "".join(filter(str.isdigit, str(requested_amount)))

        income_val = int(clean_income)
        expense_val = int(clean_expense)
        property_val = int(clean_value)
        rqst_amount = int(clean_rqst_amount)

        disposable_income = income_val - expense_val

        MIN_DISPOSABLE_INCOME = 50000
        LOAN_MULTIPLIER = 10

        if disposable_income < MIN_DISPOSABLE_INCOME:
            return (
                f"ELIGIBILITY CHECK: {full_name} is NOT ELIGIBLE for the loan. "
                f"Disposable income is {disposable_income}, "
                f"minimum required is {MIN_DISPOSABLE_INCOME}."
            )

        max_loan_amount = min(
            disposable_income * LOAN_MULTIPLIER,
            0.8 * property_val
        )

        is_rqstamt_higher = rqst_amount > max_loan_amount

        return (
            f"ELIGIBILITY CHECK: {full_name} is ELIGIBLE for the loan.\n"
            f"Annual Income: {income_val}\n"
            f"Annual Expense: {expense_val}\n"
            f"Disposable Income: {disposable_income}\n"
            f"Maximum Eligible Loan Amount: {max_loan_amount}\n"
            f"Requested_amount_exceeds_limit: {is_rqstamt_higher}"
        )

    except Exception:
        return (
            "ERROR: Could not process income or expense values. "
            "Please provide valid numeric inputs."
        )
    
@tool
def submit_loan_application(details: str) -> str:
    """Finalizes and submits the application."""
    try:
        ref = save_loan(details)
        return f"Loan submitted successfully. REF: sub{ref:07d}"
    except Exception as e:
        return f"DATABASE ERROR: {str(e)}"
