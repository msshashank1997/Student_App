// JavaScript for handling student data on the frontend

document.addEventListener('DOMContentLoaded', function() {
    // Load students when the page loads
    loadStudents();
    
    // Add event listener for the refresh button if it exists
    const refreshButton = document.getElementById('refresh-students');
    if (refreshButton) {
        refreshButton.addEventListener('click', loadStudents);
    }
    
    // Add event listener for the add student form if it exists
    const addStudentForm = document.getElementById('add-student-form');
    if (addStudentForm) {
        addStudentForm.addEventListener('submit', addStudent);
    }
});

/**
 * Load students from API and display them
 */
function loadStudents() {
    const studentsList = document.getElementById('students-list');
    if (!studentsList) return;
    
    // Show loading state
    studentsList.innerHTML = '<p>Loading students...</p>';
    
    fetch('/api/students')
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(students => {
            displayStudents(students);
        })
        .catch(error => console.error('Error loading students:', error));
}

/**
 * Display students in the DOM
 */
function displayStudents(students) {
    const studentsList = document.getElementById('students-list');
    if (!studentsList) return;
    
    if (students.length === 0) {
        studentsList.innerHTML = '<p>No students found.</p>';
        return;
    }
    
    let html = '<table class="table"><thead><tr>' +
        '<th>ID</th>' +
        '<th>First Name</th>' +
        '<th>Last Name</th>' +
        '<th>Date of Birth</th>' +
        '<th>Class</th>' +
        '<th>Session</th>' +
        '<th>Actions</th>' +
        '</tr></thead><tbody>';
        
    students.forEach(student => {
        html += `<tr>
            <td>${student.id}</td>
            <td>${student.first_name}</td>
            <td>${student.last_name}</td>
            <td>${student.dob}</td>
            <td>${student.class}</td>
            <td>${student.session}</td>
            <td>
                <button onclick="viewStudent('${student.id}')" class="btn btn-info btn-sm">View</button>
                <button onclick="deleteStudent('${student.id}')" class="btn btn-danger btn-sm">Delete</button>
            </td>
        </tr>`;
    });
    
    html += '</tbody></table>';
    studentsList.innerHTML = html;
}

/**
 * Delete a student
 */
function deleteStudent(id) {
    if (confirm('Are you sure you want to delete this student?')) {
        fetch(`/api/students/${id}`, {
            method: 'DELETE'
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            alert('Student deleted successfully');
            loadStudents(); // Reload the list
        })
        .catch(error => console.error('Error deleting student:', error));
    }
}

/**
 * View student details
 */
function viewStudent(id) {
    fetch(`/api/students/${id}`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(student => {
            // Show student details (could be in a modal)
            alert(`Student Details:\n
                ID: ${student.id}\n
                Name: ${student.first_name} ${student.last_name}\n
                DOB: ${student.dob}\n
                Class: ${student.class}\n
                Session: ${student.session}`);
        })
        .catch(error => console.error('Error loading student details:', error));
}
