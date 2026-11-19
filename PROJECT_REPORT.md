# StudentHub Project Report

## Abstract

StudentHub is a web-based student records system built with Flask and SQLite. It stores student profiles, validates submitted data, and summarizes academic performance using a documented grading scale.

## Problem statement

Student information maintained in informal lists is difficult to search, update and assess consistently. StudentHub provides one small, persistent application for managing student details and marks.

## Objectives

- Provide the required Home/Dashboard, About and Contact pages.
- Accept, validate and persist student details.
- Support student record maintenance and discovery.
- Calculate academic summaries and grades.
- Deliver an accessible, responsive interface and verify core behavior with automated tests.

## Proposed solution and architecture

The Flask application (`app.py`) handles HTTP routes, validation, CSRF checks, SQLite access and academic calculations. Jinja2 templates render the dashboard, record form, student detail and informational/error pages. A CSS stylesheet provides responsive layout. SQLite stores records on disk and is initialized/migrated at startup.

## Technology stack

Python, Flask, SQLite, HTML5, CSS3, Jinja2 and pytest. No ORM or front-end framework is required.

## Modules

- Dashboard: enrollment, average/high/low marks, pass rate, grade distribution, recent records and paginated directory.
- Student management: create, read, update, delete, search, course filter, sorting, and detail display.
- Academic logic: marks are constrained to 0–100; grade scale is A+ (90+), A (80+), B (70+), C (60+), D (40+), F (below 40). A mark of 40 is passing. Percentage equals the mark value on the 100-point scale.
- Persistence/security: SQLite, parameterized SQL, unique case-insensitive email, server-side validation, CSRF tokens, environment-driven secret key, and production debug default off.

## Database design

`students` has an integer primary key and fields for name, age, email, course, marks, creation timestamp, gender, registration date and phone. Email is unique without regard to case. Input bounds are checked in both the application and database where supported. Startup adds the later optional columns to databases from the original version.

## Application workflow

Users open the dashboard, optionally search/filter/sort, then add or open a student. Forms validate submitted values before parameterized database writes. The dashboard queries persisted data and computes summary values; edit and delete actions require a valid session CSRF token.

## Testing methodology and results

The pytest suite uses temporary SQLite databases. It covers page responses, valid and invalid input, duplicate email, record display/edit/delete, search/filter/sort/pagination, grade/statistic calculations, persistence and error responses. See `TESTING_REPORT.md` for actual execution results.

## Conclusion

The application implements all five internship task groups and is prepared for local demonstration. It is a single-user demonstration tool without login/role management or deployment automation.

## Future enhancements

Authentication and roles, CSV export, downloadable report cards, backup workflow, and deployment through a hosted WSGI service could be considered if project scope expands.
