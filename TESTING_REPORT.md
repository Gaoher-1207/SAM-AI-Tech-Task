# Testing Report

## Test cases

The automated pytest suite in `tests/test_app.py` exercises the cases below. All tests use an isolated temporary SQLite database.

| Test case | Expected result | Actual result | Status |
|---|---|---|---|
| Startup and dashboard | App initializes and dashboard returns 200 | Passed | PASS |
| About and Contact | Both pages return 200 | Passed | PASS |
| CSS asset | Static stylesheet returns 200 | Passed | PASS |
| Add valid student | Record saved and shown | Passed | PASS |
| Empty name | Validation rejects request | Passed | PASS |
| Invalid email | Validation rejects request | Passed | PASS |
| Invalid age (0 and 121) | Validation rejects request | Passed | PASS |
| Invalid marks (above range and NaN) | Validation rejects request | Passed | PASS |
| Empty course and invalid phone | Validation rejects request | Passed | PASS |
| Duplicate email | Second record rejected case-insensitively | Passed | PASS |
| Display/detail and grade | Student data, grade and result shown | Passed | PASS |
| Edit student | Updated values persisted and displayed | Passed | PASS |
| Delete student | Missing CSRF rejected; valid delete removes record | Passed | PASS |
| Search/filter/sort/pagination | Matching records and page state shown | Passed | PASS |
| Grade and dashboard calculations | Grade scale and aggregate stats correct | Passed | PASS |
| Persistence | Data remains available in another app instance | Passed | PASS |
| Error handling | Missing record returns 404; invalid CSRF returns 400 | Passed | PASS |
| Python syntax compilation | App and tests compile | Passed | PASS |

## Execution summary

- Command: `.venv\Scripts\python.exe -m pytest -q`
- Result: **17 passed in 0.72s** (rerun 2026-11-19).
- Python compilation: `.venv\Scripts\python.exe -m py_compile app.py tests\test_app.py` completed successfully (2026-11-19).
- Route and template audit: all Flask routes were enumerated; all seven HTML templates exist. The route map includes dashboard, About, Contact, static assets, student details, add, edit, and delete.
- Screenshot audit: all five referenced PNG files exist and are non-empty.
- Earlier live server smoke check: homepage HTTP 200; `/static/css/style.css` HTTP 200 (7,501 bytes).
- Earlier browser capture check: dashboard, student list, add form, edit form, and student detail pages rendered and saved in `screenshots/`.

Pytest's temporary directory is configured under the project and the optional cache plugin is disabled in `pytest.ini` to support restricted environments.
