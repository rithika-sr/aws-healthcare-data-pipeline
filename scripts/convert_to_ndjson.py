import json
import os
import glob

# Get project paths
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
json_dir = os.path.join(project_root, 'facility_json_files')

print(f"🔄 Converting JSON files to NDJSON format...\n")

converted = 0
for json_file in sorted(glob.glob(os.path.join(json_dir, '*.json'))):
    try:
        # Read the pretty-printed JSON
        with open(json_file, 'r') as f:
            data = json.load(f)
        
        # Write as single-line JSON (NDJSON)
        with open(json_file, 'w') as f:
            json.dump(data, f, separators=(',', ':'))
        
        converted += 1
        if converted % 50 == 0:
            print(f"  ✓ Converted {converted} files...")
            
    except Exception as e:
        print(f"  ❌ Error with {os.path.basename(json_file)}: {e}")

print(f"\n✅ Converted {converted} files to NDJSON format")
print(f"📁 Files are now single-line JSON (compact format)")
print(f"\n💡 Next: Re-upload to S3")