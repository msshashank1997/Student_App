from flask import Flask, jsonify, request, render_template
from pymongo import MongoClient

from datetime import datetime

# Initialize Flask app
app = Flask(__name__)

# Connect to MongoDB
client = MongoClient("mongodb+srv://demoteam88:3WwsOsXTmCfG1PLE@cluster0.gdzal.mongodb.net/")  # Replace with your MongoDB URI
db = client["student_db"]  # Database name
students_collection = db["students"]  # Collection name

# Database functions
def add_student(data):
    student = {
        "name": data["name"],
        "dob": data["dob"],
        "class": data["class"],
        "session": data["session"],
        "created_date": datetime.now().strftime("%Y-%m-%d")
    }
    result = students_collection.insert_one(student)
    student["_id"] = str(result.inserted_id)  # Convert ObjectId to string
    return student

def get_students():
    return [{
        "_id": str(student["_id"]), 
        "name": student["name"], 
        "dob": student.get("dob", ""),
        "class": student.get("class", ""),
        "session": student.get("session", ""),
        "created_date": student.get("created_date", "")
    } for student in students_collection.find()]

def get_student_by_id(student_id):
    from bson.objectid import ObjectId
    student = students_collection.find_one({"_id": ObjectId(student_id)})
    if student:
        return {
            "_id": str(student["_id"]), 
            "name": student["name"], 
            "dob": student.get("dob", ""),
            "class": student.get("class", ""),
            "session": student.get("session", ""),
            "created_date": student.get("created_date", "")
        }
    return None

def delete_student(student_id):
    from bson.objectid import ObjectId
    result = students_collection.delete_one({"_id": ObjectId(student_id)})
    if result.deleted_count > 0:
        return {"message": "Student deleted successfully"}
    return {"error": "Student not found"}
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
    if "name" not in data or "age" not in data:
        return jsonify({"error": "Missing 'name' or 'age'"}), 400
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
    # Use regex to find students by name
    students = students_collection.find({"name": {"$regex": f".*{name}.*", "$options": "i"}})
    students_list = [{"_id": str(student["_id"]), "name": student["name"], "age": student["age"]} for student in students]
    if students_list:
        return jsonify(students_list), 200
    return jsonify({"error": "No students found with the given name"}), 404

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
