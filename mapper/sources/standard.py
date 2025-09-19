class AcademicStandard:
    """A representation of an academic standard."""

    def __init__(self, id, code, description, parent_id):
        self.id = id
        self.code = code or ""
        self.description = description
        self.parent_id = parent_id

    def __repr__(self):
        return f"Row({repr(self.id)}, {repr(self.code)}, {repr(self.description)})"
