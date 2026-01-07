loan_ai_app/
│
├── app/
│   ├── main.py                          # FastAPI entry
│
│   ├── api/
│   │   └── chat.py                     # /chat endpoint
│
│   ├── core/
│   │   ├── config.py                   # env & constants
│   │   └── memory.py                   # LangGraph memory
│
│   ├── db/
│   │   ├── session.py                  # DB connection
│   │   └── models.py                   # DB helpers
│
│   ├── mock/
│   │   └── data.py                     # MOCK_USER_DB, ZIP store
│
│   ├── tools/
│   │   ├── otp.py                      # OTP tools
│   │   ├── loan.py                     # Loan tools
│   │   ├── zip.py                      # ZIP verification
│   │   └── account.py                  # 🆕 Account opening tools
│
│   ├── agents/
│   │   ├── loan_agent.py               # Loan assistant
│   │   └── account_agent.py            # 🆕 Account opening agent
│
│   ├── workflows/
│   │   ├── loan_state.py               # Loan state
│   │   ├── account_state.py            # 🆕 Account state
│   │   ├── account_graph.py            # 🆕 Account graph
│   │   └── loan_graph.py               # Loan graph (supervisor)
│
├── .env
├── requirements.txt
└── README.md
