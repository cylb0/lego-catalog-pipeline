from src.core import CatalogManifest
import pytest

LAST_MODIFIED_DATE = "Mon, 13 Apr 2026 00:00:00 GMT"
NEW_MODIFIED_DATE = "Tue, 14 Apr 2026 00:00:01 GMT"


@pytest.fixture
def manifest():
    return CatalogManifest(
        {
            "ingestion": {
                "csv_resources": {
                    "parts": {"filename": "parts.csv", "hash": "old_hash"}
                },
                "ldraw": {
                    "filename": "ldraw.zip",
                    "last_modified": LAST_MODIFIED_DATE,
                },
            }
        }
    )


class TestCatalogManifestCheckCSVChange:
    def test_check_csv_change_resource_changed(self, manifest):
        assert manifest.check_csv_change("parts", "new_hash")

    def test_check_csv_change_no_change(self, manifest):
        assert not manifest.check_csv_change("parts", "old_hash")

    def test_check_csv_change_new_resource(self, manifest):
        assert manifest.check_csv_change("colors", "new_hash")

    def test_check_csv_change_empty_manifest(self):
        manifest = CatalogManifest({})
        assert manifest.check_csv_change("parts", "new_hash")

    def test_check_csv_change_hash_missing(self):
        manifest = CatalogManifest(
            {"ingestion": {"csv_resources": {"parts": {"filename": "parts.csv"}}}}
        )
        assert manifest.check_csv_change("parts", "new_hash")


class TestCatalogManifestUpdateCSVResource:
    def test_update_csv_resource_empty_manifest(self):
        manifest = CatalogManifest({})

        result = manifest.update_csv_resource("parts", "parts.csv", "hash")

        assert result
        assert manifest.changed
        assert manifest.data["ingestion"]["csv_resources"]["parts"] == {
            "filename": "parts.csv",
            "hash": "hash",
        }

    def test_update_csv_resource_existing_resource(self, manifest):
        assert manifest.update_csv_resource("parts", "parts.csv", "new_hash")
        assert manifest.changed
        assert (
            manifest.data["ingestion"]["csv_resources"]["parts"]["hash"] == "new_hash"
        )

    def test_update_csv_resource_existing_resource_no_change(self, manifest):
        assert not manifest.update_csv_resource("parts", "parts.csv", "old_hash")
        assert not manifest.changed

    def test_update_csv_resource_new_resource(self, manifest):
        assert manifest.update_csv_resource("colors", "colors.csv", "new_hash")
        assert manifest.changed
        assert manifest.data["ingestion"]["csv_resources"]["colors"] == {
            "filename": "colors.csv",
            "hash": "new_hash",
        }

    def test_update_csv_resource_empty_ingestion(self):
        manifest = CatalogManifest({"ingestion": {}})
        assert manifest.update_csv_resource("parts", "parts.csv", "hash")
        assert manifest.data["ingestion"]["csv_resources"]["parts"] == {
            "filename": "parts.csv",
            "hash": "hash",
        }

    def test_update_csv_resource_empty_csv_resources(self):
        manifest = CatalogManifest({"ingestion": {"csv_resources": {}}})
        assert manifest.update_csv_resource("parts", "parts.csv", "hash")
        assert manifest.data["ingestion"]["csv_resources"]["parts"] == {
            "filename": "parts.csv",
            "hash": "hash",
        }


class TestCatalogManifestCheckLDrawChange:
    def test_check_ldraw_change_no_change(self, manifest):
        assert not manifest.check_ldraw_change(LAST_MODIFIED_DATE)

    def test_check_ldraw_change_new_ldraw(self, manifest):
        assert manifest.check_ldraw_change(NEW_MODIFIED_DATE)

    def test_check_ldraw_change_empty_manifest(self):
        manifest = CatalogManifest({})
        assert manifest.check_ldraw_change(NEW_MODIFIED_DATE)

    def test_check_ldraw_change_empty_ingestion(self):
        manifest = CatalogManifest({"ingestion": {}})
        assert manifest.check_ldraw_change(NEW_MODIFIED_DATE)

    def test_check_ldraw_change_empty_ldraw(self):
        manifest = CatalogManifest({"ingestion": {"ldraw": {}}})
        assert manifest.check_ldraw_change(NEW_MODIFIED_DATE)


class TestCalatogManifestUpdateLdraw:
    def test_update_ldraw_empty_manifest(self):
        manifest = CatalogManifest({})
        assert manifest.update_ldraw("ldraw.zip", LAST_MODIFIED_DATE)
        assert manifest.changed
        assert manifest.data["ingestion"]["ldraw"] == {
            "filename": "ldraw.zip",
            "last_modified": LAST_MODIFIED_DATE,
        }

    def test_update_ldraw_new_ldraw(self, manifest):
        assert manifest.update_ldraw("ldraw.zip", NEW_MODIFIED_DATE)
        assert manifest.changed
        assert manifest.data["ingestion"]["ldraw"] == {
            "filename": "ldraw.zip",
            "last_modified": NEW_MODIFIED_DATE,
        }

    def test_update_ldraw_no_change(self, manifest):
        assert not manifest.update_ldraw("ldraw.zip", LAST_MODIFIED_DATE)
        assert not manifest.changed

    def test_update_ldraw_empty_ingestion(self):
        manifest = CatalogManifest({"ingestion": {}})
        assert manifest.update_ldraw("ldraw.zip", LAST_MODIFIED_DATE)
        assert manifest.changed
        assert manifest.data["ingestion"]["ldraw"] == {
            "filename": "ldraw.zip",
            "last_modified": LAST_MODIFIED_DATE,
        }

    def test_update_ldraw_empty_ldraw(self):
        manifest = CatalogManifest({"ingestion": {"ldraw": {}}})
        assert manifest.update_ldraw("ldraw.zip", LAST_MODIFIED_DATE)
        assert manifest.changed
        assert manifest.data["ingestion"]["ldraw"] == {
            "filename": "ldraw.zip",
            "last_modified": LAST_MODIFIED_DATE,
        }


class TestCatalogManifestUpdateLdrawIndex:
    existing_index = {"3001": {}, "3003": {}}
    new_index = {"3001": {}, "3003": {}, "3004": {}}

    def test_update_ldraw_index_empty_manifest(self):
        manifest = CatalogManifest({})
        assert manifest.update_ldraw_index(self.existing_index)
        assert manifest.changed
        assert manifest.data["ingestion"]["ldraw"]["index"] == self.existing_index

    def test_update_ldraw_new_ldraw_index(self, manifest):
        manifest.data["ingestion"]["ldraw"]["index"] = self.existing_index
        assert manifest.update_ldraw_index(self.new_index)
        assert manifest.changed
        assert manifest.data["ingestion"]["ldraw"]["index"] == self.new_index

    def test_update_ldraw_no_change(self, manifest):
        manifest.data["ingestion"]["ldraw"]["index"] = self.existing_index
        assert not manifest.update_ldraw_index(self.existing_index)
        assert not manifest.changed

    def test_update_ldraw_empty_ingestion(self, manifest):
        manifest.data["ingestion"] = {}
        assert manifest.update_ldraw_index(self.existing_index)
        assert manifest.changed
        assert manifest.data["ingestion"]["ldraw"]["index"] == self.existing_index

    def test_update_ldraw_empty_ldraw(self, manifest):
        manifest.data["ingestion"]["ldraw"] = {}
        assert manifest.update_ldraw_index(self.existing_index)
        assert manifest.changed
        assert manifest.data["ingestion"]["ldraw"]["index"] == self.existing_index
