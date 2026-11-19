import re

import pytest

from app import calculate_grade, create_app


@pytest.fixture()
def app(tmp_path):
    return create_app({"TESTING": True, "SECRET_KEY": "test-secret", "DATABASE": str(tmp_path / "test.db"), "PAGE_SIZE": 2})


@pytest.fixture()
def client(app):
    return app.test_client()


def token(client):
    response = client.get("/students/add")
    match = re.search(rb'name="csrf_token" value="([^"]+)"', response.data)
    assert match
    return match.group(1).decode()


def payload(client, **overrides):
    data = {"csrf_token": token(client), "name": "Ayesha Khan", "age": "21", "email": "ayesha@example.com",
            "phone": "+91 98765 43210", "gender": "Female", "course": "Computer Science",
            "marks": "88.5", "registration_date": "2026-11-16"}
    data.update(overrides)
    return data


def add(client, **overrides):
    return client.post("/students/add", data=payload(client, **overrides), follow_redirects=True)


def test_application_startup_and_pages(client):
    assert client.get("/").status_code == 200
    assert b"Student directory" in client.get("/").data
    assert client.get("/about").status_code == 200
    assert client.get("/contact").status_code == 200
    css = client.get("/static/css/style.css")
    assert css.status_code == 200 and b".hero" in css.data


def test_add_student_success_and_details(client):
    response = add(client)
    assert response.status_code == 200
    assert b"Student added successfully" in response.data
    assert b"Ayesha Khan" in response.data
    detail = client.get("/students/1")
    assert detail.status_code == 200 and b"88.50%" in detail.data and b"A" in detail.data


@pytest.mark.parametrize("field,value", [("name", "  "), ("email", "not-an-email"), ("age", "121"),
    ("age", "0"), ("marks", "100.1"), ("marks", "nan"), ("course", ""), ("phone", "abc")])
def test_invalid_student_input_rejected(client, field, value):
    response = client.post("/students/add", data=payload(client, **{field: value}))
    assert response.status_code == 400
    assert b"error" in response.data


def test_duplicate_email_rejected_case_insensitively(client):
    add(client)
    response = add(client, name="Other Person", email="AYESHA@example.com")
    assert b"already exists" in response.data


def test_edit_student(client):
    add(client)
    assert client.get("/students/1/edit").status_code == 200
    response = client.post("/students/1/edit", data=payload(client, name="Updated Name", marks="39"), follow_redirects=True)
    assert response.status_code == 200
    assert b"Updated Name" in response.data and b"Fail" in response.data


def test_delete_student_requires_csrf_and_deletes(client):
    add(client)
    assert client.post("/students/1/delete").status_code == 400
    response = client.post("/students/1/delete", data={"csrf_token": token(client)}, follow_redirects=True)
    assert b"Student deleted" in response.data
    assert b"No student records" in response.data


def test_search_filter_sort_and_pagination(client):
    add(client)
    add(client, name="Ben Smith", email="ben@example.com", course="Mathematics", marks="72")
    add(client, name="Cara Lee", email="cara@example.com", course="Mathematics", marks="94")
    assert b"Ayesha Khan" in client.get("/?search=Ayesha").data
    assert b"Ben Smith" in client.get("/?course=Mathematics&sort=marks_high").data
    page = client.get("/?page=2")
    assert page.status_code == 200 and b"Page 2 of 2" in page.data and b"Cara Lee" in page.data


def test_grade_calculation_and_dashboard_statistics(client):
    assert [calculate_grade(n) for n in (95, 85, 75, 65, 45, 39)] == ["A+", "A", "B", "C", "D", "F"]
    add(client, marks="100")
    add(client, name="Ben Smith", email="ben@example.com", marks="0")
    page = client.get("/").data
    assert b"50.0" in page and b"100.0" in page and b"0.0" in page


def test_database_persistence(app, client):
    add(client)
    second_app = create_app({"TESTING": True, "SECRET_KEY": "second", "DATABASE": app.config["DATABASE"]})
    assert b"Ayesha Khan" in second_app.test_client().get("/").data


def test_not_found_and_csrf_error(client):
    assert client.get("/students/999").status_code == 404
    assert client.post("/students/add", data={}).status_code == 400
