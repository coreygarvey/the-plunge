
import constants as c
import requests
import json


at_token = c.AIRTABLE_ACCESS_TOKEN
at_url_base = c.AIRTABLE_API_URL_BASE
at_base_id = c.AIRTABLE_HIGH_PERFORMANCE_BASE_ID
at_latest_update_table_id = c.AIRTABLE_API_LATEST_UPDATE_TABLE_ID
at_all_content_table_id = c.AIRTABLE_ALL_CONTENT_TABLE_ID
at_keepers_no_flurries_view_id = c.AIRTABLE_KEEPERS_NO_FLURRIES_VIEW_ID

def airtable_articles_to_truman():

    # Instantiate Truman

    # Get Articles
    articles_json = airtable_get_keepers_no_flurries()

    # Run articles through Truman

    '''
	API Docs:
	https://getpocket.com/developer/docs/v3/retrieve
	Update:
		Post dataframe to Airtable
		Update latest update time for table
	'''
	#pocket_latest_update_unix = get_pocket_latest_updated_unix()
	
	#plunge_json = get_latest_plunge_articles(access_token, pocket_latest_update_unix)

	#article_count = plunge_json_to_csv(plunge_json)
	
	#airtable_articles_posted_count = post_articles_to_airtable(article_count)

	#print("Pocket articles successfully posted: {}".format(airtable_articles_posted_count))


    return len(articles_json)

def airtable_get_keepers_no_flurries():
	
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