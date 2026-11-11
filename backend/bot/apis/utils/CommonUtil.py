from datetime import datetime, timedelta, timezone
from dateutil import parser


def parse_timestamp(timestamp_str):
    try:
        # Try parsing using dateutil (handles most cases flexibly)
        return parser.parse(timestamp_str)
    except ValueError:
        # Fallback to strict parsing for known formats
        try:
            # Format: "2024-11-12 22:05:53.535 +0530"
            format1 = "%Y-%m-%d %H:%M:%S.%f %z"
            return datetime.strptime(timestamp_str, format1)
        except ValueError:
            # Handle unexpected formats explicitly if needed
            raise ValueError(f"Unsupported timestamp format: {timestamp_str}")
