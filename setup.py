import collections
import json
import logging
import os
import uuid

import boto3

from logger import logger

CONFIG_FILE = 'config.json'
TRUST_POLICY = 'iam/trust_policy.json'
PERMISSION_POLICY = 'iam/permission_policy.json'


def setup():
    config = collections.defaultdict(dict)
    uid = uuid.uuid4().hex[:8]
    create_iam_role(config, uid)
    create_rekognition_collection(config, uid)
    create_kinesis_video_stream(config, uid)
    create_kinesis_data_stream(config, uid)
    create_stream_processor(config, uid)
    write_config(config)


def already_setup():
    return os.path.isfile(CONFIG_FILE)


def get_stream_name():
    config = get_config()
    return config['KinesisData']['StreamName']


def get_collection_id():
    config = get_config()
    return config['Rekognition']['CollectionId']


def get_file_contents(path):
    with open(path) as infile:
        return infile.read()


def get_config():
    try:
        with open(CONFIG_FILE) as infile:
            return json.load(infile)
    except FileNotFoundError:
        raise FileNotFoundError(f'{CONFIG_FILE!r} does not exist. Have you run setup?')


def write_config(config):
    with open(CONFIG_FILE, 'w') as outfile:
        json.dump(config, outfile, indent=4)


def delete_config():
    logger.debug(f'Deleting file: {CONFIG_FILE}')
    os.remove(CONFIG_FILE)


def create_iam_role(config, uid):
    client = boto3.client('iam')
    role_name = 'choco-role-' + uid
    logger.debug(f'Creating role: {role_name}')
    rsp = client.create_role(
        RoleName=role_name,
        AssumeRolePolicyDocument=get_file_contents(TRUST_POLICY),
        Description='IAM role for the choco stream processor'
    )
    policy_name = 'choco-permission-policy-' + uid
    logger.debug(f'Creating policy: {policy_name}')
    client.put_role_policy(
        RoleName=role_name,
        PolicyName='choco-permission-policy-' + uid,
        PolicyDocument=get_file_contents(PERMISSION_POLICY)
    )
    config['IAM']['RoleName'] = role_name
    config['IAM']['PolicyName'] = policy_name
    config['IAM']['Arn'] = rsp['Role']['Arn']


def create_rekognition_collection(config, uid):
    client = boto3.client('rekognition')
    collection_id = 'choco-collection-' + uid
    logger.debug(f'Creating collection: {collection_id}')
    rsp = client.create_collection(
        CollectionId=collection_id
    )
    config['Rekognition']['CollectionId'] = collection_id
    config['Rekognition']['Arn'] = rsp['CollectionArn']


def create_kinesis_video_stream(config, uid):
    client = boto3.client('kinesisvideo')
    stream_name = 'choco-video-stream-' + uid
    logger.debug(f'Creating video stream: {stream_name}')
    rsp = client.create_stream(
        StreamName=stream_name
    )
    config['KinesisVideo']['StreamName'] = stream_name
    config['KinesisVideo']['Arn'] = rsp['StreamARN']


def create_kinesis_data_stream(config, uid):
    client = boto3.client('kinesis')
    stream_name = 'choco-data-stream-' + uid
    logger.debug(f'Creating data stream: {stream_name}')
    client.create_stream(
        StreamName=stream_name,
        ShardCount=1
    )
    rsp = client.describe_stream(
        StreamName=stream_name
    )
    config['KinesisData']['StreamName'] = stream_name
    config['KinesisData']['Arn'] = rsp['StreamDescription']['StreamARN']
    logger.debug(f'Waiting on data stream to start running...')
    waiter = client.get_waiter('stream_exists')
    waiter.wait(
        StreamName=stream_name
    )
    logger.debug('Done waiting')


def create_stream_processor(config, uid):
    client = boto3.client('rekognition')
    proc_name = 'choco-proc-' + uid
    logger.debug(f'Creating stream processor: {proc_name}')
    rsp = client.create_stream_processor(
        Input={
            'KinesisVideoStream': {
                'Arn': config['KinesisVideo']['Arn']
            }
        },
        Output={
            'KinesisDataStream': {
                'Arn': config['KinesisData']['Arn']
            }
        },
        Name=proc_name,
        Settings={
            'FaceSearch': {
                'CollectionId': config['Rekognition']['CollectionId'],
                'FaceMatchThreshold': 95.0
            }
        },
        RoleArn=config['IAM']['Arn']
    )
    logger.debug(f'Starting stream processor')
    client.start_stream_processor(
        Name=proc_name
    )
    config['StreamProcessor']['ProcName'] = proc_name
    config['StreamProcessor']['Arn'] = rsp['StreamProcessorArn']


if __name__ == '__main__':
    if already_setup():
        raise RuntimeError(f'{CONFIG_FILE!r} already exists. Quitting setup')
    else:
        logger.setLevel(logging.DEBUG)
        setup()
