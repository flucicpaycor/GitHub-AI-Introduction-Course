from src import app as app_module


def test_root_redirects_to_static_index(client):
    # Arrange
    expected_location = "/static/index.html"

    # Act
    response = client.get("/", follow_redirects=False)

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == expected_location


def test_get_activities_returns_expected_structure(client):
    # Arrange
    expected_activity = "Chess Club"

    # Act
    response = client.get("/activities")
    payload = response.json()

    # Assert
    assert response.status_code == 200
    assert isinstance(payload, dict)
    assert expected_activity in payload
    assert {"description", "schedule", "max_participants", "participants"}.issubset(
        payload[expected_activity].keys()
    )


def test_signup_adds_participant_successfully(client):
    # Arrange
    activity_name = "Chess Club"
    student_email = "new-student@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": student_email})

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {student_email} for {activity_name}"
    assert student_email in app_module.activities[activity_name]["participants"]


def test_signup_returns_not_found_for_missing_activity(client):
    # Arrange
    missing_activity = "Nonexistent Club"
    student_email = "student@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{missing_activity}/signup",
        params={"email": student_email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_rejects_duplicate_participant(client):
    # Arrange
    activity_name = "Chess Club"
    existing_email = app_module.activities[activity_name]["participants"][0]

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": existing_email})

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_signup_rejects_when_activity_is_full(client):
    # Arrange
    activity_name = "Debate Team"
    max_participants = app_module.activities[activity_name]["max_participants"]
    app_module.activities[activity_name]["participants"] = [
        f"student{i}@mergington.edu" for i in range(max_participants)
    ]

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": "overflow@mergington.edu"},
    )

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Activity is full"


def test_signup_requires_email_query_param(client):
    # Arrange
    activity_name = "Chess Club"

    # Act
    response = client.post(f"/activities/{activity_name}/signup")
    payload = response.json()

    # Assert
    assert response.status_code == 422
    assert isinstance(payload.get("detail"), list)
    assert any(
        error.get("loc") == ["query", "email"] and error.get("type") == "missing"
        for error in payload["detail"]
    )


def test_unregister_removes_participant_successfully(client):
    # Arrange
    activity_name = "Chess Club"
    registered_email = app_module.activities[activity_name]["participants"][0]

    # Act
    response = client.post(
        f"/activities/{activity_name}/unregister",
        params={"email": registered_email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Unregistered {registered_email} from {activity_name}"
    assert registered_email not in app_module.activities[activity_name]["participants"]


def test_unregister_returns_not_found_for_missing_activity(client):
    # Arrange
    missing_activity = "Nonexistent Club"

    # Act
    response = client.post(
        f"/activities/{missing_activity}/unregister",
        params={"email": "student@mergington.edu"},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_returns_not_found_for_non_member(client):
    # Arrange
    activity_name = "Chess Club"
    non_member_email = "not-registered@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{activity_name}/unregister",
        params={"email": non_member_email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Student is not signed up for this activity"


def test_unregister_requires_email_query_param(client):
    # Arrange
    activity_name = "Chess Club"

    # Act
    response = client.post(f"/activities/{activity_name}/unregister")
    payload = response.json()

    # Assert
    assert response.status_code == 422
    assert isinstance(payload.get("detail"), list)
    assert any(
        error.get("loc") == ["query", "email"] and error.get("type") == "missing"
        for error in payload["detail"]
    )
