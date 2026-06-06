#!/usr/bin/env python3
"""Create GitHub repository for WIE project"""

import requests
import json

PAT = "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"
USERNAME = "KnowNowSites"

headers = {
    "Authorization": f"token {PAT}",
    "Content-Type": "application/json"
}

data = {
    "name": "wedge-intelligence-engine",
    "private": True,
    "description": "AI-powered startup wedge detection platform — live dashboard with scrapers, detectors, and scoring engine."
}

response = requests.post("https://api.github.com/user/repos", headers=headers, json=data)

if response.status_code == 201:
    repo_data = response.json()
    print(f"✅ Repository created successfully!")
    print(f"URL: {repo_data['html_url']}")
    print(f"Clone URL: {repo_data['clone_url']}")
else:
    print(f"❌ Error creating repository: {response.status_code}")
    print(f"Response: {response.json()}")
