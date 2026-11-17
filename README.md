# Capu website

The capu.ai marketing site follows the supplied **Capu Website v2 2** design. The static page in `site/` includes interactive feature previews, Classic and Liquid Glass appearance controls, and the Capu and Conductor comparison. The seven feature sections use eight live demo bundles, with the desktop preview also used in the hero and appearance section. The exported runtime and assets are local, so there is no install or build step.

## Preview

Run from the repository root:

```sh
python3 -m http.server 8000 --bind 127.0.0.1 --directory site
```

Open http://127.0.0.1:8000.

## Check changes

Use Python 3.9+ and Node.js:

```sh
python3 scripts/check_site.py
```

The check validates local assets, navigation, demo resources, accessibility labels, JavaScript syntax, and team, workspace, and appearance selection. It also checks appearance messages and rapid switches between styles. Before changing the design, compare desktop and phone captures, switch the team roles, workspaces, and appearance controls, and exercise the live demos.

Edit page content and demo data in `site/index.html`. `site/site.css` contains responsive navigation, workspace and comparison styles, and accessible button and focus styles. `site/assets/resources.js` maps resource names to the exported assets. Keep the exported demos and runtime intact when changing the marketing page.

## Publish with GitHub Pages

The **Website** workflow checks pull requests and deploys `site/` when changes reach `main`. GitHub Pages must use **GitHub Actions** as its publishing source. The workflow uses GitHub's [custom workflow setup](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages).

Set the custom domain to `capu.ai` in [repository Pages settings](https://github.com/harshach/Capu-Releases/settings/pages). At the DNS provider, point the apex domain's A records to:

```text
185.199.108.153
185.199.109.153
185.199.110.153
185.199.111.153
```

If you use `www`, point its CNAME record to `harshach.github.io`. After GitHub issues the certificate, enable **Enforce HTTPS**. See GitHub's [custom-domain instructions](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/managing-a-custom-domain-for-your-github-pages-site). Actions deployments require the domain in Pages settings; the included `site/CNAME` alone does not configure it.

## Downloads

The hero's **Download for Mac** link and all three download cards open the [latest GitHub release](https://github.com/harshach/Capu-Releases/releases/latest). GitHub keeps this destination current as new versions are published.

The release includes Mac downloads for Apple silicon on macOS 27+, and Linux tarballs and Arch packages. The iPhone card points to the release notes for TestFlight information. No public TestFlight invitation or App Store link is configured.
