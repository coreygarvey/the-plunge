# All Airtable API Calls
import requests
import pandas as pd
import constants as c
import time


at_token = c.AIRTABLE_ACCESS_TOKEN
at_url_base = c.AIRTABLE_API_URL_BASE
at_base_id = c.AIRTABLE_HIGH_PERFORMANCE_BASE_ID
at_creators_table_id = c.AIRTABLE_CREATORS_TABLE_ID
at_all_content_table_id = c.AIRTABLE_ALL_CONTENT_TABLE_ID
at_latest_update_table_id = c.AIRTABLE_API_LATEST_UPDATE_TABLE_ID
temp_csv_creators = c.TEMP_CSV_CREATORS
temp_csv_api_updates = c.TEMP_CSV_API_UPDATES


# Function for getting attribute from data
def get_attribute(data, attribute, default_value = None):
	return data.get(attribute) or default_value


# Get Creators records
def airtable_get_pocket_unix():
	at_latest_update_url = at_url_base + at_base_id + "/" + at_latest_update_table_id
	headers = {'Authorization': 'Bearer {}'.format(at_token)}
	try:
		r = requests.get(at_latest_update_url, headers=headers)
	except requests.exceptions.RequestException as e:
		raise SystemExit(e)
	json = r.json()
	# Store creator details in CSV
	api_updates = json['records']
	
	updates_list = []
	
	for update in api_updates:
		row = {}
		row['AirtableId'] = get_attribute(update, 'id')
		row['CreatedTime'] = get_attribute(update, 'createdTime')

		fields = update['fields']
		row['LatestUpdateUnix'] = int(get_attribute(fields, 'LatestUpdateUnix'))
		row['Api'] = get_attribute(fields, 'Api')

		updates_list.append(row)

	updates_df = pd.DataFrame(updates_list)
	#print("updates_df: {}".format(updates_df))
	updates_df.to_csv(temp_csv_api_updates, index=False)
	

	return updates_df


def airtable_post_articles(articles_df):
	update_times_df = airtable_get_pocket_unix()
	airtable_articles_posted = 0
	if(len(articles_df) > 0):
		airtable_articles_posted += airtable_post_article_records(articles_df)
		current_time_unix = int(time.time())

		pocket_row_index = update_times_df.index[
				update_times_df['Api'] == "Pocket"
			].tolist()[0]

		update_times_df.at[pocket_row_index, 'LatestUpdateUnix'] = current_time_unix
		
		# Post API Update time update to airtable
		updates_df = update_times_df.iloc[[pocket_row_index]]
		
		update_fields_list = [
			'LatestUpdateUnix'
		]
		airtable_update_times_response = airtable_update_api_latest(updates_df, update_fields_list)

	update_times_df.to_csv(temp_csv_api_updates, index=False)
	return airtable_articles_posted


def airtable_post_article_records(articles_df):
	# Post Request URL
	at_article_url = at_url_base + at_base_id + "/" + at_all_content_table_id
	headers = {
		"Authorization": "Bearer {}".format(at_token),
		"Content-Type": "application/json"
	}
	# Build empty data object
	articles_data = {}

	article_post_count = 0
	length = len(articles_df.index)
	i = 0
	j = 10
	last = False
	# Loop through groups of 10 articles
	while last == False:
		if(j<=length):
			articles_to_post = articles_df[i:j]
			if(j == length):
				last = True
		else:
			articles_to_post = articles_df[i:]
			last = True
		article_post_count += len(articles_to_post)
		articles_to_post = articles_to_post.fillna('')
		# Build request for 10 videos
		articles_dict_list = articles_to_post.to_dict('records')
		articles_records_list = list(map(build_articles_record_for_request, articles_dict_list))
		articles_data["records"] = articles_records_list
		# Upsert to update where article is present based on pocket_id
		articles_data["performUpsert"] = {}
		articles_data["performUpsert"]["fieldsToMergeOn"] = ["Pocket_Id"]
		articles_data["typecast"] = True
		
		# Make request
		try:
			r = requests.patch(at_article_url, headers=headers, json=articles_data)
			print("Article request response: {}\n".format(r))
			r.raise_for_status()
		except requests.exceptions.RequestException as e:
			print(r)
			print(r.content)
			raise SystemExit(e)
		i += 10
		j += 10

	return article_post_count


def build_articles_record_for_request(article_dict):
	return {"fields": article_dict}


def airtable_update_api_latest(update_df, update_fields_list):
	# Post Request URL
	at_api_latest_update_url = at_url_base + at_base_id + "/" + at_latest_update_table_id
	# Build request
	headers = {
		"Authorization": "Bearer {}".format(at_token),
		"Content-Type": "application/json"
	}
	#print(update_df)
	api_id = update_df['AirtableId'].iloc[0]
	api_update_df = update_df[update_fields_list]
	api_update_dict = api_update_df.to_dict('records')[0]
	# REFACTOR
	api_update_record = build_update_record_for_request(api_update_dict, api_id)
	
	api_data = {}
	api_data["records"] = [api_update_record]
	api_data["typecast"] = True
	
	# Make request
	try:
		r = requests.patch(at_api_latest_update_url, headers=headers, json=api_data)
	except requests.exceptions.RequestException as e:
		raise SystemExit(e)
	# If response is valid, continue
	print("Pocket API Latest request response: {}\n".format(r))
	return "Pocket API Latest updated"


def build_update_record_for_request(api_update_dict, api_id):
	return {
		"id": api_id,
		"fields": api_update_dict
	}