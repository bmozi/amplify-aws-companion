"""Copy only browser build inputs into the separately locked publisher directory."""

from pathlib import Path
import shutil


BASE = Path(__file__).resolve().parents[1]
SOURCE = BASE / "app"
TARGET = SOURCE / "frontend-publisher"
DIRECTORIES = ("src", "public")
FILES = ("index.html", "vite.config.ts")


def require_regular_tree(path: Path) -> None:
    for member in (path, *path.rglob("*")):
        if member.is_symlink() or not (member.is_dir() or member.is_file()):
            raise ValueError(f"Unsupported browser source entry: {member}")


def stage() -> None:
    target = TARGET
    if target.is_symlink():
        raise ValueError("Refusing symlink publisher directory")
    target.mkdir(parents=True, exist_ok=True)
    for name in DIRECTORIES:
        source = SOURCE / name
        require_regular_tree(source)
        destination = target / name
        if destination.is_symlink():
            raise ValueError(f"Refusing symlink destination: {destination}")
        if destination.exists():
            shutil.rmtree(destination)
        shutil.copytree(source, destination)
    for name in FILES:
        source = SOURCE / name
        if source.is_symlink() or not source.is_file():
            raise ValueError(f"Unsupported browser source entry: {source}")
        destination = target / name
        if destination.is_symlink():
            raise ValueError(f"Refusing symlink destination: {destination}")
        shutil.copy2(source, destination)
    print(f"Staged browser source and public files in {target}; no backend or account output copied")


if __name__ == "__main__":
    stage()
