#!/usr/bin/env python3
"""
RC Pakistan Cargo & Logistics - Data Generator v1.0 (2022)
Legacy version with Python 3.8 compatibility
"""

import random
from datetime import datetime, timedelta
import csv

# Simple data generator for 2022 version
def generate_basic_data(records=100):
    """Generate basic logistics data - 2022 version"""
    
    customers = []
    bookings = []
    
    cities = ["Dubai", "Karachi", "Lahore", "Islamabad"]
    
    for i in range(records):
        # Simple customer record
        customer = {
            "id": i + 1,
            "name": f"Customer_{i+1}",
            "city": random.choice(cities),
            "created": datetime.now().strftime("%Y-%m-%d")
        }
        customers.append(customer)
        
        # Simple booking record
        booking = {
            "id": i + 1,
            "customer_id": i + 1,
            "origin": "Dubai",
            "destination": random.choice(["Karachi", "Lahore", "Islamabad"]),
            "weight": round(random.uniform(10, 500), 2),
            "date": datetime.now().strftime("%Y-%m-%d")
        }
        bookings.append(booking)
    
    return customers, bookings

if __name__ == "__main__":
    customers, bookings = generate_basic_data(500)
    print(f"Generated {len(customers)} customers and {len(bookings)} bookings")
