from .csp import download_csp_data


class TexasCspApiSource:
    def __init__(self, desc):
        if "subject" not in desc:
            raise RuntimeError("missing subject in Texas CSP source")

        # TODO Process Texas data.
        self.data = download_csp_data("Texas", desc["subject"])

    def __iter__(self):
        return iter(self.data)

    def __len__(self):
        return len(self.data)
