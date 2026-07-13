from pathlib import Path


def test_required_starter_files_exist():
    root = Path(__file__).parents[1]
    assert (root / ".cursor/prompts/00_MASTER_BUILD_PROMPT.md").exists()
    assert (root / "config/hiring-standard.yaml").exists()
    assert (root / "docs/01_Zume_Project_Blueprint.docx").exists()
