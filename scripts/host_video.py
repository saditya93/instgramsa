import os
from datetime import date
from urllib.parse import quote, unquote, urlparse

import requests


def get_public_url_from_env():
    url = os.getenv("VIDEO_PUBLIC_URL")
    return url.strip() if url else None


def get_cloudinary_url_from_env():
    url = os.getenv("CLOUDINARY_URL", "").strip().strip('"').strip("'")
    if "cloudinary://" in url:
        url = url[url.index("cloudinary://") :].strip().strip('"').strip("'")
    return url


def parse_cloudinary_url(url):
    parsed = urlparse(url)
    if parsed.scheme != "cloudinary" or not parsed.username or not parsed.password or not parsed.hostname:
        return None

    return {
        "cloud_name": parsed.hostname,
        "api_key": unquote(parsed.username),
        "api_secret": unquote(parsed.password),
    }


def is_publicly_accessible(url):
    headers = {"User-Agent": "facebookexternalhit/1.1"}

    try:
        response = requests.get(url, headers=headers, stream=True, timeout=30)
        response.close()
    except requests.RequestException as exc:
        print(f"Public URL check failed: {exc}")
        return False

    if response.status_code != 200:
        print(f"Public URL check failed: HTTP {response.status_code} for {url}")
        return False

    content_type = response.headers.get("Content-Type", "")
    if "video" not in content_type and "octet-stream" not in content_type:
        print(f"Public URL check warning: unexpected Content-Type {content_type!r}")

    return True


def upload_to_cloudinary(file_path):
    cloudinary_url = get_cloudinary_url_from_env()
    has_cloudinary_url = bool(cloudinary_url)
    has_cloudinary_keys = all(
        os.getenv(name)
        for name in ("CLOUDINARY_CLOUD_NAME", "CLOUDINARY_API_KEY", "CLOUDINARY_API_SECRET")
    )
    if not (has_cloudinary_url or has_cloudinary_keys):
        return None

    try:
        import cloudinary
        import cloudinary.uploader

        if has_cloudinary_url:
            config = parse_cloudinary_url(cloudinary_url)
            if not config:
                print("Cloudinary upload failed: CLOUDINARY_URL must look like cloudinary://API_KEY:API_SECRET@CLOUD_NAME")
                return None
            cloudinary.config(**config, secure=True)
        else:
            cloudinary.config(
                cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
                api_key=os.getenv("CLOUDINARY_API_KEY"),
                api_secret=os.getenv("CLOUDINARY_API_SECRET"),
                secure=True,
            )

        public_id = f"instagram-automation/{os.path.splitext(os.path.basename(file_path))[0]}"
        result = cloudinary.uploader.upload(
            file_path,
            resource_type="video",
            public_id=public_id,
            overwrite=True,
        )
        url = result.get("secure_url")
        if url:
            print(f"Uploaded to Cloudinary: {url}")
            return url

        print("Cloudinary upload did not return a secure_url")
        return None
    except Exception as exc:
        print(f"Cloudinary upload failed: {exc}")
        return None


def upload_to_github_release(file_path):
    github_token = os.getenv("GITHUB_TOKEN")
    github_repo = os.getenv("GITHUB_REPO")

    if not github_token or not github_repo:
        print("Missing GITHUB_TOKEN or GITHUB_REPO")
        return None

    try:
        today = date.today().isoformat()
        tag = f"video-{today}"
        filename = os.path.basename(file_path)

        headers = {
            "Authorization": f"token {github_token}",
            "Accept": "application/vnd.github.v3+json",
        }

        release_url = f"https://api.github.com/repos/{github_repo}/releases/tags/{tag}"
        response = requests.get(release_url, headers=headers, timeout=30)

        if response.status_code == 404:
            create_url = f"https://api.github.com/repos/{github_repo}/releases"
            release_data = {
                "tag_name": tag,
                "name": f"Daily Quote Video {today}",
                "body": f"Auto-generated video for {today}",
            }
            response = requests.post(create_url, json=release_data, headers=headers, timeout=30)
            response.raise_for_status()
            print(f"Created release: {tag}")
        elif response.status_code == 200:
            print(f"Using existing release: {tag}")
        else:
            print(f"Failed to get/create release: {response.status_code} - {response.text}")
            return None

        release = response.json()
        release_id = release["id"]

        for asset in release.get("assets", []):
            if asset.get("name") == filename:
                delete_url = f"https://api.github.com/repos/{github_repo}/releases/assets/{asset['id']}"
                requests.delete(delete_url, headers=headers, timeout=30)
                print(f"Removed old asset: {filename}")

        upload_url = (
            f"https://uploads.github.com/repos/{github_repo}/releases/{release_id}/assets"
            f"?name={quote(filename)}"
        )
        upload_headers = {
            "Authorization": f"token {github_token}",
            "Accept": "application/vnd.github.v3+json",
            "Content-Type": "video/mp4",
        }

        with open(file_path, "rb") as handle:
            response = requests.post(upload_url, data=handle, headers=upload_headers, timeout=120)

        if response.status_code not in (200, 201):
            print(f"Upload failed: {response.status_code} - {response.text}")
            response.raise_for_status()

        asset = response.json()
        download_url = asset.get("browser_download_url") or asset.get("url")
        print(f"Uploaded to GitHub: {filename}")
        return download_url

    except Exception as exc:
        print(f"GitHub upload failed: {exc}")
        return None


def get_or_upload(file_path):
    public = get_public_url_from_env()
    if public:
        if is_publicly_accessible(public):
            return public
        print("VIDEO_PUBLIC_URL is not publicly accessible")

    cloudinary_url = upload_to_cloudinary(file_path)
    if cloudinary_url:
        if is_publicly_accessible(cloudinary_url):
            return cloudinary_url
        print("Cloudinary URL is not publicly accessible")
        return None

    if get_cloudinary_url_from_env() or os.getenv("CLOUDINARY_CLOUD_NAME"):
        print("Cloudinary is configured but upload failed. Not falling back to GitHub.")
        return None

    try:
        github_url = upload_to_github_release(file_path)
        if github_url:
            if is_publicly_accessible(github_url):
                print(f"GitHub Release URL: {github_url}")
                return github_url
            print("GitHub Release URL is not publicly accessible. If the repo is private, Meta cannot fetch it.")
    except Exception as exc:
        print("Hosting upload failed:", exc)

    return None
