import subprocess
import sys
import os
import glob

url = sys.argv[1]

os.makedirs("subs", exist_ok=True)

try:
    command = [
        "yt-dlp",
        "--skip-download",

        # Download manual subtitles if available
        "--write-subs",

        # Also download auto-generated subtitles
        "--write-auto-subs",

        # Prefer English
        "--sub-langs", "en.*,en",

        # VTT subtitle format
        "--sub-format", "vtt",

        # Output location
        "-o", "subs/%(id)s.%(ext)s",

        url
    ]

    result = subprocess.run(
        command,
        capture_output=True,
        text=True
    )

    print(result.stdout)
    print(result.stderr)

    if result.returncode != 0:
        raise Exception("yt-dlp failed")

    files = glob.glob("subs/*.vtt")

    print("\nDownloaded subtitle files:")
    print(files)

    if not files:
        raise Exception("No subtitles found")

    with open(files[0], "r", encoding="utf-8") as f:
        print("\n===== SUBTITLE CONTENT =====\n")
        print(f.read())

except Exception as e:
    print("ERROR:", str(e))
    sys.exit(1)
