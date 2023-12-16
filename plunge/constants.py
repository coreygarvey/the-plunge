# Constants
import os
from dotenv import load_dotenv

load_dotenv()

# Global Constants
YT_REQUEST_MAX_RESULTS = 5 # 0-50 inclusive
YT_VIDEOS_TO_DROP = 0
YT_PAGE_COUNT_MAX = 20  # Use to go beyond the 50 item limit for a single request

POD_REQUEST_MAX_RESULTS = 1000
POD_PAGE_COUNT_MAX = 5
POD_EPISODES_TO_DROP = 0
POD_EPISODES_MAX = 1000

# Pocket
POCKET_URL_BASE = "https://getpocket.com"
POCKET_REDIRECT_URI = "pocketapp106066:authorizationFinished"
POCKET_CONSUMER_KEY = "106066-2d5bf271b68873a5879ddb4"
POCKET_ACCESS_TOKEN = os.getenv('POCKET_ACCESS_TOKEN')
POCKET_LATEST_UPDATED_UNIX = 1702606786

# Airtable
AIRTABLE_ACCESS_TOKEN = os.getenv('AIRTBLE_ACCESS_TOKEN')
AIRTABLE_URL_BASE = "https://api.airtable.com"
AIRTABLE_HIGH_PERFORMANCE_BASE_ID = "appaXjqrpTbMpOdm0"
AIRTABLE_ALL_CONTENT_TABLE_ID = "tbl5yEjuPWGg5jC5J"
AIRTABLE_KEEPERS_NO_FLURRIES_VIEW_ID = "viwZfY7ctFDmmAX0U"





AIRTABLE_API_URL_BASE = "https://api.airtable.com/v0/"

AIRTABLE_CREATORS_TABLE_ID = "tblqd5YlmhoMgzS62"

AIRTABLE_YOUTUBE_TABLE_ID = "tblpPNRJSMfBG0L6b"

AIRTABLE_PODCAST_TABLE_ID = "tbl8hzDlMvykJMgCl"



AIRTABLE_API_LATEST_UPDATE_TABLE_ID = "tblmEKtJU7AHjq4ZI"





# Google
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

# EditorX - Velo
VELO_FUNCTIONS_URL_BASE = "https://cgarv16.editorx.io/mysite/_functions/"

VELO_REDIRECT_URI = "pocketapp106066:authorizationFinished"


# CSV Filenames
TEMP_CSV_CREATORS = "temp_creators.csv"

TEMP_CSV_ALL_CONTENT = "temp_all_content.csv"

TEMP_CSV_YT_VIDEOS = "temp_yt_videos.csv"

TEMP_CSV_PODCAST_EPISODES = "temp_podcast_episodes.csv"

TEMP_CSV_API_UPDATES = "temp_api_updates.csv"

TEMP_CSV_POCKET_ARTICLES = "temp_pocket_articles.csv"



TEMP_CSV_HISTORIC_VIDEOS = "historic_video_records.csv"

TEMP_CSV_LATEST_VIDEOS = "latest_video_records.csv"

TEMP_CSV_LATEST_PODCAST_EPISODES = "latest_podcast_episode_records.csv"


