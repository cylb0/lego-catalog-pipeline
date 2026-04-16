from src.storage import S3CatalogManager
import boto3
from botocore.exceptions import ClientError
import json
import builtins
from unittest.mock import mock_open, MagicMock, patch
import pytest
import pandas

MOCK_MANIFEST = {
    "ingestion": {
        "csv_resources": {
            "parts": {"filename": "parts.csv.gz", "hash": "parts_hash"},
            "categories": {"filename": "categories.csv.gz", "hash": "categories_hash"},
        }
    }
}

S3_KEY = "file.csv.gz"
LOCAL_FILE_PATH = "tmp/file.csv.gz"


@pytest.fixture
def mock_s3_client_working(monkeypatch):
    class MockS3Client:
        def __init__(self):
            self.get_paginator = MagicMock()
            self.get_object = MagicMock()

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
        assert manager.manifest.data == MOCK_MANIFEST

    def test_fetch_manifest_returns_empty_dict_when_client_error(self, monkeypatch):
        class MockS3Client:
            def download_file(self, Bucket, Key, Filename):
                raise ClientError()

        monkeypatch.setattr(boto3, "client", lambda _: MockS3Client())

        manager = S3CatalogManager("test-bucket", "test-manifest.json", "test-tmp")
        assert manager.manifest.data == {}

    def test_fetch_manifest_returns_empty_dict_when_corrupted_file(
        self, monkeypatch, mock_s3_client_working
    ):
        m = mock_open(read_data="123_invalid_json")
        monkeypatch.setattr(builtins, "open", m)

        manager = S3CatalogManager("test-bucket", "test-manifest.json", "test-tmp")
        assert manager.manifest.data == {}


class TestCheckForResourceChangesLogic:
    EXISTING_RESOURCE = "parts"
    EXISTING_HASH = MOCK_MANIFEST["ingestion"]["csv_resources"][EXISTING_RESOURCE][
        "hash"
    ]
    NEW_RESOURCE = "colors"
    NEW_HASH = "new_hash"

    def test_check_for_resource_changes_resource_changed(self, manager):
        assert manager.check_for_resource_changes(self.EXISTING_RESOURCE, self.NEW_HASH)

    def test_check_for_resource_changes_no_changes(self, manager):
        assert not manager.check_for_resource_changes(
            self.EXISTING_RESOURCE, self.EXISTING_HASH
        )

    def test_check_for_resource_changes_new_resource(self, manager):
        assert manager.check_for_resource_changes(self.NEW_RESOURCE, self.NEW_HASH)

    def test_check_for_resource_changes_hash_missing(self, monkeypatch, manager):
        assert manager.check_for_resource_changes(self.EXISTING_RESOURCE, None)


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
        manager.client.upload_file.assert_called_once_with(
            LOCAL_FILE_PATH, manager.bucket, S3_KEY
        )


class TestRemoveFromS3Logic:
    def test_remove_from_s3_success(self, manager):
        assert manager.remove_from_s3(S3_KEY) is True

    def test_remove_from_s3_ghost_file(self, monkeypatch):
        class MockS3Client:
            def __init__(self):
                self.delete_object = MagicMock(
                    return_value={"ResponseMetadata": {"HTTPStatusCode": 204}}
                )

        mock_s3_client = MockS3Client()
        monkeypatch.setattr(boto3, "client", lambda _: mock_s3_client)

        manager = S3CatalogManager("test-bucket", "manifest.json", "tmp")
        non_existent_key = "non_existent_key"

        assert manager.remove_from_s3(non_existent_key) is True
        manager.client.delete_object.assert_called_once_with(
            Bucket=manager.bucket, Key=non_existent_key
        )

    def test_remove_from_s3_iam_permission_denied(self, monkeypatch):
        class MockS3Client:
            def __init__(self):
                self.delete_object = MagicMock(
                    side_effect=ClientError({"Error": {"Code": "403"}}, "Error")
                )

        mock_s3_client = MockS3Client()
        monkeypatch.setattr(boto3, "client", lambda _: mock_s3_client)

        manager = S3CatalogManager("test-bucket", "manifest.json", "tmp")

        assert manager.remove_from_s3(S3_KEY) is False
        manager.client.delete_object.assert_called_once_with(
            Bucket=manager.bucket, Key=S3_KEY
        )

    def test_remove_from_s3_passed_with_correct_bucket_and_key(self, manager):
        manager.client.delete_object = MagicMock()

        manager.remove_from_s3(S3_KEY)

        manager.client.delete_object.assert_called_once_with(
            Bucket=manager.bucket, Key=S3_KEY
        )


class TestUpdateManifestResourceLogic:
    EXISTING_RESOURCE = "parts"
    NEW_RESOURCE = "colors"
    NEW_FILENAME = "new_filename"
    NEW_HASH = "new_hash"

    def test_update_manifest_resource_updates_existing_resource_success(self, manager):
        manager.update_manifest_resource(
            self.EXISTING_RESOURCE, self.NEW_FILENAME, self.NEW_HASH
        )

        assert manager.manifest.data["ingestion"]["csv_resources"][
            self.EXISTING_RESOURCE
        ] == {"filename": self.NEW_FILENAME, "hash": self.NEW_HASH}
        assert manager.manifest.changed is True

    def test_update_manifest_resource_adds_new_resource_success(self, manager):
        manager.update_manifest_resource(
            self.NEW_RESOURCE, self.NEW_FILENAME, self.NEW_HASH
        )

        assert manager.manifest.data["ingestion"]["csv_resources"][
            self.NEW_RESOURCE
        ] == {"filename": self.NEW_FILENAME, "hash": self.NEW_HASH}
        assert manager.manifest.changed is True

    def test_update_manifest_resource_io_error(self, monkeypatch, manager):
        def mock_open_io_error(*args, **kwargs):
            raise IOError("Access denied")

        monkeypatch.setattr(builtins, "open", mock_open_io_error)

        result = manager.update_manifest_resource(
            self.EXISTING_RESOURCE, self.NEW_FILENAME, self.NEW_HASH
        )

        assert result is False
        assert manager.manifest.data["ingestion"]["csv_resources"][
            self.EXISTING_RESOURCE
        ] == {"filename": self.NEW_FILENAME, "hash": self.NEW_HASH}
        assert manager.manifest.changed is True


class TestUploadManifestLogic:
    def test_upload_manifest_no_changes(self, manager):
        manager.manifest.changed = False

        with patch.object(manager, "upload_to_s3") as mock_upload_to_s3:
            result = manager.upload_manifest()

            assert result is True
            mock_upload_to_s3.assert_not_called()

    def test_upload_manifest_success(self, manager):
        manager.manifest.changed = True

        with patch.object(
            manager, "upload_to_s3", return_value=True
        ) as mock_upload_to_s3:
            result = manager.upload_manifest()

            assert result is True
            mock_upload_to_s3.assert_called_once_with(
                manager.local_manifest_path, manager.manifest_key
            )

    def test_upload_manifest_client_error(self, manager):
        manager.manifest.changed = True

        manager.upload_to_s3 = MagicMock(return_value=False)

        result = manager.upload_manifest()

        assert result is False
        assert manager.manifest.changed is True
        manager.upload_to_s3.assert_called_once()


class TestGetExistingGlbsListLogic:
    def test_get_existing_glbs_list_success(self, manager):
        mock_paginator = MagicMock()
        manager.client.get_paginator.return_value = mock_paginator

        mock_paginator.paginate.return_value = (
            {
                "Contents": [
                    {"Key": "parts/3001.glb"},
                    {"Key": "parts/3003.glb"},
                ]
            },
            {
                "Contents": [
                    {"Key": "parts/3005.glb"},
                ]
            },
        )

        result = manager._get_existing_glbs_list()

        assert result == {"3001", "3003", "3005"}
        manager.client.get_paginator.assert_called_once_with("list_objects_v2")
        mock_paginator.paginate.assert_called_once_with(
            Bucket=manager.bucket, Prefix="glbs/"
        )

    def test_get_existing_glbs_list_empty(self, manager):
        mock_paginator = MagicMock()
        manager.client.get_paginator.return_value = mock_paginator

        mock_paginator.paginate.return_value = {}

        result = manager._get_existing_glbs_list()

        assert result == set()
        manager.client.get_paginator.assert_called_once_with("list_objects_v2")
        mock_paginator.paginate.assert_called_once_with(
            Bucket=manager.bucket, Prefix="glbs/"
        )

    def test_get_existing_glbs_list_ignore_non_glb_files(self, manager):
        mock_paginator = MagicMock()
        manager.client.get_paginator.return_value = mock_paginator

        mock_paginator.paginate.return_value = (
            {
                "Contents": [
                    {"Key": "parts/3001.glb"},
                    {"Key": "parts/3001.mp3"},
                    {"Key": "parts/3003.glb"},
                ]
            },
            {
                "Contents": [
                    {"Key": "parts/3005.glb"},
                    {"Key": "parts/3006.txt"},
                ]
            },
        )

        result = manager._get_existing_glbs_list()

        assert result == {"3001", "3003", "3005"}
        manager.client.get_paginator.assert_called_once_with("list_objects_v2")
        mock_paginator.paginate.assert_called_once_with(
            Bucket=manager.bucket, Prefix="glbs/"
        )


class TestGetPartIdsFromCSVLogic:
    def test_get_part_ids_from_csv_success(self, manager):
        manager.get_csv_filename = MagicMock(return_value="test_parts.csv.gz")

        with (
            patch.object(manager.client, "get_object") as mock_get,
            patch("gzip.GzipFile"),
            patch("pandas.read_csv") as mock_read,
        ):
            mock_read.return_value = pandas.DataFrame({"part_num": ["3001", "3003"]})

            result = manager._get_part_ids_from_csv()

            assert result == {"3001", "3003"}
            mock_get.assert_called_once_with(
                Bucket=manager.bucket, Key="test_parts.csv.gz"
            )

    def test_get_part_ids_from_csv_missing_filename(self, manager):
        manager.get_csv_filename = MagicMock(return_value="")

        with (
            patch.object(manager.client, "get_object") as mock_get,
            patch("gzip.GzipFile") as mock_gzip,
            patch("pandas.read_csv") as mock_read,
        ):
            result = manager._get_part_ids_from_csv()

            assert result == set()
            mock_get.assert_not_called()
            mock_gzip.assert_not_called()
            mock_read.assert_not_called()

    def test_get_part_ids_from_csv_different_datatype_part_nums(self, manager):
        manager.get_csv_filename = MagicMock(return_value="test_parts.csv.gz")

        with (
            patch.object(manager.client, "get_object") as mock_get,
            patch("gzip.GzipFile"),
            patch("pandas.read_csv") as mock_read,
        ):
            mock_read.return_value = pandas.DataFrame(
                {"part_num": [3001, "3003", "3245a"]}
            )

            result = manager._get_part_ids_from_csv()

            assert result == {"3001", "3003", "3245a"}
            mock_get.assert_called_once_with(
                Bucket=manager.bucket, Key="test_parts.csv.gz"
            )

    def test_get_part_ids_from_csv_duplicate_part_nums(self, manager):
        manager.get_csv_filename = MagicMock(return_value="test_parts.csv.gz")

        with (
            patch.object(manager.client, "get_object") as mock_get,
            patch("gzip.GzipFile"),
            patch("pandas.read_csv") as mock_read,
        ):
            mock_read.return_value = pandas.DataFrame(
                {"part_num": ["3001", "3003", "3001"]}
            )

            result = manager._get_part_ids_from_csv()

            assert result == {"3001", "3003"}
            mock_get.assert_called_once_with(
                Bucket=manager.bucket, Key="test_parts.csv.gz"
            )

    def test_get_part_ids_from_csv_corrupted_csv(self, manager):
        manager.get_csv_filename = MagicMock(return_value="corrupted_parts.csv.gz")

        with (
            patch.object(manager.client, "get_object") as mock_get,
            patch("gzip.GzipFile") as mock_gzip,
            patch("pandas.read_csv") as mock_read,
        ):
            mock_gzip.side_effect = Exception("Corrupted gzip file")

            result = manager._get_part_ids_from_csv()

            assert result == set()
            mock_get.assert_called_once_with(
                Bucket=manager.bucket, Key="corrupted_parts.csv.gz"
            )
            mock_read.assert_not_called()

    def test_get_part_ids_from_csv_empty_csv(self, manager):
        manager.get_csv_filename = MagicMock(return_value="empty_parts.csv.gz")

        with (
            patch.object(manager.client, "get_object") as mock_get,
            patch("gzip.GzipFile"),
            patch("pandas.read_csv") as mock_read,
        ):
            mock_read.return_value = pandas.DataFrame({"part_num": []})

            result = manager._get_part_ids_from_csv()

            assert result == set()
            mock_get.assert_called_once_with(
                Bucket=manager.bucket, Key="empty_parts.csv.gz"
            )


class TestSyncStateLogic:
    def test_get_sync_state_success(self, manager):
        manager._get_part_ids_from_csv = MagicMock(return_value={"a", "b", "c"})
        manager._get_existing_glbs_list = MagicMock(return_value={"a"})
        manager.manifest.get_ldraw_index = MagicMock(return_value={"a", "b"})

        state = manager.get_sync_state()

        assert state["to_convert_state"] == {"b"}
