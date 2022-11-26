## 必要な準備

### SendGrid

- API Key
  - Mail Send only (Full Access)

### AWS

- DynamoDB tables
  - for mail sender
    - Partition key : id (String)
  - for mail sent log
    - Partition key : messageId (String)
- Lambda Function
  - IAM Role
    - Create new Role
      - Default Basic role (for CloudWatch logs)
    - Add Policy
      - `dynamodb:ListStreams`
        - Resource : `*`
      - `dynamodb:PutItem`, `dynamodb:GetItem`, `dynamodb:Query`
        - Resource : `arn:aws:dynamodb:[Region]:[Account ID]:table/[for mail sent log]`
  - Configuration
    - General
      - Timedout : 30 sec.
    - Environment variables
      - `SENDGRID_API_KEY` : SendGrid API Key
      - `TABLE_SENT_LOG` : Table name (for sent log)
- DynamoDB tables
  - for mail sender
    - DynamoDB Streams
      - Trigger : lambda funvtion
        - Batch size : 100
