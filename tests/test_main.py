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


class TestGetUserFromFace:

    def test_unknown(self):
        faces = {'MatchedFaces': []}
        db = Mock()
        result = get_user_from_face(db, faces)
        assert result is Unknown

    def test_known(self):
        known_user = User('First', 'Last', '12345-mock-id')
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