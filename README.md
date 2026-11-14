# WowTech Solution Website

A bilingual (Arabic/English), responsive static website for WowTech Solution.

## 1. Project overview

This project is a static website. It does **not** require Node.js, npm, a database, a build command, or a backend server.

Main pages:
- `index.html` — homepage and main service sections.
- `benefits.html` — benefits page.
- `clients.html` — clients and portfolio page.

Supporting files:
- `styles.css` — layout, styling, responsive behavior, and animations.
- `app.js` — navigation, language interaction, visual effects, and contact actions.
- `i18n.js` — Arabic translations.
- `service-images/` — service images.
- `client-logos/` — client logos.
- `wow_it_tag_logo.png` — company logo.
- `instagram.svg` — Instagram icon.

**Important:** Keep the folder structure and file names unchanged. The HTML pages load assets using relative paths.

## 2. Launch locally (optional)

1. Extract the ZIP archive.
2. Open a terminal in the extracted project folder.
3. Run:

```bash
python3 -m http.server 8080
```

4. Open `http://localhost:8080` in your browser.
5. Press `Ctrl+C` in the terminal to stop the local server.

You can also open `index.html` directly, but using the local server is recommended for testing.

## 3. Publish the website on your domain

### Option A: cPanel hosting (including GoDaddy hosting plans that provide cPanel)

1. Purchase or activate a web-hosting plan and add your domain to it.
2. Open the hosting control panel and launch **File Manager**.
3. Open the document root for your domain. It is commonly `public_html`, but use the exact folder assigned to your domain by the hosting provider.
4. Upload the project ZIP file into that folder.
5. Select the ZIP file and choose **Extract**.
6. Make sure `index.html` is directly inside the domain's document root. For example:

```text
public_html/
  index.html
  benefits.html
  clients.html
  styles.css
  app.js
  i18n.js
  wow_it_tag_logo.png
  instagram.svg
  service-images/
  client-logos/
```

If extraction creates an extra nested folder, move the contents into the document root. Do not leave the homepage at a path such as `public_html/project-folder/index.html` unless that folder is configured as the domain's document root.

7. In your domain DNS settings, point the domain to the hosting provider using the exact A, AAAA, or CNAME records supplied by that provider. Do not guess record values.
8. Enable the provider's SSL certificate, then visit your domain using `https://`.

### Option B: Static hosting

For Netlify, Cloudflare Pages, or another static hosting provider:

1. Create a new static site/project.
2. Upload or connect the extracted project folder (the folder containing `index.html`).
3. Set the publish/output directory to that folder. No build command is required; leave the build command empty if the provider asks for one.
4. Add your custom domain in the hosting dashboard.
5. Apply the DNS records shown by the provider and enable HTTPS.

## 4. Pre-launch checklist

- [ ] The homepage opens at the root domain.
- [ ] Arabic and English language switching works.
- [ ] The homepage, `benefits.html`, and `clients.html` all load correctly.
- [ ] All service images and client logos display correctly.
- [ ] WhatsApp opens the correct business chat.
- [ ] The phone link works on a mobile device.
- [ ] The Instagram link opens the correct account.
- [ ] The layout is checked on mobile, tablet, and desktop.
- [ ] HTTPS is active and the browser shows no certificate warning.
- [ ] The domain works with and without `www` if both versions are intended; configure one to redirect to the preferred version.

## 5. Business contact links currently in the website

- Phone / WhatsApp: `+971 52 196 1007`
- Instagram: `https://www.instagram.com/wowtech.solutions`

Before publishing, confirm these details are still correct. To change the WhatsApp number, update the international-format number (digits only, without `+` or spaces) wherever it appears in `index.html`, `benefits.html`, `clients.html`, and `app.js`. Also update the visible phone number in the relevant page content. To change Instagram, update the account URL in all three HTML pages.

## 6. Updating website content

- Edit English page content in the relevant HTML file.
- Update Arabic translations in `i18n.js` when changing translatable text.
- Edit colors, spacing, typography, and responsive layout in `styles.css`.
- Keep image filenames and paths unchanged when replacing images, or update the corresponding paths in the HTML files.
- When changing shared content, check all three HTML pages so that the homepage and standalone pages remain consistent.

## 7. Important technical notes

- This is a front-end-only static website. It does not include a database, customer login, admin dashboard, server-side form processing, or an order-management system.
- The contact actions currently direct visitors to WhatsApp or phone contact; they do not store enquiries on a server.
- The previous ChatGPT-hosted preview is separate from this source package. Publishing these files and connecting a domain must be completed through your hosting provider and domain DNS settings.

---

For the Arabic launch guide, see [`README_AR.md`](README_AR.md).
