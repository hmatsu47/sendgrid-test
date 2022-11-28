import json
import boto3
import os
import traceback
from botocore.exceptions import ClientError

table_sent_log = os.environ['TABLE_SENT_LOG']
table_bounce   = os.environ['TABLE_BOUNCE']

def lambda_handler(event, context):
    # バウンス用テーブルの準備
    dynamodb = boto3.resource('dynamodb')
    tableSentLog = dynamodb.Table(table_sent_log)
    tableBounce  = dynamodb.Table(table_bounce)
    # リクエストから必要情報を取得
    body = json.loads(event['body'])
    # バウンス用テーブルに記録
    for bodyItem in body:
        try:
            bounceItem = BounceItem(tableSentLog, bodyItem)
            tb_response = store(tableBounce, bounceItem)
            print('Result table:', tb_response)
        except Exception as e:
            # 例外→ログを残す
            print(traceback.format_exc())
            print(bodyItem)
            # 異常終了
            return {
                'statusCode': 500,
                'body'      : json.dumps({'message':'NG'})
    }
    # 正常終了
    return {
        'statusCode': 200,
        'body'      : json.dumps({'message':'OK'})
    }

class BounceItem():
    # バウンス項目クラス
    def __init__(self, table, item):
        # コンストラクタ
        self.full_message_id = item['sg_message_id']
        self.to_email        = item['email']
        self.event           = item['event']
        self.type            = '' if self.event != 'bounce' else item['type']
        self.reason          = item['reason']
        self.timestamp       = item['timestamp']
        keyMessageId = item['sg_message_id'].split('.')[0]
        response     = table.get_item(Key={'messageId': keyMessageId})
        sentItem     = response['Item']
        sentFrom     = json.loads(sentItem['from'])
        self.from_email      = sentFrom.get('email')
        self.from_name       = sentFrom.get('name')
        sentTo       = json.loads(sentItem['to'])
        toName = ''
        for toItem in sentTo:
            if item['email'] == toItem['email']:
                toName = toItem.get('name', '')
        self.to_name         = toName
        self.subject         = sentItem['subject']
        
def store(table, item):
    # バウンス用テーブルに転記
    response = table.put_item(
        Item={
            'fullMessageId': item.full_message_id,
            'fromEmail'    : item.from_email,
            'fromName'     : item.from_name,
            'toEmail'      : item.to_email,
            'toName'       : item.to_name,         
            'subject'      : item.subject,
            'timestamp'    : item.timestamp,
            'event'        : item.event,
            'type'         : item.type,
            'reason'       : item.reason
        }
    )
    if (response['ResponseMetadata']['HTTPStatusCode'] != 200):
        # ステータスコードが200以外→エラー
        print('DynamoDB put_item error:', response)
    return response