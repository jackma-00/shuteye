class EntrySaveError(Exception):
    """Raised when a sleep entry cannot be saved to the log file."""

    pass


class PlanUpdateError(Exception):
    """Raised when there is an error updating the sleep plan."""

    pass
