## How to run testcases

- Go to -> Application\backend
    - `cd Application`
    - `cd backend`
- Run pytest here
    - `python -m pytest tests`

- Remove Warning ( if any )
    - `python -m pytest tests -p no:warnings`


## Test folder structure

```text
backend
│ -------------------
│ -----------
│ -------
├── tests/
│   ├── db_factory/
│   │   ├── base.py
│   │   └── factory.py
│   ├── fixtures/
│   │   ├── auth_fixture.py
│   │   └── factory_fixture.py
│   ├── modules/
│   │   ├── auth/
│   │   │   ├── test_login.py
│   │   │   ├── test_logout.py
│   │   │   ├── test_register.py
│   │   │   ├── test_resendotp.py
│   │   │   └── test_verifyotp.py
│   │   └── system_admin/
│   │       ├── test_system_admin_audit_Log.py
│   │       └── test_system_admin_stats.py
│   ├── conftest.py
|   ├── readme.md

```
## What implemented 
The test file names indecate what is being added.


