from src.s3_manager import S3CatalogManager
import boto3
from botocore.exceptions import ClientError
import json
import builtins
from unittest.mock import mock_open, MagicMock
import pytest

MOCK_MANIFEST = {
    "parts": {
        "filename": "parts.csv.gz",
    "hash": "parts_hash"
    },
    "categories": {
        "filename": "categories.csv.gz",
        "hash": "categories_hash"
    }
}

S3_KEY = "file.csv.gz"
LOCAL_FILE_PATH = "tmp/file.csv.gz"

@pytest.fixture
def mock_s3_client_working(monkeypatch):
    class MockS3Client:
        def download_file(self, Bucket, Key, Filename):
            pass
        def upload_file(self, Filename, Bucket, Key):
            pass
        def delete_object(self, Bucket, Key):
            pass
    monkeypatch.setattr(boto3, "client", lambda _: MockS3Client())
    return MockS3Client()

@pytest.fixture
def manager(monkeypatch, mock_s3_client_working):
    m = mock_open(read_data=json.dumps(MOCK_MANIFEST))
    monkeypatch.setattr(builtins, "open", m)
    
    return S3CatalogManager("test-bucket", "test-manifest.json", "test-tmp")

class TestFetchManifestLogic:
    def test_fetch_manifest_success(self, manager):
        assert manager.manifest == MOCK_MANIFEST

    def test_fetch_manifest_returns_empty_dict_when_client_error(self, monkeypatch):
        class MockS3Client:
            def download_file(self, Bucket, Key, Filename):
                raise ClientError()
        monkeypatch.setattr(boto3, "client", lambda _: MockS3Client())

        manager = S3CatalogManager("test-bucket", "test-manifest.json", "test-tmp")
        assert manager.manifest == {}

    def test_fetch_manifest_returns_empty_dict_when_corrupted_file(self, monkeypatch, mock_s3_client_working):
        m = mock_open(read_data="123_invalid_json")
        monkeypatch.setattr(builtins, "open", m)

        manager = S3CatalogManager("test-bucket", "test-manifest.json", "test-tmp")
        assert manager.manifest == {}

class TestCheckForChangesLogic:
    EXISTING_RESOURCE = "parts"
    EXISTING_HASH = MOCK_MANIFEST[EXISTING_RESOURCE]["hash"]
    NEW_RESOURCE = "colors"
    NEW_HASH = "new_hash"

    def test_check_for_changes_resource_changed(self, manager):
        assert manager.check_for_changes(self.EXISTING_RESOURCE, self.NEW_HASH) == True

    def test_check_for_changes_no_changes(self, manager):
        assert manager.check_for_changes(self.EXISTING_RESOURCE, self.EXISTING_HASH) == False

    def test_check_for_changes_new_resource(self, manager):
        assert manager.check_for_changes(self.NEW_RESOURCE, self.NEW_HASH) == True

    def test_check_for_changes_hash_missing(self, monkeypatch, manager):
        assert manager.check_for_changes(self.EXISTING_RESOURCE, None) == True

class TestUploadToS3Logic:
    def test_upload_to_s3_success(self, manager):
        assert manager.upload_to_s3(LOCAL_FILE_PATH, S3_KEY) is True

    def test_upload_to_s3_file_not_found(self, monkeypatch):
        class MockS3Client:
            def upload_file(self, Filename, Bucket, Key):
                raise FileNotFoundError()
        monkeypatch.setattr(boto3, "client", lambda _: MockS3Client())
 
        manager = S3CatalogManager("test-bucket", "manifest.json", "tmp")
        assert manager.upload_to_s3(LOCAL_FILE_PATH, S3_KEY) is False

    def test_upload_to_s3_client_error(self, monkeypatch):
        class MockS3Client:
            def upload_file(self, Filename, Bucket, Key):
                raise ClientError({"Error": {"Code": "500"}}, "Error")
        monkeypatch.setattr(boto3, "client", lambda _: MockS3Client())
 
        manager = S3CatalogManager("test-bucket", "manifest.json", "tmp")
        assert manager.upload_to_s3(LOCAL_FILE_PATH, S3_KEY) is False

    def test_upload_to_s3_passed_with_correct_bucket_and_key(self, manager):
        manager.client.upload_file = MagicMock()

        manager.upload_to_s3(LOCAL_FILE_PATH, S3_KEY)
        manager.client.upload_file.assert_called_once_with(LOCAL_FILE_PATH, manager.bucket, S3_KEY)

class TestRemoveFromS3Logic:
    def test_remove_from_s3_success(self, manager):
        assert manager.remove_from_s3(S3_KEY) is True

    def test_remove_from_s3_ghost_file(self, monkeypatch):
        class MockS3Client:
            def __init__(self):
                self.delete_object = MagicMock(return_value={"ResponseMetadata": {"HTTPStatusCode": 204}})
        mock_s3_client = MockS3Client()
        monkeypatch.setattr(boto3, "client", lambda _: mock_s3_client)

        manager = S3CatalogManager("test-bucket", "manifest.json", "tmp")
        non_existent_key = "non_existent_key"
        
        assert manager.remove_from_s3(non_existent_key) is True
        manager.client.delete_object.assert_called_once_with(Bucket=manager.bucket, Key=non_existent_key)

    def test_remove_from_s3_iam_permission_denied(self, monkeypatch):
        class MockS3Client:
            def __init__(self):
                self.delete_object = MagicMock(side_effect=ClientError({"Error": {"Code": "403"}}, "Error"))
        mock_s3_client = MockS3Client()
        monkeypatch.setattr(boto3, "client", lambda _: mock_s3_client)

        manager = S3CatalogManager("test-bucket", "manifest.json", "tmp")
        
        assert manager.remove_from_s3(S3_KEY) is False
        manager.client.delete_object.assert_called_once_with(Bucket=manager.bucket, Key=S3_KEY)

    def test_remove_from_s3_passed_with_correct_bucket_and_key(self, manager):
        manager.client.delete_object = MagicMock()

        manager.remove_from_s3(S3_KEY)

        manager.client.delete_object.assert_called_once_with(Bucket=manager.bucket, Key=S3_KEY)

class TestUpdateManifestLogic:
    EXISTING_RESOURCE = "parts"
    NEW_RESOURCE = "colors"
    NEW_FILENAME = "new_filename"
    NEW_HASH = "new_hash"

    def test_update_manifest_updates_existing_resource_success(self, manager):
        manager.update_manifest(self.EXISTING_RESOURCE, self.NEW_FILENAME, self.NEW_HASH)

        assert manager.manifest[self.EXISTING_RESOURCE] == {"filename": self.NEW_FILENAME, "hash": self.NEW_HASH}
        assert manager.manifest_changed is True

    def test_update_manifest_adds_new_resource_success(self, manager):
        manager.update_manifest(self.NEW_RESOURCE, self.NEW_FILENAME, self.NEW_HASH)

        assert manager.manifest[self.NEW_RESOURCE] == {"filename": self.NEW_FILENAME, "hash": self.NEW_HASH}
        assert manager.manifest_changed is True

    def test_update_manifest_io_error(self, monkeypatch, manager):
        def mock_open_io_error(*args, **kwargs):
            raise IOError("Access denied")
        monkeypatch.setattr(builtins, "open", mock_open_io_error)

        result = manager.update_manifest(self.EXISTING_RESOURCE, self.NEW_FILENAME, self.NEW_HASH)

        assert result is False
        assert manager.manifest[self.EXISTING_RESOURCE] == {"filename": self.NEW_FILENAME, "hash": self.NEW_HASH}
        assert manager.manifest_changed is False
        
class TestUploadManifestLogic:
    def test_upload_manifest_success(self):
        pass

    def test_upload_manifest_client_error(self):
        pass