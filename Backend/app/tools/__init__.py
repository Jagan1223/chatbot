from app.tools.zip import get_agent_info, verify_us_zip_code
from app.tools.otp import send_otp, verify_otp_and_fetch_account
from app.tools.loan import get_loan_requirements, check_loan_eligibility, submit_loan_application, get_user_loan_requests

LOAN_TOOLS = [
    send_otp,
    verify_otp_and_fetch_account,
    get_loan_requirements,
    check_loan_eligibility,
    submit_loan_application,
    get_agent_info,
    verify_us_zip_code,
    get_user_loan_requests
]