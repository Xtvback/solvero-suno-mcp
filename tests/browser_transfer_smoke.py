"""No-Suno browser-download transport test. Uses only synthetic bytes."""
from pathlib import Path
from playwright.sync_api import sync_playwright

def main():
    out = Path("transfer-test")
    out.mkdir(exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(accept_downloads=True)
        page.goto("about:blank")
        page.set_content('<button id="download">Download test</button>')
        page.locator("#download").evaluate("""element => element.addEventListener('click', () => {
            const bytes = new TextEncoder().encode('SOLVERO_TRANSFER_TEST_v1');
            const blob = new Blob([bytes], {type:'text/plain'});
            const url = URL.createObjectURL(blob);
            const anchor = document.createElement('a');
            anchor.href = url;
            anchor.download = 'test-transfer.txt';
            anchor.click();
            URL.revokeObjectURL(url);
        })""")
        with page.expect_download() as captured:
            page.locator("#download").click()
        downloaded = captured.value
        assert downloaded.suggested_filename == "test-transfer.txt"
        file = out / downloaded.suggested_filename
        downloaded.save_as(file)
        assert file.read_bytes() == b"SOLVERO_TRANSFER_TEST_v1"
        browser.close()
    print(f"PASS: browser blob download captured and saved to {file}")

if __name__ == "__main__":
    main()
