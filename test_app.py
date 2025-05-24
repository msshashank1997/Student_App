import pytest
from app import app, students_collection, add_student, get_students, get_student_by_id, delete_student
from bson import ObjectId
from datetime import datetime

@pytest.fixture(autouse=True)
def cleanup_db():
    # Clean up test data before each test
    students_collection.delete_many({})

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

def test_get_student_by_name(client):
    # Updated schema with new fields
    students_collection.insert_one({
        "first_name": "Alice",
        "last_name": "Smith",
        "dob": "2000-01-01",
        "class": "10",
        "session": "2023-2024",
        "created_date": datetime.now().strftime("%Y-%m-%d")
    })
    response = client.get('/api/students/name/Alice')
    assert response.status_code == 200
    assert len(response.json) > 0
    assert response.json[0]["name"] == "Alice"

def test_get_student_by_name_not_found(client):
    response = client.get('/api/students/name/NonExistentName')
    assert response.status_code == 404
    assert response.json["error"] == "No students found with the given name"

def test_add_student(client):
    # Updated student data with new required fields
    response = client.post('/api/students', json={
        "name": "Bob", 
        "dob": "2001-05-15",
        "class": "9",
        "session": "2023-2024"
    })
    assert response.status_code == 201
    assert response.json["name"] == "Bob"
    assert response.json["dob"] == "2001-05-15"
    assert response.json["class"] == "9"
    assert response.json["session"] == "2023-2024"

def test_get_all_students(client):
    # Updated schema for inserted test data
    students_collection.insert_one({
        "name": "TestUser", 
        "dob": "2002-03-20",
        "class": "11",
        "session": "2023-2024",
        "created_date": datetime.now().strftime("%Y-%m-%d")
    })
    response = client.get('/api/students')
    assert response.status_code == 200
    assert isinstance(response.json, list)
    assert len(response.json) > 0

def test_delete_student(client):
    # Updated schema for inserted test data
    student = students_collection.insert_one({
        "name": "Charlie", 
        "dob": "2003-07-22",
        "class": "12",
        "session": "2023-2024",
        "created_date": datetime.now().strftime("%Y-%m-%d")
    })
    response = client.delete(f'/api/students/{student.inserted_id}')
    assert response.status_code == 200
    assert response.json["message"] == "Deleted"

    # Ensure student is deleted
    response = client.get(f'/api/students/{student.inserted_id}')
    assert response.status_code == 404

def test_add_student_missing_fields(client):
    # Test missing required fields in new schema
    response = client.post('/api/students', json={"name": "Eve"})
    assert response.status_code == 400

def test_get_student_by_partial_name(client):
    # Updated schema for inserted test data
    students_collection.insert_one({
        "name": "Alice", 
        "dob": "2000-01-01",
        "class": "10",
        "session": "2023-2024",
        "created_date": datetime.now().strftime("%Y-%m-%d")
    })
    response = client.get('/api/students/name/Ali')
    assert response.status_code == 200
    assert any("Alice" in s["name"] for s in response.json)
