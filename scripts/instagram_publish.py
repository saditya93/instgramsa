import os
import time

import requests

from scripts.host_video import get_or_upload


GRAPH_VERSION = os.getenv("GRAPH_API_VERSION", "v17.0")
CONTAINER_POLL_ATTEMPTS = 12
CONTAINER_POLL_SECONDS = 5


def _print_graph_error(response, context):
    try:
        body = response.json()
    except ValueError:
        body = response.text

    print(f"{context}: HTTP {response.status_code}")
    print("Response:", body)


def _wait_for_container_ready(creation_id, token):
    status_url = f"https://graph.facebook.com/{GRAPH_VERSION}/{creation_id}"
    params = {"fields": "status_code,status", "access_token": token}

    for attempt in range(1, CONTAINER_POLL_ATTEMPTS + 1):
        response = requests.get(status_url, params=params, timeout=30)
        if not response.ok:
            _print_graph_error(response, "Could not check Instagram media status")
            return False

        data = response.json()
        status_code = data.get("status_code")
        status = data.get("status")
        print(f"Instagram media processing: {status_code or status or 'unknown'}")

        if status_code == "FINISHED":
            return True
        if status_code == "ERROR":
            print("Instagram media processing failed:", data)
            return False

        if attempt < CONTAINER_POLL_ATTEMPTS:
            time.sleep(CONTAINER_POLL_SECONDS)

    print("Instagram media was not ready before timeout")
    return False


def publish_video(video_path, caption=""):
    ig_user = os.getenv("IG_USER_ID")
    token = os.getenv("IG_ACCESS_TOKEN")

    if not ig_user or not token:
        print("IG_USER_ID or IG_ACCESS_TOKEN missing in env")
        return False

    # Instagram content publishing uses the Instagram professional account ID,
    # not the Facebook Page ID.
    endpoint_id = ig_user

    video_url = get_or_upload(video_path)
    if not video_url:
        print("Could not get public video URL")
        return False

    print(f"Public video URL: {video_url}")

    base = f"https://graph.facebook.com/{GRAPH_VERSION}/{endpoint_id}"

    params = {
        "media_type": "REELS",
        "video_url": video_url,
        "caption": caption,
        "access_token": token,
    }

    try:
        response = requests.post(f"{base}/media", data=params, timeout=60)
        if not response.ok:
            _print_graph_error(response, "Instagram media container creation failed")
            return False

        creation_id = response.json().get("id")
        if not creation_id:
            print("No creation id in response:", response.text)
            return False

        if not _wait_for_container_ready(creation_id, token):
            return False

        publish_response = requests.post(
            f"https://graph.facebook.com/{GRAPH_VERSION}/{endpoint_id}/media_publish",
            data={"creation_id": creation_id, "access_token": token},
            timeout=60,
        )
        if not publish_response.ok:
            _print_graph_error(publish_response, "Instagram media publish failed")
            return False

        print("Published on Instagram:", publish_response.json())
        return True
    except requests.RequestException as exc:
        print("Instagram publish failed:", exc)
        return False
