def validate_text(
    value: str,
    field_name: str,
    min_length: int,
    max_length: int,
) -> str | None:
    if any(char.isspace() for char in value):
        return f"{field_name}不可包含空白"

    if not min_length <= len(value) <= max_length:
        return f"{field_name}長度必須為 {min_length}～{max_length} 個字元"

    return None
