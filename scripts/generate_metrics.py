"""
🔥 Custom GitHub Profile Metrics Generator
Generates beautiful SVG visualizations for the GitHub profile README.
Runs via GitHub Actions — outputs SVG files to assets/generated/
"""

import json
import urllib.request
import os
import sys
from datetime import datetime, timezone

# ─── Configuration ───────────────────────────────────────────────────────────
USERNAME = os.environ.get("GITHUB_USERNAME", "fazal-e-haq")
TOKEN = os.environ.get("GITHUB_TOKEN", "")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "assets", "generated")

# 🔥 Fire theme colors
COLORS = {
    "bg":          "#0d1117",
    "card_bg":     "#161b22",
    "border":      "#FF450040",
    "title":       "#FF4500",
    "text":        "#c9d1d9",
    "subtext":     "#8b949e",
    "accent1":     "#FF4500",
    "accent2":     "#FF6347",
    "accent3":     "#FF8C00",
    "accent4":     "#FFA500",
    "bar_bg":      "#21262d",
    "green1":      "#0e4429",
    "green2":      "#006d32",
    "green3":      "#26a641",
    "green4":      "#39d353",
}


def github_api(endpoint):
    """Fetch data from GitHub API."""
    url = f"https://api.github.com/{endpoint}"
    req = urllib.request.Request(url)
    req.add_header("Accept", "application/vnd.github+json")
    if TOKEN:
        req.add_header("Authorization", f"Bearer {TOKEN}")
    req.add_header("User-Agent", "GitHub-Profile-Metrics")
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        print(f"⚠️  API call failed for {endpoint}: {e}")
        return None


def fetch_user_data():
    """Fetch all needed data from GitHub API."""
    user = github_api(f"users/{USERNAME}") or {}
    repos = github_api(f"users/{USERNAME}/repos?per_page=100&sort=updated") or []

    # Calculate stats
    total_stars = sum(r.get("stargazers_count", 0) for r in repos)
    total_forks = sum(r.get("forks_count", 0) for r in repos)
    total_repos = len(repos)
    followers = user.get("followers", 0)
    following = user.get("following", 0)

    # Language breakdown
    lang_counts = {}
    for r in repos:
        lang = r.get("language")
        if lang:
            lang_counts[lang] = lang_counts.get(lang, 0) + 1
    total_lang = sum(lang_counts.values()) or 1
    languages = sorted(lang_counts.items(), key=lambda x: -x[1])[:6]

    return {
        "name": user.get("name", USERNAME),
        "bio": user.get("bio", "Flutter Developer & Product Designer"),
        "avatar": user.get("avatar_url", ""),
        "public_repos": user.get("public_repos", total_repos),
        "followers": followers,
        "following": following,
        "total_stars": total_stars,
        "total_forks": total_forks,
        "languages": languages,
        "total_lang": total_lang,
        "created_at": user.get("created_at", ""),
        "repos": repos,
    }


# ─── Language Colors ─────────────────────────────────────────────────────────
LANG_COLORS = {
    "Dart":        "#00B4AB",
    "JavaScript":  "#f1e05a",
    "TypeScript":  "#3178c6",
    "Python":      "#3572A5",
    "HTML":        "#e34c26",
    "CSS":         "#563d7c",
    "C++":         "#f34b7d",
    "Java":        "#b07219",
    "Kotlin":      "#A97BFF",
    "Swift":       "#F05138",
    "Ruby":        "#701516",
    "Go":          "#00ADD8",
    "Rust":        "#dea584",
    "Shell":       "#89e051",
    "PHP":         "#4F5D95",
    "Vue":         "#41b883",
    "SCSS":        "#c6538c",
    "C#":          "#178600",
    "Dockerfile":  "#384d54",
    "Makefile":    "#427819",
    "CMake":       "#DA3434",
}


def generate_stats_card(data):
    """Generate a beautiful stats overview SVG card."""
    stats = [
        ("⭐", "Total Stars",    str(data["total_stars"])),
        ("🍴", "Total Forks",    str(data["total_forks"])),
        ("📦", "Public Repos",   str(data["public_repos"])),
        ("👥", "Followers",      str(data["followers"])),
        ("👤", "Following",      str(data["following"])),
    ]

    rows = ""
    for i, (icon, label, value) in enumerate(stats):
        y = 95 + i * 42
        # Animated bar
        bar_width = min(int(value) * 8, 220) if value.isdigit() else 60
        rows += f'''
        <g transform="translate(30, {y})" style="animation: fadeIn 0.5s ease {i * 0.1}s both;">
          <text x="0" y="0" fill="{COLORS['text']}" font-size="14" font-family="'Segoe UI', Ubuntu, sans-serif" dominant-baseline="middle">{icon} {label}</text>
          <rect x="180" y="-8" width="240" height="16" rx="8" fill="{COLORS['bar_bg']}"/>
          <rect x="180" y="-8" width="{bar_width}" height="16" rx="8" fill="url(#fireGradient)" opacity="0.9">
            <animate attributeName="width" from="0" to="{bar_width}" dur="1.2s" fill="freeze" begin="{i * 0.15}s"/>
          </rect>
          <text x="430" y="0" fill="{COLORS['accent1']}" font-size="15" font-weight="bold" font-family="'JetBrains Mono', monospace" dominant-baseline="middle" text-anchor="end">{value}</text>
        </g>'''

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="480" height="340" viewBox="0 0 480 340">
  <defs>
    <linearGradient id="fireGradient" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="{COLORS['accent1']}"/>
      <stop offset="50%" stop-color="{COLORS['accent2']}"/>
      <stop offset="100%" stop-color="{COLORS['accent3']}"/>
    </linearGradient>
    <linearGradient id="borderGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="{COLORS['accent1']}" stop-opacity="0.6"/>
      <stop offset="100%" stop-color="{COLORS['accent3']}" stop-opacity="0.2"/>
    </linearGradient>
    <filter id="glow">
      <feGaussianBlur stdDeviation="3" result="blur"/>
      <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <style>
      @keyframes fadeIn {{ from {{ opacity: 0; transform: translateX(-10px); }} to {{ opacity: 1; transform: translateX(0); }} }}
    </style>
  </defs>

  <!-- Card background -->
  <rect x="1" y="1" width="478" height="338" rx="16" fill="{COLORS['card_bg']}"/>
  <rect x="1" y="1" width="478" height="338" rx="16" fill="none" stroke="url(#borderGrad)" stroke-width="1.5"/>

  <!-- Title -->
  <text x="240" y="40" fill="{COLORS['accent1']}" font-size="20" font-weight="bold" font-family="'Segoe UI', Ubuntu, sans-serif" text-anchor="middle" filter="url(#glow)">📊 GitHub Stats Overview</text>
  <line x1="40" y1="58" x2="440" y2="58" stroke="{COLORS['border']}" stroke-width="1"/>

  <!-- Stats rows -->
  {rows}

  <!-- Timestamp -->
  <text x="240" y="325" fill="{COLORS['subtext']}" font-size="10" font-family="'Segoe UI', Ubuntu, sans-serif" text-anchor="middle">Last updated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}</text>
</svg>'''
    return svg


def generate_language_card(data):
    """Generate a beautiful language breakdown SVG with pie-chart-style bars."""
    languages = data["languages"]
    total = data["total_lang"]

    slices = ""
    legend = ""
    bar_y = 80

    for i, (lang, count) in enumerate(languages):
        pct = round(count / total * 100, 1)
        color = LANG_COLORS.get(lang, "#8b949e")
        bar_width = max(int(pct * 3.5), 12)

        # Bar
        slices += f'''
        <g transform="translate(30, {bar_y + i * 38})">
          <text x="0" y="0" fill="{COLORS['text']}" font-size="13" font-family="'Segoe UI', Ubuntu, sans-serif" dominant-baseline="middle">{lang}</text>
          <rect x="120" y="-9" width="260" height="18" rx="9" fill="{COLORS['bar_bg']}"/>
          <rect x="120" y="-9" width="{bar_width}" height="18" rx="9" fill="{color}" opacity="0.85">
            <animate attributeName="width" from="0" to="{bar_width}" dur="1s" fill="freeze" begin="{i * 0.12}s"/>
          </rect>
          <text x="395" y="0" fill="{color}" font-size="13" font-weight="bold" font-family="'JetBrains Mono', monospace" dominant-baseline="middle" text-anchor="end">{pct}%</text>
          <!-- Color dot -->
          <circle cx="415" cy="0" r="5" fill="{color}"/>
        </g>'''

    height = 110 + len(languages) * 38

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="460" height="{height}" viewBox="0 0 460 {height}">
  <defs>
    <linearGradient id="borderGrad2" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="{COLORS['accent1']}" stop-opacity="0.6"/>
      <stop offset="100%" stop-color="{COLORS['accent3']}" stop-opacity="0.2"/>
    </linearGradient>
  </defs>

  <!-- Card -->
  <rect x="1" y="1" width="458" height="{height - 2}" rx="16" fill="{COLORS['card_bg']}"/>
  <rect x="1" y="1" width="458" height="{height - 2}" rx="16" fill="none" stroke="url(#borderGrad2)" stroke-width="1.5"/>

  <!-- Title -->
  <text x="230" y="40" fill="{COLORS['accent1']}" font-size="20" font-weight="bold" font-family="'Segoe UI', Ubuntu, sans-serif" text-anchor="middle">💻 Top Languages</text>
  <line x1="40" y1="58" x2="420" y2="58" stroke="{COLORS['border']}" stroke-width="1"/>

  {slices}

  <text x="230" y="{height - 12}" fill="{COLORS['subtext']}" font-size="10" font-family="'Segoe UI', Ubuntu, sans-serif" text-anchor="middle">Based on {total} repositories</text>
</svg>'''
    return svg


def generate_profile_card(data):
    """Generate a hero profile card SVG."""
    name = data["name"] or USERNAME
    bio = data["bio"] or "Flutter Developer & Product Designer"
    # Truncate bio if too long
    if len(bio) > 60:
        bio = bio[:57] + "..."

    quick_stats = [
        ("📦", str(data["public_repos"]), "Repos"),
        ("⭐", str(data["total_stars"]), "Stars"),
        ("👥", str(data["followers"]), "Followers"),
        ("🍴", str(data["total_forks"]), "Forks"),
    ]

    stat_items = ""
    for i, (icon, val, label) in enumerate(quick_stats):
        x = 60 + i * 115
        stat_items += f'''
        <g transform="translate({x}, 140)">
          <text x="0" y="0" fill="{COLORS['accent1']}" font-size="22" font-weight="bold" font-family="'JetBrains Mono', monospace" text-anchor="middle">{val}</text>
          <text x="0" y="20" fill="{COLORS['subtext']}" font-size="11" font-family="'Segoe UI', Ubuntu, sans-serif" text-anchor="middle">{icon} {label}</text>
        </g>'''

    # Skills tags
    skills = ["Flutter", "Dart", "Firebase", "Figma", "Supabase", "REST API"]
    skill_tags = ""
    for i, skill in enumerate(skills):
        x = 32 + i * 76
        skill_tags += f'''
          <rect x="{x}" y="185" width="70" height="22" rx="11" fill="{COLORS['accent1']}15" stroke="{COLORS['accent1']}40" stroke-width="0.8"/>
          <text x="{x + 35}" y="200" fill="{COLORS['accent2']}" font-size="10" font-family="'Segoe UI', Ubuntu, sans-serif" text-anchor="middle">{skill}</text>'''

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="500" height="230" viewBox="0 0 500 230">
  <defs>
    <linearGradient id="heroGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="{COLORS['accent1']}" stop-opacity="0.15"/>
      <stop offset="100%" stop-color="{COLORS['accent3']}" stop-opacity="0.05"/>
    </linearGradient>
    <linearGradient id="heroBorder" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="{COLORS['accent1']}" stop-opacity="0.7"/>
      <stop offset="50%" stop-color="{COLORS['accent2']}" stop-opacity="0.4"/>
      <stop offset="100%" stop-color="{COLORS['accent3']}" stop-opacity="0.7"/>
    </linearGradient>
  </defs>

  <rect x="1" y="1" width="498" height="228" rx="16" fill="{COLORS['card_bg']}"/>
  <rect x="1" y="1" width="498" height="228" rx="16" fill="url(#heroGrad)"/>
  <rect x="1" y="1" width="498" height="228" rx="16" fill="none" stroke="url(#heroBorder)" stroke-width="1.5"/>

  <!-- Name -->
  <text x="250" y="45" fill="{COLORS['text']}" font-size="26" font-weight="bold" font-family="'Segoe UI', Ubuntu, sans-serif" text-anchor="middle">{name}</text>

  <!-- Bio -->
  <text x="250" y="72" fill="{COLORS['subtext']}" font-size="13" font-family="'Segoe UI', Ubuntu, sans-serif" text-anchor="middle">{bio}</text>

  <!-- Divider -->
  <line x1="60" y1="90" x2="440" y2="90" stroke="{COLORS['border']}" stroke-width="1"/>

  <!-- Quick stats -->
  {stat_items}

  <!-- Skill tags -->
  {skill_tags}
</svg>'''
    return svg


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"🔥 Fetching data for @{USERNAME}...")
    data = fetch_user_data()

    print("📊 Generating stats card...")
    stats_svg = generate_stats_card(data)
    with open(os.path.join(OUTPUT_DIR, "stats-card.svg"), "w", encoding="utf-8") as f:
        f.write(stats_svg)

    print("💻 Generating language card...")
    lang_svg = generate_language_card(data)
    with open(os.path.join(OUTPUT_DIR, "languages-card.svg"), "w", encoding="utf-8") as f:
        f.write(lang_svg)

    print("🎯 Generating profile card...")
    profile_svg = generate_profile_card(data)
    with open(os.path.join(OUTPUT_DIR, "profile-card.svg"), "w", encoding="utf-8") as f:
        f.write(profile_svg)

    print("✅ All SVGs generated successfully!")
    print(f"   Output: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
