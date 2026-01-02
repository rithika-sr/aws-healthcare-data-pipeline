import json
import os
import glob

# Get project paths
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
json_dir = os.path.join(project_root, 'facility_json_files')

print(f"🔍 Validating JSON files in: {json_dir}\n")

valid_files = []
invalid_files = []
total_files = 0

# Check all JSON files
for json_file in sorted(glob.glob(os.path.join(json_dir, '*.json'))):
    total_files += 1
    filename = os.path.basename(json_file)
    
    try:
        with open(json_file, 'r') as f:
            data = json.load(f)
            
        # Validate required fields exist
        required_fields = ['facility_id', 'facility_name', 'employee_count', 
                          'services', 'accreditations', 'state']
        
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            invalid_files.append((filename, f"Missing fields: {missing_fields}"))
        else:
            valid_files.append(filename)
            
    except json.JSONDecodeError as e:
        invalid_files.append((filename, f"JSON Error: {str(e)}"))
    except Exception as e:
        invalid_files.append((filename, f"Error: {str(e)}"))

# Print results
print(f"📊 VALIDATION RESULTS:")
print(f"=" * 60)
print(f"✅ Valid files: {len(valid_files)}/{total_files}")
print(f"❌ Invalid files: {len(invalid_files)}/{total_files}")

if invalid_files:
    print(f"\n❌ INVALID FILES:")
    print(f"=" * 60)
    for filename, error in invalid_files:
        print(f"  • {filename}: {error}")
    
    print(f"\n🗑️  DELETE INVALID FILES? (y/n): ", end='')
    response = input().lower()
    
    if response == 'y':
        for filename, error in invalid_files:
            filepath = os.path.join(json_dir, filename)
            os.remove(filepath)
            print(f"  ✓ Deleted: {filename}")
        print(f"\n✅ Deleted {len(invalid_files)} invalid files")
        print(f"📁 {len(valid_files)} valid files remaining")
    else:
        print(f"\n⚠️  No files deleted")
else:
    print(f"\n✅ All files are valid!")

print(f"\n💡 Next step: Re-upload files to S3 if any were deleted")