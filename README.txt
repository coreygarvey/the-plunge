- Issue Creation:
    - Select articles from various sources tagging with Pocket
    - "Process" articles
    - Select articles to add to issue from list of written articles
    - Select food to add to issue from Pantry

- Article "Processing"
    - Pocket to Airtable (Articles)
        - Get Plunge articles from Pocket
        - Prep Plunge articles for Airtable
        - Post Plunge articles to Airtable
        - Cleanup temp data

    - Airtable article creation
        - Get articles that are set to 'Keep' with no Flurry
        - Get article URL
        - For each URL
            - Extract article URL
            - Get HTML Text with Requests
            - Get Article Title
            - Get Article Images
            - Isolate Article Text
            - Capture summaries of article parts if they exist:
                - Overview - this should always exist
                - Methods - details of how research was conducted
                - Results - outcome of research
                - Future - further research and future studies
            - Determine article type (research or summary) base on which summaries are present
            - Determine the prompt based on article type
            - Create summary of entire article based on input of parts and article type using fine-tuned model
                - These summaries should match the "notes" from previous article, so this part goes through fine-tuned model
            - Create article title from fine-tuned model
                - Use same fine-tuned model with input title, notes as input and output title
        - Return:
            - Article, title, provided images, keywords for image search (turn into URL with image search, orientation filter)

- Pocket to Airtable (Food)
    - Get food saved from Pocket
    - Prep Instagram details for Airtable
    - Post Instagram details to Airtable
    - Cleanup temp data
    - Finish with image uploads/downloads
        - Download image
        - Resize
        - Upload to Airtable
        - Upload to S3
        - Add URL from S3 to Airtable


- Fine Tune Model
    - List all articles in proper format. Input article text (notes?), input title, article type, and output text, title
    - Upload to model for responses with tone of The Plunge

Todo:
- Only 'Keep' articles without a Flurry are those I want articles for
- Past articles tagged with type (research or summary)

