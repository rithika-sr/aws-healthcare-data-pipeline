import boto3
import json
import logging
from datetime import datetime, timedelta
from botocore.exceptions import ClientError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# AWS Configuration
BUCKET_NAME = 'healthcare-accreditation-data-pipeline'
RAW_PREFIX = 'raw/'
PROCESSED_PREFIX = 'processed/'

# Date Configuration
TODAY = datetime(2026, 1, 1)  # Current date: January 1, 2026
SIX_MONTHS_FROM_NOW = TODAY + timedelta(days=180)

def parse_date(date_string):
    """Parse date string in YYYY-MM-DD format"""
    try:
        return datetime.strptime(date_string, '%Y-%m-%d')
    except ValueError as e:
        logger.warning(f"Invalid date format: {date_string} - {e}")
        return None

def has_expiring_accreditation(facility):
    """
    Check if facility has any accreditation expiring within 6 months
    """
    accreditations = facility.get('accreditations', [])
    
    for accreditation in accreditations:
        expiry_date_str = accreditation.get('expiry_date')
        if not expiry_date_str:
            continue
            
        expiry_date = parse_date(expiry_date_str)
        if not expiry_date:
            continue
            
        # Check if expiry is within 6 months
        if TODAY <= expiry_date <= SIX_MONTHS_FROM_NOW:
            logger.debug(f"Facility {facility.get('facility_id')} has expiring accreditation: "
                        f"{accreditation.get('name')} expires on {expiry_date_str}")
            return True
    
    return False

def process_facilities():
    """
    Main function to read, filter, and write facility data
    """
    # Initialize S3 client
    s3_client = boto3.client('s3')
    
    logger.info(f"Starting facility processing...")
    logger.info(f"Bucket: {BUCKET_NAME}")
    logger.info(f"Date range: {TODAY.strftime('%Y-%m-%d')} to {SIX_MONTHS_FROM_NOW.strftime('%Y-%m-%d')}")
    
    processed_count = 0
    expiring_count = 0
    error_count = 0
    
    try:
        # List all JSON files in raw folder
        logger.info(f"Listing objects in {RAW_PREFIX}...")
        response = s3_client.list_objects_v2(
            Bucket=BUCKET_NAME,
            Prefix=RAW_PREFIX
        )
        
        if 'Contents' not in response:
            logger.error(f"No files found in {RAW_PREFIX}")
            return
        
        json_files = [obj for obj in response['Contents'] if obj['Key'].endswith('.json')]
        logger.info(f"Found {len(json_files)} JSON files to process")
        
        # Process each file
        for obj in json_files:
            file_key = obj['Key']
            
            try:
                # Read JSON file from S3
                logger.debug(f"Reading {file_key}...")
                response = s3_client.get_object(Bucket=BUCKET_NAME, Key=file_key)
                file_content = response['Body'].read().decode('utf-8')
                facility = json.loads(file_content)
                
                processed_count += 1
                
                # Check if facility has expiring accreditation
                if has_expiring_accreditation(facility):
                    expiring_count += 1
                    facility_id = facility.get('facility_id', 'unknown')
                    
                    # Write to processed folder
                    output_key = f"{PROCESSED_PREFIX}expiring-{facility_id}.json"
                    
                    s3_client.put_object(
                        Bucket=BUCKET_NAME,
                        Key=output_key,
                        Body=json.dumps(facility, separators=(',', ':')),
                        ContentType='application/json'
                    )
                    
                    logger.info(f"✓ Filtered: {facility_id} - {facility.get('facility_name')}")
                
                # Progress indicator
                if processed_count % 50 == 0:
                    logger.info(f"Progress: {processed_count}/{len(json_files)} files processed, "
                              f"{expiring_count} with expiring accreditations")
                    
            except ClientError as e:
                error_count += 1
                logger.error(f"AWS Error processing {file_key}: {e}")
            except json.JSONDecodeError as e:
                error_count += 1
                logger.error(f"JSON Error processing {file_key}: {e}")
            except Exception as e:
                error_count += 1
                logger.error(f"Unexpected error processing {file_key}: {e}")
        
        # Final summary
        logger.info("=" * 70)
        logger.info("PROCESSING COMPLETE")
        logger.info("=" * 70)
        logger.info(f"Total files processed: {processed_count}")
        logger.info(f"Facilities with expiring accreditations: {expiring_count}")
        logger.info(f"Errors encountered: {error_count}")
        logger.info(f"Output location: s3://{BUCKET_NAME}/{PROCESSED_PREFIX}")
        logger.info("=" * 70)
        
    except ClientError as e:
        logger.error(f"Failed to list objects in S3: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in main process: {e}")
        raise

if __name__ == "__main__":
    try:
        process_facilities()
    except Exception as e:
        logger.error(f"Script failed: {e}")
        exit(1)