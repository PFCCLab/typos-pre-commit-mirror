# /// script
# requires-python = ">=3.9"
# dependencies = [
#     "tomli>=2.2.1",
#     "tomli-w>=1.2.0",
#     "urllib3>=2",
#     "packaging>=21.0",
# ]
# ///

import subprocess
import re
from pathlib import Path

import tomli
import tomli_w
import urllib3
from packaging.requirements import Requirement
from packaging.version import Version


def main():
    # Load pyproject.toml
    with open(Path(__file__).parent / "pyproject.toml", "rb") as f:
        pyproject = tomli.load(f)
    # Load README.md
    with open(Path(__file__).parent / "README.md", "r") as f:
        readme = f.read()

    # 获取当前版本的 typos
    deps = pyproject["project"]["dependencies"]
    assert len(deps) == 1
    typos_dep = Requirement(deps[0])
    assert typos_dep.name == "typos"
    typos_specs = list(typos_dep.specifier)
    assert len(typos_specs) == 1
    assert typos_specs[0].operator == "=="
    current_version = Version(typos_specs[0].version)

    # Get typos versions from PyPI
    http = urllib3.PoolManager()
    resp = http.request("GET", "https://pypi.org/pypi/typos/json")
    if resp.status != 200:
        raise RuntimeError("Failed to fetch data from PyPI")

    versions = [Version(release) for release in resp.json()["releases"]]
    versions = [v for v in versions if v > current_version and not v.is_prerelease]
    versions.sort()

    if not versions:
        print("No new versions to update")
        return

    print(f"Found {len(versions)} new version(s): {versions}")

    # Update typos for each version
    for version in versions:
        print(f"Processing version {version}...")
        
        # Update pyproject.toml
        pyproject["project"]["version"] = str(version)
        pyproject["project"]["dependencies"] = [f"typos=={version}"]
        # Update README.md
        # Replace the rev line specifically to avoid partial matches
        updated_readme = re.sub(
            r'(\s+rev:\s+)v[0-9]+\.[0-9]+\.[0-9]+',
            rf'\1v{version}',
            readme
        )

        # Write pyproject.toml and README.md
        with open(Path(__file__).parent / "pyproject.toml", "wb") as f:
            tomli_w.dump(pyproject, f)
        with open(Path(__file__).parent / "README.md", "w") as f:
            f.write(updated_readme)

        # Commit and tag
        subprocess.run(["git", "add", "pyproject.toml", "README.md"], check=True)
        subprocess.run(
            ["git", "commit", "-m", f":arrow_up: bump typos version to {version}"],
            check=True
        )
        # Check if tag already exists before creating it
        result = subprocess.run(["git", "tag", "-l", f"v{version}"], capture_output=True, text=True)
        if not result.stdout.strip():
            subprocess.run(["git", "tag", f"v{version}"], check=True)
            print(f"Created tag v{version}")
        else:
            print(f"Tag v{version} already exists, skipping")

        # Update readme for next iteration
        readme = updated_readme

    print(f"Successfully processed {len(versions)} version(s)")


if __name__ == "__main__":
    main()
