from pocket import pocket_articles

def main():

	# Pocket
	pocket_updates()

	return

def pocket_updates():
	pocket_updates_bool = input("Update Pocket data (y/n)?\n")

	if pocket_updates_bool == 'y':
		pocket_articles_count = pocket_articles()
		print("Latest Pocket articles count: {}\n".format(pocket_articles_count))
	return

if __name__ == "__main__":
	main()
