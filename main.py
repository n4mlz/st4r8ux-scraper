#!/usr/bin/env python3
"""
st4r8ux Job Scraper - Minimal version
"""

import json
import os
import sys
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

BASE = os.getenv("ST4R8UX_URL")


def fetch_page():
    """Fetch the career page."""
    url = BASE + "/jobfind-pc/area/Kanto/Ibaraki/08220"

    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"Error fetching page: {e}")
        sys.exit(1)


def parse_jobs(html: str):
    """Parse job information from HTML."""
    soup = BeautifulSoup(html, "html.parser")
    jobs = []

    for box in soup.select("div.jobs_name"):
        h2 = box.find("h2")
        h3 = box.find("h3")
        a = h2.find("a") if h2 else None

        # Store name (including annotations) as-is
        store_name = (
            a.get_text(strip=True) if a else (h2.get_text(strip=True) if h2 else "")
        )
        role = h3.get_text(strip=True) if h3 else ""

        # ID and URL (useful for duplicate detection and notification links)
        href = a["href"] if (a and a.has_attr("href")) else None
        url = urljoin(BASE, href) if href else None
        job_id = href.rsplit("/", 1)[-1] if href else store_name  # e.g., "86529"

        if store_name:
            jobs.append(
                {
                    "id": job_id,
                    "store": store_name,
                    "role": role,
                    "url": url,
                }
            )

    # Remove duplicates by ID (just in case)
    uniq = {j["id"]: j for j in jobs}
    return list(uniq.values())


def notify_discord(jobs, include_empty=False):
    """Send notification to Discord."""
    webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
    if not webhook_url:
        print("No Discord webhook URL set")
        return

    # Check store names against target keywords (annotations included in matching)
    target_keywords = ["中央図書館", "筑波大学", "つくば", "研究学園"]
    target = [
        j
        for j in jobs
        if any(kw.lower() in j["store"].lower() for kw in target_keywords)
    ]

    if target:
        embeds = []
        for j in target[:10]:
            title = f"{j['store']} — {j['role']}" if j["role"] else j["store"]
            embeds.append(
                {
                    "title": title,
                    "url": j["url"],
                    "color": 0x00FF00,
                }
            )

        payload = {
            "content": f"🆕 New jobs found: {len(target)} positions",
            "embeds": embeds,
        }
        log_message = f"Notification sent for {len(target)} jobs"
    else:
        if not include_empty:
            print("No target jobs found")
            return

        content = (
            "ℹ️ New jobs were detected, but none matched the target keywords."
            if jobs
            else "ℹ️ No new jobs detected at this time."
        )
        payload = {"content": content}
        log_message = "Notification sent with no matching updates"

    try:
        response = requests.post(webhook_url, json=payload, timeout=10)
        response.raise_for_status()
        print(log_message)
    except Exception as e:
        print(f"Error sending notification: {e}")


def main():
    """Main function."""
    data_file = Path("/app/data/data.json")

    # Load previous data
    seen_jobs = {}  # {id: {"store": store_name, "role": role}}
    if data_file.exists():
        try:
            with open(data_file) as f:
                data = json.load(f)
                seen_jobs = data.get("seen_jobs", {})
        except Exception as e:
            print(f"Error loading data: {e}")

    # Fetch and parse
    html = fetch_page()
    jobs = parse_jobs(html)

    # Find new jobs
    new_jobs = [job for job in jobs if job["id"] not in seen_jobs]

    if new_jobs:
        print(f"Found {len(new_jobs)} new jobs")

        # Update seen jobs with new jobs
        for job in new_jobs:
            seen_jobs[job["id"]] = {"store": job["store"], "role": job["role"]}

        # Also update existing jobs in case store names changed
        for job in jobs:
            if job["id"] in seen_jobs:
                seen_jobs[job["id"]] = {"store": job["store"], "role": job["role"]}

        with open(data_file, "w") as f:
            json.dump({"seen_jobs": seen_jobs}, f, ensure_ascii=False, indent=2)
    else:
        print("No new jobs found")

        # Update existing jobs in case store names changed
        for job in jobs:
            if job["id"] in seen_jobs:
                seen_jobs[job["id"]] = {"store": job["store"], "role": job["role"]}

        # Save updated job information
        with open(data_file, "w") as f:
            json.dump({"seen_jobs": seen_jobs}, f, ensure_ascii=False, indent=2)

    notify_discord(new_jobs, include_empty=True)


if __name__ == "__main__":
    main()
