#!/usr/bin/env python3
"""
Extract clade hierarchy from a Nextclade tree.json and output as YAML.

For each clade, the parent is the nearest ancestor node with a different clade.
"""

import argparse
import json
import os
import yaml


def traverse(node, parent_clade, clade_parents):
    clade_attr = node["node_attrs"].get("clade")
    clade = clade_attr["value"] if clade_attr else parent_clade

    if clade is not None and clade != parent_clade:
        if clade not in clade_parents:
            clade_parents[clade] = set()
        if parent_clade is not None:
            clade_parents[clade].add(parent_clade)
        current_clade = clade
    else:
        current_clade = parent_clade

    for child in node.get("children", []):
        traverse(child, current_clade, clade_parents)


def main(tree_path, output_path=None):
    with open(tree_path) as f:
        data = json.load(f)

    clade_parents = {}
    traverse(data["tree"], None, clade_parents)

    result = {
        clade: {
            "aliases": [],
            "parents": sorted(parents),
        }
        for clade, parents in sorted(clade_parents.items())
    }
    for clade, parents in clade_parents.items():
        if len(parents) > 1:
            print(f"Warning: Clade '{clade}' has multiple parents: {parents}")

    yaml_str = yaml.dump(result, default_flow_style=False, sort_keys=True, allow_unicode=True)

    if output_path:
        os.makedirs(output_path, exist_ok=True)
        output_file = os.path.join(output_path, "lineages.yaml")
        with open(output_file, "w") as f:
            f.write(yaml_str)
        print(f"Written to {output_file}")
    else:
        print(yaml_str)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate hierarchy definition YAML files from a Nextclade tree.json file."
    )
    parser.add_argument(
        "--output-dir",
        default="definitions",
        help="Output directory for hierarchy files (default: definitions)",
    )
    parser.add_argument(
        "--tree-path",
        help="Path to the Nextclade tree.json file"
    )
    parser.add_argument(
        "--dataset-tag",
        help="Tag for the dataset"
    )
    args = parser.parse_args()
    output_dir = args.output_dir + "/" + args.dataset_tag if args.dataset_tag else args.output_dir
    main(args.tree_path, output_dir)
