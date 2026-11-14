import base64
import gzip
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import subprocess
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1] / "site"
html = (ROOT / "index.html").read_text()
resources = json.loads((ROOT / "assets/resources.js").read_text().split("=", 1)[1].rstrip(";\n"))
errors = []


def check_local(url):
    parsed = urlsplit(url)
    if parsed.scheme or parsed.netloc or not parsed.path or "{{" in url:
        return
    target = (ROOT / unquote(parsed.path)).resolve()
    if not target.is_relative_to(ROOT) or not target.is_file():
        errors.append(f"Missing local resource: {url}")


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = set()
        self.targets = set()
        self.title = False
        self.h1_count = 0

    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        if "id" in attrs and "{{" not in attrs["id"]:
            self.ids.add(attrs["id"])
        if tag == "title":
            self.title = True
        if tag == "h1":
            self.h1_count += 1
        for name in ("src", "href", "from"):
            value = attrs.get(name, "")
            check_local(value)
            if name == "src" and "{{" in value:
                errors.append("Unresolved src would cause a request before rendering")
        if attrs.get("href", "").startswith("#"):
            self.targets.add(attrs["href"][1:])
        if "popovertarget" in attrs:
            self.targets.add(attrs["popovertarget"])
        if tag == "img" and "alt" not in attrs:
            errors.append("Image is missing alt text")
        if tag == "iframe" and not attrs.get("title"):
            errors.append("Demo iframe is missing a title")


page = Page()
page.feed(html)
feature_ids = set(re.findall(r'\{ id: "([a-z]+)", note:', html))
for target in page.targets - page.ids - feature_ids:
    errors.append(f"Missing navigation target: #{target}")
for path in resources.values():
    check_local(path)
for path in re.findall(r'url\([\'"]?(assets/[^\'"\)]+)', html):
    check_local(path)
for identifier in re.findall(r'RES\("([^\"]+)"', html):
    if identifier not in resources:
        errors.append(f"Missing resource mapping: {identifier}")

assert page.title and page.h1_count == 1, "The page needs a title and one main heading"
assert '<html lang="en">' in html, "The page needs a language"
assert len(feature_ids) == 7, "All seven feature demos must be present"
assert {"team", "always"} <= page.ids, "The team and background-session sections must be present"
assert (ROOT / "CNAME").read_text().strip() == "capu.ai"

demo_resources = {name: path for name, path in resources.items() if name.startswith("app")}
assert set(demo_resources) == {
    "appCanvas", "appLive", "appEdge", "appReviews", "appPhone", "appDuo", "appMemories", "appAnalytics"
}, "All eight live demo bundles must be present"
for name, path in demo_resources.items():
    bundle = (ROOT / path).read_text()
    match = re.search(r'<script type="__bundler/manifest">(.*?)</script>', bundle, re.S)
    assert match, f"{name} is missing its bundled resources"
    for asset in json.loads(match[1]).values():
        data = base64.b64decode(asset["data"], validate=True)
        if asset.get("compressed"):
            data = gzip.decompress(data)
        assert data, f"{name} contains an empty asset"
    assert '__bundler/template' in bundle, f"{name} is missing its template"

for script in re.findall(r'<script[^>]*data-dc-script[^>]*>(.*?)</script>', html, re.S):
    result = subprocess.run(["node", "--check"], input=script, text=True, capture_output=True)
    if result.returncode:
        errors.append(result.stderr)
    result = subprocess.run(["node"], input="""
const assert = require('node:assert/strict');
const window = { __resources: """ + json.dumps(resources) + """ };
class DCLogic {
  setState(update) {
    Object.assign(this.state, typeof update === 'function' ? update(this.state) : update);
  }
}
""" + script + """
const component = new Component();
assert.equal(component.renderVals().teamCur.status, 'Working · step 3 of 5');
for (const [index, status] of ['Done · 4 min', 'Working · step 3 of 5', 'Waiting for Builder'].entries()) {
  component.renderVals().team[index].pick();
  const view = component.renderVals();
  assert.equal(view.teamCur.status, status);
  assert.equal(view.team.filter(agent => agent.selected).length, 1);
  assert.ok(view.team[index].selected);
}
assert.deepEqual(component.renderVals().devices.map(device => device.src),
  [window.__resources.appPhone, window.__resources.appDuo]);
""", text=True, capture_output=True)
    if result.returncode:
        errors.append(result.stderr)

if errors:
    raise SystemExit("\n".join(errors))
print(f"PASS: {len(resources)} resource mappings, {len(demo_resources)} demo bundles, navigation, metadata, JavaScript syntax, and team selection")
