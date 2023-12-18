
parse_html_message = f""" 
Analyze the HTML file provided and extract the title, main image, and article text based on the following logic for each. Return a text file with this information:

Title: This is the title tag within the HTML Header

Main Image: Find the img tag within the body of the HTML that has the largest value for the width attribute. This is the Main Image. Get the src value from this image tag.

Article Text: All text within the HTML body tag that is within a paragraph tag makes up the article text. Get all of this text.

Do not confirm whether the data is accurate. If there is no data, return a blank file.
"""