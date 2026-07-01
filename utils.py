from datetime import datetime


def log(message, callback=print):
    """
    Log a message with timestamp.
    """
    timestamp = datetime.now().strftime("%H:%M:%S")
    callback(f"[{timestamp}] {message}")


def format_size(size_bytes):
    """
    Convert bytes to human readable size.
    """
    units = ["B", "KB", "MB", "GB"]

    size = float(size_bytes)

    for unit in units:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024

    return f"{size:.2f} TB"