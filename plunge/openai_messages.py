
parse_html_message = f""" 
Analyze the HTML file provided and extract the title, main image, and article text based on the following logic for each. Return a text file with this information:

Title: This is the title tag within the HTML Header

Main Image: Find the img tag within the body of the HTML that has the largest value for the width attribute. This is the Main Image. Get the src value from this image tag.

Article Text: All text within the HTML body tag that is within a paragraph tag makes up the article text. Get all of this text.


Do not confirm whether the data is accurate. If there is no data, return a blank file.
"""

create_article_message_basic = f"""
You are an assistant helping me create a newsletter. Using the article text in the file(s) provided, write a summary of the article that is 150 words or less.
Return the summary in a text file.
"""

create_article_message = f"""
You are an assistant helping me create a newsletter.
Using the Article Text you found, write a summary that is 150 words or less, written in a tone suitable for a men's health magazine and highlighting the impact of this information on healthspan. Healthspan is the the optimization of a person's life for both longevity and happiness.

Store the summary into a file and return the summary.

Do not confirm whether the summary is accurate. If you cannot create a summary, return a blank file.
"""