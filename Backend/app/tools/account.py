
from langchain_core.tools import tool

@tool
def transfer_back_to_loan_assistant(reason: str):
    """
    Call this tool if the user wants to cancel account opening, 
    if they mention they already have a bank account, 
    or if they want to go back to the loan application process.
    """
    return f"Transferring back to Loan Assistant. Reason: {reason}"

@tool
def submit_account_opening(details: dict) -> dict:
    """
    Submits a new bank account opening request.
    Args:
        details: Dictionary containing user information such as
                 full_name, employment_type, address, and KYC data.
    Returns:
        A dictionary containing the created account details.
    """
    print("Inside account_assistant Tools....")
    return {
        "status": "success",
        "account_details": {
            "account_id": "ACC12345",
            "full_name": details.get("full_name"),
            "employment_type": details.get("employment_type")
        }
    }
