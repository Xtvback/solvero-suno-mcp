"""Safe three-file Drive transfer orchestration.

Dependency-injected connector with list_names(folder_id), upload(folder_id,name,source),
fetch_sha256(file_id), and delete(file_id). Never logs binary data or credentials.
Rollback deletes ONLY confirmed new IDs from this invocation, and only if the
uploaded resource can be verified as still owned by this operation.
This is not atomic; concurrent writers require server-side preconditions.
"""
from dataclasses import dataclass
from typing import Protocol

@dataclass(frozen=True)
class Component:
    name: str
    source: object
    sha256: str

class DrivePort(Protocol):
    def list_names(self, folder_id: str) -> list[str]: ...
    def upload(self, folder_id: str, name: str, source: object) -> dict: ...
    def fetch_sha256(self, file_id: str) -> str: ...
    def delete(self, file_id: str) -> bool: ...

class TransferFailure(RuntimeError):
    def __init__(self, message, created_ids, cleanup_results):
        super().__init__(message)
        self.created_ids = tuple(created_ids)
        self.cleanup_results = cleanup_results

def transfer_verified(port: DrivePort, folder_id: str, components: list[Component],
                      *, allow_test_cleanup: bool = False) -> dict:
    if len(components) != 3 or len({x.name.casefold() for x in components}) != 3:
        raise ValueError("Exactly three uniquely named components required")
    if not folder_id or any(not x.name or not x.sha256 or len(x.sha256) != 64 for x in components):
        raise ValueError("Missing folder, filename, or SHA256")
    created = []
    verified = []
    try:
        for item in components:
            # Re-read just before EACH upload. Cannot replace atomic create-if-absent.
            current = port.list_names(folder_id)
            if any(x.casefold() == item.name.casefold() for x in current):
                raise FileExistsError("Target name exists: " + item.name)
            result = port.upload(folder_id, item.name, item.source)
            if result.get("created") is not True or not result.get("id") or result.get("parent_id") != folder_id or result.get("name") != item.name:
                # If connector created a resource but returned uncertain metadata, do
                # not guess its ownership or delete it. Surface manual inspection.
                raise RuntimeError("Upload result not safely attributable: " + item.name)
            created.append({"id":result["id"],"name":item.name})
            actual = port.fetch_sha256(result["id"])
            if actual != item.sha256:
                raise ValueError("Remote SHA256 mismatch: " + item.name)
            verified.append(result["id"])
        return {"status":"verified","created_ids":[x["id"] for x in created],
                "verified_ids":verified,"cleanup_performed":False}
    except Exception as error:
        cleanup = []
        if allow_test_cleanup:
            for resource in reversed(created):
                try:
                    # Deletion is scoped strictly to uploaded IDs recorded above.
                    ok = port.delete(resource["id"])
                    cleanup.append({"id":resource["id"],"deleted":ok})
                except Exception:
                    cleanup.append({"id":resource["id"],"deleted":False})
        raise TransferFailure(str(error), [x["id"] for x in created], cleanup) from error
