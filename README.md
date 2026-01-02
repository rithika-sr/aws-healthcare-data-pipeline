# AWS Healthcare Accreditation Data Pipeline 

**AWS data engineering pipeline for healthcare facility accreditation tracking**

## 🎯 Project Overview

This project implements a complete, production-ready data pipeline on AWS that processes healthcare facility accreditation data, identifies facilities with expiring accreditations, and provides automated analytics through serverless architecture.

**Challenge Completed:** Stages 1, 2, 3, and 4 (All 4 stages)

## Project Architecture

<img width="2816" height="1536" alt="image" src="https://github.com/user-attachments/assets/94584466-ece7-485d-a0a9-9864a836bf75" />

```
Raw Data (S3) → Athena Query → Python Processing → Lambda Function → Step Functions Orchestration
                     ↓              ↓                    ↓                    ↓
                 Stage 1        Stage 2              Stage 3              Stage 4
```

### Data Flow
1. **Source:** 250 healthcare facility JSON records in S3
2. **Stage 1 (Athena):** SQL extraction of facility metrics
3. **Stage 2 (Python):** Filter facilities with accreditations expiring within 6 months
4. **Stage 3 (Lambda):** Event-driven Athena query execution on new data uploads
5. **Stage 4 (Step Functions):** Complete workflow orchestration with error handling

## 🏗️ Stages Completed

### ✅ Stage 1: Data Extraction with Athena
**Objective:** Extract key facility metrics using SQL queries on JSON data in S3

**Implementation:**
- Created Athena database: `healthcare_pipeline`
- Designed table schema with nested JSON support (ARRAY and STRUCT types)
- Converted 250 CSV records to NDJSON format for optimal Athena performance
- Extracted: facility_id, facility_name, employee_count, number_of_services, first_accreditation_expiry
- Query performance: <1 second, 65KB data scanned

**Key SQL Features:**
```sql
SELECT 
  facility_id,
  facility_name,
  employee_count,
  CARDINALITY(services) AS number_of_offered_services,
  accreditations[1].expiry_date AS expiry_date_of_first_accreditation
FROM facilities;
```

### ✅ Stage 2: Data Processing with Python (boto3)
**Objective:** Filter facilities with accreditations expiring within 6 months

**Implementation:**
- Python script with comprehensive error handling and logging
- Read 250 JSON files from S3 bucket
- Filtered facilities with expiry dates between Jan 1 - Jul 1, 2026
- Output: 144 facilities (57.6%) with expiring accreditations
- Processing time: ~3 seconds, zero errors

**Key Features:**
- Date parsing with datetime library
- boto3 S3 client operations
- Comprehensive logging with progress indicators
- Error handling for AWS, JSON, and unexpected errors

### ✅ Stage 3: Event-Driven Processing with Lambda
**Objective:** Automatic Athena query execution on new S3 uploads

**Implementation:**
- Lambda function (Python 3.14) with S3 trigger
- Executes Athena query to count facilities by state
- Environment variables for configuration
- Query timeout handling (60-second max)
- CloudWatch logging for monitoring

**Results:**
- Execution time: 2.6 seconds
- Memory used: 128 MB
- Successfully retrieves state-wise facility counts

### ✅ Stage 4: Workflow Orchestration with Step Functions
**Objective:** Complete pipeline orchestration with error handling

**Implementation:**
- Standard Step Functions state machine
- 7-state workflow with branching logic
- Retry logic (2 attempts, exponential backoff)
- Success path: Lambda → Wait → Check → Copy to Production
- Failure path: Error catching → Notification
- Execution time: 8.9 seconds


**Workflow States:**

<img width="914" height="912" alt="image" src="https://github.com/user-attachments/assets/0768b284-eda9-40a3-8e5f-7f09f23dd96f" />


1. InvokeLambdaFunction
2. WaitForQueryCompletion (5 seconds)
3. CheckQueryStatus
4. QuerySucceeded / QueryFailed
5. CopyResultsToProduction
6. End

## 📁 Project Structure 

```
aws-healthcare-data-pipeline/
├── data/
│   └── Healthcare_Survey_Sample_Data.csv
├── facility_json_files/          # 250 generated JSON files
├── scripts/
│   ├── csv_to_json.py           # CSV to JSON converter
│   ├── stage2_filter_expiring_accreditations.py
│   ├── validate_and_fix_json.py
│   └── convert_to_ndjson.py
├── lambda/
│   ├── stage3_athena_query_lambda.py
│   └── lambda_function.zip
├── step_functions/
│   └── state_machine_definition.json
└── README.md
```


## 🚀 Deployment Instructions

### Prerequisites
- AWS Account with Free Tier
- AWS CLI configured
- Python 3.12+
- boto3 installed

### Stage 1: Athena Setup
```bash
# 1. Create S3 bucket
aws s3 mb s3://healthcare-accreditation-data-pipeline

# 2. Upload data
aws s3 sync facility_json_files/ s3://healthcare-accreditation-data-pipeline/raw/

# 3. Run Athena DDL (in Athena Console)
# See: scripts/athena_create_table.sql
```

### Stage 2: Python Processing
```bash
cd scripts
python3 stage2_filter_expiring_accreditations.py
```

### Stage 3: Lambda Deployment
```bash
cd lambda
aws lambda create-function \
  --function-name Stage3-AthenaQueryFunction \
  --runtime python3.14 \
  --role arn:aws:iam::ACCOUNT_ID:role/HealthcareLambdaExecutionRole \
  --handler stage3_athena_query_lambda.lambda_handler \
  --zip-file fileb://lambda_function.zip
```

### Stage 4: Step Functions
```bash
aws stepfunctions create-state-machine \
  --name HealthcarePipelineStateMachine \
  --definition file://step_functions/state_machine_definition.json \
  --role-arn arn:aws:iam::ACCOUNT_ID:role/StepFunctionsRole
```

## 📈 Results & Performance

| Metric | Value |
|--------|-------|
| Total Facilities Processed | 250 |
| Facilities with Expiring Accreditations | 144 (57.6%) |
| Athena Query Time | <1 second |
| Python Processing Time | 3 seconds |
| Lambda Execution Time | 2.6 seconds |
| Step Functions Execution | 8.9 seconds |
| Total Errors | 0 |

## 🛠️ Technologies Used

- **AWS Services:** S3, Athena, Lambda, Step Functions, IAM, CloudWatch
- **Languages:** Python 3.14, SQL
- **Libraries:** boto3, pandas, json, datetime
- **Tools:** AWS CLI, VS Code, Git

## 💡 Key Technical Decisions

### Why These Stages?
I completed all 4 stages to demonstrate comprehensive AWS skills:
- **Stages 1 & 2:** Core data engineering (SQL + Python)
- **Stage 3:** Serverless event-driven architecture
- **Stage 4:** Enterprise workflow orchestration

### Design Choices
1. **NDJSON Format:** Optimized for Athena's JSON SerDe performance
2. **Retry Logic:** 2 attempts with exponential backoff for resilience
3. **Environment Variables:** Configuration without code changes
4. **Comprehensive Logging:** CloudWatch integration for monitoring
5. **Error Handling:** Try-catch blocks at every level

## 🎓 Learning Outcomes

- Mastered Athena SQL with nested JSON structures
- Implemented production-grade Python with boto3
- Designed event-driven serverless architectures
- Built complex workflow orchestration with Step Functions
- Applied AWS best practices (IAM least privilege, logging, error handling)

## 📝 Future Enhancements

- Add SNS notifications for real failures
- Implement DynamoDB for state tracking
- Add CloudWatch dashboards for monitoring
- Create CloudFormation template for one-click deployment
- Add unit tests and CI/CD pipeline

