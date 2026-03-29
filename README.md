# EC2 Instance Scheduler — AWS Project

**Automated start/stop of EC2 instances using AWS Lambda and Amazon EventBridge**

---

## Project Overview

This project automates the starting and stopping of an AWS EC2 instance on a fixed business-hours schedule. Two Python Lambda functions are triggered by Amazon EventBridge cron rules, eliminating the need for manual intervention and reducing compute costs significantly.

The instance runs **Monday–Friday, 09:00–17:00 UTC only** — cutting runtime from 730 hours/month (24/7) to approximately 200 hours/month, a saving of over **70%**.

---

## Architecture

```
Amazon EventBridge          AWS Lambda              Amazon EC2
──────────────────    ──────────────────────    ──────────────────
start-rule             start-ec2 (Python 3.14)   apache-ec2-dev
cron(0 9 ? * mon-fri *)  ──► start_instances()  ──►  t2.micro
                                                    (eu-west-2)
stop-rule              stop-ec2 (Python 3.14)
cron(0 17 ? * mon-fri *) ──► stop_instances()  ──►
```

### Services Used

| Service | Role |
|---|---|
| **AWS Lambda** | Serverless functions to start/stop EC2 via Boto3 |
| **Amazon EventBridge** | Cron-based scheduler that triggers Lambda functions |
| **Amazon EC2** | The managed compute instance (apache-ec2-dev, t2.micro) |
| **AWS IAM** | Execution roles with AmazonEC2FullAccess + AWSLambdaBasicExecutionRole |
| **Amazon CloudWatch** | Metrics monitoring — invocations, duration, error rate |
| **Python 3.14 + Boto3** | Runtime and AWS SDK for the Lambda code |

---

## Schedule

| Rule | Cron Expression | Action | Days |
|---|---|---|---|
| `start-rule` | `cron(0 9 ? * mon-fri *)` | Starts EC2 instance | Monday – Friday |
| `stop-rule` | `cron(0 17 ? * mon-fri *)` | Stops EC2 instance | Monday – Friday |

All times are **UTC**.

---

## Lambda Functions

### `start-ec2`

```python
import json
import boto3

client = boto3.client('ec2', region_name='eu-west-2')
instance_id = "i-024236f32f8f5c04c"

def lambda_handler(event, context):
    response = client.start_instances(
        InstanceIds=[instance_id]
    )
```

### `stop-ec2`

```python
import json
import boto3

client = boto3.client('ec2', region_name='eu-west-2')
instance_id = "i-024236f32f8f5c04c"

def lambda_handler(event, context):
    response = client.stop_instances(
        InstanceIds=[instance_id]
    )
```

---

## IAM Permissions

Each Lambda execution role has:
- `AmazonEC2FullAccess` — allows start/stop of EC2 instances
- `AWSLambdaBasicExecutionRole` — allows writing logs to CloudWatch

Each Lambda function also has a resource-based policy granting `events.amazonaws.com` permission to invoke it:

```json
{
  "StatementId": "EventBridgeInvokeStartEC2",
  "Principal": "events.amazonaws.com",
  "Action": "lambda:InvokeFunction"
}
```

---

## How to Deploy

### Prerequisites
- AWS account with appropriate permissions
- An EC2 instance already created
- Python 3.x and AWS CLI configured locally (for testing)

### Step 1 — Create the Lambda Functions

1. Open **AWS Lambda** → **Create function**
2. Choose **Author from scratch**
3. Name: `start-ec2` / Runtime: **Python 3.14**
4. Paste the code from `lambda/start_ec2/lambda_function.py`
5. Update `instance_id` to your EC2 instance ID
6. Deploy the function
7. Repeat for `stop-ec2` using `lambda/stop_ec2/lambda_function.py`

### Step 2 — Attach IAM Permissions

1. Go to **IAM** → **Roles** → find the Lambda execution role
2. Attach `AmazonEC2FullAccess` and `AWSLambdaBasicExecutionRole`

### Step 3 — Create EventBridge Scheduled Rules

1. Open **Amazon EventBridge** → **Scheduled rules**
2. Create `start-rule`:
   - Schedule pattern: **Fine-grained cron**
   - Cron: `0 9 ? * mon-fri *`
   - Target: **AWS service** → **Lambda function** → `start-ec2`
3. Create `stop-rule`:
   - Cron: `0 17 ? * mon-fri *`
   - Target: Lambda function → `stop-ec2`

### Step 4 — Test

- Use the **Test** button in Lambda console with any sample event
- Check the EC2 console to confirm state changes (Running ↔ Stopped)
- View CloudWatch metrics under Lambda → Monitor tab

---

## Test Results

| Test | Result |
|---|---|
| `stop-ec2` manual Lambda test | ✅ EC2 entered Stopping state — Status: Succeeded |
| `start-ec2` manual Lambda test | ✅ EC2 entered Running state — Status: Succeeded |
| EventBridge stop-rule live trigger | ✅ EC2 automatically stopped on schedule |
| CloudWatch metrics | ✅ 3 invocations, 0 errors, 100% success rate, avg ~609ms |

---

## Business Case

**Problem:** EC2 instances left running 24/7 accumulate unnecessary compute costs — developers forget to stop them, weekends pass, and the bill grows.

**Solution:** Automate the schedule. Run instances only during business hours. No human intervention required.

**Impact:**
- ~730 hours/month (24/7) reduced to ~200 hours/month (business hours)
- **70%+ cost reduction** on compute with zero operational effort
- Scales to any number of instances by expanding `InstanceIds`

**Complements Auto Scaling:**
- Auto Scaling handles **unpredictable load** — scales out during traffic spikes
- Instance Scheduler handles **predictable patterns** — turns everything off outside business hours
- Together they provide complete cost control across both axes

---

## CloudWatch Metrics

Lambda sends runtime metrics automatically:

- **Invocations:** Total function calls (3 recorded during testing)
- **Duration:** Average ~609ms, Maximum ~615ms
- **Error count:** 0 errors across all invocations
- **Success rate:** 100%

---

## Repository Structure

```
ec2-instance-scheduler/
├── README.md
├── lambda/
│   ├── start_ec2/
│   │   └── lambda_function.py
│   └── stop_ec2/
│       └── lambda_function.py
└── docs/
    └── EC2_Instance_Scheduler_Project.pdf
```

---

## Author

**David Koduah** — Cloud Engineer  
AWS Projects Portfolio — March 2026
