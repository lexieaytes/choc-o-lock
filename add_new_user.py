# Standard
import argparse
import os

# Local
from database import *
from face_utils import *


def add_new_user(image_dir):
    if not os.path.isdir(image_dir):
        raise FileNotFoundError(f"'{image_dir}' is not a directory")

    first_name = input('Enter first name: ')
    last_name = input('Enter last name: ')
    print(f'Adding {first_name} {last_name} to database...')
    new_user = add_user_to_db(first_name, last_name)

    for image in os.listdir(image_dir):
        print(f"Indexing '{image}' into Rekognition...")
        full_path_to_image = os.path.join(image_dir, image)
        response = index_face(full_path_to_image, new_user.id, collection)
        if not response['FaceRecords']:
            print(f"Skipping '{image}'. No face detected")

    print('Finished adding new user')
    return new_user


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Add a new user for authentication with the Choc-o-Lock system')
    parser.add_argument('-i', '--imagedir', required=True, help='path to directory containing images of user')

    args = parser.parse_args()
    add_new_user(args.imagedir)



'''
{   'FaceModelVersion': '5.0',
    'FaceRecords': [   {   'Face': {   'BoundingBox': {   'Height': 0.7437556982040405,
                                                          'Left': 0.3012446463108063,
                                                          'Top': 0.13071659207344055,
                                                          'Width': 0.4871083199977875},
                                       'Confidence': 99.9964828491211,
                                       'ExternalImageId': '3267ed11-ae06-48cf-9bb3-59e5e6b2ae39',
                                       'FaceId': '5c108177-6050-41f3-93b9-5b3877a2aa70',
                                       'ImageId': '584415a6-adbe-3696-8e95-6fc379ed457d'},
                           'FaceDetail': {   'BoundingBox': {   'Height': 0.7437556982040405,
                                                                'Left': 0.3012446463108063,
                                                                'Top': 0.13071659207344055,
                                                                'Width': 0.4871083199977875},
                                             'Confidence': 99.9964828491211,
                                             'Landmarks': [   {   'Type': 'eyeLeft',
                                                                  'X': 0.4835874140262604,
                                                                  'Y': 0.44311776757240295},
                                                              {   'Type': 'eyeRight',
                                                                  'X': 0.7089918851852417,
                                                                  'Y': 0.45362067222595215},
                                                              {   'Type': 'mouthLeft',
                                                                  'X': 0.4850400686264038,
                                                                  'Y': 0.6750281453132629},
                                                              {   'Type': 'mouthRight',
                                                                  'X': 0.6735813021659851,
                                                                  'Y': 0.683603823184967},
                                                              {   'Type': 'nose',
                                                                  'X': 0.6127387285232544,
                                                                  'Y': 0.5930704474449158}],
                                             'Pose': {   'Pitch': -2.29068660736084,
                                                         'Roll': 1.9217547178268433,
                                                         'Yaw': 10.575569152832031},
                                             'Quality': {   'Brightness': 90.90770721435547,
                                                            'Sharpness': 86.86019134521484}}}],
    'ResponseMetadata': {   'HTTPHeaders': {   'connection': 'keep-alive',
                                               'content-length': '1050',
                                               'content-type': 'application/x-amz-json-1.1',
                                               'date': 'Sat, 14 Nov 2020 '
                                                       '03:31:44 GMT',
                                               'x-amzn-requestid': 'a50fa4b0-2a8d-4d21-b186-87d4cf1e6075'},
                            'HTTPStatusCode': 200,
                            'RequestId': 'a50fa4b0-2a8d-4d21-b186-87d4cf1e6075',
                            'RetryAttempts': 0},
    'UnindexedFaces': []}
'''
