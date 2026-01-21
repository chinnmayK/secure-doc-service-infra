# 📄 Secure Document Metadata Service

**AWS · Terraform · Cost-Optimized · Production-Grade**

---

## 📌 Project Overview

This project implements a **secure, cost-optimized document metadata ingestion service** on AWS using **Terraform**.

Users upload documents via an HTTP API exposed through an **Application Load Balancer (ALB)**.
Only **metadata** (filename, size, timestamp) is stored in **DynamoDB**.
The backend runs on **EC2 instances in private subnets**, managed by an **Auto Scaling Group**.

The project focuses heavily on:

* **Real backend behavior**
* **AWS networking correctness**
* **Cost optimization with proof**
* **Operational debugging**
* **Production-grade hardening**
* **Safe teardown strategy**

This is not a demo — it is a **realistic cloud system** built and debugged end-to-end.

---

## 🧱 Final Architecture

```
Internet
   |
Application Load Balancer (Public Subnets)
   |
Auto Scaling Group
   |
EC2 Instances (Private Subnets)
   ├── Flask backend
   ├── Local logs (/var/log/app)
   └── logrotate
   |
DynamoDB (Metadata Storage)

Outbound traffic:
- DynamoDB → Gateway VPC Endpoint (no NAT)
- SSM → Interface VPC Endpoints (no NAT)
- Internet → NAT Gateway (minimized usage)
```

---

## 🧩 PHASE-BY-PHASE IMPLEMENTATION

---

## 🔹 PHASE 0 — Project Initialization & Terraform Setup

### What was done

* Created a new Git repository
* Installed and configured Terraform
* Set AWS credentials for Terraform usage
* Defined variables and basic provider configuration
* Established phase-based Git commit discipline

### Key decisions

* Terraform is the **single source of truth**
* No manual AWS resource creation
* Every phase must be committed independently

### Outcome

✅ Terraform working
✅ Clean Git history started

---

## 🔹 PHASE 1 — Backend Service (Local First)

### What was built

* Flask backend with:

  * `/upload` endpoint (file upload)
  * `/status` endpoint (health check)
* Metadata stored:

  * filename
  * size_bytes
  * uploaded_at (UTC)

### Initial testing

```bash
curl http://localhost:8080/status
curl -F "file=@test.txt" http://localhost:8080/upload
```

### Mistakes made

❌ `curl -F "file=@sample.pdf"` failed locally
**Reason:** file didn’t exist or wrong path

### Fix

✔️ Created real test files using:

```bash
echo "hello" > test.txt
```

---

## 🔹 PHASE 2 — VPC & Networking Foundation

### Infrastructure created

* Custom VPC
* Public subnets (for ALB)
* Private subnets (for EC2)
* Internet Gateway
* Route tables
* NAT Gateway (single, cost-optimized)

### Key decision

💡 **Single NAT Gateway**

* Lower cost
* Acceptable for non-HA demo / early startup

---

## 🔹 PHASE 3 — ALB, Target Group & ASG

### What was added

* Application Load Balancer
* Target Group on port `8080`
* Health check endpoint `/status`
* Auto Scaling Group (min=1, max=1)
* Launch Template

### Major issue encountered

❌ **502 Bad Gateway from ALB**

### Root causes

* Application not running
* Health checks failing
* App crashing before binding port

### Fixes

✔️ Verified:

```bash
ss -lntp | grep 8080
```

✔️ Ensured Flask bound to:

```python
app.run(host="0.0.0.0", port=8080)
```

---

## 🔹 PHASE 4 — IAM, DynamoDB & Permissions

### What was added

* DynamoDB table (PAY_PER_REQUEST)
* EC2 IAM Role
* Least-privilege policy (`dynamodb:PutItem`)
* Instance profile attached to Launch Template

### Major error encountered

❌ **`NoRegionError: You must specify a region`**

### Root cause

* `boto3.resource("dynamodb")` without region
* EC2 had no AWS_REGION env variable

### Fix

✔️ Injected region in user data:

```bash
export AWS_REGION="ap-south-1"
```

---

## 🔹 PHASE 5 — User Data, Launch Templates & ASG Refresh

### What was implemented

* Full EC2 bootstrap via user data:

  * Python install
  * Flask app creation
  * Dependency install
  * App startup using `nohup`

### Major mistake

❌ Environment variables added incorrectly using Terraform-style `environment {}` block in Launch Template

### Fix

✔️ Environment variables exported inside **user data script**
✔️ Forced ASG instance refresh

---

## 🔹 PHASE 6 — Logging & Log Rotation

### Logging design

* App logs → `/var/log/app/document-service.log`
* Stdout → `/var/log/app/app.out`
* Rotation via `logrotate`

  * daily
  * rotate 7
  * compress

### Major errors encountered

#### ❌ Logrotate file missing

```bash
/etc/logrotate.d/document-service: No such file
```

**Fix**
✔️ Created file in user data
✔️ Verified manually using:

```bash
sudo logrotate -f /etc/logrotate.d/document-service
```

#### ❌ Permission denied writing logs

```text
PermissionError: /var/log/app/document-service.log
```

**Root cause**

* File existed but owned by root
* App running as non-root

**Final fix**

```bash
chmod 755 /var/log/app
touch /var/log/app/document-service.log
chmod 644 /var/log/app/document-service.log
```

---

## 🔹 PHASE 7 — NAT Gateway Reality & Cost Awareness

### Observation

* NAT Gateway metrics showed **constant traffic**
* Even SSM + DynamoDB traffic used NAT

### Insight

💡 NAT is **the biggest silent AWS cost**

---

## 🔹 PHASE 8 — NAT Cost Reduction with VPC Endpoints

### What was implemented

#### DynamoDB Gateway Endpoint

* DynamoDB traffic bypasses NAT entirely

#### SSM Interface Endpoints

* `ssm`
* `ssmmessages`
* `ec2messages`

### Validation

* NAT Gateway metrics dropped within 1 hour
* Uploads still worked
* DynamoDB writes succeeded
* SSM access worked without internet

### This was **measured**, not assumed.

---

## 🔹 PHASE 9.1 — Production Hardening

### Improvements

* ALB health checks hardened
* ASG `protect_from_scale_in = true`
* IMDSv2 enforced
* SSH fully disabled
* SSM only access

### Terraform behavior observed

❗ Launch Template replacement required
✔️ Safe and expected behavior

---

## 🔹 PHASE 9.2 — Data Retention Strategy

### Decision

✅ DynamoDB data must be preserved

### Production-grade strategies

* Enable Point-in-Time Recovery (PITR)
* Or export table to S3 before teardown

### Interview explanation

> “In production, we enable PITR or export DynamoDB to S3 before infrastructure teardown.”

---

## 🔹 PHASE 9.3 — Documentation & Finalization

### Completed

* Full README
* TEARDOWN.md
* Resume-ready bullets
* Interview narrative

---

## ⚠️ COMMON MISTAKES TO WATCH FOR (REAL ONES)

| Mistake                     | Impact                 |
| --------------------------- | ---------------------- |
| App not binding to 0.0.0.0  | ALB health checks fail |
| Missing AWS_REGION          | boto3 crashes          |
| Wrong log permissions       | App crashes silently   |
| No NAT optimization         | Unexpected AWS bill    |
| Manual console deletions    | Terraform drift        |
| Forgetting instance refresh | Old user data runs     |

---

## 💰 COST OPTIMIZATION SUMMARY

* Single NAT Gateway
* DynamoDB Gateway Endpoint
* SSM Interface Endpoints
* Local logs (no CloudWatch ingestion)
* PAY_PER_REQUEST DynamoDB

---

## 🧠 INTERVIEW ONE-LINER (FINAL)

> “I built a secure document metadata service on AWS using Terraform, focusing on real backend behavior, private networking, NAT cost reduction using VPC endpoints, and production-grade hardening with IMDSv2, SSM-only access, and safe teardown strategies.”

---

## 🏁 FINAL STATUS

✅ Fully working backend
✅ Healthy ALB & ASG
✅ Verified cost reduction
✅ Real debugging experience
✅ Resume-ready project