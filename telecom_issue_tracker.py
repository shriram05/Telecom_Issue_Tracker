from database import Database
from models import Customer, Technician, Complaint, Assignment
from utils import clear_screen, validate_phone, get_expertise_options, get_issue_type_options, get_status_filter_options
from tabulate import tabulate

class TelecomIssueTracker:
    def __init__(self, host="localhost", user="root", password="shriram2003", database="telecom_tracker"):
        """Initialize the Telecom Issue Tracker application"""
        # Connect to database
        self.db = Database(host, user, password, database)      
        # Initialize models
        self.customer = Customer(self.db)
        self.technician = Technician(self.db)
        self.complaint = Complaint(self.db)
        self.assignment = Assignment(self.db)
        
    def register_customer(self):
        """Register a new customer"""
        clear_screen()
        print("\n===== CUSTOMER REGISTRATION =====")
        name = input("Enter customer name: ")
        # Validate phone number
        while True:
            phone = input("Enter phone number: ")
            if validate_phone(phone):
                break
            print("Invalid phone number. Please enter at least 10 digits.")
        
        email = input("Enter email (optional): ")
        address = input("Enter address: ")
        try:
            self.customer.register(name, phone, email, address)
            print("\nCustomer registered successfully!")
            customer_data = self.customer.get_by_phone(phone)
            if customer_data:
                customer_id, customer_name = customer_data
                print(f"Customer ID: {customer_id}")
                print(f"Name: {customer_name}")
                print(f"Phone: {phone}")      
        except Exception as e:
            if "Duplicate entry" in str(e):
                print("\nError: This phone number is already registered.")
            else:
                print(f"\nError: {e}")
        
        input("\nPress Enter to continue...")

    def register_technician(self):
        """Register a new technician"""
        clear_screen()
        print("\n===== TECHNICIAN REGISTRATION =====")
        name = input("Enter technician name: ")
        # Validate phone number
        while True:
            phone = input("Enter phone number: ")
            if validate_phone(phone):
                break
            print("Invalid phone number. Please enter at least 10 digits.")
        email = input("Enter email (optional): ")
        location = input("Enter location/service area: ")
        print("\nExpertise options:")
        print("1. Network Infrastructure")
        print("2. Mobile Services")
        print("3. Internet Services")
        print("4. General Troubleshooting")
        while True:
            choice = input("Select expertise (1-4): ")
            if choice in ["1", "2", "3", "4"]:
                break
            print("Invalid choice. Please select 1-4.")
        expertise_map = get_expertise_options()
        expertise = expertise_map[choice]
        try:
            self.technician.register(name, phone, email, location, expertise)
            print("\nTechnician registered successfully!")
            
            # Get the technician ID by querying the database
            self.db.execute_query("SELECT tech_id FROM technicians WHERE phone = %s", (phone,))
            tech_id = self.db.cursor.fetchone()[0]
            
            print(f"Technician ID: {tech_id}")
            print(f"Name: {name}")
            print(f"Location: {location}")
            print(f"Expertise: {expertise}")       
        except Exception as e:
            if "Duplicate entry" in str(e):
                print("\nError: This phone number is already registered.")
            else:
                print(f"\nError: {e}")
        
        input("\nPress Enter to continue...")

    def log_complaint(self):
        """Log a new customer complaint"""
        clear_screen()
        print("\n===== LOG NETWORK COMPLAINT =====")
        # Check if customer exists
        customer_phone = input("Enter customer phone number: ")
        customer = self.customer.get_by_phone(customer_phone)
        if not customer:
            print("\nCustomer not found. Please register the customer first.")
            input("\nPress Enter to continue...")
            return
        customer_id, customer_name = customer
        print(f"\nCustomer found: {customer_name} (ID: {customer_id})")
        # Issue type selection
        print("\nIssue Types:")
        print("1. Call Drop")
        print("2. Slow Internet")
        print("3. No Signal")
        print("4. Other")
        while True:
            choice = input("Select issue type (1-4): ")
            if choice in ["1", "2", "3", "4"]:
                break
            print("Invalid choice. Please select 1-4.")
        issue_map = get_issue_type_options()
        issue_type = issue_map[choice]
        description = input("Enter detailed description of the issue: ")
        location = input("Enter location where issue is occurring: ")
        try:
            complaint_id = self.complaint.log(customer_id, issue_type, description, location)
            print(f"\nComplaint logged successfully with ID: {complaint_id}")
            print("Status: Open")
        except Exception as e:
            print(f"\nError: {e}")

        input("\nPress Enter to continue...")

    def assign_technician(self):
        """Assign a technician to an open complaint"""
        clear_screen()
        print("\n===== ASSIGN TECHNICIAN TO COMPLAINT =====")
        # Get open complaints
        open_complaints = self.complaint.get_open()
        if not open_complaints:
            print("\nNo open complaints to assign.")
            input("\nPress Enter to continue...")
            return
        print("\nOpen Complaints:")
        headers = ["ID", "Customer", "Issue Type", "Location", "Created At"]
        print(tabulate(open_complaints, headers=headers, tablefmt="grid"))
        complaint_id = input("\nEnter Complaint ID to assign: ")
        # Validate complaint ID
        try:
            complaint_id = int(complaint_id)
            
            # Check if complaint exists and is open
            query = """
            SELECT c.issue_type, c.location
            FROM complaints c
            WHERE c.complaint_id = %s AND c.status = 'Open'
            """
            complaint_info = self.db.fetch_one(query, (complaint_id,))
            
            if not complaint_info:
                print("\nComplaint not found or already assigned.")
                input("\nPress Enter to continue...")
                return
            issue_type, location = complaint_info
            # Find available technicians
            available_techs = self.technician.get_available()
            if not available_techs:
                print("\nNo available technicians at the moment.")
                input("\nPress Enter to continue...")
                return
            print("\nAvailable Technicians:")
            headers = ["ID", "Name", "Expertise", "Location"]
            print(tabulate(available_techs, headers=headers, tablefmt="grid"))
            tech_id = input("\nEnter Technician ID to assign: ")
            try:
                tech_id = int(tech_id)
                # Verify technician exists and is available
                tech_info = self.technician.get_by_id(tech_id)
                if not tech_info:
                    print("\nTechnician not found.")
                    input("\nPress Enter to continue...")
                    return
                tech_name, availability = tech_info
                
                if not availability:
                    print("\nTechnician is not available.")
                    input("\nPress Enter to continue...")
                    return        
                # Create assignment
                self.assignment.create(complaint_id, tech_id)
                # Update complaint status
                self.complaint.update_status(complaint_id, "Assigned")
                # Update technician availability
                self.technician.update_availability(tech_id, 0)
                print(f"\nComplaint #{complaint_id} successfully assigned to {tech_name}.")
            except ValueError:
                print("\nInvalid Technician ID. Please enter a number.")
        except ValueError:
            print("\nInvalid Complaint ID. Please enter a number.")
        
        input("\nPress Enter to continue...")

    def update_complaint_status(self):
        """Update the status of a complaint"""
        clear_screen()
        print("\n===== UPDATE COMPLAINT STATUS =====")
        # Get assigned/in-progress complaints
        active_complaints = self.complaint.get_active()
        if not active_complaints:
            print("\nNo active complaints to update.")
            input("\nPress Enter to continue...")
            return
        print("\nActive Complaints:")
        headers = ["ID", "Customer", "Issue Type", "Status", "Technician", "Assigned At"]
        print(tabulate(active_complaints, headers=headers, tablefmt="grid"))
        complaint_id = input("\nEnter Complaint ID to update: ")
        try:
            complaint_id = int(complaint_id)
            complaint_info = self.complaint.get_by_id_with_tech(complaint_id)
            if not complaint_info:
                print("\nComplaint not found or cannot be updated.")
                input("\nPress Enter to continue...")
                return
            current_status, tech_id, tech_name = complaint_info
            print(f"\nComplaint #{complaint_id}")
            print(f"Current Status: {current_status}")
            print(f"Assigned Technician: {tech_name}")
            print("\nSelect new status:")
            if current_status == "Assigned":
                print("1. In Progress")
                print("2. Resolved")
                valid_choices = ["1", "2"]
            else:  # In Progress
                print("1. Resolved")
                valid_choices = ["1"]
            while True:
                choice = input("\nEnter choice: ")
                if choice in valid_choices:
                    break
                print("Invalid choice. Please try again.")
            if current_status == "Assigned" and choice == "1":
                new_status = "In Progress"
                resolution_notes = None
            else:
                new_status = "Resolved"
                resolution_notes = input("Enter resolution notes: ")
                # Update technician availability
                self.technician.update_availability(tech_id, 1)
                # Update assignment with resolution details
                self.assignment.update_resolution(complaint_id, tech_id, resolution_notes)
            # Update complaint status
            self.complaint.update_status(complaint_id, new_status)
            print(f"\nComplaint status updated to {new_status} successfully.")
        except ValueError:
            print("\nInvalid Complaint ID. Please enter a number.")
        
        input("\nPress Enter to continue...")

    def view_all_complaints(self):
        """View all complaints in the system"""
        clear_screen()
        print("\n===== VIEW ALL COMPLAINTS =====")
        print("\nFilter by status:")
        print("1. All Complaints")
        print("2. Open")
        print("3. Assigned")
        print("4. In Progress")
        print("5. Resolved")
        choice = input("\nEnter choice (1-5): ")
        status_filter = get_status_filter_options()
        status = status_filter.get(choice, None)
        complaints = self.complaint.get_with_filter(status)
        if not complaints:
            print("\nNo complaints found with the selected filter.")
            input("\nPress Enter to continue...")
            return
        headers = ["ID", "Customer", "Issue Type", "Description", "Location", "Status", "Created At", "Technician"]
        print("\n" + tabulate(complaints, headers=headers, tablefmt="grid"))
        # Option to view detailed information about a specific complaint
        view_detail = input("\nEnter Complaint ID to view details (or press Enter to go back): ")
        if view_detail.strip():
            try:
                complaint_id = int(view_detail)
                self.view_complaint_details(complaint_id)
            except ValueError:
                print("\nInvalid Complaint ID.")
                
        input("\nPress Enter to continue...")

    def view_complaint_details(self, complaint_id):
        """View detailed information about a specific complaint"""
        clear_screen()
        print(f"\n===== COMPLAINT #{complaint_id} DETAILS =====")
        # Get complaint details
        complaint = self.complaint.get_details(complaint_id)
        if not complaint:
            print("\nComplaint not found.")
            return
        # Format complaint information
        print(f"Complaint ID: {complaint[0]}")
        print(f"Customer: {complaint[1]} (Phone: {complaint[2]})")
        print(f"Issue Type: {complaint[3]}")
        print(f"Description: {complaint[4]}")
        print(f"Location: {complaint[5]}")
        print(f"Status: {complaint[6]}")
        print(f"Created: {complaint[7]}")
        print(f"Last Updated: {complaint[8]}")
        # Get assignment information if available
        assignment = self.assignment.get_details(complaint_id)
        if assignment:
            print("\nAssignment Information:")
            print(f"Technician: {assignment[0]} (Phone: {assignment[1]})")
            print(f"Expertise: {assignment[2]}")
            print(f"Assigned At: {assignment[3]}")
            if assignment[4]:  # If resolution notes exist
                print(f"\nResolution Notes: {assignment[4]}")
                print(f"Resolved At: {assignment[5]}")

    def main_menu(self):
        """Display the main menu and handle user choices"""
        while True:
            clear_screen()
            print("\n===== TELECOM NETWORK ISSUE TRACKER =====")
            print("1. Register New Customer")
            print("2. Register New Technician")
            print("3. Log New Complaint")
            print("4. Assign Technician to Complaint")
            print("5. Update Complaint Status")
            print("6. View All Complaints")
            print("7. Exit")
            choice = input("\nEnter your choice (1-7): ")
            if choice == '1':
                self.register_customer()
            elif choice == '2':
                self.register_technician()
            elif choice == '3':
                self.log_complaint()
            elif choice == '4':
                self.assign_technician()
            elif choice == '5':
                self.update_complaint_status()
            elif choice == '6':
                self.view_all_complaints()
            elif choice == '7':
                self.close_connection()
                print("\nThank you for using the Telecom Network Issue Tracker!")
                print("Exiting the system...\n")
                break
            else:
                print("\nInvalid choice. Please try again.")
                input("\nPress Enter to continue...")

    def close_connection(self):
        """Close the database connection"""
        self.db.close()


if __name__ == "__main__":
    print("Starting Telecom Network Issue Tracker...")
    
    # You can modify these parameters to match your MySQL configuration
    tracker = TelecomIssueTracker(
        host="localhost",
        user="root",
        password="shriram2003",
        database="telecom_tracker"
    )
    
    tracker.main_menu()