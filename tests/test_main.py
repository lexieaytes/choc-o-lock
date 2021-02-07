import pytest

from unittest.mock import patch, Mock

from main import *

class TestGetEnv:

    test_var = 'TEST_ENV_VARIABLE'
        
    @patch('os.getenv', return_value='mocked_value')
    def test_valid(self, mock_getenv):
        result = getenv(self.test_var)
        mock_getenv.assert_called_once_with(self.test_var)
        assert result == 'mocked_value'

    @patch('os.getenv', return_value=None)
    def test_invalid(self, mock_getenv):
        with pytest.raises(ValueError):
            getenv(self.test_var)

a = {'DetectedFace': {'BoundingBox': {'Height': 0.45408943, 'Width': 0.23616561, 'Left': 0.4157195, 'Top': 0.40063164}, 'Confidence': 99.99786, 'Landmarks': [{'X': 0.478196, 'Y': 0.58581376, 'Type': 'eyeLeft'}, {'X': 0.5845851, 'Y': 0.57766896, 'Type': 'eyeRight'}, {'X': 0.49412093, 'Y': 0.7521364, 'Type': 'mouthLeft'}, {'X': 0.58304405, 'Y': 0.74526626, 'Type': 'mouthRight'}, {'X': 0.53912395, 'Y': 0.68752277, 'Type': 'nose'}], 'Pose': {'Pitch': -0.51267076, 'Roll': -4.3871083, 'Yaw': 1.2388688}, 'Quality': {'Brightness': 68.50818, 'Sharpness': 46.0298}}, 'MatchedFaces': [{'Similarity': 99.93723, 'Face': {'BoundingBox': {'Height': 0.743756, 'Width': 0.487108, 'Left': 0.301245, 'Top': 0.130717}, 'FaceId': 'd7d59fd8-7dfb-497f-aa09-654a66a5b2a1', 'Confidence': 99.9965, 'ImageId': '7a05d47d-7bbc-3ad9-bbdb-74bd766a8957', 'ExternalImageId': '3d2cf3ab-3beb-43e2-8065-86d4e0f99035'}}]}

class TestGetUserFromFace:

    def test_unknown(self):
        faces = {'MatchedFaces': []}
        db = Mock()
        result = get_user_from_face(db, faces)
        assert result is Unknown

    def test_known(self):
        known_user = User('Tony', 'Stark', '12345-mock-id')
        faces = {'MatchedFaces': [
            {
                'Face': {'ExternalImageId': '12345-mock-id'},
                'Similarity': 99.15
            }
        ]}
        db = Mock()
        db.get_user.return_value = known_user
        result = get_user_from_face(db, faces)
        assert result is known_user 