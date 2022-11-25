import boto3
import datetime
import json
import os
import sendgrid
import time
import traceback
from base64 import b64decode
from boto3.dynamodb.conditions import Key
from boto3.dynamodb.types import TypeDeserializer
from sendgrid.helpers.mail import *

deserializer = TypeDeserializer()

sg_api_key = boto3.client('kms').decrypt(
    CiphertextBlob=b64decode(os.environ['SENDGRID_API_KEY']),
    EncryptionContext={'LambdaFunctionName': os.environ['AWS_LAMBDA_FUNCTION_NAME']}
)['Plaintext'].decode('utf-8')

table_sent_log = os.environ['TABLE_SENT_LOG']

def lambda_handler(event, context):
    # 送信ログ用テーブルの準備
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(table_sent_log)
    # ストリームから受け取った変更後レコードリストをループ処理
    for record in event['Records']:
        eventName = record['eventName']
        if (eventName == 'INSERT' or eventName == 'MODIFY'):
            image = record['dynamodb']['NewImage']
            try:
                # eventをdictに変換して値を抽出
                item = deserialize(image)
                message = Message(item)
                # SendGridで送信
                sg_response = send(message)
                status = sg_response.status_code
                if (status > 299):
                    raise Exception('SendGrid API Error.')
                message_id = sg_response.headers['X-Message-Id'].split('.')[0]
                # 表示用テーブルに転記
                tb_response = store(table, message, message_id)
                print('Result table:', tb_response)
            except Exception as e:
                # 例外→ログを残す
                print(traceback.format_exc())
                print(image)
    return 'Successfully processed {} records.'.format(len(event['Records']))

class Message():
    # 送信メールメッセージクラス
    def __init__(self, item):
        # コンストラクタ
        self.id         = item['id']
        self.from_email = json.loads(item['from'])
        self.subject    = item['subject']
        self.content    = item['content']
        self.to_email   = json.loads(item['to'])

def deserialize(image):
    # dictに変換
    d = {}
    for key in image:
        d[key] = deserializer.deserialize(image[key])
    return d

def send(message):
    # SendGridで通知
    sg         = sendgrid.SendGridAPIClient(api_key=sg_api_key)

    from_email = Email(message.from_email.get('email'), message.from_email.get('name'))
    subject    = message.subject
    content    = Content("text/plain", message.content)

    to_email = []
    for toItem in message.to_email:
        to_email.append(To(toItem.get('email'), toItem.get('name')))

    mail       = Mail(from_email, to_email, subject, content)

    return sg.client.mail.send.post(request_body=mail.get())

def store(table, message, message_id):
    # 送信ログ用テーブルに転記
    response = table.put_item(
        Item={
            'messageId': message_id,
            'from': json.dumps(message.from_email),
            'subject': message.subject,
            'to': json.dumps(message.to_email)
        }
    )
    if (response['ResponseMetadata']['HTTPStatusCode'] != 200):
        # ステータスコードが200以外→エラー
        print('DynamoDB put_item error:', response)
    return response