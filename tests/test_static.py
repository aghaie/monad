from app.server.main import WEB_DIR


def test_shell_files_exist_and_reference_entry():
    index = (WEB_DIR / "index.html")
    assert index.is_file(), "app/web/index.html must exist"
    html = index.read_text(encoding="utf-8")
    assert "shell/layout.js" in html
    assert (WEB_DIR / "src" / "lib" / "api.js").is_file()
    assert (WEB_DIR / "src" / "shell" / "registry.js").is_file()
    assert (WEB_DIR / "src" / "shell" / "layout.js").is_file()
