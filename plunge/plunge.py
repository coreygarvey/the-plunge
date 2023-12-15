from pocket import pocket_articles_to_airtable
from truman import airtable_articles_to_truman

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
		truman_articles_count = airtable_articles_to_truman()
		#truman_articles_count = 1
		print("Articles processed by Truman: {}\n".format(truman_articles_count))
	return


if __name__ == "__main__":
	main()
