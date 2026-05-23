import os
import requests
from datetime import date


def get_public_url_from_env():
    url = os.getenv("VIDEO_PUBLIC_URL")
    return url.strip() if url else None


def upload_to_github_release(file_path):
    # Upload to GitHub Releases and return direct download URL
    github_token = os.getenv("GITHUB_TOKEN")
    github_repo = os.getenv("GITHUB_REPO")  # format: owner/repo

    if not github_token or not github_repo:
        return None

    try:
        today = date.today().isoformat()
        tag = f"video-{today}"
        filename = os.path.basename(file_path)
        
        headers = {
            "Authorization": f"token {github_token}",
            "Accept": "application/vnd.github.v3+json",
        }
        
        # Create or get release
        release_url = f"https://api.github.com/repos/{github_repo}/releases/tags/{tag}"
        r = requests.get(release_url, headers=headers)
        
        if r.status_code == 404:
            # Create new release
            create_url = f"https://api.github.com/repos/{github_repo}/releases"
            release_data = {"tag_name": tag, "name": f"Daily Quote Video {today}", "body": f"Auto-generated video for {today}"}
            r = requests.post(create_url, json=release_data, headers=headers)
            r.raise_for_status()
        
        release = r.json()
        release_id = release["id"]
        
        # Upload asset
        upload_url = f"https://uploads.github.com/repos/{github_repo}/releases/{release_id}/assets?name={filename}"
        with open(file_path, "rb") as f:
            headers["Content-Type"] = "video/mp4"
            r = requests.post(upload_url, data=f, headers=headers)
            r.raise_for_status()
        
        asset = r.json()
        return asset.get("browser_download_url") or asset.get("url")
        
    except Exception as e:
        print("❌ GitHub upload failed:", e)
        return None


def get_or_upload(file_path):
    # Prefer env URL
    public = get_public_url_from_env()
    if public:
        return public

    # Use GitHub Releases
    try:
        url = upload_to_github_release(file_path)
        if url:
            print(f"✅ GitHub Release URL: {url}")
            return url
    except Exception as e:
        print("❌ Hosting upload failed:", e)

    return None
