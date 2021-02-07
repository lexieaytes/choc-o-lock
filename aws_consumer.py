# Third-party
from kinesis.consumer import KinesisConsumer

class Consumer:

    def __init__(self, aws_stream_name):
        self.consumer = iter(KinesisConsumer(stream_name=aws_stream_name))

    def get_faces_in_video(self):
        message = next(self.consumer)
        data = eval(message['Data'])
        faces = data['FaceSearchResponse']
        return faces