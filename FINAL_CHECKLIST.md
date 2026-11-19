# Internship Requirement Checklist

| Requirement | Implementation | Verification evidence |
|---|---|---|
| Task 1: setup, homepage, About, Contact | Flask app factory, dashboard and navigation pages | `test_application_startup_and_pages` |
| Task 2: inputs and validation | Student forms; backend validates name, age, email, phone, gender, course, date and marks | `test_invalid_student_input_rejected` (parameterized), `test_add_student_success_and_details` |
| Task 3: calculations and decisions | Average, percentage, grade and pass/fail; 40 is passing | `test_grade_calculation_and_dashboard_statistics`; scale documented in README and report |
| Task 4: persistent data management | SQLite create/read/update/delete, unique email, list/search/filter/sort/pagination | add, duplicate, edit, delete, search/pagination and persistence tests |
| Task 5: polish and review | Responsive CSS, labels, feedback, empty states, deletion confirmation, errors, tests, reports and five genuine screenshots | test suite, live homepage/CSS smoke check and `screenshots/` captures |
| Dashboard metrics | Total, average, highest, lowest, pass rate, grade distribution, recent records | Dashboard calculation test |
| Security | CSRF, parameterized SQL, environment secret, debug off by default, input constraints | invalid CSRF exercised; source review; 400/404 handling tests |
| Database initialization/migration | Startup creates schema and adds missing profile columns to older data | App startup and persistence tests |
| Documentation/repository preparation | README, project report, testing report, development status, `.env.example`, `.gitignore` | File review; no Git repository detected, no push performed |
| Application/asset launch | Local Flask server | Dashboard HTTP 200; CSS HTTP 200 (7,501 bytes) |

## Automated test summary

Final observed test command and count are recorded in `TESTING_REPORT.md`. Tests use a temporary SQLite file and do not touch the demonstration database.
