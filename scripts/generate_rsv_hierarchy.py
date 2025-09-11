#!/usr/bin/env python3
"""
Generate RSV hierarchy definition YAML files from RSV lineage designation repositories.

This script downloads the latest lineage designation files from the RSV lineage repositories
and converts them into the silo hierarchy format used by this project.
"""

import argparse
import os
import sys
import tempfile
import zipfile
from collections import OrderedDict, defaultdict
from pathlib import Path
from typing import Any, Dict, List

import requests
import yaml


def download_repo_zip(repo_url: str, temp_dir: str) -> str:
    """Download a GitHub repository as a ZIP file and extract it."""
    zip_url = f"{repo_url}/archive/refs/heads/main.zip"
    response = requests.get(zip_url)
    response.raise_for_status()

    zip_path = os.path.join(temp_dir, "repo.zip")
    with open(zip_path, "wb") as f:
        f.write(response.content)

    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(temp_dir)

    # Find the extracted directory (it will have a name like "lineage-designation-A-main")
    extracted_dirs = [
        d
        for d in os.listdir(temp_dir)
        if os.path.isdir(os.path.join(temp_dir, d)) and d != "__pycache__"
    ]
    if not extracted_dirs:
        raise ValueError("No extracted directory found")

    return os.path.join(temp_dir, extracted_dirs[0])


def load_lineage_files(lineages_dir: str) -> Dict[str, Any]:
    """Load all lineage YAML files from a directory."""
    lineages = {}
    lineages_path = Path(lineages_dir) / "lineages"

    if not lineages_path.exists():
        raise ValueError(f"Lineages directory not found: {lineages_path}")

    for yaml_file in lineages_path.glob("*.yml"):
        with open(yaml_file, "r") as f:
            data = yaml.safe_load(f)
            lineages[data["name"]] = data

    return lineages


def topological_sort(lineages: Dict[str, Any]) -> List[str]:
    """
    Sort lineages topologically (parents before children, depth-first).
    Returns a list of lineage names in the correct order.
    """
    # Build adjacency list for children
    children = defaultdict(list)
    roots = []

    for name, data in lineages.items():
        parent = data["parent"]
        if parent == "none":
            roots.append(name)
        else:
            children[parent].append(name)

    # Depth-first traversal
    visited = set()
    result = []

    def dfs(node: str):
        if node in visited:
            return
        visited.add(node)
        result.append(node)

        # Sort children alphabetically for consistent output
        for child in sorted(children[node]):
            dfs(child)

    # Process all roots (should typically be just one per subtype)
    for root in sorted(roots):
        dfs(root)

    return result


def convert_to_silo_format(lineages: Dict[str, Any]) -> OrderedDict:
    """Convert lineage data to silo hierarchy format with topological ordering."""
    silo_hierarchy = OrderedDict()

    # Get topologically sorted order
    sorted_names = topological_sort(lineages)

    # Build hierarchy in correct order
    for name in sorted_names:
        data = lineages[name]
        silo_hierarchy[name] = {
            "aliases": [],
            "parents": [data["parent"]] if data["parent"] != "none" else [],
        }

    return silo_hierarchy


def generate_hierarchy_file(
    subtype: str, output_dir: str, dataset_tag: str | None = None
) -> None:
    """Generate hierarchy file for a specific RSV subtype (A or B)."""
    repo_url = f"https://github.com/rsv-lineages/lineage-designation-{subtype}"

    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"Downloading RSV-{subtype} lineage data from {repo_url}...")
        extracted_dir = download_repo_zip(repo_url, temp_dir)

        print(f"Loading lineage files for RSV-{subtype}...")
        lineages = load_lineage_files(extracted_dir)

        print(
            f"Converting {len(lineages)} lineages to silo format with topological sorting..."
        )
        silo_hierarchy = convert_to_silo_format(lineages)

        # Create output directory structure
        if dataset_tag:
            subtype_dir = os.path.join(
                output_dir, f"rsv-{subtype.lower()}", dataset_tag
            )
        else:
            subtype_dir = os.path.join(output_dir, f"rsv-{subtype.lower()}")
        os.makedirs(subtype_dir, exist_ok=True)

        # Write hierarchy file
        output_file = os.path.join(subtype_dir, "lineages.yaml")
        with open(output_file, "w") as f:
            # Convert OrderedDict to regular dict for clean YAML output
            # but maintain the topological order by iterating through our sorted structure
            for name in silo_hierarchy:
                f.write(f"{name}:\n")
                f.write(f"  aliases: {silo_hierarchy[name]['aliases']}\n")
                if silo_hierarchy[name]["parents"]:
                    f.write(f"  parents:\n")
                    for parent in silo_hierarchy[name]["parents"]:
                        f.write(f"  - {parent}\n")
                else:
                    f.write(f"  parents: []\n")

        print(f"Generated hierarchy file: {output_file}")


def main():
    parser = argparse.ArgumentParser(
        description="Generate RSV hierarchy definition YAML files"
    )
    parser.add_argument(
        "--output-dir",
        default="definitions",
        help="Output directory for hierarchy files (default: definitions)",
    )
    parser.add_argument(
        "--subtype",
        choices=["A", "B", "both"],
        default="both",
        help="RSV subtype to process (default: both)",
    )
    parser.add_argument(
        "--dataset-tag",
        help="Dataset tag to organize files in subfolders (e.g., nextclade dataset tag)",
    )

    args = parser.parse_args()

    try:
        if args.subtype in ["A", "both"]:
            generate_hierarchy_file("A", args.output_dir, args.dataset_tag)

        if args.subtype in ["B", "both"]:
            generate_hierarchy_file("B", args.output_dir, args.dataset_tag)

        print("✅ RSV hierarchy generation completed successfully!")

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
