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
        if "sc-camel-on-click" in attrs and tag != "button":
            errors.append("Interactive selectors must be keyboard-accessible buttons")


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
assert {"team", "always", "workspaces"} <= page.ids, "The team, background-session, and workspace sections must be present"
assert {"looks", "compare"} <= page.ids, "The appearance and comparison sections must be present"
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
const window = { location: { origin: 'https://capu.ai' }, __resources: """ + json.dumps(resources) + """ };
let timerId = 0;
const timers = new Map();
const setTimeout = (callback, delay) => { timers.set(++timerId, { callback, delay }); return timerId; };
const clearTimeout = id => timers.delete(id);
const flushTimers = () => {
  for (const [id, timer] of [...timers].sort((a, b) => a[1].delay - b[1].delay)) {
    timers.delete(id);
    timer.callback();
  }
};
class DCLogic {
  setState(update) {
    Object.assign(this.state, typeof update === 'function' ? update(this.state) : update);
  }
}
""" + script + """
const component = new Component();
const heroMessages = [], looksMessages = [];
let view = component.renderVals();
assert.equal(view.heroSrc, window.__resources.appCanvas + '#bare=1');
assert.equal(view.heroLooks.find(option => option.selected).t, 'Liquid Glass');
assert.equal(view.lookOpts.find(option => option.selected).t, 'Tinted');
view.heroIfr({ contentWindow: { postMessage: (message, origin) => heroMessages.push({ message, origin }) } });
view.looksIfr({ contentWindow: { postMessage: (message, origin) => looksMessages.push({ message, origin }) } });
view.heroLoad();
view.looksLoad();
flushTimers();
assert.ok(heroMessages.length && looksMessages.length, 'Loaded previews receive their initial appearance');
assert.deepEqual(heroMessages.at(-1), { message: { hzGlass: { on: true, style: 'tinted', panes: 'solid', opacity: 50 } }, origin: window.location.origin });
const looks = [
  ['Classic', { on: false }],
  ['Clear', { on: true, style: 'clear', panes: 'solid', opacity: 50 }],
  ['Tinted', { on: true, style: 'tinted', panes: 'solid', opacity: 50 }],
  ['Full', { on: true, style: 'full', panes: 'glass', opacity: 50 }],
];
for (const [name, payload] of looks) {
  component.renderVals().lookOpts.find(option => option.t === name).pick();
  view = component.renderVals();
  assert.equal(view.lookOpts.filter(option => option.selected).length, 1);
  assert.equal(view.lookOpts.find(option => option.selected).t, name);
  assert.equal(view.heroLooks.find(option => option.selected).t, 'Liquid Glass');
  assert.ok(view.lookDesc);
  flushTimers();
  assert.deepEqual(looksMessages.at(-1), { message: { hzGlass: payload }, origin: window.location.origin });
}
heroMessages.length = 0;
component.renderVals().heroLooks[0].pick();
component.renderVals().heroLooks[1].pick();
flushTimers();
assert.ok(heroMessages.length, 'Rapid appearance changes still reach the preview');
assert.ok(heroMessages.every(({ message }) => message.hzGlass.style === 'tinted'), 'Old retries must not overwrite the latest appearance');
assert.equal(component.renderVals().lookOpts.find(option => option.selected).t, 'Full');
component.renderVals().heroLooks[0].pick();
flushTimers();
assert.deepEqual(heroMessages.at(-1).message, { hzGlass: { on: false } });
assert.equal(component.renderVals().heroLooks.find(option => option.selected).t, 'Classic');
const pending = new Component();
pending.renderVals().lookOpts[3].pick();
pending.renderVals().looksIfr({ contentWindow: { postMessage: message => looksMessages.push(message) } });
pending.renderVals().looksLoad();
flushTimers();
assert.deepEqual(looksMessages.at(-1), { hzGlass: { on: true, style: 'full', panes: 'glass', opacity: 50 } });
component.renderVals().heroLoad();
component.componentWillUnmount();
const messageCount = heroMessages.length;
flushTimers();
assert.equal(heroMessages.length, messageCount, 'Unmounted previews receive no delayed messages');
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
assert.equal(component.renderVals().ws.machine, 'Mac Studio');
for (const [index, [name, machine, agent, project]] of [
  ['Marketing', 'Mac Studio', 'Codex', 'horizon'],
  ['Personal', 'MacBook Pro', 'Claude', 'sleep-tracker'],
  ['Acme · client', 'devbox', 'Gemini', 'acme-ingest'],
  ['Open source', 'vps-eu-1', 'Claude', 'capu-cli'],
].entries()) {
  component.renderVals().wsList[index].pick();
  const view = component.renderVals();
  assert.equal(view.wsList[index].t, name);
  assert.equal(view.ws.machine, machine);
  assert.equal(view.ws.agent, agent);
  assert.equal(view.ws.projects[0].t, project);
  assert.equal(view.wsList.filter(workspace => workspace.selected).length, 1);
  assert.ok(view.wsList[index].selected);
  assert.equal(view.wsList[index].miniLabel, name);
  assert.equal(view.teamCur.status, 'Waiting for Builder');
}
component.renderVals().wsList[0].pick();
assert.equal(component.renderVals().ws.machine, 'Mac Studio');
""", text=True, capture_output=True)
    if result.returncode:
        errors.append(result.stderr)

if errors:
    raise SystemExit("\n".join(errors))
print(f"PASS: {len(resources)} resource mappings, {len(demo_resources)} demo bundles, navigation, metadata, JavaScript syntax, team, workspace and appearance selection")
