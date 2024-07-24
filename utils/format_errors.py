

def validation_error(errors):
    result = {}
    for field, error_messages in errors.items():
        result[field] = error_messages[0] if isinstance(error_messages, list) else error_messages
    return result

