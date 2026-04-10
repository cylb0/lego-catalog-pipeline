class CatalogManifest:
    def __init__(self, data: dict):
        self.data = data or {}
        self.changed = False

    def check_csv_change(self, resource: str, new_hash: str) -> bool:
        section = self.data.get("ingestion", {}).get("csv_resources", {})
        return section.get(resource, {}).get("hash") != new_hash
        
    def update_csv_resource(self, resource: str, new_filename: str, new_hash: str) -> bool:
        ingestion = self.data.setdefault("ingestion", {})
        csv_resources = ingestion.setdefault("csv_resources", {})
        csv_resources[resource] = {"filename": new_filename, "hash": new_hash}
        self.changed = True

    def update_ldraw(self, filename: str, version: str) -> bool:
        ingestion = self.data.setdefault("ingestion", {})
        ldraw = ingestion.setdefault("ldraw", {})
        ldraw["filename"] = filename
        ldraw["version"] = version
        self.changed = True