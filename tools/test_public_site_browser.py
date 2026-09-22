#!/usr/bin/env python3
"""Browser smoke tests for local build artifacts, not provider Access validation."""
import functools
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import threading
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
ROUTES = ('/', '/start/', '/start/index.en.html', '/ahicp/', '/ppf/', '/vault-interface/', '/starter/', '/agent/')


def main():
    report = []
    artifacts = ROOT / 'artifacts/public-site'
    artifacts.mkdir(parents=True, exist_ok=True)
    handler = functools.partial(SimpleHTTPRequestHandler, directory=str(ROOT / '_site'))
    server = ThreadingHTTPServer(('127.0.0.1', 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            for name, js, width in (('desktop', True, 1440), ('mobile', True, 390), ('nojs', False, 1440)):
                context = browser.new_context(java_script_enabled=js, viewport={'width': width, 'height': 950}, locale='zh-CN')
                page = context.new_page()
                errors = []
                page.on('pageerror', lambda error: errors.append(str(error)))
                for route in ROUTES:
                    response = page.goto(f'http://127.0.0.1:{server.server_port}{route}', wait_until='networkidle')
                    assert response.status == 200, (name, route, response.status)
                    assert page.locator('h1:visible').count() > 0, (name, route, 'blank page')
                    assert page.locator('.stack-nav a[href="/agent/"]').count() == 1
                    assert page.locator('.stack-nav a[href="/"]').count() == 1
                    if not js and page.locator('#zh').count():
                        assert page.locator('#zh').is_visible(), (route, 'Chinese fallback hidden')
                    if js and page.locator('#enBtn').count():
                        page.locator('#enBtn').click()
                        assert page.locator('html').get_attribute('lang') == 'en'
                        page.locator('#zhBtn').click()
                        assert page.locator('html').get_attribute('lang') == 'zh-CN'
                    if js and route in ('/', '/ahicp/'):
                        page.wait_for_selector('#guideContentZh h1', state='attached')
                        assert len(page.locator('#guideContentZh').inner_text()) > 1000
                    assert not errors, (name, route, errors)
                    # Mobile content must not cause horizontal page overflow.
                    assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth + 1'), (name, route, 'horizontal overflow')
                    report.append({'viewport': name, 'path': route, 'status': 'PASS'})
                    if route == '/':
                        page.screenshot(path=str(artifacts / f'{name}.png'), full_page=False)
                context.close()
            browser.close()
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
    (artifacts / 'browser-report.json').write_text(json.dumps({'provider_access_tested': False, 'checks': report}, indent=2) + '\n')
    print(f'PASS: {len(report)} route/viewport checks, language switches, no-JS fallback and guide loading')


if __name__ == '__main__':
    main()
