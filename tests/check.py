from pathlib import Path

import os
from tempfile import TemporaryDirectory
from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parents[1]

with sync_playwright() as p, TemporaryDirectory() as temp:
    browser = p.chromium.launch(executable_path=os.environ.get("CHROME_PATH"))
    page = browser.new_page()
    errors = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    page.goto((ROOT / "index.html").as_uri())
    for key, value in {
        "date": "2026-11-24",
        "start": "22:00",
        "end": "06:00",
        "pause": "30",
    }.items():
        page.locator("#" + key).fill(value)
    page.get_by_role("button", name="Add shift").click()
    assert "7 h 30 min" in page.locator("#total").inner_text()
    with page.expect_download() as download:
        page.locator("#export").click()
    dest = Path(temp) / "timesheet.csv"
    download.value.save_as(dest)
    assert "22:00,06:00,30,450" in dest.read_text()
    page.get_by_role("button", name="Remove").click()
    assert page.locator("#export").is_disabled()
    assert not errors, errors
    browser.close()
