import json

from project.api.models import User


def test_add_user(test_app, test_database):
    client = test_app.test_client()

    response = client.post(
        "/users",
        data=json.dumps({"username": "roger", "email": "rher92@test.com"}),
        content_type="application/json",
    )
    data = json.loads(response.data.decode())

    assert response.status_code == 201
    assert "rher92@test.com was added" in data["message"]


def test_add_invalid_user(test_app, test_database):
    client = test_app.test_client()

    response = client.post(
        "/users", data=json.dumps({}), content_type="application/json"
    )
    data = json.loads(response.data.decode())

    assert response.status_code == 400
    assert "Input payload validation failed" in data["message"]


def test_add_user_invalid_json_keys(test_app, test_database):
    client = test_app.test_client()

    response = client.post(
        "/users",
        data=json.dumps({"email": "rher92@test.com"}),
        content_type="application/json",
    )
    data = json.loads(response.data.decode())

    assert response.status_code == 400
    assert "Input payload validation failed" in data["message"]


def test_add_user_duplicate_email(test_app, test_database):
    client = test_app.test_client()

    client.post(
        "/users",
        data=json.dumps({"email": "rher92@test.com", "username": "roger"}),
        content_type="application/json",
    )
    response = client.post(
        "/users",
        data=json.dumps({"email": "rher92@test.com", "username": "roger"}),
        content_type="application/json",
    )
    data = json.loads(response.data.decode())

    assert response.status_code == 400
    assert "Sorry. That email already exists" in data["message"]


def test_single_user(test_app, test_database, add_user):
    client = test_app.test_client()
    user = add_user("roger", "rher92@test.com")

    response = client.get(f"/users/{user.id}")
    data = json.loads(response.data.decode())

    assert response.status_code == 200
    assert "roger" in data["username"]
    assert "rher92@test.com" in data["email"]


def test_single_user_incorrect_id(test_app, test_database):
    client = test_app.test_client()

    response = client.get("/users/9302")
    data = json.loads(response.data.decode())

    assert response.status_code == 404
    assert "User 9302 does not exist" in data["message"]


def test_get_all_users(test_app, test_database, add_user):
    test_database.session.query(User).delete()
    add_user("pako", "pako@test.com")
    add_user("roger", "rher92@test.com")
    client = test_app.test_client()

    response = client.get("/users")
    data = json.loads(response.data.decode())

    assert response.status_code == 200
    assert len(data) == 2
    assert "pako" in data[0]["username"]
    assert "pako@test.com" in data[0]["email"]
    assert "3" in str(data[0]["id"])
    assert "roger" in data[1]["username"]
    assert "rher92@test.com" in data[1]["email"]
    assert "4" in str(data[1]["id"])
