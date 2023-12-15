from pocket import pocket_articles_to_airtable
from truman import airtable_articles_to_truman
from clients.at_client import AirTableService
import constants as c

airtable_url_base = c.AIRTABLE_API_URL_BASE
airtable_token = c.AIRTABLE_ACCESS_TOKEN

def main():

	# Pocket - tagged articles to Airtable
	pocket_to_airtable()

	# AirTable Keepers - articles set to "Keep" with no Flurry
	airtable_to_truman()

	return

def pocket_to_airtable():
	pocket_to_airtable_bool = input("Bring Pocket articles to Airtable (y/n)?\n")

	if pocket_to_airtable_bool == 'y':
		pocket_articles_count = pocket_articles_to_airtable()
		print("Latest Pocket articles count: {}\n".format(pocket_articles_count))
	return


def airtable_to_truman():
	airtable_to_truman_bool = input("Run Airtable Keepers through Truman (y/n)?\n")

	if airtable_to_truman_bool == 'y':
		#truman_articles_count = airtable_articles_to_truman()

		airtable_service = AirTableService("https://api.airtable.com", airtable_token)

		keeper_no_flurry_articles = airtable_service.get_keepers_no_flurries(['Url', 'Title'])
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
