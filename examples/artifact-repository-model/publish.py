"""A tiny local artifact identity exercise; no AWS APIs or credentials are used."""
import hashlib
import json
from pathlib import Path
import re


IDENTIFIER = re.compile(r"[A-Za-z0-9][A-Za-z0-9._+-]{0,79}\Z")


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def location(root: Path, name: str, version: str) -> Path:
    if not IDENTIFIER.fullmatch(name) or not IDENTIFIER.fullmatch(version):
        raise ValueError("Use a simple artifact name and explicit version")
    return root / name / version


def publish(root: Path, name: str, version: str, source: Path) -> dict:
    destination = location(root, name, version)
    if destination.exists():
        raise FileExistsError(f"Version already exists: {name}@{version}")
    data = source.read_bytes()
    destination.mkdir(parents=True)
    (destination / "artifact.bin").write_bytes(data)
    receipt = {"name": name, "version": version, "sha256": digest(data), "bytes": len(data)}
    (destination / "receipt.json").write_text(json.dumps(receipt, sort_keys=True) + "\n")
    return receipt


def retrieve(root: Path, name: str, version: str) -> bytes:
    destination = location(root, name, version)
    receipt = json.loads((destination / "receipt.json").read_text())
    data = (destination / "artifact.bin").read_bytes()
    if receipt.get("name") != name or receipt.get("version") != version:
        raise ValueError("Receipt identity does not match the requested artifact")
    if receipt.get("sha256") != digest(data) or receipt.get("bytes") != len(data):
        raise ValueError("Stored bytes do not match the receipt")
    return data


def retention_preview(root: Path, name: str, keep: int) -> list[str]:
    """Return old-version candidates only; preview never deletes data."""
    versions = sorted((root / name).iterdir(), key=lambda path: path.name)
    if keep < 1:
        raise ValueError("Keep at least one version")
    return [path.name for path in versions[:-keep]]


def main() -> None:
    from tempfile import TemporaryDirectory

    with TemporaryDirectory(prefix="artifact-model-") as directory:
        root = Path(directory) / "repository"
        source = Path(directory) / "website.zip"
        source.write_bytes(b"release bytes: Tuesday\n")
        first = publish(root, "repair-site", "1.0.0", source)
        source.write_bytes(b"release bytes: Wednesday\n")
        second = publish(root, "repair-site", "1.1.0", source)
        assert retrieve(root, "repair-site", "1.0.0") == b"release bytes: Tuesday\n"
        assert retrieve(root, "repair-site", "1.1.0") == b"release bytes: Wednesday\n"
        assert first["sha256"] != second["sha256"]
        try:
            publish(root, "repair-site", "1.0.0", source)
        except FileExistsError:
            pass
        else:
            raise AssertionError("An existing version must not be overwritten")
        stored = root / "repair-site" / "1.1.0" / "artifact.bin"
        stored.write_bytes(b"silently replaced bytes\n")
        try:
            retrieve(root, "repair-site", "1.1.0")
        except ValueError as error:
            assert "do not match" in str(error)
        else:
            raise AssertionError("Changed bytes must fail the receipt check")
        assert retention_preview(root, "repair-site", keep=1) == ["1.0.0"]
        assert (root / "repair-site" / "1.0.0" / "artifact.bin").is_file()
        print("PASS: explicit versions, no overwrite, digest mismatch detected.")
        print("Retention preview selected 1.0.0; preview did not delete it.")
        print("Local filesystem model only; no AWS service behavior was tested.")


if __name__ == "__main__":
    import sys
    if sys.flags.optimize:
        raise SystemExit("Run without Python optimization")
    main()
