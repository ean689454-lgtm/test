import os
import re
import sys

from youtube_transcript_api import YouTubeTranscriptApi


# Get URL from command line
url = sys.argv[1]

match = re.search(r'(?:v=|\/)([0-9A-Za-z_-]{11})', url)

if not match:
    raise ValueError("Invalid YouTube URL")

video_id = match.group(1)


try:
    api = YouTubeTranscriptApi()

    if hasattr(api, "list"):
        transcript_list = api.list(video_id)
    elif hasattr(api, "list_transcripts"):
        transcript_list = api.list_transcripts(video_id)
    else:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)

    transcript = None

    # Manual English
    try:
        transcript = transcript_list.find_manually_created_transcript(
            ["en", "en-US", "en-GB"]
        )
    except Exception:
        pass

    # Auto-generated English
    if not transcript:
        try:
            transcript = transcript_list.find_generated_transcript(
                ["en", "en-US", "en-GB"]
            )
        except Exception:
            pass

    # Any language fallback
    if not transcript:
        for t in transcript_list:
            transcript = t
            break

    if not transcript:
        raise Exception("No transcripts found.")

    fetched_data = transcript.fetch()

    full_text = " ".join([
        item.text if hasattr(item, "text") else item["text"]
        for item in fetched_data
    ])

    print("\n" + "=" * 60)
    print(f"TRANSCRIPT ({transcript.language_code})")
    print(f"VIDEO ID: {video_id}")
    print("=" * 60)
    print(full_text)
    print("=" * 60)

except Exception as e:
    print(f"Error fetching transcript: {e}")
    sys.exit(1)
