import os
import pprint

import boto3

from setup import get_collection_id

pp = pprint.PrettyPrinter(indent=4)
client = boto3.client('rekognition')


def image_to_bytes(image_path):
    with open(image_path, 'rb') as image_file:
        image = image_file.read()
        return bytearray(image)


def index_face(image_path, user_id, collection_id):
    rsp = client.index_faces(
        CollectionId=collection_id,
        Image={
            'Bytes': image_to_bytes(image_path)
        },
        ExternalImageId=user_id,
        MaxFaces=1
    )
    return rsp


def search_face(image_path, collection_id):
    rsp = client.search_faces_by_image(
        CollectionId=collection_id,
        Image={
            'Bytes': image_to_bytes(image_path)
        }
    )
    return rsp['FaceMatches']


def list_faces(collection_id):
    rsp = client.list_faces(
        CollectionId=collection_id
    )
    return rsp['Faces']


def delete_all_faces(collection_id):
    faces = list_faces(collection_id)
    face_ids = [face['FaceId'] for face in faces]
    rsp = client.delete_faces(
        CollectionId=collection_id,
        FaceIds=face_ids
    )
    return rsp


def index_all():
    collection_id = get_collection_id()
    image_dirs = [p for p in os.scandir('images') if p.is_dir()]
    for image_dir in image_dirs:
        user_id, friendly_name = image_dir.name.split('_')
        print(f'*** Indexing {friendly_name} : {user_id}')
        for image in os.scandir(image_dir):
            index_face(image, user_id, collection_id)


if __name__ == '__main__':
    print('Attempting to index all images...')
    index_all()