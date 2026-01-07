import time, random
from langchain_core.tools import tool
from app.mock.data import MOCK_USER_DB

otp_store = {}

@tool
def send_otp(mobile: str) -> str:
    """
    Generates and stores a mock OTP for the given mobile number.
    """
    try:
        otp = random.randint(1000, 9999)
        expiry = int(time.time()) + 300        # 5 minutes expiry
        print("OTP: ",otp)
        otp_store[mobile] = {
            "otp": str(otp),
            "expires_at": expiry
        }

        # In real systems, send via SMS gateway here
        return "SUCCESS: A verification code has been sent."

    except Exception as e:
        return f"ERROR: Failed to generate OTP. {str(e)}"

@tool
def verify_otp_and_fetch_account(mobile: str, otp: str) -> dict:
    """
    Verifies OTP from otp_store and retrieves account info
    associated with the given mobile number.
    """
    record = otp_store.get(mobile)

    if not record or time.time() > record["expires_at"]:
        return {"status": "error", "message": "OTP invalid or expired"}

    if record["otp"] != otp:
        return {"status": "error", "message": "Incorrect OTP"}

    del otp_store[mobile]

    account = MOCK_USER_DB.get(mobile)

    return {
        "status": "success",
        "account_exists": bool(account),
        "account_details": account
    }