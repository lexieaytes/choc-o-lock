# Standard
import pprint

# Third-party
import boto3

pp = pprint.PrettyPrinter(indent=4)
client = boto3.client('rekognition')

collection = 'test-collection-west'


def image_to_bytes(image_path):
    with open(image_path, 'rb') as image_file:
        image = image_file.read()
        return bytearray(image)

def index_face(image_path, user_id, collection_id):
    image_bytes = image_to_bytes(image_path)
    response = client.index_faces(
        CollectionId=collection_id,
        Image={
            'Bytes': image_bytes
        },
        ExternalImageId=user_id,
        MaxFaces=1
    )
    return response

def search_face(image_path, collection_id):
    image = image_to_bytes(image_path)
    response = client.search_faces_by_image(
        CollectionId=collection_id,
        Image={
            'Bytes': image
        }
    )
    return response['FaceMatches']

def list_faces(collection_id):
    response = client.list_faces(
        CollectionId=collection_id
    )
    return response['Faces']

def delete_all_faces(collection_id):
    faces = list_faces(collection_id)
    faces = [face['FaceId'] for face in faces]
    response = client.delete_faces(
        CollectionId=collection_id,
        FaceIds=faces
    )
    return response
