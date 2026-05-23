import os
import requests

from scripts.host_video import get_or_upload


GRAPH_VERSION = os.getenv("GRAPH_API_VERSION", "v17.0")


def publish_video(video_path, caption=""):
    ig_user = os.getenv("IG_USER_ID")
    token = os.getenv("IG_ACCESS_TOKEN")

    if not ig_user or not token:
        print("❌ IG_USER_ID or IG_ACCESS_TOKEN missing in env")
        return False

    # Ensure video is reachable
    video_url = get_or_upload(video_path)
    if not video_url:
        print("❌ Could not get public video URL")
        return False

    print(f"🔗 Public video URL: {video_url}")

    base = f"https://graph.facebook.com/{GRAPH_VERSION}/{ig_user}"

    # 1) Create media object
    params = {
        "video_url": video_url,
        "caption": caption,
        "access_token": token,
    }

    try:
        r = requests.post(f"{base}/media", data=params)
        r.raise_for_status()
        creation_id = r.json().get("id")
        if not creation_id:
            print("❌ No creation id in response:", r.text)
            return False

        # 2) Publish
        pub = requests.post(f"https://graph.facebook.com/{GRAPH_VERSION}/{ig_user}/media_publish",
                            data={"creation_id": creation_id, "access_token": token})
        pub.raise_for_status()
        print("✅ Published on Instagram:", pub.json())
        return True
    except Exception as e:
        print("❌ Instagram publish failed:", e)
        try:
            print(r.text)
        except Exception:
            pass
        return False
