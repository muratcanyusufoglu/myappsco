#!/usr/bin/env python3
"""Builds the static site into the repo root: index.html, claude.html and apps/<slug>.html.

    python3 tools/build.py            # writes the pages
    python3 tools/build.py --dist DIR # also copies only what gets deployed into DIR

The apps live in APPS below; screenshots and icons are already in assets/apps/<slug>/ (fetched from
the App Store listing). Every page links with relative paths so the files also open from disk.
"""
import html
import os
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = 'https://myappsco.app'
EMAIL = 'contact@myappsco.app'
DEVELOPER = 'https://apps.apple.com/developer/id1682346986'

APPS = [
    {
        'slug': 'hairon', 'name': 'HairOn', 'store_name': 'HairOn – AI Hairstyle Try On',
        'tagline': 'See it before you cut it.',
        'category': 'Photo & Video', 'platforms': ['iOS', 'Android'], 'featured': True,
        'appstore': 'https://apps.apple.com/app/id6766210297',
        'play': 'https://play.google.com/store/apps/details?id=com.haironai.app',
        'privacy': 'https://hairon-legal.muratcan-ysfgl.workers.dev/legal/privacy/',
        'accent': '#b0426a',
        'summary': 'Upload a selfie and try more than 100 hairstyles and hair colors on your own face before you book the salon. The results follow your face shape, skin tone and lighting, so they look like you rather than a filter.',
        'facts': [('Languages', '31'), ('Model', 'Free with subscription'), ('Released', 'June 2026')],
        'features': [
            ('Hairstyle try-on', 'Wolf cuts, curtain bangs, bobs, pixies, shags, buzz cuts and 100+ more, rendered on your own photo.'),
            ('Hair color', 'From honey blonde to platinum or auburn, every shade shown on your hair with no dye and no guessing.'),
            ('Beard, makeup and glasses', 'One place to put together the whole look, not just the haircut.'),
            ('Before and after', 'Compare looks side by side and save the ones you want to show your stylist.'),
        ],
        'built': [
            'React Native (Expo) on iOS and Android, from one codebase.',
            '35 Supabase Edge Functions: generation, server-side quota, push re-engagement, subscription reconciliation and account deletion.',
            'Image editing models run behind a server-side quota, so the free tier can never run up the bill.',
            'RevenueCat subscriptions are verified on the server, with webhooks from both stores.',
            'Store listings in 31 languages, kept in sync by fastlane.',
        ],
    },
    {
        'slug': 'milo', 'name': 'Milo', 'store_name': 'Milo: Book Quotes & Journal',
        'tagline': 'Keep the sentences, not just the books.',
        'category': 'Books', 'platforms': ['iOS'], 'featured': True,
        'appstore': 'https://apps.apple.com/app/id6812041975',
        'privacy': 'https://milo-legal.muratcan-ysfgl.workers.dev/privacy/',
        'accent': '#c6633c',
        'summary': 'A reading journal built around the moment a line stops you. Photograph the page, and Milo reads the text off it and keeps the sentence along with the book, the date and the page.',
        'facts': [('Languages', '11'), ('Model', 'Free with Pro'), ('Released', 'September 2026')],
        'features': [
            ('Catch a line in seconds', 'Text is recognized on the phone, so the photo of the page never has to leave it.'),
            ('Word notebook', 'Tap a word in a quote to see what it means in that sentence, in your language, whatever language the book is in.'),
            ('Milo Post', 'Seal a quote and watch it fly across a world map to a reader somewhere else. It arrives hours later, and they can write back.'),
            ('Shelves that stay honest', 'Track what you are reading, what is next and what you finished, without turning reading into bookkeeping.'),
        ],
        'built': [
            'Expo SDK 57 with on-device OCR. Photos of pages stay on the phone.',
            'Supabase for sync, letters and analytics. No third-party analytics SDK.',
            'Word definitions are moving to Claude (Haiku 5.5): 29/30 on our multilingual eval. They ship in the next release.',
            'Nothing is sent to an AI until the reader agrees, and the consent names the provider (Apple 5.1.2(i)).',
            'UI in 11 languages, including Traditional Chinese, Japanese and Korean.',
        ],
    },
    {
        'slug': 'stirred', 'name': 'Stirred', 'store_name': 'Stirred: Cocktail Recipes',
        'tagline': 'What can your bar make tonight?',
        'category': 'Food & Drink', 'platforms': ['iOS', 'iPadOS'], 'featured': True,
        'appstore': 'https://apps.apple.com/app/id6816961742',
        'privacy': 'https://stirred-legal.muratcan-ysfgl.workers.dev/',
        'accent': '#9a5b2c',
        'summary': 'Mark the bottles on your shelf and Stirred shows every cocktail you can make, the drinks you are one bottle away from, and the single bottle that opens up the most new recipes.',
        'facts': [('Languages', '31'), ('Model', 'Free with Pro'), ('Released', 'October 2026')],
        'features': [
            ('600 tested recipes', 'Every IBA official cocktail, modern classics and 100 mocktails. Each recipe is checked against two independent published sources.'),
            ('Smart matching', 'A bottle of bourbon counts toward any whiskey recipe, and close substitutes are suggested.'),
            ('Shelf scan', 'Photograph your bar and the bottles go straight into your inventory.'),
            ('The next bottle', 'Ranked by how many new drinks it would open up for you.'),
        ],
        'built': [
            'Works offline: the full recipe catalog ships inside the app, with no account and no ads.',
            'Shelf scan runs on a Cloudflare Worker with schema-constrained model output. The model can only name bottles that exist in the catalog.',
            'Matching rules (parent and child ingredients, substitutes, garnishes) are unit-tested.',
            'Localized into 31 languages through our Claude Opus i18n pipeline.',
        ],
    },
    {
        'slug': 'whos-imposter', 'name': "Who's Imposter?", 'store_name': "Who's Imposter? Party Games",
        'tagline': 'One phone. Zero WiFi. Twelve party games.',
        'category': 'Games', 'platforms': ['iOS', 'iPadOS'],
        'appstore': 'https://apps.apple.com/app/id6760238596',
        'accent': '#b8402f',
        'summary': 'An offline party-game collection for groups of 3 to 15 players, passed around a single phone. The classic Imposter round comes with eleven more games.',
        'facts': [('Players', '3–15'), ('Model', 'Free with Pro'), ('Released', 'April 2026')],
        'features': [
            ('Imposter', 'Everyone sees the secret word except the Imposter. Blend in, or catch the spy.'),
            ('Six free games', 'Truth or Dare, Never Have I Ever, Most Likely To, Hot Takes and Would You Rather.'),
            ('Pro games', 'Two Truths & a Lie, Heads Up!, Word Chain and more, all unlocked with one subscription.'),
        ],
        'built': ['React Native (Expo). Fully offline, with no account and no ads.'],
    },
    {
        'slug': 'copydeck', 'name': 'Copydeck', 'store_name': 'Copydeck – Clipboard Manager',
        'tagline': 'Everything you copy, remembered for months.',
        'category': 'Productivity', 'platforms': ['macOS'], 'wide': True,
        'appstore': 'https://apps.apple.com/app/id6796044611',
        'privacy': 'https://clipnest-legal.muratcan-ysfgl.workers.dev/legal/privacy/',
        'accent': '#2f7a5b',
        'summary': 'A fast, native menu-bar app that keeps a searchable history of your clipboard, including text, links and images, so anything you copied is one keystroke away.',
        'facts': [('Shortcut', '⌘⇧V'), ('Model', 'Free, one-time Pro'), ('Released', 'September 2026')],
        'features': [
            ('Long memory', 'Keeps hundreds of clips by default, and you decide how long.'),
            ('Text inside images', 'On-device OCR makes screenshots searchable and copyable.'),
            ('Keyboard-first', 'Arrow keys to browse, Enter to copy, Esc to close.'),
            ('Private by design', 'Everything stays on your Mac, and content copied from password managers is ignored.'),
        ],
        'built': ['Native Swift and SwiftUI menu-bar app. OCR uses Apple Vision, entirely on-device.'],
    },
    {
        'slug': 'soundboard-pro', 'name': 'Soundboard Pro', 'store_name': 'Soundboard Pro: Meme Sounds',
        'tagline': 'Tap a pad. The sound is out.',
        'category': 'Entertainment', 'platforms': ['iOS', 'iPadOS'],
        'appstore': 'https://apps.apple.com/app/id6742381379',
        'accent': '#7a4bb5',
        'summary': '227 sound effects on five boards: podcast stings, drumrolls and the memes everyone knows. Every sound is already on your phone.',
        'facts': [('Rating', '5.0 ★'), ('Model', 'Paid once'), ('Languages', '38')],
        'features': [
            ('Instant pads', 'Every one of the 227 sounds plays on the first tap.'),
            ('Import your own', 'Any audio file becomes a pad like the rest.'),
            ('No strings', 'No ads, no subscription, no account, and no analytics.'),
        ],
        'built': ['React Native (Expo). Works with the WiFi off.'],
    },
    {
        'slug': 'name-generator', 'name': 'Name Generator', 'store_name': 'Name Generator: Baby & Brand',
        'tagline': 'The right name, with its meaning.',
        'category': 'Productivity', 'platforms': ['iOS', 'iPadOS'],
        'appstore': 'https://apps.apple.com/app/id6741737856',
        'accent': '#3d5a99',
        'summary': 'Unique names in seconds for a baby, brand, startup, pet or character. Every suggestion comes with its meaning and cultural origin.',
        'facts': [('Styles', '40+'), ('Model', 'Free with Premium'), ('Released', 'February 2025')],
        'features': [
            ('Purpose-aware', 'Separate modes for babies, brands, businesses, gaming, pets and more.'),
            ('Meanings and origins', 'Every result is explained, from Latin and Nordic names to Japanese and Arabic ones.'),
            ('Name Insight', 'Look up the meaning of any name.'),
        ],
        'built': ['React Native (Expo). Generation runs through our own API on Cloudflare Workers.'],
    },
    {
        'slug': 'aurora', 'name': 'Aurora', 'store_name': 'Aurora: Quotes & Affirmations',
        'tagline': 'A small spark, every day.',
        'category': 'Health & Fitness', 'platforms': ['iOS', 'iPadOS'],
        'appstore': 'https://apps.apple.com/app/id6747951525',
        'accent': '#c08a2e',
        'summary': 'Daily quotes and affirmations matched to your mood and goals, with home-screen widgets, streaks and themes.',
        'facts': [('Categories', '24+'), ('Model', 'Free with Premium'), ('Released', 'August 2025')],
        'features': [
            ('Mood-matched', 'Quotes chosen for how you feel today.'),
            ('Widgets', 'Your daily quote on the home screen.'),
            ('Streaks and reminders', 'Gentle nudges to keep the habit going.'),
        ],
        'built': ['React Native (Expo) with native iOS widgets.'],
    },
    {
        'slug': 'petmorph', 'name': 'PetMorph AI', 'store_name': 'PetMorph AI',
        'tagline': 'Your pet, reimagined.',
        'category': 'Photo & Video', 'platforms': ['iOS', 'iPadOS'],
        'appstore': 'https://apps.apple.com/app/id6744692370',
        'accent': '#4b8a8a',
        'summary': 'Turn a photo of your cat or dog into a human portrait, an anime hero, a Renaissance painting and more.',
        'facts': [('Styles', '10+'), ('Model', 'Free'), ('Released', 'May 2025')],
        'features': [
            ('10+ styles', 'Realistic human, anime, cyberpunk, fantasy, Renaissance, watercolor and more.'),
            ('Gallery', 'Save your creations and revisit your style history.'),
        ],
        'built': ['Image generation models behind a three-step flow: upload, pick a style, generate. No sign-up.'],
    },
]

PLATFORM_ORDER = ['iOS', 'iPadOS', 'Android', 'macOS']

e = html.escape


def shots(slug):
    folder = ROOT / 'assets' / 'apps' / slug
    return sorted(p.name for p in folder.glob('shot-*.webp'))


APPLE = '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M16.4 12.6c0-2.3 1.9-3.4 2-3.5-1.1-1.6-2.8-1.8-3.4-1.8-1.4-.2-2.8.8-3.5.8-.7 0-1.8-.8-3-.8-1.5 0-3 .9-3.8 2.3-1.6 2.8-.4 7 1.2 9.3.8 1.1 1.7 2.4 2.9 2.3 1.2 0 1.6-.7 3-.7s1.8.7 3 .7c1.3 0 2.1-1.1 2.8-2.3.9-1.3 1.3-2.6 1.3-2.6s-2.5-1-2.5-3.7zM14.2 5.8c.6-.8 1.1-1.8 1-2.8-.9 0-2 .6-2.7 1.4-.6.7-1.1 1.7-1 2.7 1 .1 2-.5 2.7-1.3z"/></svg>'
PLAY = '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M4.2 2.6c-.3.3-.4.7-.4 1.2v16.4c0 .5.1.9.4 1.2l9.1-9.4-9.1-9.4zm10.4 8.1 2.6-2.7-10.9-6.2c-.4-.2-.8-.3-1.1-.2l9.4 9.1zm0 2.6-9.4 9.1c.3.1.7 0 1.1-.2l10.9-6.2-2.6-2.7zm5.6-3.6-2.3-1.3-2.9 2.9 2.9 2.9 2.3-1.3c.9-.5.9-1.7 0-2.2z"/></svg>'


def store_buttons(app, compact=False):
    out = []
    label_as = 'Mac App Store' if app['platforms'] == ['macOS'] else 'App Store'
    out.append(f'<a class="store-btn" href="{app["appstore"]}" target="_blank" rel="noopener">{APPLE}<span><small>Download on the</small>{label_as}</span></a>')
    if app.get('play'):
        out.append(f'<a class="store-btn" href="{app["play"]}" target="_blank" rel="noopener">{PLAY}<span><small>Get it on</small>Google Play</span></a>')
    return f'<div class="store-row{" compact" if compact else ""}">{"".join(out)}</div>'


def platform_tags(app):
    return ''.join(f'<span class="chip">{p}</span>' for p in PLATFORM_ORDER if p in app['platforms'])


def page(title, description, body, root='', current=''):
    def nav(href, label, key):
        cur = ' aria-current="page"' if key == current else ''
        return f'<a href="{root}{href}"{cur}>{label}</a>'
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{e(title)}</title>
  <meta name="description" content="{e(description)}">
  <meta property="og:title" content="{e(title)}">
  <meta property="og:description" content="{e(description)}">
  <meta property="og:type" content="website">
  <link rel="icon" href="{root}favicon.svg" type="image/svg+xml">
  <link rel="apple-touch-icon" href="{root}apple-touch-icon.png">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Newsreader:opsz,wght@6..72,400;6..72,500&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="{root}styles.css">
</head>
<body>

<header class="site-header">
  <div class="wrap">
    <a class="brand" href="{root}index.html"><img class="brand-mark" src="{root}favicon.svg" alt=""> MyApps Studio</a>
    <nav class="nav">
      {nav('index.html#work', 'Work', 'work')}
      {nav('claude.html', 'How we build', 'claude')}
      {nav('index.html#studio', 'Studio', 'studio')}
      <a class="nav-cta" href="mailto:{EMAIL}">Contact</a>
    </nav>
  </div>
</header>

<main>
{body}
</main>

<footer class="site-footer">
  <div class="wrap footer-grid">
    <div>
      <a class="brand" href="{root}index.html"><img class="brand-mark" src="{root}favicon.svg" alt=""> MyApps Studio</a>
      <p class="muted">An independent app studio in Ankara, Türkiye. Founded in 2024.</p>
    </div>
    <div>
      <h4>Apps</h4>
      {''.join(f'<a href="{root}apps/{a["slug"]}.html">{e(a["name"])}</a>' for a in APPS)}
    </div>
    <div>
      <h4>Studio</h4>
      <a href="{root}claude.html">How we build</a>
      <a href="{root}index.html#studio">About</a>
      <a href="{DEVELOPER}" target="_blank" rel="noopener">App Store developer page</a>
      <a href="https://github.com/muratcanyusufoglu" target="_blank" rel="noopener">GitHub</a>
      <a href="mailto:{EMAIL}">{EMAIL}</a>
    </div>
  </div>
  <div class="wrap footer-base muted">© 2026 MyApps Studio · Muratcan Yusufoğlu</div>
</footer>

</body>
</html>
'''


def app_card(app, root=''):
    return f'''<a class="app-card" href="{root}apps/{app['slug']}.html">
          <img class="app-icon" src="{root}assets/apps/{app['slug']}/icon.png" alt="" loading="lazy">
          <div>
            <h3>{e(app['name'])}</h3>
            <p>{e(app['tagline'])}</p>
            <div class="chips">{platform_tags(app)}<span class="chip chip-plain">{e(app['category'])}</span></div>
          </div>
        </a>'''


def featured_block(app):
    imgs = ''.join(f'<img src="assets/apps/{app["slug"]}/{s}" alt="{e(app["name"])} screenshot" loading="lazy">' for s in shots(app['slug'])[:3])
    return f'''<article class="feature" style="--accent:{app['accent']}">
        <div class="feature-text">
          <div class="app-title">
            <img class="app-icon" src="assets/apps/{app['slug']}/icon.png" alt="">
            <div><h3>{e(app['name'])}</h3><small>{e(app['category'])} · {' · '.join(p for p in PLATFORM_ORDER if p in app['platforms'])}</small></div>
          </div>
          <p class="feature-tagline">{e(app['tagline'])}</p>
          <p>{e(app['summary'])}</p>
          <dl class="facts">{''.join(f'<div><dt>{e(k)}</dt><dd>{e(v)}</dd></div>' for k, v in app['facts'])}</dl>
          <div class="feature-actions">
            <a class="btn btn-primary" href="apps/{app['slug']}.html">Read more</a>
            {store_buttons(app, compact=True)}
          </div>
        </div>
        <div class="shots">{imgs}</div>
      </article>'''


def build_index():
    featured = [a for a in APPS if a.get('featured')]
    rest = [a for a in APPS if not a.get('featured')]
    hero_shots = [('hairon', 'shot-1.webp'), ('milo', 'shot-1.webp'), ('stirred', 'shot-1.webp')]
    body = f'''  <section class="hero">
    <div class="wrap hero-grid">
      <div>
        <p class="eyebrow">Independent app studio · Ankara</p>
        <h1>We make focused, well-crafted apps for everyday moments.</h1>
        <p class="lede">MyApps Studio designs, builds and runs consumer apps end to end: product, engineering, localization and growth. There are nine apps on the App Store today, three of them in active development.</p>
        <div class="hero-actions">
          <a class="btn btn-primary" href="#work">See our work</a>
          <a class="btn btn-ghost" href="claude.html">How we build</a>
        </div>
      </div>
      <div class="hero-phones" aria-hidden="true">
        {''.join(f'<img src="assets/apps/{s}/{f}" alt="">' for s, f in hero_shots)}
      </div>
    </div>
    <div class="wrap">
      <div class="stats">
        <div class="stat"><b>9</b><span>apps live on the App Store</span></div>
        <div class="stat"><b>31</b><span>languages in our largest apps</span></div>
        <div class="stat"><b>4</b><span>platforms: iOS, iPadOS, Android, macOS</span></div>
        <div class="stat"><b>2024</b><span>founded in Ankara, Türkiye</span></div>
      </div>
    </div>
  </section>

  <section id="work">
    <div class="wrap">
      <div class="section-head">
        <p class="eyebrow">Selected work</p>
        <h2>Products in active development</h2>
        <p>Each of these runs on its own backend, checks subscriptions on the server, and ships updates every few weeks.</p>
      </div>
      {''.join(featured_block(a) for a in featured)}
    </div>
  </section>

  <section id="apps">
    <div class="wrap">
      <div class="section-head">
        <p class="eyebrow">Catalog</p>
        <h2>Everything we've shipped</h2>
      </div>
      <div class="app-grid">
        {''.join(app_card(a) for a in rest)}
      </div>
    </div>
  </section>

  <section id="principles">
    <div class="wrap">
      <div class="section-head">
        <p class="eyebrow">How we work</p>
        <h2>A few rules every app follows</h2>
      </div>
      <div class="principles">
        <div><h3>Private by default</h3><p>OCR, recipe matching and clipboard history run on the device. When data has to leave the phone, we send the minimum and name who receives it.</p></div>
        <div><h3>Works offline</h3><p>Catalogs and sound libraries ship inside the app. Party games, recipes and soundboards work with the WiFi off.</p></div>
        <div><h3>Built for every language</h3><p>Our larger apps ship in 31 languages, with plural forms and placeholders checked automatically before every release.</p></div>
        <div><h3>AI where it earns its place</h3><p>Every model is chosen against an eval set, runs behind a server-side quota, and has a graceful fallback when it is unavailable.</p></div>
      </div>
    </div>
  </section>

  <section id="stack">
    <div class="wrap split">
      <div class="section-head">
        <p class="eyebrow">Stack</p>
        <h2>One toolkit, reused across every app</h2>
        <p>New apps start from our own Expo template, which comes with localization, theming, onboarding, a paywall, server-side quotas and store automation already wired in. That's how a small studio ships at this pace.</p>
        <p><a href="claude.html">Read how Claude fits into this →</a></p>
      </div>
      <ul class="stack-list">
        <li><b>Apps</b><span>React Native · Expo · TypeScript · Swift / SwiftUI</span></li>
        <li><b>Backend</b><span>Supabase (Postgres, Edge Functions) · Cloudflare Workers, D1</span></li>
        <li><b>AI</b><span>Claude API · image models via fal.ai · on-device Vision OCR</span></li>
        <li><b>Revenue</b><span>RevenueCat · StoreKit · Google Play Billing</span></li>
        <li><b>Release</b><span>EAS Build · fastlane · store listings in 31 languages</span></li>
        <li><b>Engineering</b><span>Claude Code in every repository</span></li>
      </ul>
    </div>
  </section>

  <section id="studio">
    <div class="wrap split">
      <div class="section-head">
        <p class="eyebrow">Studio</p>
        <h2>Founded and run by Muratcan Yusufoğlu</h2>
      </div>
      <div class="about">
        <p>I'm a full-stack and mobile engineer with more than four years of experience shipping production systems in React Native, React and NestJS, from mobile apps and admin panels to event-driven backends.</p>
        <p>I started MyApps Studio in April 2024 to build my own products. I handle product, design, engineering and growth for each app end to end, and Claude Code is my day-to-day engineering partner.</p>
        <div class="hero-actions">
          <a class="btn btn-primary" href="mailto:{EMAIL}">{EMAIL}</a>
          <a class="btn btn-ghost" href="https://github.com/muratcanyusufoglu" target="_blank" rel="noopener">GitHub</a>
        </div>
      </div>
    </div>
  </section>
'''
    return page('MyApps Studio — Independent App Studio',
                'MyApps Studio is an independent app studio in Ankara with nine apps on the App Store, including HairOn, Milo and Stirred.',
                body, current='work')


def build_app(app):
    i = APPS.index(app)
    nxt = APPS[(i + 1) % len(APPS)]
    root = '../'
    wide = ' wide' if app.get('wide') else ''
    gallery = ''.join(f'<img src="{root}assets/apps/{app["slug"]}/{s}" alt="{e(app["name"])} screenshot {n + 1}" loading="lazy">'
                      for n, s in enumerate(shots(app['slug'])))
    links = [f'<a href="{app["appstore"]}" target="_blank" rel="noopener">App Store listing</a>']
    if app.get('play'):
        links.append(f'<a href="{app["play"]}" target="_blank" rel="noopener">Google Play listing</a>')
    if app.get('privacy'):
        links.append(f'<a href="{app["privacy"]}" target="_blank" rel="noopener">Privacy policy</a>')
    body = f'''  <section class="app-hero" style="--accent:{app['accent']}">
    <div class="wrap">
      <a class="back" href="{root}index.html#work">← All work</a>
      <div class="app-head">
        <img class="app-icon app-icon-lg" src="{root}assets/apps/{app['slug']}/icon.png" alt="">
        <div>
          <h1>{e(app['name'])}</h1>
          <p class="lede">{e(app['tagline'])}</p>
          <div class="chips">{platform_tags(app)}<span class="chip chip-plain">{e(app['category'])}</span></div>
        </div>
      </div>
      <p class="app-summary">{e(app['summary'])}</p>
      {store_buttons(app)}
    </div>
  </section>

  <section class="gallery-section">
    <div class="wrap">
      <div class="gallery{wide}">{gallery}</div>
    </div>
  </section>

  <section>
    <div class="wrap app-body">
      <div>
        <p class="eyebrow">What it does</p>
        <div class="feature-list">
          {''.join(f'<div><h3>{e(t)}</h3><p>{e(d)}</p></div>' for t, d in app['features'])}
        </div>
        <p class="eyebrow" style="margin-top:48px">How it's built</p>
        <ul class="built-list">{''.join(f'<li>{e(b)}</li>' for b in app['built'])}</ul>
      </div>
      <aside class="app-aside">
        <dl class="facts">
          <div><dt>Category</dt><dd>{e(app['category'])}</dd></div>
          <div><dt>Platforms</dt><dd>{', '.join(p for p in PLATFORM_ORDER if p in app['platforms'])}</dd></div>
          {''.join(f'<div><dt>{e(k)}</dt><dd>{e(v)}</dd></div>' for k, v in app['facts'])}
        </dl>
        <div class="aside-links">{''.join(links)}</div>
      </aside>
    </div>
  </section>

  <section>
    <div class="wrap">
      <a class="next-app" href="{nxt['slug']}.html">
        <span class="muted">Next app</span>
        <span class="next-name"><img class="app-icon" src="{root}assets/apps/{nxt['slug']}/icon.png" alt=""> {e(nxt['name'])} →</span>
      </a>
    </div>
  </section>
'''
    return page(f'{app["name"]} · MyApps Studio', f'{app["store_name"]}: {app["summary"]}', body, root=root)


def build_claude():
    body = (ROOT / 'src' / 'claude.body.html').read_text()
    return page('How We Build · MyApps Studio',
                'How a one-person app studio uses Claude Code and the Claude API to build, localize and ship nine apps.',
                body, current='claude')


def main():
    (ROOT / 'apps').mkdir(exist_ok=True)
    (ROOT / 'index.html').write_text(build_index())
    (ROOT / 'claude.html').write_text(build_claude())
    for app in APPS:
        (ROOT / 'apps' / f'{app["slug"]}.html').write_text(build_app(app))
    print(f'built index, claude and {len(APPS)} app pages')

    if '--dist' in sys.argv:
        dist = Path(sys.argv[sys.argv.index('--dist') + 1]).resolve()
        if dist.exists():
            shutil.rmtree(dist)
        dist.mkdir(parents=True)
        for name in ['index.html', 'claude.html', 'styles.css', 'favicon.svg', 'apple-touch-icon.png', 'robots.txt', 'sitemap.xml']:
            if (ROOT / name).exists():
                shutil.copy2(ROOT / name, dist / name)
        shutil.copytree(ROOT / 'apps', dist / 'apps')
        shutil.copytree(ROOT / 'assets', dist / 'assets')
        print(f'dist → {dist}')


if __name__ == '__main__':
    main()
