# sendgrid-test

SendGrid テスト用リポジトリ

## AWS Lambda 関数

※あらかじめ [SendGrid Python SDK](https://github.com/sendgrid/sendgrid-python) を Lambda Layer 化しておき、各 Lambda 関数で使用する

- [testMailReceiver](lambda/testMailReceiver/README.md)
  - SendGrid でメールを受信して S3 バケットに保存する
    - ユーザー名の識別は行わない
- [testMailSender](lambda/testMailSender/README.md)
  - DynamoDB table (for mail sender) にメールの情報を登録するとメールを送信
    - id : Partition key
    - from : Sender address
      - ex. {"email": "[mail address]", "name": "[sender name]"}
    - to : Receiver addresses
      - ex. [{"email": "[mail address]", "name": "[receiver name]"}, {"email": "[mail address]", "name": "[receiver name]"}]
    - subject : Subject (Title)
    - content : Content body
- [testBounceReceiver](lambda/testBounceReceiver/README.md)
  - Bounce を Event Webhook から受信して DynamoDB table (for bounce) に書き込み
