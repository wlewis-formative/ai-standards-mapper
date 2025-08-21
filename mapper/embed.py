import argparse
import csv
import json
import logging
from openai import OpenAI
from tqdm import tqdm
import sys
from dotenv import load_dotenv
from .sources.csp import CspApiSource


def main(source, output):
    load_dotenv()
    try:
        get_embeddings(source, output)
    except Exception as e:
        print(f"an error occurred: {e}", file=sys.stderr)
        sys.exit(1)


def get_embeddings(source_desc, output):
    with open(output, mode="w", newline="") as file:
        writer = csv.writer(file)
        header = ["ID", "Code", "Description", "Embedding"]
        writer.writerow(header)

        source = get_source(source_desc)
        openai = OpenAI(max_retries=5)
        logging.info("Generating embeddings")
        for row in tqdm(source, total=len(source) if "__len__" in source else None):
            embedding = get_embedding(openai, row.description)
            writer.writerow([row.id, row.code, row.description, embedding])


def get_source(source_desc):
    try:
        parsed = json.loads(source_desc)
        if "type" not in parsed:
            raise RuntimeError("source must have 'type'")

        source_type = parsed.get("type")
        if source_type == "csp-api":
            return CspApiSource(parsed.get("jurisdiction"), parsed.get("subject"))
        else:
            raise RuntimeError(f"unknown source: {source_type}")

    except json.decoder.JSONDecodeError:
        raise RuntimeError("source must be JSON")


def get_embedding(openai, text):
    model = "text-embedding-3-small"
    text = text.replace("\n", " ")
    response = openai.embeddings.create(input=[text], model=model)
    return response.data[0].embedding


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logging.getLogger("httpx").setLevel(logging.WARNING)

    parser = argparse.ArgumentParser(
        prog="embed", description="Generate embeddings for a standard set"
    )
    parser.add_argument("-o", "--output", help="Output CSV filename", required=True)
    parser.add_argument(
        "-s",
        "--source",
        help="""A 'source descriptor' describing how to load the desired standards

             The source descriptor is a JSON object that describes how to load
             the desired standards. Currently, the only supported source is the
             Common Standards Project API. Source descriptors of this type look
             like: {"type": "csp-api", "jurisdiction": "California", "subject":
             "Math"}""",
        required=True,
    )
    args = parser.parse_args()

    main(args.source, args.output)
