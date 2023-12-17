from pocket import pocket_json_to_df
from airtable import post_airtable_articles
from truman import airtable_articles_to_truman
from clients.at_client import AirTableService
from clients.pocket_client import PocketService
import constants as c

import time


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
		airtable_service = AirTableService(c.AIRTABLE_URL_BASE, c.AIRTABLE_ACCESS_TOKEN)
		latest_updates = airtable_service.get_latest_updates()
		
		latest_pocket_update = [x for x in latest_updates if x["fields"]["Api"] == "Pocket"][0]
		latest_pocket_update_unix = latest_pocket_update["fields"]["LatestUpdateUnix"]
		latest_pocket_update_id = latest_pocket_update["id"]
		#print("latest pocket update id:\n{update_id}".format(update_id=latest_pocket_update_id))
		
		

		pocket_service = PocketService(c.POCKET_URL_BASE)
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
		#print("Latest Pocket articles count: {}\n".format(pocket_articles_count))
	return


def airtable_to_truman():
	airtable_to_truman_bool = input("Run Airtable Keepers through Truman (y/n)?\n")

	if airtable_to_truman_bool == 'y':
		#truman_articles_count = airtable_articles_to_truman()

		airtable_service = AirTableService(c.AIRTABLE_URL_BASE, c.AIRTABLE_ACCESS_TOKEN)

		keeper_no_flurry_articles = airtable_service.get_keepers_no_flurries(['Url'])
		print(keeper_no_flurry_articles)

		return keeper_no_flurry_articles

		'''
		at_keepers_no_flurries_url = at_url_base + at_base_id + "/" + at_all_content_table_id + "?view=" + at_keepers_no_flurries_view_id
		headers = {'Authorization': 'Bearer {}'.format(at_token)}
		try:
			r = requests.get(at_keepers_no_flurries_url, headers=headers)
		except requests.exceptions.RequestException as e:
			raise SystemExit(e)
		json_response = r.json()
		articles = json_response["records"]
		for article in articles:
			print(article["fields"]["Url"])
		#print(json.dumps(json_response, indent = 4))
		return json_response
		'''

		#truman_articles_count = 1
		print("Articles processed by Truman: {}\n".format(truman_articles_count))
	return


if __name__ == "__main__":
	main()
