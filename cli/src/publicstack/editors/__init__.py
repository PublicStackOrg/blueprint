class AlreadyApplied(Exception):
    """Raised when an editor detects that the requested change is already in
    place. Idempotent retries should treat this as success in the calling
    context, but `add` commands surface it as a user-visible error."""
