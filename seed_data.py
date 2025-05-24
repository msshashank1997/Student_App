from pymongo import MongoClient
from datetime import datetime, timedelta
import random


# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["student_db"]
students_collection = db["students"]

# Create the database if it doesn't exist
if "student_db" not in client.list_database_names():
    db = client.create_database("student_db")

# create the collection if it doesn't exist
if "students" not in db.list_collection_names():
    students_collection = db.create_collection("students")

# Clear existing data (optional)
students_collection.delete_many({})

# Generate random dates within a range
def random_date(start_date, end_date):
    time_between_dates = end_date - start_date
    days_between_dates = time_between_dates.days
    random_days = random.randrange(days_between_dates)
    return start_date + timedelta(days=random_days)

# Sample student data
first_names = ["James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda", "William", 
              "Elizabeth", "David", "Susan", "Richard", "Jessica", "Joseph", "Sarah", "Thomas", "Karen", 
              "Charles", "Nancy", "Aisha", "Mohammed", "Raj", "Priya", "Chen", "Yuki", "Sofia", "Diego"]

last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", 
             "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", 
             "Moore", "Jackson", "Martin", "Lee", "Patel", "Kim", "Nguyen", "Chen", "Wang", "Singh", "Gupta"]

# Academic sessions
sessions = ["2022-2023", "2023-2024", "2024-2025"]

# Create sample students
sample_students = []
today = datetime.now()

for i in range(50):  # Create 50 sample students
    dob = random_date(datetime(2000, 1, 1), datetime(2010, 12, 31))
    created = random_date(datetime(2022, 1, 1), today)
    
    first_name = random.choice(first_names)
    last_name = random.choice(last_names)
    
    student = {
        "first_name": first_name,
        "last_name": last_name,
        "dob": dob.strftime("%Y-%m-%d"),
        "class": str(random.randint(1, 12)),  # Classes 1 through 12
        "session": random.choice(sessions),
        "created_date": created.strftime("%Y-%m-%d")
    }
    sample_students.append(student)

# Insert the sample data
result = students_collection.insert_many(sample_students)

print(f"Successfully inserted {len(result.inserted_ids)} student records")
print("\n" + "="*80)
print(f"{'Name':<25} {'Date of Birth':<15} {'Class':<8} {'Academic Session':<15} {'Registration Date':<15}")
print("="*80)
for i, student in enumerate(sample_students[:10], 1):  # Show 10 examples
    print(f"{student['name']:<25} {student['dob']:<15} {student['class']:<8} {student['session']:<15} {student['created_date']:<15}")
print("="*80)
print("...")

# Display total count
count = students_collection.count_documents({})
print(f"\nTotal students in database: {count}")
print("\nFields for each student record:")
print("- Name")
print("- Date of Birth (DOB)")
print("- Class")
print("- Academic Session")
print("- Registration Date")
