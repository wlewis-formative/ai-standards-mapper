import os
import logging
import requests
from tqdm import tqdm
from .standard import AcademicStandard


class TxCspApiSource:
    def __init__(self, desc):
        if "subject" not in desc:
            raise RuntimeError("missing subject in Texas CSP source")

        self.data = get_data(desc["subject"])

    def __iter__(self):
        return iter(self.data)

    def __len__(self):
        return len(self.data)


def get_data(subject):
    api_key = os.environ.get("CSP_API_KEY")
    if not api_key:
        raise RuntimeError("missing CSP_API_KEY")

    logging.info("Loading jurisdiction")
    headers = {"Api-Key": api_key}

    jurisdiction_id = "28903EF2A9F9469C9BF592D4D0BE10F8"
    res = requests.get(
        f"http://commonstandardsproject.com/api/v1/jurisdictions/{jurisdiction_id}",
        headers=headers,
    ).json()
    all_standard_sets = res.get("data").get("standardSets")

    standard_set_ids = [
        ss.get("id") for ss in all_standard_sets if ss.get("subject") == subject
    ]
    if len(standard_set_ids) == 0:
        raise RuntimeError("no standard sets found")

    data = []
    logging.info(f"Loading all Texas {subject} standards")
    for ss_id in tqdm(standard_set_ids):
        res = requests.get(
            f"http://commonstandardsproject.com/api/v1/standard_sets/{ss_id}",
            headers=headers,
        ).json()
        standards_set = res.get("data").get("standards")
        data.extend(format_standards(standards_set))

    return data


def format_standards(standards_set):
    nodes = {}
    roots = []

    def process(standard):
        if standard["id"] in nodes:
            return

        parent_id = standard.get("parentId")

        entry = {
            "id": standard["id"],
            "code": standard.get("statementNotation"),
            "description": standard["description"],
            "parent_id": parent_id,
            "children": [],
        }

        if parent_id:
            if parent_id not in nodes:
                parent = standards_set[parent_id]
                process(parent)
            nodes[parent_id]["children"].append(entry)

        nodes[entry["id"]] = entry

        if not parent_id:
            roots.append(entry)

    for standard in standards_set.values():
        process(standard)

    standards = []
    for root in roots:
        standards.extend(map_leaves_to_standards(root))

    return standards


def map_leaves_to_standards(node, prefix=""):
    if not node["children"]:
        return [
            AcademicStandard(
                node["id"],
                node["code"],
                f"{prefix} {node['description']}",
                node["parent_id"],
            )
        ]

    standards = []
    for child in node["children"]:
        standards.extend(
            map_leaves_to_standards(
                child, (prefix + " " if prefix else "") + node["description"]
            )
        )
    return standards
