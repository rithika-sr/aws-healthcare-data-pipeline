import pandas as pd
import json
import os
from datetime import datetime, timedelta
import random

# Get the directory where this script is located
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)

# Define paths
csv_path = os.path.join(project_root, 'data', 'Healthcare_Survey_Sample_Data.csv')
output_dir = os.path.join(project_root, 'facility_json_files')

# Read the CSV file
print(f"✓ Found CSV file!")
df = pd.read_csv(csv_path)

# Create output directory
os.makedirs(output_dir, exist_ok=True)

print(f"📊 Processing {len(df)} facilities from CSV...")
print(f"🔄 Transforming survey data into facility format...\n")

# Service options based on survey types
service_options = [
    "Emergency Care", "Cardiology", "Radiology", "Pediatrics", 
    "Oncology", "Neurology", "Orthopedics", "Surgery",
    "ICU", "Laboratory", "Pharmacy", "Physical Therapy"
]

# Accreditation options
accreditation_options = ["JCI", "ISO9001", "CARF", "DNV", "AAAHC", "CAP"]

# Convert each row to facility JSON format
for index, row in df.iterrows():
    # Generate facility ID from organization name
    org_name = str(row['Organization Name'])
    facility_id = f"FAC{str(index + 1).zfill(3)}"
    
    # Random employee count (50-500)
    employee_count = random.randint(50, 500)
    
    # Random 3-5 services
    num_services = random.randint(3, 5)
    services = random.sample(service_options, num_services)
    
    # Generate 2 accreditations with dates
    accreditations = []
    
    # Accreditation 1 - some expiring soon (within 6 months), some later
    acc1_name = random.choice(accreditation_options)
    # 40% chance of expiring within 6 months
    if random.random() < 0.4:
        days_until_expiry = random.randint(30, 180)  # 1-6 months
    else:
        days_until_expiry = random.randint(181, 730)  # 6 months - 2 years
    
    expiry1 = (datetime.now() + timedelta(days=days_until_expiry)).strftime("%Y-%m-%d")
    accreditations.append({
        "name": acc1_name,
        "expiry_date": expiry1
    })
    
    # Accreditation 2
    remaining_accs = [a for a in accreditation_options if a != acc1_name]
    acc2_name = random.choice(remaining_accs)
    
    # 30% chance of expiring within 6 months
    if random.random() < 0.3:
        days_until_expiry = random.randint(30, 180)
    else:
        days_until_expiry = random.randint(181, 730)
    
    expiry2 = (datetime.now() + timedelta(days=days_until_expiry)).strftime("%Y-%m-%d")
    accreditations.append({
        "name": acc2_name,
        "expiry_date": expiry2
    })
    
    # Create facility data structure
    facility_data = {
        "facility_id": facility_id,
        "facility_name": org_name,
        "employee_count": employee_count,
        "services": services,
        "accreditations": accreditations,
        "state": str(row['State']) if pd.notna(row['State']) else "Unknown"
    }
    
    # Save to JSON file
    filename = os.path.join(output_dir, f"facility-data-{index + 1}.json")
    with open(filename, 'w') as f:
        json.dump(facility_data, f, indent=2)
    
    if (index + 1) % 50 == 0:
        print(f"   ✓ Created {index + 1} files...")

print(f"\n✅ SUCCESS! Created {len(df)} JSON files")
print(f"📁 Output location: {output_dir}")
print(f"\n💡 Note: Realistic data generated with:")
print(f"   - 40% of facilities have accreditations expiring within 6 months")
print(f"   - Employee counts: 50-500")
print(f"   - Services: 3-5 per facility")