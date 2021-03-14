import logging

import boto3

from logger import logger
from setup import delete_config, get_config


def cleanup():
    config = get_config()
    delete_stream_processor(config)
    delete_kinesis_data_stream(config)
    delete_kinesis_video_stream(config)
    delete_rekognition_collection(config)
    delete_iam_role(config)
    delete_config()


def delete_stream_processor(config):
    client = boto3.client('rekognition')
    proc_name = config['StreamProcessor']['ProcName']
    logger.debug(f'Deleting stream processor: {proc_name}')
    try:
        client.stop_stream_processor(
            Name=proc_name
        )
    except client.exceptions.ResourceNotFoundException:
        logger.debug('Stream processor not found, skipping...')
        return
    except client.exceptions.ResourceInUseException:
        logger.debug('Stream processor not running')

    client.delete_stream_processor(
        Name=proc_name
    )


def delete_kinesis_data_stream(config):
    client = boto3.client('kinesis')
    stream_name = config['KinesisData']['StreamName']
    logger.debug(f'Deleting data stream: {stream_name}')
    try:
        client.delete_stream(
            StreamName=stream_name
        )
    except client.exceptions.ResourceNotFoundException:
        logger.debug('Data stream not found, skipping...')


def delete_kinesis_video_stream(config):
    client = boto3.client('kinesisvideo')
    stream_name = config['KinesisVideo']['StreamName']
    logger.debug(f'Deleting video stream: {stream_name}')
    try:
        client.delete_stream(
            StreamARN=config['KinesisVideo']['Arn']
        )
    except client.exceptions.ResourceNotFoundException:
        logger.debug('Video stream not found, skipping...')


def delete_rekognition_collection(config):
    client = boto3.client('rekognition')
    collection_id = config['Rekognition']['CollectionId']
    logger.debug(f'Deleting collection: {collection_id}')
    try:
        client.delete_collection(
            CollectionId=collection_id
        )
    except client.exceptions.ResourceNotFoundException:
        logger.debug('Collection not found, skipping...')


def delete_iam_role(config):
    client = boto3.client('iam')
    role_name = config['IAM']['RoleName']
    policy_name = config['IAM']['PolicyName']
    logger.debug(f'Deleting policy role: {policy_name}')
    try:
        client.delete_role_policy(
            RoleName=role_name,
            PolicyName=policy_name
        )
    except client.exceptions.NoSuchEntityException:
        logger.debug('Policy role not found, skipping...')

    logger.debug(f'Deleting IAM role: {role_name}')
    try:
        client.delete_role(
            RoleName=role_name
        )
    except client.exceptions.NoSuchEntityException:
        logger.debug('IAM role not found, skipping...')


if __name__ == '__main__':
    logger.setLevel(logging.DEBUG)
    cleanup()
