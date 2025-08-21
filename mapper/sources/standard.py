class AcademicStandard:
    """A representation of an academic standard."""

    def __init__(self, id, code, description):
        self.id = id
        self.code = code or ""
        self.description = description

    def __repr__(self):
        return f"Row({repr(self.id)}, {repr(self.code)}, {repr(self.description)})"
