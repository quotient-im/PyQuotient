import re
from pathlib import Path


def replace_in_file(filepath: Path, pattern: str, string: str, use_re=True):
    file_content = ''
    with open(filepath) as file:
        file_content = file.read()

    if use_re:
        file_content = re.sub(pattern, string, file_content)
    else:
        file_content = file_content.replace(pattern, string)

    with open(filepath, 'w') as file:
        file.write(file_content)
