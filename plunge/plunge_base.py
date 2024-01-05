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

import sys
import time
import os
import json
import shutil

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
		# Get all issues being built
		issues_building = airtable_service.get_issues_building(['PublishDateString'])

		# Get all Flurries where Issue has status == Building
		building_flurries = airtable_service.get_flurries_building()
		building_flurries_formatted_str = json.dumps(building_flurries, indent=4)
		if not os.path.exists("scrap/"):
			os.mkdir("scrap/")
		building_flurries_file_path = "scrap/building_flurries.json"
		with open(building_flurries_file_path, "w") as f:
			f.write(building_flurries_formatted_str)
		
		# Directory for storing text files
		if not os.path.exists("text_files/"):
			os.mkdir("text_files/")
		# Directory for storing AI generated summaries
		if not os.path.exists("summaries/"):
				os.mkdir("summaries/")

		# Updated Flurry records to be patched to AT
		flurries_with_notes = []

		# For each Flurry: 
		for flurry in building_flurries:
			# Store text as files locally
			flurry_id = flurry["id"]
			flurry_fields = flurry["fields"]
			flurry_text_file_paths = []
			if "ArticleText" in flurry_fields:
				article_text_file_path = "text_files/" + flurry_id + "-a.html"
				article_text = flurry_fields["ArticleText"]
				with open(article_text_file_path, "wb") as f:
					f.write(article_text.encode('utf-8'))
				flurry_text_file_paths.append(article_text_file_path)
			if "JournalText" in flurry_fields:
				journal_text_file_path = "text_files/" + flurry_id + "-j.html"
				journal_text = flurry_fields["JournalText"]
				with open(journal_text_file_path, "wb") as f:
					f.write(journal_text.encode('utf-8'))
				flurry_text_file_paths.append(journal_text_file_path)
			
			# OpenAI Actions
			# Create OpenAI file(s)
			open_ai_file_ids = []
			for path in flurry_text_file_paths:
				openai_file = openai_service.files.create(
					file=open(path, "rb"),
					purpose='assistants'
				)
				print(f"File: {openai_file}")
				open_ai_file_ids.append(openai_file.id)

			# Create Thread
			thread = openai_service.beta.threads.create(
				messages=[
					{
					"role": "user",
					"content": msgs.create_article_message_basic,
					"file_ids": open_ai_file_ids
					}
				]
			)
			print(f"Parse Thread ID: {thread.id}")
			
			# Run Thread
			run = openai_service.beta.threads.runs.create(
				thread_id=thread.id,
				assistant_id=assistant_id,
			)
			print(f"Run ID: {run.id}")
			
			# Query Run to determine when complete
			run = wait_for_run_completion(thread.id, run.id)

			if run.status == 'failed':
				print(run.error)
			
			print_messages_from_thread(thread.id)

			# Store latest message file in external
			summaries_file_path = "summaries/" + flurry_id + ".txt"
			store_thread_files(thread.id, summaries_file_path)

			with open(summaries_file_path) as f:
				flurry_summary = f.read()
				print(f"flurry summary:{flurry_summary}")

			flurry_with_notes_dict = {
				"id": flurry_id,
				"fields": {
					"Notes": flurry_summary
				}
			}
			flurries_with_notes.append(flurry_with_notes_dict)

		# Update Flurries through call to AT Service
		flurry_update = {}
		flurry_update["records"] = flurries_with_notes
		flurry_update["typecast"] = True
		print(f"flurry_update \n {flurry_update}")
		airtable_service.patch_flurries(flurry_update)
			
		
		
		# Create thread with assistant that includes text files
		# Run thread
		# Wait for thread completion
		# Store returned file locally
		# Update Flurry notes with text from retrieved file
		issue_choice_bool = input("Choose an issue (y/n)?\n")
		if issue_choice_bool == 'y':	
			keeper_no_flurry_articles = airtable_service.get_keepers_no_flurries(['Url'])
			'''
			print("keeper_no_flurry_articles: {}".format(keeper_no_flurry_articles))
			if not os.path.exists("html/"):
				os.mkdir("html/")
			
			if not os.path.exists("parsed/"):
				os.mkdir("parsed/")
			
			if not os.path.exists("summaries/"):
				os.mkdir("summaries/")

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
				thread = openai_service.beta.threads.create(
					messages=[
						{
						"role": "user",
						"content": msgs.parse_html_message,
						"file_ids": [openai_file.id]
						}
					]
				)
				print(f"Parse Thread ID: {thread.id}")
				# Run Thread
				run = openai_service.beta.threads.runs.create(
					thread_id=thread.id,
					assistant_id=assistant_id,
				)
				print(f"Run ID: {run.id}")
				
				# Query Run to determine when complete
				run = wait_for_run_completion(thread.id, run.id)

				if run.status == 'failed':
					print(run.error)
				
				print_messages_from_thread(thread.id)

				# Store latest message file in external
				parsed_file_path = "parsed/" + file_name + ".txt"
				store_thread_files(thread.id, parsed_file_path)
				
				article_message = openai_service.beta.threads.messages.create(
					thread_id=thread.id,
					role="user",
					content=msgs.create_article_message_basic
				)

				run = openai_service.beta.threads.runs.create(
					thread_id=thread.id,
					assistant_id=assistant_id,
				)

				print(f"Run ID: {run.id}")
				
				# Query Run to determine when complete
				run = wait_for_run_completion(thread.id, run.id)

				if run.status == 'failed':
					print(run.error)
				
				print_messages_from_thread(thread.id)

				# Store latest message file in external
				parsed_file_path = "summaries/" + file_name + ".txt"
				store_thread_files(thread.id, parsed_file_path)


			return keeper_no_flurry_articles
			'''
			return

		
		#print("Articles processed by Truman: {}\n".format(truman_articles_count))
	#remove_dir("scrap/")
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

def remove_dir(directory):
	try:
		shutil.rmtree(directory)
	except OSError as e:
		print("Error: %s - %s." % (e.filename, e.strerror))

if __name__ == "__main__":
	main()
