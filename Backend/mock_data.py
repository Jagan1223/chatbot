MOCK_USER_DB = {
    "1234567890": {"name": "John Doe", "email": "john@example.com", "customer_tier": "Gold", "customer_id": "120056"},
    "9876543210": {"name": "Alice Smith", "email": "alice@example.com", "customer_tier": "Silver", "customer_id": "120057"}
}

MOCK_US_ZIP_STORE = {
    "10001": {
        "country": "US",
        "state": "New York",
        "state_code": "NY",
        "county": "New York County",
        "city": "New York",
        "area": "Manhattan",
        "serviceable": True,
        "risk_zone": "LOW",
        "metro": "NYC Metro",
        "bank_agent": {
            "agent_id": "NYC-AG-001",
            "name": "Sarah Thompson",
            "branch": "Midtown Manhattan",
            "phone": "+1-212-555-0198",
            "email": "sarah.thompson@bank.com"
        }
    },
    "90001": {
        "country": "US",
        "state": "California",
        "state_code": "CA",
        "county": "Los Angeles County",
        "city": "Los Angeles",
        "area": "South Los Angeles",
        "serviceable": True,
        "risk_zone": "MEDIUM",
        "metro": "LA Metro",
        "bank_agent": {
            "agent_id": "LA-AG-014",
            "name": "Michael Rodriguez",
            "branch": "South LA Branch",
            "phone": "+1-323-555-0142",
            "email": "michael.rodriguez@bank.com"
        }
    },
    "60601": {
        "country": "US",
        "state": "Illinois",
        "state_code": "IL",
        "county": "Cook County",
        "city": "Chicago",
        "area": "Loop",
        "serviceable": True,
        "risk_zone": "LOW",
        "metro": "Chicago Metro",
        "bank_agent": {
            "agent_id": "CC-AG-014",
            "name": "Michael Rod",
            "branch": "South CC Branch",
            "phone": "+1-323-555-0142",
            "email": "michael.rod@bank.com"
        }
    },
    "73301": {
        "country": "US",
        "state": "Texas",
        "state_code": "TX",
        "county": "Travis County",
        "city": "Austin",
        "area": "Downtown",
        "serviceable": True,
        "risk_zone": "LOW",
        "metro": "Austin Metro",
        "bank_agent": {
            "agent_id": "TC-AG-001",
            "name": "Sarah Tom",
            "branch": "West Austin",
            "phone": "+1-212-555-0198",
            "email": "sarah.tom@bank.com"
        }
    },
    "33101": {
        "country": "US",
        "state": "Florida",
        "state_code": "FL",
        "county": "Miami-Dade County",
        "city": "Miami",
        "area": "Downtown Miami",
        "serviceable": False,
        "risk_zone": "HIGH",
        "metro": "Miami Metro",
        "bank_agent": {
            "agent_id": "MDC-AG-014",
            "name": "Michael Guez",
            "branch": "South Miami Branch",
            "phone": "+1-323-555-0142",
            "email": "michael.guez@bank.com"
        }
    }
}