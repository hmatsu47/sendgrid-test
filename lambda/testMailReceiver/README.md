## 必要な準備

### SendGrid

- Domain Authentication
- Link Branding

### AWS

- S3 Bucket
  - Block Public Access
    - ON
- Lambda Function
  - IAM Role
    - Create new Role
      - Default Basic role (for CloudWatch logs)
    - Add Policy
      - `s3:PutObject`
        - Resource : `arn:aws:s3:::[S3 Bucket name]/*`
  - Layer
    - [SendGrid Python SDK](https://github.com/sendgrid/sendgrid-python)
  - Configuration
    - General
      - Timedout : 30 sec.
    - Environment variables
      - `S3_BUCKET_NAME` : S3 Bucket name
- API Gateway
  - Resource Path
    - Long and random path
      - Action : POST only
        - Integration request : type LAMBDA_PROXY
      - POST Method Response : add 500
        - `application/json`
        - Empty
  - Stage
    - `v1`
