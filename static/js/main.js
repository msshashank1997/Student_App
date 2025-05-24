// Common JavaScript functions for the application

// Format dates in a user-friendly way
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString();
}

// Show/hide elements with animation
function toggleElement(element, show) {
    if (show) {
        element.style.display = 'block';
        setTimeout(() => {
            element.style.opacity = '1';
        }, 10);
    } else {
        element.style.opacity = '0';
        setTimeout(() => {
            element.style.display = 'none';
        }, 300);
    }
}

// Handle API errors
function handleApiError(error) {
    console.error('API Error:', error);
    // You could show a toast notification or alert here
}
