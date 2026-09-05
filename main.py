import os
import re
import sys
import requests

from youtube_transcript_api import YouTubeTranscriptApi


# Get YouTube URL from GitHub Actions
url = sys.argv[1]

# Get n8n webhook URL from GitHub Actions secret
n8n_webhook = sys.argv[2]


# Extract Video ID
match = re.search(r'(?:v=|\/)([0-9A-Za-z_-]{11})', url)

if not match:
    raise ValueError("Invalid YouTube URL")

video_id = match.group(1)


try:
    api = YouTubeTranscriptApi()

    # Get transcript list
    if hasattr(api, "list"):
        transcript_list = api.list(video_id)

    elif hasattr(api, "list_transcripts"):
        transcript_list = api.list_transcripts(video_id)

    else:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)


    transcript = None


    # Try manually created English transcript
    try:
        transcript = transcript_list.find_manually_created_transcript(
            ["en", "en-US", "en-GB"]
        )
    except Exception:
        pass


    # Try automatically generated English transcript
    if not transcript:
        try:
            transcript = transcript_list.find_generated_transcript(
                ["en", "en-US", "en-GB"]
            )
        except Exception:
            pass


    # Fallback: use any available language
    if not transcript:
        for t in transcript_list:
            transcript = t
            break


    if not transcript:
        raise Exception("No transcripts found for this video.")


    # Fetch transcript
    fetched_data = transcript.fetch()


    # Convert to plain text
    full_text = " ".join([
        item.text if hasattr(item, "text") else item["text"]
        for item in fetched_data
    ])


    print(f"Transcript found: {video_id}")
    print(f"Language: {transcript.language_code}")


    # Data to send to n8n
    data = {
        "success": True,
        "video_id": video_id,
        "youtube_url": url,
        "language": transcript.language_code,
        "transcript": full_text
    }


    # Send transcript to n8n
    response = requests.post(
        n8n_webhook,
        json=data,
        timeout=120
    )

    response.raise_for_status()

    print("Successfully sent transcript to n8n!")


except Exception as e:

    print(f"Error: {e}")


    # Send error to n8n
    try:

        error_data = {
            "success": False,
            "youtube_url": url,
            "error": str(e)
        }

        requests.post(
            n8n_webhook,
            json=error_data,
            timeout=60
        )

    except Exception:
        pass


    sys.exit(1)
