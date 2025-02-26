class Customer:
    def __init__(self, db):
        self.db = db
    
    def register(self, name, phone, email, address):
        """Register a new customer"""
        query = """
        INSERT INTO customers (name, phone, email, address)
        VALUES (%s, %s, %s, %s)
        """
        self.db.execute_query(query, (name, phone, email, address))
        self.db.commit()
    
    def get_by_phone(self, phone):
        """Get customer by phone number"""
        query = "SELECT customer_id, name FROM customers WHERE phone = %s"
        return self.db.fetch_one(query, (phone,))
    
    def get_by_id(self, customer_id):
        """Get customer by ID"""
        query = "SELECT * FROM customers WHERE customer_id = %s"
        return self.db.fetch_one(query, (customer_id,))


class Technician:
    def __init__(self, db):
        self.db = db
    
    def register(self, name, phone, email, location, expertise):
        """Register a new technician"""
        query = """
        INSERT INTO technicians (name, phone, email, location, expertise)
        VALUES (%s, %s, %s, %s, %s)
        """
        self.db.execute_query(query, (name, phone, email, location, expertise))
        self.db.commit()
    
    def get_by_id(self, tech_id):
        """Get technician by ID"""
        query = "SELECT name, availability FROM technicians WHERE tech_id = %s"
        return self.db.fetch_one(query, (tech_id,))
    
    def get_available(self):
        """Get all available technicians"""
        query = """
        SELECT tech_id, name, expertise, location
        FROM technicians
        WHERE availability = 1
        """
        return self.db.fetch_all(query)
    
    def update_availability(self, tech_id, available):
        """Update technician availability"""
        query = """
        UPDATE technicians
        SET availability = %s
        WHERE tech_id = %s
        """
        self.db.execute_query(query, (available, tech_id))
        self.db.commit()


class Complaint:
    def __init__(self, db):
        self.db = db
    
    def log(self, customer_id, issue_type, description, location):
        """Log a new complaint"""
        query = """
        INSERT INTO complaints (customer_id, issue_type, description, location, status)
        VALUES (%s, %s, %s, %s, 'Open')
        """
        self.db.execute_query(query, (customer_id, issue_type, description, location))
        self.db.commit()
        
        # Get the complaint ID
        return self.db.fetch_one("SELECT LAST_INSERT_ID()")[0]
    
    def get_open(self):
        """Get all open complaints"""
        query = """
        SELECT c.complaint_id, cu.name, c.issue_type, c.location, c.created_at
        FROM complaints c
        JOIN customers cu ON c.customer_id = cu.customer_id
        WHERE c.status = 'Open'
        ORDER BY c.created_at
        """
        return self.db.fetch_all(query)
    
    def get_active(self):
        """Get all active (assigned/in-progress) complaints"""
        query = """
        SELECT c.complaint_id, cu.name, c.issue_type, c.status, t.name, a.assigned_at
        FROM complaints c
        JOIN customers cu ON c.customer_id = cu.customer_id
        JOIN assignments a ON c.complaint_id = a.complaint_id
        JOIN technicians t ON a.tech_id = t.tech_id
        WHERE c.status IN ('Assigned', 'In Progress')
        ORDER BY a.assigned_at
        """
        return self.db.fetch_all(query)
    
    def get_by_id_with_tech(self, complaint_id):
        """Get complaint by ID with technician info"""
        query = """
        SELECT c.status, a.tech_id, t.name
        FROM complaints c
        JOIN assignments a ON c.complaint_id = a.complaint_id
        JOIN technicians t ON a.tech_id = t.tech_id
        WHERE c.complaint_id = %s AND c.status IN ('Assigned', 'In Progress')
        """
        return self.db.fetch_one(query, (complaint_id,))
    
    def get_with_filter(self, status=None):
        """Get complaints with optional status filter"""
        query = """
        SELECT c.complaint_id, cu.name, c.issue_type, c.description, c.location, 
               c.status, c.created_at, IFNULL(t.name, 'Unassigned') as technician
        FROM complaints c
        JOIN customers cu ON c.customer_id = cu.customer_id
        LEFT JOIN assignments a ON c.complaint_id = a.complaint_id
        LEFT JOIN technicians t ON a.tech_id = t.tech_id
        """
        
        if status:
            query += f"WHERE c.status = '{status}'"
        
        query += " ORDER BY c.created_at DESC"
        
        return self.db.fetch_all(query)
    
    def get_details(self, complaint_id):
        """Get detailed information about a complaint"""
        query = """
        SELECT c.complaint_id, cu.name as customer_name, cu.phone, c.issue_type, 
               c.description, c.location, c.status, c.created_at, c.updated_at
        FROM complaints c
        JOIN customers cu ON c.customer_id = cu.customer_id
        WHERE c.complaint_id = %s
        """
        return self.db.fetch_one(query, (complaint_id,))
    
    def update_status(self, complaint_id, status):
        """Update complaint status"""
        query = """
        UPDATE complaints
        SET status = %s
        WHERE complaint_id = %s
        """
        self.db.execute_query(query, (status, complaint_id))
        self.db.commit()


class Assignment:
    def __init__(self, db):
        self.db = db
    
    def create(self, complaint_id, tech_id):
        """Create a new assignment"""
        query = """
        INSERT INTO assignments (complaint_id, tech_id)
        VALUES (%s, %s)
        """
        self.db.execute_query(query, (complaint_id, tech_id))
        self.db.commit()
    
    def update_resolution(self, complaint_id, tech_id, notes):
        """Update assignment with resolution details"""
        query = """
        UPDATE assignments
        SET resolution_notes = %s, resolved_at = NOW()
        WHERE complaint_id = %s AND tech_id = %s
        """
        self.db.execute_query(query, (notes, complaint_id, tech_id))
        self.db.commit()
    
    def get_details(self, complaint_id):
        """Get assignment details for a complaint"""
        query = """
        SELECT t.name, t.phone, t.expertise, a.assigned_at, 
               a.resolution_notes, a.resolved_at
        FROM assignments a
        JOIN technicians t ON a.tech_id = t.tech_id
        WHERE a.complaint_id = %s
        """
        return self.db.fetch_one(query, (complaint_id,))