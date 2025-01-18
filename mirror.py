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

    # Update typos for each version
    for version in versions:
        # Update pyproject.toml
        pyproject["project"]["version"] = str(version)
        pyproject["project"]["dependencies"] = [f"typos=={version}"]
        with open(Path(__file__).parent / "pyproject.toml", "wb") as f:
            tomli_w.dump(pyproject, f)

        # Commit and tag
        subprocess.run(["git", "add", "pyproject.toml"])
        subprocess.run(["git", "commit", "-m", f"Update typos to {version}"])
        subprocess.run(["git", "tag", f"v{version}"])


if __name__ == "__main__":
    main()
