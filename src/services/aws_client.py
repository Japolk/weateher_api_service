import aioboto3
import json
import uuid
from datetime import datetime
from typing import Optional
from botocore.exceptions import ClientError

from src.misc.utils import get_logger


class AWSClient:
    def __init__(self):
        self._bucket_name = None
        self._dynamodb_table = None
        self._aws_session = None
        self._logger = get_logger(__name__)

    def initialize(
            self,
            access_key_id : str,
            access_key_secret: str,
            aws_region: str,
            bucket_name: str,
            dynamodb_table: str,
    ):
        self._bucket_name = bucket_name
        self._dynamodb_table = dynamodb_table
        self._aws_session = aioboto3.Session(
            aws_access_key_id=access_key_id,
            aws_secret_access_key=access_key_secret,
            region_name=aws_region,
        )
        self._logger.info('AWSClient initialized')

    async def put_s3_file(self, file_key: str, data: dict):
        """
        this is the life

        """
        file_address = None
        async with self._aws_session.client('s3') as s3_client:
            json_body = json.dumps(data, indent=2).encode('utf-8')
            try:
                await s3_client.put_object(Bucket=self._bucket_name, Key=file_key, Body=json_body)
                file_address = f's3://{self._bucket_name}/{file_key}'
            except ClientError as e:
                self._logger.error(f'Error on saving city weather to s3: {e}')
        return file_address

    async def get_s3_file(self, file_key: str) -> Optional[dict]:
        """
        this is the life

        """
        file_data = None
        async with self._aws_session.client('s3') as s3_client:
            try:
                result = await s3_client.get_object(Bucket=self._bucket_name, Key=file_key)
                file_bytes = await result['Body'].read()
                file_data = json.loads(file_bytes.decode('utf-8'))
            except ClientError as e:
                self._logger.error(f'Error getting city weather from s3: {e}')
        return file_data

    async def find_recent_s3_file(self, city_name: str, cutoff_time: datetime) -> Optional[dict]:
        """
        Find recent file for a given city appeared after the cutoff_time
        """
        async with self._aws_session.client('s3') as s3_client:
            paginator = s3_client.get_paginator('list_objects_v2')
            try:
                async for page in paginator.paginate(Bucket=self._bucket_name, Prefix=f'{city_name}_'):
                    matching_files = [
                        obj for obj in page.get('Contents', [])
                        if obj['LastModified'] >= cutoff_time
                    ]
                    if matching_files:
                        return max(matching_files, key=lambda x: x['LastModified'])
            except ClientError as e:
                self._logger.error(f'Error finding recent city weather file in s3: {e}')
            return None

    async def log_to_dynamodb(self, city: str, timestamp: int, s3_file_url: str):
        """
        Log weather event to DynamoDB
        """
        async with self._aws_session.client('dynamodb') as dynamodb_client:
            try:
                await dynamodb_client.put_item(
                    TableName=self._dynamodb_table,
                    Item={
                        'id': {'S': str(uuid.uuid4())},
                        'city': {'S': city},
                        's3_file_url': {'S': s3_file_url},
                        'timestamp': {'N': str(timestamp)},
                    }
                )
            except ClientError as e:
                self._logger.error(f'Error logging to DynamoDB: {e}')
