from flask import Flask, jsonify, request, render_template
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
import sys
from datetime import datetime

# Initialize Flask app
app = Flask(__name__)

# Connect to MongoDB with error handling
try:
    client = MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=5000)
    # Verify connection is successful
    client.server_info()
    db = client["student_db"]  # Database name
    students_collection = db["students"]  # Collection name
    print("Successfully connected to MongoDB")
except (ConnectionFailure, ServerSelectionTimeoutError) as e:
    print(f"Failed to connect to MongoDB: {e}")
    sys.exit(1)

# Database functions
def add_student(data):
    student = {
        "first_name": data["first_name"],
        "last_name": data["last_name"],
        "dob": data["dob"],
        "class": data["class"],
        "session": data["session"],
        "created_date": datetime.now().strftime("%Y-%m-%d")
    }
    result = students_collection.insert_one(student)
    student["_id"] = str(result.inserted_id)  # Convert ObjectId to string
    return student

def get_students():
    students = []
    for student in students_collection.find():
        students.append({
            "id": str(student["_id"]),
            # Replace name field with first_name and last_name
            "first_name": student["first_name"],
            "last_name": student["last_name"],
            "dob": student["dob"],
            "class": student["class"],
            "session": student["session"],
            "created_date": student.get("created_date", "")
        })
    return students

def get_student_by_id(student_id):
    from bson.objectid import ObjectId
    student = students_collection.find_one({"_id": ObjectId(student_id)})
    if student:
        return {
            "id": str(student["_id"]),
            # Replace name field with first_name and last_name
            "first_name": student["first_name"],
            "last_name": student["last_name"],
            "dob": student["dob"],
            "class": student["class"],
            "session": student["session"],
            "created_date": student.get("created_date", "")
        }
    return None

def delete_student(student_id):
    from bson.objectid import ObjectId
    result = students_collection.delete_one({"_id": ObjectId(student_id)})
    if result.deleted_count > 0:
        return {"message": "Student deleted successfully"}
    return {"error": "Student not found"}, 404
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/web/students')
def students_page():
    return render_template('students.html')

@app.route('/web/add_student')
def add_student_page():
    return render_template('add_student.html')

# API routes
@app.route('/api/students', methods=['POST'])
def add():
    data = request.get_json()
    if "first_name" not in data or "last_name" not in data or "dob" not in data or "class" not in data or "session" not in data:
        return jsonify({"error": "Missing required fields"}), 400
    return jsonify(add_student(data)), 201

@app.route('/api/students', methods=['GET'])
def get_all():
    return jsonify(get_students()), 200

@app.route('/api/students/<string:student_id>', methods=['GET'])
def get_by_id(student_id):
    student = get_student_by_id(student_id)
    if student:
        return jsonify(student), 200
    return jsonify({"error": "Student not found"}), 404

@app.route('/api/students/<string:student_id>', methods=['DELETE'])
def delete(student_id):
    return jsonify(delete_student(student_id)), 200

@app.route('/api/students/name/<string:name>', methods=['GET'])
def get_by_name(name):
    # Update to search in both first_name and last_name fields
    students = list(students_collection.find({
        "$or": [
            {"first_name": {"$regex": name, "$options": "i"}},
            {"last_name": {"$regex": name, "$options": "i"}}
        ]
    }))
    
    if not students:
        return {"error": "No students found with the given name"}, 404
    
    # Format the response
    formatted_students = []
    for student in students:
        formatted_students.append({
            "id": str(student["_id"]),
            "first_name": student["first_name"],
            "last_name": student["last_name"],
            "dob": student["dob"],
            "class": student["class"],
            "session": student["session"],
            "created_date": student.get("created_date", "")
        })
    
    return jsonify(formatted_students)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
