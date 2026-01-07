from langchain_core.tools import tool
from app.mock.data import MOCK_AGENT_INFO, MOCK_US_ZIP_STORE

@tool
def verify_us_zip_code(zip_code: str) -> dict:
    """
    Mock tool to verify US ZIP codes (5-digit).
    """

    # Format validation (US ZIP = 5 digits)
    if not zip_code.isdigit() or len(zip_code) != 5:
        return {
            "status": "error",
            "reason": "Invalid US ZIP format"
        }

    zip_data = MOCK_US_ZIP_STORE.get(zip_code)

    if not zip_data:
        return {
            "status": "not_found",
            "reason": "ZIP code not found in mock store"
        }

    if not zip_data["serviceable"]:
        return {
            "status": "rejected",
            "reason": "ZIP not serviceable",
            "location": zip_data
        }

    return {
        "status": "verified",
        "location": zip_data,
        "verification_source": "MOCK_US_ZIP_STORE",
    }

@tool
def get_agent_info(zip_code: str) -> dict:
    """
    Tool to get details of Bank Agent based on ZIP codes (5-digit).
    """

    # Format validation (US ZIP = 5 digits)
    if not zip_code.isdigit() or len(zip_code) != 5:
        return {
            "status": "error",
            "reason": "Invalid US ZIP format"
        }

    agent_data = MOCK_AGENT_INFO.get(zip_code)

    if not agent_data:
        return {
            "status": "not_found",
            "reason": "ZIP code not found in Agent info Store"
        }

    return {
        "status": "Agent Found",
        "bank_agent": agent_data,
        "verification_source": "AGENT_INFO_STORE",
    }