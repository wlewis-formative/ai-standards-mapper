import os
import logging
import requests
from tqdm import tqdm
from .standard import AcademicStandard


class CspApiSource:
    def __init__(self, jurisdiction, subject):
        if not jurisdiction:
            raise RuntimeError("missing jurisdiction in CSP source")
        if not subject:
            raise RuntimeError("missing subject in CSP source")

        api_key = os.environ.get("CSP_API_KEY")
        if not api_key:
            raise RuntimeError("missing CSP_API_KEY")

        self.data = CspApiSource._load_data(api_key, jurisdiction, subject)

    def _load_data(api_key, jurisdiction, subject):
        logging.info("Loading jurisdiction")
        headers = {"Api-Key": api_key}
        res = requests.get(
            "http://commonstandardsproject.com/api/v1/jurisdictions",
            headers=headers,
        ).json()
        all_jurisdictions = res.get("data")
        jurisdiction_id = next(
            (j.get("id") for j in all_jurisdictions if j.get("title") == jurisdiction),
            None,
        )
        if not jurisdiction_id:
            raise RuntimeError("jurisdiction doesn't exist")

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
        logging.info(f"Loading all {jurisdiction} {subject} standards")
        for ss_id in tqdm(standard_set_ids):
            res = requests.get(
                f"http://commonstandardsproject.com/api/v1/standard_sets/{ss_id}",
                headers=headers,
            ).json()
            standards = res.get("data").get("standards").values()
            for standard in standards:
                data.append(
                    AcademicStandard(
                        standard.get("id"),
                        standard.get("statementNotation"),
                        standard.get("description"),
                    )
                )

        return data

    def __iter__(self):
        return CspApiSourceIterator(self.data)

    def __len__(self):
        return len(self.data)


class CspApiSourceIterator:
    def __init__(self, data):
        self.data = data
        self.cursor = 0

    def __next__(self):
        if self.cursor >= len(self.data):
            raise StopIteration
        out = self.data[self.cursor]
        self.cursor += 1
        return out
