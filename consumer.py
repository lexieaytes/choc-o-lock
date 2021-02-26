from kinesis.consumer import KinesisConsumer

from classes import Unknown 
from logger import logger


def get_user_from_face(db, face):
        matched_faces = face['MatchedFaces']

        if not matched_faces:
            # Face didn't match any known users
            return Unknown

        top_match = matched_faces[0]
        user_id = top_match['Face']['ExternalImageId']
        user = db.get_user(user_id)
        logger.debug(f'Recognized: {user.first_name} {user.last_name}') 
        logger.debug(f'Similarity: {top_match["Similarity"]}')
        return user


def get_users_in_video(db, kc):
    return [get_user_from_face(db, face) for face in kc.get_faces_in_video()]


class Consumer:

    def __init__(self, aws_stream_name):
        self.consumer = iter(KinesisConsumer(stream_name=aws_stream_name))

    def get_faces_in_video(self):
        message = next(self.consumer)
        data = eval(message['Data'])
        faces = data['FaceSearchResponse']
        return faces
