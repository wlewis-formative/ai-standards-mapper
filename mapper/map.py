import argparse
import ast
import csv
import logging
import os
import vdblite
from tqdm import tqdm


def main(core_set_filename, mapped_sets_filenames, output_directory):
    core_set, _ = os.path.splitext(os.path.basename(core_set_filename))

    logging.info(f"Populating vector database with standards from {core_set}")
    vdb = populate_db(core_set_filename)

    for mapped_set_filename in mapped_sets_filenames:
        map_standards(vdb, mapped_set_filename, core_set, output_directory)


def populate_db(core_set_filename):
    vdb = vdblite.Vdb()
    with open(core_set_filename, "r") as f:
        reader = csv.DictReader(f)
        for row in tqdm(
            map(preprocess_row, reader), total=count_rows(core_set_filename)
        ):
            vdb.add(row)
    return vdb


output_field_names = [
    "ID",
    "Code",
    "Description",
    "Score",
    "ID (Recommended)",
    "Code (Recommended)",
    "Description (Recommended)",
]


def map_standards(vdb, mapped_set_filename, core_set, output_directory):
    mapped_set, _ = os.path.splitext(os.path.basename(mapped_set_filename))
    logging.info(f"Mapping standards from {mapped_set} to {core_set}")

    output_filename = os.path.join(output_directory, f"{mapped_set}-{core_set}.csv")

    with open(output_filename, "w") as f:
        writer = csv.DictWriter(f, fieldnames=output_field_names)
        writer.writeheader()
        with open(mapped_set_filename, "r") as f:
            reader = csv.DictReader(f)
            for row in tqdm(
                map(preprocess_row, reader), total=count_rows(mapped_set_filename)
            ):
                output_row = get_closest_match(vdb, row)
                if output_row:
                    writer.writerow(output_row)


def get_closest_match(vdb, row):
    results = vdb.search(row["Embedding"], "Embedding", 1)
    match = results[0]
    if match:
        return dict(
            zip(
                output_field_names,
                [
                    row["ID"],
                    row["Code"],
                    row["Description"],
                    match["score"],
                    match["ID"],
                    match["Code"],
                    match["Description"],
                ],
            )
        )


def count_rows(filename):
    """Count the number of rows in a CSV file.

    This is a little wasteful, but it's necessary to display progress bars, which
    are really nice to have."""
    with open(filename, "r") as f:
        reader = csv.reader(f)
        return sum(1 for _ in reader)


def preprocess_row(row):
    return {**row, "Embedding": ast.literal_eval(row["Embedding"])}


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser(
        prog="map",
        description='Identify the most similar standard from a "core" standard set for each standard in the provided "mapped" standard sets',
    )
    parser.add_argument(
        "-c",
        "--core-standard-set",
        help='The path to a CSV file containing embedding data for a standard set. Standards from each "mapped" set will be mapped to standards in this set.',
        required=True,
    )
    parser.add_argument(
        "-m",
        "--mapped-standard-set",
        help='The path to a CSV file containing embedding data for a standard set. Each standard in this file will be mapped to a standard in the "core" set.',
        required=True,
        action="append",
    )
    parser.add_argument(
        "-o", "--output-directory", help="The directory to write the output files to."
    )
    args = parser.parse_args()

    main(args.core_standard_set, args.mapped_standard_set, args.output_directory)
