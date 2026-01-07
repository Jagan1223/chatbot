from langchain_core.tools import tool
from typing import List
from app.db.models import get_loans_by_user, save_loan

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
def submit_loan_application(user_id: str, details: str) -> str:
    """
    Submits a loan application.

    Args:
        user_id (str): Unique identifier of the user submitting the loan.
        details (str): Complete loan application details in serialized JSON or text form.

    Returns:
        str: Confirmation message with reference number if successful,
             or an error message if submission fails.
    """
    try:
        ref_id = save_loan(user_id=user_id, details=details)
        return f"Loan submitted successfully. REF: sub{ref_id:07d}"
    except Exception as e:
        return f"DATABASE ERROR: {str(e)}"

@tool
def get_user_loan_requests(user_id: str) -> dict:
    """
    Fetches all loan applications submitted by a specific user.

    Args:
        user_id (str): Unique identifier of the user whose loan applications
                       need to be retrieved.

    Returns:
        dict:
            status (str): "success" if loans are found,
                          "not_found" if no loans exist,
                          "error" if a database error occurs.
            loans (list, optional): List of loan records. Each record contains:
                - loan_id (int): Unique loan identifier
                - details (str): Loan application details
                - status (str): Current loan status
                - submission_date (str): Timestamp of submission
    """
    try:
        loans = get_loans_by_user(user_id)

        if not loans:
            return {
                "status": "not_found",
                "message": "No loan applications found for this user."
            }

        return {
            "status": "success",
            "loans": loans
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }