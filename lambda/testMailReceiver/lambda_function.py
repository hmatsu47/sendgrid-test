import boto3
import datetime
import json
import os

s3_bucket_name = os.environ['S3_BUCKET_NAME']

def lambda_handler(event, context):
    # リクエスト情報からキーを生成
    request_context = event['requestContext']
    epoch_time = request_context['requestTimeEpoch']
    request_id = request_context['requestId']
    record_datetime = datetime.datetime.fromtimestamp(epoch_time / 1000) + datetime.timedelta(hours = 9)
    record_datetime_string = record_datetime.strftime('%Y-%m-%d_%H:%M:%S.%f')[:-3]
    s3_key = '{}_{}'.format(record_datetime_string, request_id)
    # メール本文（添付ファイル等含む）を取得
    body = event['body']
    # S3へ
    s3_client = boto3.client("s3")
    try:
        s3_client.put_object(
                Bucket=s3_bucket_name,
                Key=s3_key,
                Body=body
                )
    except:
        # S3 アップロードエラーならリトライ
        return {
            'statusCode': 500,
            'body': json.dumps({'message':'Internal Server Error.'})
        }
    # 正常終了
    return {
        'statusCode': 200,
        'body': json.dumps({'message':'OK'})
    }