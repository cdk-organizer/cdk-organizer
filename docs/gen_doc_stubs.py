"""Mkdocs Code Reference Generator."""

import json
from pathlib import Path

import mkdocs_gen_files

src_root = Path(".")

for path in src_root.glob("packages/**/project.json"):
    project_path = str(path.parent)
    print(project_path)
    with open(path, "r") as project_file:
        project = json.loads(project_file.read())
        custom_patterns = [
            # Markdowns
            f"{project_path}/*.md",
            f"{project_path}/*[!cdk.out]/**/*.md",

            # Images
            f"{project_path}/*[!cdk.out]/**/*.jpg",
            f"{project_path}/*[!cdk.out]/**/*.png"
        ]

        for pattern in custom_patterns:
            for path in src_root.glob(pattern):
                doc_path = Path("reference", path.relative_to(src_root))
                with mkdocs_gen_files.open(doc_path, "wb") as f:
                    f.write(path.read_bytes())

                if not path.suffix.endswith(".jpg") and not path.suffix.endswith(".png"):
                    mkdocs_gen_files.set_edit_path(doc_path, f"../{path}")
