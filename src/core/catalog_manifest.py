class CatalogManifest:
    def __init__(self, data: dict):
        self.data = data or {}
        self.changed = False

    def get_csv_filename(self, resource: str) -> str:
        return (
            self.data.get("ingestion", {})
            .get("csv_resources", {})
            .get(resource, {})
            .get("filename", "")
        )

    def get_ldraw_filename(self) -> str:
        return self.data.get("ingestion", {}).get("ldraw", {}).get("filename", "")

    def get_ldraw_last_modified(self) -> str:
        return self.data.get("ingestion", {}).get("ldraw", {}).get("last_modified", "")

    def check_csv_change(self, resource: str, new_hash: str) -> bool:
        """
        Check if the CSV resource has changed.

        :param resource: The name of the CSV resource.
        :param new_hash: The new hash of the CSV resource.
        :return: True if the CSV resource has changed, False otherwise.
        """
        section = self.data.get("ingestion", {}).get("csv_resources", {})
        return section.get(resource, {}).get("hash") != new_hash

    def update_csv_resource(
        self, resource: str, new_filename: str, new_hash: str
    ) -> bool:
        """
        Update the CSV resource if it has changed.

        :param resource: The name of the CSV resource.
        :param new_filename: The new filename of the CSV resource.
        :param new_hash: The new hash of the CSV resource.
        :return: True if the CSV resource has changed, False otherwise.
        """
        if not self.check_csv_change(resource, new_hash):
            return False

        ingestion = self.data.setdefault("ingestion", {})
        csv_resources = ingestion.setdefault("csv_resources", {})

        csv_resources[resource] = {"filename": new_filename, "hash": new_hash}
        self.changed = True

        return True

    def check_ldraw_change(self, last_modified: str) -> bool:
        """
        Check if the LDraw resource has changed.

        :param last_modified: The last modified date of the LDraw resource.
        :return: True if the LDraw resource has changed, False otherwise.
        """
        section = self.data.get("ingestion", {}).get("ldraw", {})
        return section.get("last_modified") != last_modified

    def update_ldraw(self, filename: str, last_modified: str) -> bool:
        """
        Update the LDraw resource if it has changed.

        :param filename: The filename of the LDraw resource.
        :param last_modified: The last modified date of the LDraw resource.
        :return: True if the LDraw resource has changed, False otherwise.
        """
        if not self.check_ldraw_change(last_modified):
            return False

        ingestion = self.data.setdefault("ingestion", {})

        ingestion["ldraw"] = {"filename": filename, "last_modified": last_modified}
        self.changed = True

        return True
