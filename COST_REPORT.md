# AWS Cost Report - Healthcare Data Pipeline

**Project:** AWS Healthcare Data Pipeline Challenge  
**Date:** January 1, 2026  
**Account:** Free Tier with $120 credits

## 💰 Cost Summary

### Total Project Cost: $0.00

All resources utilized remained within AWS Free Tier limits, resulting in zero charges.

## 📊 Resource Usage Breakdown

### Amazon S3
- **Storage:** ~31 MB (250 JSON files + query results)
- **Requests:** ~500 PUT/GET operations
- **Free Tier Limit:** 5 GB storage, 20,000 GET, 2,000 PUT requests/month
- **Usage:** <1% of Free Tier
- **Cost:** $0.00

### AWS Athena
- **Data Scanned:** ~130 KB total across all queries
- **Queries Executed:** 8 queries
- **Free Tier Limit:** 1 TB data scanned/month
- **Usage:** <0.01% of Free Tier
- **Cost:** $0.00

### AWS Lambda
- **Invocations:** 3 executions
- **Compute Time:** ~8 seconds total (128 MB memory)
- **Free Tier Limit:** 1M requests/month, 400,000 GB-seconds
- **Usage:** <0.001% of Free Tier
- **Cost:** $0.00

### AWS Step Functions
- **Executions:** 1 execution
- **State Transitions:** 7 transitions
- **Free Tier Limit:** 4,000 state transitions/month
- **Usage:** 0.175% of Free Tier
- **Cost:** $0.00

### AWS CloudWatch Logs
- **Log Storage:** ~2 KB
- **Free Tier Limit:** 5 GB ingestion, 5 GB storage
- **Usage:** <0.01% of Free Tier
- **Cost:** $0.00

## 💡 Cost Optimization Strategies Implemented

1. **Efficient Data Format:** NDJSON format minimizes Athena scan costs
2. **Targeted Queries:** SQL queries scan only necessary data
3. **Minimal Lambda Memory:** 128 MB allocation optimizes cost/performance
4. **Data Lifecycle:** Can implement S3 lifecycle policies for long-term cost savings
5. **Free Tier Monitoring:** Active tracking to stay within limits

## 📈 Projected Costs at Scale

If scaling to production with 10,000 facilities:

| Service | Monthly Cost (Estimated) |
|---------|-------------------------|
| S3 Storage (500 MB) | $0.01 |
| Athena (10 GB scanned) | $0.05 |
| Lambda (1,000 invocations) | $0.00 (Free Tier) |
| Step Functions (100 executions) | $0.00 (Free Tier) |
| **Total** | **~$0.06/month** |

## ✅ Cost Efficiency Highlights

- **Zero cost** for development and testing phase
- **Serverless architecture** = pay only for actual usage
- **No idle resources** = no wasted spend
- **Free Tier optimized** = sustainable for ongoing development

--- 
**Services Used:** 5 (S3, Athena, Lambda, Step Functions, CloudWatch)  
**Total Charges:** $0.00
