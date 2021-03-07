import collections
import json
import os.path
import uuid

import boto3

_CONFIG_FILE = 'config.json'
_TRUST_POLICY = 'iam/trust_policy.json'
_PERMISSION_POLICY = 'iam/permission_policy.json'


def setup():
    config = collections.defaultdict(dict)
    uid = uuid.uuid4().hex[:8]
    create_rekognition_collection(config, uid)
    create_kinesis_video_stream(config, uid)
    create_kinesis_data_stream(config, uid)
    create_iam_role(config, uid)
    create_stream_processor(config, uid)
    write_config(config)


def already_setup():
    return os.path.exists(_CONFIG_FILE)


def get_stream_name():
    with open(_CONFIG_FILE) as infile:
        config = json.load(infile)
    return config['KinesisData']['StreamName']


def get_file_contents(path):
    with open(path) as infile:
        return infile.read()


def write_config(config):
    with open(_CONFIG_FILE, 'w') as outfile:
        json.dump(config, outfile, indent=4)


def create_rekognition_collection(config, uid):
    client = boto3.client('rekognition')
    collection_id = 'choco-collection-' + uid
    rsp = client.create_collection(
        CollectionId=collection_id
    )
    config['Rekognition']['CollectionId'] = collection_id
    config['Rekognition']['Arn'] = rsp['CollectionArn']


def create_kinesis_video_stream(config , uid):
    client = boto3.client('kinesisvideo')
    stream_name = 'choco-video-stream-' + uid
    rsp = client.create_stream(
        StreamName=stream_name
    )
    config['KinesisVideo']['StreamName'] = stream_name
    config['KinesisVideo']['Arn'] = rsp['StreamARN']


def create_kinesis_data_stream(config, uid):
    client = boto3.client('kinesis')
    stream_name = 'choco-data-stream-' + uid
    client.create_stream(
        StreamName=stream_name,
        ShardCount=1
    )
    rsp = client.describe_stream(
        StreamName=stream_name
    )
    config['KinesisData']['StreamName'] = stream_name
    config['KinesisData']['Arn'] = rsp['StreamDescription']['StreamARN']


def create_stream_processor(config, uid):
    client = boto3.client('rekognition')
    proc_name = 'choco-proc-' + uid
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
    client.start_stream_processor(
        Name=proc_name
    )
    config['StreamProcessor']['ProcName'] = proc_name
    config['StreamProcessor']['Arn'] = rsp['StreamProcessorArn']


def create_iam_role(config, uid):
    client = boto3.client('iam')
    role_name = 'choco-role-' + uid
    rsp = client.create_role(
        RoleName=role_name,
        AssumeRolePolicyDocument=get_file_contents(_TRUST_POLICY),
        Description='IAM role for the choco stream processor'
    )
    client.put_role_policy(
        RoleName=role_name,
        PolicyName='choco-permission-policy-' + uid,
        PolicyDocument=get_file_contents(_PERMISSION_POLICY)
    )
    config['IAM']['RoleName'] = role_name
    config['IAM']['Arn'] = rsp['Role']['Arn']


if __name__ == '__main__':
    if already_setup():
        raise RuntimeError(f'{_CONFIG_FILE!r} already exists: aborting setup')
    else:
        setup()






