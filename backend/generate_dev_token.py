"""Print a short-lived token for local API testing only."""

import argparse
import uuid

from dotenv import load_dotenv

from security.dev_tokens import generate_dev_token


def main() -> None:
    load_dotenv()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--user-id", default=str(uuid.uuid4()))
    parser.add_argument("--minutes", type=int, default=60)
    args = parser.parse_args()

    try:
        print(generate_dev_token(args.user_id, args.minutes))
    except (RuntimeError, ValueError) as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    main()
