import os
from pathlib import Path
from typing import List
import chevron
from .msh_constants import TEMPLATE_META_FILES


def walk_files(directory: str) -> List[str]:
    """Walk through all directories and subdirectories."""
    files = []
    for root, _, filenames in os.walk(directory):
        for filename in filenames:
            # Exclude template_meta.[yaml|yml] files
            if filename not in TEMPLATE_META_FILES:
                files.append(os.path.join(root, filename))
    return files


def render_path(path: str, metas: dict) -> str:
    """Render the given path with the provided metas."""
    return chevron.render(path, metas)


def render_file(file_path: str, metas: dict) -> str:
    """Render the content of the file with the provided metas."""
    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()
    return chevron.render(content, metas)


def render_template(
    template_path: str,
    output_path: str,
    metas: dict,
) -> str:
    """Render templates with the provided metas."""
    files = walk_files(template_path)
    for file_path in files:
        rendered_path = render_path(file_path, metas)
        rendered_output_path = rendered_path.replace(template_path, output_path)
        rendered_content = render_file(file_path, metas)
        Path(rendered_output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(rendered_output_path, "w", encoding="utf-8") as output_file:
            output_file.write(rendered_content)
