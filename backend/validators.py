def validate_text(
    value: str,
    field_name: str,
    min_length: int,
    max_length: int,
) -> str | None:
    if any(char.isspace() for char in value):
        return f"{field_name} must not contain whitespace."

    if not min_length <= len(value) <= max_length:
        return f"{field_name} must be between {min_length} and {max_length} characters."

    return None
