import json
import boto3
import time
import os
from datetime import datetime

# Initialize AWS clients
s3_client = boto3.client('s3')
athena_client = boto3.client('athena')

# Configuration from environment variables
ATHENA_DATABASE = os.environ.get('ATHENA_DATABASE', 'healthcare_pipeline')
ATHENA_OUTPUT_LOCATION = os.environ.get('ATHENA_OUTPUT_LOCATION', 's3://healthcare-accreditation-data-pipeline/athena-results/')
ATHENA_WORKGROUP = os.environ.get('ATHENA_WORKGROUP', 'primary')

def lambda_handler(event, context):
    """
    Lambda function triggered by S3 upload events.
    Executes Athena query to count accredited facilities per state.
    """
    
    print(f"Lambda function invoked at {datetime.now()}")
    print(f"Event: {json.dumps(event)}")
    
    try:
        # Extract S3 event details
        for record in event['Records']:
            bucket_name = record['s3']['bucket']['name']
            object_key = record['s3']['object']['key']
            
            print(f"New file uploaded: s3://{bucket_name}/{object_key}")
            
            # Only process JSON files from raw folder
            if not object_key.startswith('raw/') or not object_key.endswith('.json'):
                print(f"Skipping non-JSON or non-raw file: {object_key}")
                continue
            
            # Execute Athena query
            query_execution_id = execute_athena_query()
            
            # Wait for query completion
            query_status = wait_for_query_completion(query_execution_id)
            
            if query_status == 'SUCCEEDED':
                print(f"Query succeeded! Execution ID: {query_execution_id}")
                
                # Get query results
                results = get_query_results(query_execution_id)
                print(f"Query results: {json.dumps(results, indent=2)}")
                
                return {
                    'statusCode': 200,
                    'body': json.dumps({
                        'message': 'Athena query executed successfully',
                        'query_execution_id': query_execution_id,
                        'results': results
                    })
                }
            else:
                error_msg = f"Query failed with status: {query_status}"
                print(error_msg)
                return {
                    'statusCode': 500,
                    'body': json.dumps({'error': error_msg})
                }
                
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

def execute_athena_query():
    """
    Execute Athena query to count facilities per state
    """
    query = """
    SELECT 
        state,
        COUNT(*) as facility_count,
        COUNT(DISTINCT facility_id) as unique_facilities
    FROM facilities
    WHERE state IS NOT NULL
    GROUP BY state
    ORDER BY facility_count DESC;
    """
    
    print(f"Executing Athena query...")
    print(f"Database: {ATHENA_DATABASE}")
    print(f"Output location: {ATHENA_OUTPUT_LOCATION}")
    
    response = athena_client.start_query_execution(
        QueryString=query,
        QueryExecutionContext={
            'Database': ATHENA_DATABASE
        },
        ResultConfiguration={
            'OutputLocation': ATHENA_OUTPUT_LOCATION
        },
        WorkGroup=ATHENA_WORKGROUP
    )
    
    query_execution_id = response['QueryExecutionId']
    print(f"Query execution started: {query_execution_id}")
    
    return query_execution_id

def wait_for_query_completion(query_execution_id, max_wait_time=60):
    """
    Wait for Athena query to complete with timeout handling
    """
    print(f"Waiting for query completion...")
    
    start_time = time.time()
    
    while True:
        # Check if we've exceeded max wait time
        elapsed_time = time.time() - start_time
        if elapsed_time > max_wait_time:
            print(f"Query timeout after {elapsed_time:.2f} seconds")
            raise Exception(f"Query execution timeout after {max_wait_time} seconds")
        
        # Get query execution status
        response = athena_client.get_query_execution(
            QueryExecutionId=query_execution_id
        )
        
        status = response['QueryExecution']['Status']['State']
        print(f"Query status: {status} (elapsed: {elapsed_time:.2f}s)")
        
        if status in ['SUCCEEDED', 'FAILED', 'CANCELLED']:
            if status == 'FAILED':
                reason = response['QueryExecution']['Status'].get('StateChangeReason', 'Unknown')
                print(f"Query failed: {reason}")
            return status
        
        # Wait before checking again
        time.sleep(2)

def get_query_results(query_execution_id):
    """
    Retrieve results from completed Athena query
    """
    print(f"Retrieving query results...")
    
    response = athena_client.get_query_results(
        QueryExecutionId=query_execution_id,
        MaxResults=100
    )
    
    # Parse results
    results = []
    rows = response['ResultSet']['Rows']
    
    # Skip header row
    for row in rows[1:]:
        data = row['Data']
        results.append({
            'state': data[0].get('VarCharValue', 'N/A'),
            'facility_count': data[1].get('VarCharValue', '0'),
            'unique_facilities': data[2].get('VarCharValue', '0')
        })
    
    print(f"Retrieved {len(results)} result rows")
    return results