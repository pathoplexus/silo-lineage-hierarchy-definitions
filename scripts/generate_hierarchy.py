#!/usr/bin/env python3
"""
Generate hierarchy definition YAML files from lineage designation repositories.

This script downloads the latest lineage designation files from the lineage repositories
and converts them into the silo hierarchy format used by this project.
"""

import argparse
import os
import sys
import tempfile
import subprocess
from collections import OrderedDict, defaultdict
from pathlib import Path
from typing import Any, Dict, List

import yaml

def download_repo_zip(repo_url: str, temp_dir: str, lineage_definition_path: str):
    """Download and extract a GitHub repository ZIP file."""
    subprocess.run([
        "git",
        "clone",
        "--filter=blob:none",
        "--sparse",
        repo_url,
        temp_dir,
    ])

    subprocess.run(["git", "-C", temp_dir, "sparse-checkout", "set", lineage_definition_path])


def load_lineage_files(lineages_path: Path) -> Dict[str, Any]:
    """Load all lineage YAML files from a directory."""
    lineages = {}

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
    organism: str, output_dir: str, lineage_definition_repo: str, lineage_definition_path: str, dataset_tag: str | None = None,
) -> None:
    """Generate hierarchy file for a specific RSV subtype (A or B)."""

    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"Downloading {organism} lineage data from {lineage_definition_repo}...")
        download_repo_zip(lineage_definition_repo, temp_dir, lineage_definition_path)

        print(f"Loading lineage files for {organism}...")
        lineages = load_lineage_files(Path(os.path.join(temp_dir, lineage_definition_path)))

        print(
            f"Converting {len(lineages)} lineages to silo format with topological sorting..."
        )
        silo_hierarchy = convert_to_silo_format(lineages)

        # Create output directory structure
        if dataset_tag:
            subtype_dir = os.path.join(
                output_dir, f"{organism}", dataset_tag
            )
        else:
            subtype_dir = os.path.join(output_dir, f"{organism}")
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
        description="Generate hierarchy definition YAML files"
    )
    parser.add_argument(
        "--output-dir",
        default="definitions",
        help="Output directory for hierarchy files (default: definitions)",
    )
    parser.add_argument(
        "--organism",
        default="rsv-a",
        help="Organism, added to output path (default: rsv-a)",
    )
    parser.add_argument(
        "--lineage-definition-repo",
        default="https://github.com/rsv-lineages/lineage-designation-A.git",
        help="URL for the lineage definition repository (default: RSV-A repository)",
    )
    parser.add_argument(
        "--lineage-definition-path",
        default="lineages",
        help="Path to the lineage definition files within the repository (default: lineages)",
    )
    parser.add_argument(
        "--dataset-tag",
        help="Dataset tag to organize files in subfolders (e.g., nextclade dataset tag)",
    )

    args = parser.parse_args()

    try:
        generate_hierarchy_file(args.organism, args.output_dir, args.lineage_definition_repo, args.lineage_definition_path, args.dataset_tag)

        print(f"✅ Hierarchy generation completed successfully for {args.organism}!")

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
