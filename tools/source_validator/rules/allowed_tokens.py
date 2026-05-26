SEVERITIES = ("BLOCKING", "ERROR", "WARNING", "INFO")

EXIT_CODES = {
    "PASS": 0,
    "WARNING_ONLY": 1,
    "ERROR": 2,
    "BLOCKING": 3,
    "TOOL_FAILURE": 4,
}

GOV_FILE = "GOV-00"
SRC_INDEX_FILE = "SRC-INDEX"

SOURCE_FILE_IDS = tuple(f"SRC-{number:02d}" for number in range(0, 11))

