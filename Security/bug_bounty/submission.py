class BugSubmission:
    def __init__(self, reporter, description, severity, reproducible):
        self.reporter = reporter
        self.description = description
        self.severity = severity
        self.reproducible = reproducible

    def is_valid(self):
        return (
            self.severity >= 7
            and self.reproducible is True
            and len(self.description) > 50
        )
