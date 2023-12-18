from pocket import pocket_json_to_df
from airtable import post_airtable_articles
from truman import airtable_articles_to_truman
from clients.at_client import AirTableService
from clients.pocket_client import PocketService
from clients.user_agent_client import UserAgentService
import constants as c
import openai_messages as msgs

from bs4 import BeautifulSoup
import openai

import time
import os
import json

airtable_service = AirTableService(c.AIRTABLE_URL_BASE, c.AIRTABLE_ACCESS_TOKEN)
pocket_service = PocketService(c.POCKET_URL_BASE)
openai_service = openai

def main():
	# Pocket - tagged articles to Airtable
	pocket_to_airtable()

	# AirTable Keepers - articles set to "Keep" with no Flurry
	airtable_to_truman()

	return

def pocket_to_airtable():
	pocket_to_airtable_bool = input("Bring Pocket articles to Airtable (y/n)?\n")

	if pocket_to_airtable_bool == 'y':
		#pocket_articles_count = pocket_articles_to_airtable()
		
		latest_updates = airtable_service.get_latest_updates()
		
		latest_pocket_update = [x for x in latest_updates if x["fields"]["Api"] == "Pocket"][0]
		latest_pocket_update_unix = latest_pocket_update["fields"]["LatestUpdateUnix"]
		latest_pocket_update_id = latest_pocket_update["id"]
		#print("latest pocket update id:\n{update_id}".format(update_id=latest_pocket_update_id))
		
		pocket_articles_json = pocket_service.get_plunge_articles(latest_pocket_update_unix)
		
		# Parse articles from JSON into dataframe with needed fields
		pocket_articles_clean = pocket_json_to_df(pocket_articles_json)
		if len(pocket_articles_clean.index) > 0:
			current_time_unix = int(time.time())
			# Update latest update Unix on Airtable to current time
			print("Pocket articles being posted to Airtable: \n {} \n".format(pocket_articles_clean[['Title']].to_string(index=True)))
			continue_input = input("Continue posting to Airtable? (y/n)\n")
			if continue_input == 'y':
				patched_articles_count = post_airtable_articles(airtable_service, pocket_articles_clean)

				# Patch API Updates Latest:
				pocket_latest_update_dict = {
					"id": latest_pocket_update_id,
					"fields": {
						"LatestUpdateUnix": int(time.time())
					}
				}
				pocket_latest_update = {}
				pocket_latest_update["records"] = [pocket_latest_update_dict]
				pocket_latest_update["typecast"] = True
				airtable_service.patch_latest_updates(pocket_latest_update)
			
			
				print(patched_articles_count)
	return


def airtable_to_truman():
	assistant_id = c.OPENAI_ASSISTANT_ID
	airtable_to_truman_bool = input("Run Airtable Keepers through Truman (y/n)?\n")

	if airtable_to_truman_bool == 'y':

		keeper_no_flurry_articles = airtable_service.get_keepers_no_flurries(['Url'])
		print("keeper_no_flurry_articles: {}".format(keeper_no_flurry_articles))
		if not os.path.exists("html/"):
			os.mkdir("html/")
		
		if not os.path.exists("parsed/"):
			os.mkdir("parsed/")

		articles = []
		for article in keeper_no_flurry_articles[:1]:
			print(article)
			article_id = article["id"]
			article_url = article['fields']['Url']
			articles.append((article_id, article_url))
			user_agent_service = UserAgentService()
			article_html = user_agent_service.get(article_url)
			article_soup = BeautifulSoup(article_html.content, "lxml")
			if article_url[-1] == '/':
				article_url = article_url[:-1]
			file_name = article_url.split('/')[-1].replace('.html', '')
			html_file_path = "html/" + file_name + ".html"
			
			with open(html_file_path, "wb") as f:
				f.write(article_soup.encode('utf-8'))
		
			# OpenAI Actions
			# Create OpenAI file
			openai_file = openai_service.files.create(
				file=open(html_file_path, "rb"),
				purpose='assistants'
			)
			print(f"File: {openai_file}")
			
			# Create Thread
			parse_thread = openai_service.beta.threads.create(
				messages=[
					{
					"role": "user",
					"content": msgs.parse_html_message,
					"file_ids": [openai_file.id]
					}
				]
			)
			print(f"Parse Thread ID: {parse_thread.id}")
			# Run Thread
			run = openai_service.beta.threads.runs.create(
				thread_id=parse_thread.id,
				assistant_id=assistant_id,
			)
			print(f"Run ID: {run.id}")
			
			# Query Run to determine when complete
			run = wait_for_run_completion(parse_thread.id, run.id)

			if run.status == 'failed':
				print(run.error)
			
			print_messages_from_thread(parse_thread.id)

			# Store latest message file in external
			parsed_file_path = "parsed/" + file_name + ".txt"
			store_thread_files(parse_thread.id, parsed_file_path)
			

			# Create New Thread
			# Refer to newly created file
			# Using the Article Text, create a summary
			# Get ouptut message and file_id
			# Donwload to summary/ article
			# Create Airtable Flurry
				# Linked to Article
				# Title from parsed file
				# Image URL from parsed file
				# Notes from summary returned by OpenAI
				# Push to Airtable
		'''
		Organize all article URLs into list
		For each URL:
		- Get HTML from Requests
		- Parse with BeautifulSoup
		- Store HTML as File
		- Create File in OpenAI with File
		- Create Assistant thread for file (Assistant already created), passing in OpenAI file
		- Store the Title, Image URL, and Article Text in a file for download
		- Download the file and save in /parsed/ on local machine
		'''


		return keeper_no_flurry_articles

		
		#print("Articles processed by Truman: {}\n".format(truman_articles_count))
		
	return

def wait_for_run_completion(thread_id, run_id):
    while True:
        time.sleep(1)
        run = openai_service.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run_id)
        print(f"Current run status: {run.status}")
        if run.status in ['completed', 'failed', 'requires_action']:
            return run
	
def print_messages_from_thread(thread_id):
    messages = openai_service.beta.threads.messages.list(thread_id=thread_id)
    for msg in messages:
        print(f"{msg.role}: {msg.content[0].text.value}")

def store_thread_files(thread_id, parsed_file_path):
	messages = openai_service.beta.threads.messages.list(thread_id=thread_id)
	messages_json_str = json.dumps(messages.data, default=obj_dict, indent=4)
	messages_json = json.loads(messages_json_str)
	latest_message = messages_json[0]
	try:
		file_id = latest_message["file_ids"][0]
	except:
		return
	output_data = openai_service.files.content(file_id)
	output_data_txt = output_data.read()

	with open(parsed_file_path, "wb") as file:
		file.write(output_data_txt)
	return

def obj_dict(obj):
    return obj.__dict__

if __name__ == "__main__":
	main()
