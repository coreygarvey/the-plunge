import sys
import os
import requests
import pandas as pd
import webbrowser
import datetime
import re

from airtable import airtable_get_pocket_unix, airtable_post_articles

import constants as c

# Test Update
temp_csv_pocket_articles = c.TEMP_CSV_POCKET_ARTICLES
temp_csv_api_updates = c.TEMP_CSV_API_UPDATES
pocket_redirect_uri = c.POCKET_REDIRECT_URI
pocket_consumer_key = c.POCKET_CONSUMER_KEY
pocket_access_token = c.POCKET_ACCESS_TOKEN
google_api_key = c.GOOGLE_API_KEY

headers = {
	"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
	"X-Accept": "application/json"
}

def pocket_articles_to_airtable():

	access_token = get_pocket_access_token()
	
	'''
	API Docs:
	https://getpocket.com/developer/docs/v3/retrieve
	Update:
		Post dataframe to Airtable
		Update latest update time for table
	'''
	pocket_latest_update_unix = get_pocket_latest_updated_unix()
	
	plunge_json = get_latest_plunge_articles(access_token, pocket_latest_update_unix)

	article_count = plunge_json_to_csv(plunge_json)
	
	airtable_articles_posted_count = post_articles_to_airtable(article_count)

	print("Pocket articles successfully posted: {}".format(airtable_articles_posted_count))


	return article_count

def get_pocket_access_token():
	access_token_input = input("New access token? (y/n)\n")
	if access_token_input == 'y':

		# 2. Request token
		
		request_token_data = {
			"consumer_key": pocket_consumer_key,
			"redirect_uri": pocket_redirect_uri
		}
		request_token_url = "https://getpocket.com/v3/oauth/request"
		request_token_response = requests.post(request_token_url, headers=headers, data=request_token_data)
		
		request_token = request_token_response.json()["code"]
		# 3. Redirect to Pocket for authorization
		redirect_url = "https://getpocket.com/auth/authorize?request_token=" + request_token + "&redirect_uri=" + pocket_redirect_uri
		webbrowser.open(redirect_url, new=0, autoraise=True)

		# 4. Receive callback from Pocket

		# 5. Access token
		ready_input = input("Proceed? (y/n)")

		access_token_url = "https://getpocket.com/v3/oauth/authorize"
		access_token_data = {
			"consumer_key": pocket_consumer_key,
			"code": request_token
		}
		
		access_token_response = requests.post(access_token_url, headers=headers, data=access_token_data)
		print(access_token_response)
		print(access_token_response.content)
		access_token = access_token_response.json()["access_token"]
	else:
		access_token = pocket_access_token

	return access_token


def get_pocket_latest_updated_unix():
	

	use_latest_input = input("Use latest update time? (y/n)\n")
	
	if use_latest_input == 'y':
		
		# Retrieve latest update time from tblmEKtJU7AHjq4ZI (API = Pocket)
		try:
			latest_updates_df = airtable_get_pocket_unix()
		except:
			print("An error occured in airtable_get_pocket_unix()")
			sys.exit(1)

		# Latest Update
		pocket_latest_update_unix = latest_updates_df[latest_updates_df["Api"]=='Pocket'].iloc[0]["LatestUpdateUnix"]
		pocket_latest_update_unix = int(pocket_latest_update_unix)	
		pocket_since_unix = pocket_latest_update_unix
	else:
		days_ago_input = input("How many days ago?\n")
		
		# Handle invalid input
		try:
			days_ago_int = int(days_ago_input)
		except:
			return "Invalid input"

		pocket_since_date = datetime.date.today() - datetime.timedelta(days=days_ago_int)
		pocket_since_unix = int(pocket_since_date.strftime('%s'))
	
	pocket_since_datetime = datetime.datetime.utcfromtimestamp(pocket_since_unix).strftime("%Y-%m-%d %H:%M:%s")
	
	print("Getting Pocket 'plunge' since: {}".format(pocket_since_datetime))

	proceed_input = input("Proceed? (y/n)\n")
	if proceed_input != 'y':
		remove_tmp_files()
		sys.exit(1)

	return pocket_since_unix


def get_latest_plunge_articles(access_token, pocket_latest_update_unix):

	# Retrieve 'plunge' tag since latest time
	authenticated_request_url = "https://getpocket.com/v3/get"
	authenticated_request_data = {
		"consumer_key": pocket_consumer_key,
		"access_token": access_token,
		"tag": "plunge",
		"detailType": "complete",
		"since": pocket_latest_update_unix,
		"count": 200
	}

	authenticated_response = requests.post(authenticated_request_url, headers=headers, data=authenticated_request_data)

	plunge_json = authenticated_response.json()

	#print(json.dumps(plunge_json, indent=4))

	return plunge_json


def plunge_json_to_csv(plunge_json):
	article_count = 0
	articles_list = []
	# Parse responses based on content type and create Airtable rows
	if len(plunge_json["list"]) > 0:
		for key, article in plunge_json["list"].items():

			row = build_pocket_content(article)

			articles_list.append(row)
			article_count += 1

	# Populate Airtable dataframe
	article_records_df = pd.DataFrame(articles_list)

	# Write articles to csv
	article_records_df.to_csv(temp_csv_pocket_articles, mode='w', index=False, header=True)
	return article_count


def post_articles_to_airtable(article_count):
	airtable_articles_posted_count = 0
	if article_count > 0:
		articles_df = pd.read_csv(temp_csv_pocket_articles)
		articles_df['Pocket_Id'] = articles_df['Pocket_Id'].astype(str)
		#print(articles_df['Pocket_Id'])

		print("Pocket articles being posted to Airtable: \n {} \n".format(articles_df[['Title']].to_string(index=True)))

		continue_input = input("Continue posting to Airtable? (y/n)\n")
		if continue_input == 'y':
			airtable_articles_posted_count = airtable_post_articles(articles_df)
		else:
			airtable_articles_posted_count = 0
		
		# Delete Article CSV
		remove_tmp_files()
		

	return airtable_articles_posted_count


def remove_tmp_files():
	if(os.path.exists(temp_csv_api_updates) and os.path.isfile(temp_csv_api_updates)):
		os.remove(temp_csv_api_updates)
		print("Temp API Updates CSV deleted.\n")
	else:
		print("Temp API Updates CSV file not found.\n")

	if(os.path.exists(temp_csv_pocket_articles) and os.path.isfile(temp_csv_pocket_articles)):
		os.remove(temp_csv_pocket_articles)
		print("Temp Pocket Articles CSV deleted.\n")
	else:
		print("Temp Pocket Articles CSV file not found.\n")
		

def build_pocket_content(article):
	row = {}

	row["Title"] = article["resolved_title"]
	row["Pocket_Url"] = article["resolved_url"]
	row["Pocket_Id"] = str(article["resolved_id"])
	row["Pocket_Excerpt"] = article["excerpt"]
	row["Pocket_GivenTitle"] = article["given_title"]
	row["Pocket_ResolvedTitle"] = article["resolved_title"]
	
	row = get_source(row, article)
	row = get_article(row, article)
	row = get_image(row, article)
	row = get_video(row, article)

	if row["Pocket_SourceName"] == "Instagram":
		row = parse_instagram(row, article)
	#if row["Pocket_SourceName"] == "Twitter":
	#	row = parse_twitter(row, article)
	if row["Pocket_SourceName"] == "YouTube":
		row = parse_youtube(row, article)

	#print(row["pocket_id"])
	#print(type(row["pocket_id"]))
	
	# Future properties
	#	tags

	#print("key: {}".format(key))
	#print(json.dumps(article, indent=4))

	return row


def get_source(row, article):
	domain_name = None
	if "domain_metadata" in article:
		domain_name = article["domain_metadata"]["name"]

	row["Pocket_SourceName"] = domain_name

	return row


def get_article(row, article):
	time_to_read_sec = word_count = listen_duration_estimate_sec = None
	# is_article == 0-false, 1-true
	if article["is_article"] == "1":
		if "time_to_read" in article:
			article["time_to_read"] = int(article["time_to_read"])
			time_to_read_sec = article["time_to_read"] * 60
		if "word_count" in article:
			article["word_count"] = int(article["word_count"])
			word_count = article["word_count"]
		if "listen_duration_estimate" in article:
			article["listen_duration_estimate"] = int(article["listen_duration_estimate"])
			listen_duration_estimate_sec = article["listen_duration_estimate"]
		
	row["Pocket_TimeToRead"] = time_to_read_sec
	row["Pocket_WordCount"] = word_count
	row["Pocket_ListenDurationEstimate"] = listen_duration_estimate_sec

	return row


def get_image(row, article):
	image_src = image_width = image_height = None
	# has_image == 0-no image, 1-has image, 2-is image
	if article["has_image"] in ["1", "2"]:
		image = article["image"]
		image_src = image["src"]
		image["width"] = int(image["width"])
		image["height"] = int(image["height"])

		if image["width"] != 0:
			image_width = image["width"]
		if image["height"] != 0:
			image_height = image["height"]
	elif "top_image_url" in article:
		image_src = article["top_image_url"]
	
	row["Pocket_ImageUrlRaw"] = image_src
	row["Pocket_ImageWidth"] = image_width
	row["Pocket_ImageHeight"] = image_height

	return row


def get_video(row, article):
	video_src = video_width = video_height = video_length_seconds = None
	# has_video == 0-no video, 1-has video, 2-is video
	if article["has_video"] in ["1", "2"]:
		videos = article["videos"]
		video = list(videos.values())[0]
		video_src = video["src"]
		video["width"] = int(video["width"])
		video["height"] = int(video["height"])
		video["length"] = int(video["length"])

		if video["width"] > 0:
			video_width = video["width"]
		if video["height"] > 0:
			video_height = video["height"]
		if video["length"] > 0:
			video_length_seconds = video["length"]
	
	row["Pocket_VideoUrlRaw"] = video_src
	row["Pocket_VideoWidth"] = video_width
	row["Pocket_VideoHeight"] = video_height
	row["Pocket_VideoLength"] = video_length_seconds

	return row


def parse_instagram(row, article):

	# Instagram Post Type
	post_type_regex = ".*instagram\.com\/([a-z]*)"
	post_type = re.search(post_type_regex, article["resolved_url"]).group(1)

	# Post ID
	post_id_regex = ".*{}\/([0-9a-z]*)".format(post_type)
	post_id = re.search(post_id_regex, article["resolved_url"]).group(1)

	# TODO
	#	Get Instagram Name from given_title

	return row


def parse_twitter(row, article):

	# Twitter User
	user_handle_regex = ".*twitter\.com\/([0-9a-z]*)"
	user_handle = re.search(user_handle_regex, article["resolved_url"]).group(1)

	# Post ID
	post_id_regex = ".*status\/([0-9a-z]*)"
	post_id = re.search(post_id_regex, article["resolved_url"]).group(1)


	authors = article["authors"]
	twitter_user = list(authors.values())[0]
	twitter_name = twitter_user["name"]
	twitter_user_url = twitter_user["url"]

	return row

def parse_youtube(row, article):

	video_id_regex = ".*v=([0-9A-Za-z]*)"
	print('article["resolved_url"]: {}'.format(article["resolved_url"]))
	video_id = re.search(video_id_regex, article["resolved_url"]).group(1)
	video_details_url = "https://www.googleapis.com/youtube/v3/videos?part=snippet%2CcontentDetails%2Cstatistics%2Cstatus%2Cid&id={}&key={}".format(video_id, google_api_key)
	r = requests.get(video_details_url)
	video_details_json = r.json()
	#print(json.dumps(video_details_json, indent=4))
	videos = video_details_json['items']
	
	for video in videos:
		
		row['Yt_ItemId'] = video['id']
		snippet = video['snippet']
		row['Title'] = snippet['title']
		row['Yt_Channel'] = snippet['channelTitle']
		row['Yt_ChannelId'] = snippet['channelId']
		row['Yt_Description'] = snippet['description']
		row['Yt_PrivacyStatus'] = video['status']['privacyStatus']
		row['Yt_PublishedAt'] = snippet['publishedAt']
		row['Yt_ThumbnailUrl'] = snippet['thumbnails']['high']['url']
		row['Yt_ThumbnailWidth'] = snippet['thumbnails']['high']['width']
		row['Yt_ThumbnailHeight'] = snippet['thumbnails']['high']['height']
		row['Yt_Title'] = snippet['title']
		row['Yt_VideoId'] = video['id']
		row['Yt_ViewCount'] = video['statistics']['viewCount']
		row['Yt_Duration'] = pd.Timedelta(video['contentDetails']['duration'])

	return row



if __name__ == "__main__":
	pocket_articles_to_airtable()
