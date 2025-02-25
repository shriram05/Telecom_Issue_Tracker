import os

def clear_screen():
    """Clear the console screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def validate_phone(phone):
    """Validate phone number"""
    return len(phone) >= 10 and phone.isdigit()

def get_expertise_options():
    """Get expertise options map"""
    return {
        "1": "Network Infrastructure",
        "2": "Mobile Services",
        "3": "Internet Services",
        "4": "General Troubleshooting"
    }

def get_issue_type_options():
    """Get issue type options map"""
    return {
        "1": "Call Drop",
        "2": "Slow Internet",
        "3": "No Signal", 
        "4": "Other"
    }

def get_status_filter_options():
    """Get status filter options"""
    return {
        "2": "Open",
        "3": "Assigned",
        "4": "In Progress",
        "5": "Resolved"
    }