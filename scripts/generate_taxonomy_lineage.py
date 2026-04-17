#!/usr/bin/env python3
import argparse
import gzip
import sqlite3
import urllib.error
import urllib.request


def load_db(url) -> sqlite3.Connection:
    try:
        with urllib.request.urlopen(url) as response:
            data = gzip.decompress(response.read())
    except urllib.error.HTTPError as e:
        raise RuntimeError(
            f"downloading db from {url} failed with code {e.code}, {e.reason}"
        )

    conn = sqlite3.connect(":memory:")
    conn.deserialize(data)

    return conn


def fetch_sublineage(db_conn: sqlite3.Connection, root: int):
    query = """
    WITH RECURSIVE sublineage AS (
        SELECT * FROM taxonomy WHERE tax_id = ?
        UNION ALL
        SELECT t.* FROM taxonomy t
        JOIN sublineage s ON t.parent_id = s.tax_id
        WHERE t.tax_id != t.parent_id
      )
      SELECT * FROM sublineage;
    """

    result = []
    db_conn.row_factory = sqlite3.Row
    for row in db_conn.execute(query, (root,)).fetchall():
        data = dict(row)
        if data["tax_id"] == root:
            data["parent_id"] = None
        result.append(data)

    # sort by depth level, and alphabetically on scientific name within depth level
    return {
        i["tax_id"]: i
        for i in sorted(result, key=lambda x: (x["depth"], x["scientific_name"]))
    }


def convert_to_silo_format(sublineage, root_id, root_label):
    silo_hierarchy = dict()
    for tax_id, data in sublineage.items():
        aliases = root_label if data["tax_id"] == root_id else []
        parent = data["parent_id"]
        silo_hierarchy[tax_id] = {
            "aliases": [aliases] if aliases else [],
            "parents": [parent] if parent else [],
        }
    return silo_hierarchy


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--roots",
        type=int,
        required=True,
        nargs="+",
        help="Taxon IDs for the roots of sublineages to generate",
    )
    parser.add_argument(
        "--labels",
        type=str,
        required=True,
        nargs="+",
        help="Labels to use for sublineages specified by --roots",
    )
    parser.add_argument(
        "--output",
        type=str,
        required=True,
        help="Name of the output file to store lineages in",
    )
    parser.add_argument(
        "--db_version",
        type=str,
        default="ncbi_taxonomy_latest.sqlite.gz",
        help="DB version to generate sublineages from. Provide the full file name. [DEFAULT: ncbi_taxonomy_latest.sqlite.gz]",
    )

    return parser.parse_args()


def main():
    args = parse_args()
    base_url = "https://loculus-public.hel1.your-objectstorage.com/taxonomy"
    url = f"{base_url}/{args.db_version}"

    if len(args.roots) != len(args.labels):
        raise ValueError("Got a different number of roots and labels")
    if len(set(args.roots)) != len(args.roots) or len(set(args.labels)) != len(
        args.labels
    ):
        raise ValueError("Labels or roots were not unique")

    roots = [
        {"tax_id": root, "label": label} for root, label in zip(args.roots, args.labels)
    ]

    print(f"Downloading db {url}")
    db_conn = load_db(url)
    sublineages = []
    for root in roots:
        print(f"Getting sublineage '{root['label']}' starting at {root['tax_id']}...")
        sublineage = fetch_sublineage(db_conn, root["tax_id"])
        silo = convert_to_silo_format(sublineage, root["tax_id"], root["label"])
        sublineages.append(silo)
        print(f"Sublineage '{root['label']}' contains {len(silo)} taxa")

    print(f"Writing sublineages to {args.output}")
    with open(args.output, "w") as o:
        for sublineage in sublineages:
            for name in sublineage:
                o.write(f"{name}:\n")
                o.write(f"  aliases: {sublineage[name]['aliases']}\n")
                if sublineage[name]["parents"]:
                    o.write("  parents:\n")
                    for parent in sublineage[name]["parents"]:
                        o.write(f"  - {parent}\n")
                else:
                    o.write("  parents: []\n")


if __name__ == "__main__":
    main()
