import re
from re import RegexFlag, Match


def find_all_matches(
    pattern: str, text: str, flags: RegexFlag = re.IGNORECASE
) -> list[str] | None:
    return re.findall(pattern, text, flags=flags)


def replace_pattern(
    pattern: str, replacement: str, text: str, flags: RegexFlag = re.IGNORECASE
) -> str | None:
    return re.sub(pattern, replacement, text, flags=flags)


def split_by_pattern(
    pattern: str, text: str, maxsplit: int = 0, flags: RegexFlag = re.IGNORECASE
) -> list[str] | None:
    return re.split(pattern, text, maxsplit=maxsplit, flags=flags)


def search_pattern(
    pattern: str, text: str, flags: RegexFlag = re.IGNORECASE
) -> Match | None:
    return re.search(pattern, text, flags=flags)
