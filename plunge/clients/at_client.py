from .base_client import BaseClient

import constants as c

class AirTableService(BaseClient):
    def __init__(self, base_url, auth):
        super().__init__(base_url, auth)
    
    
    def get_latest_updates(self):
        res = self.get(
            "/v0/{base_id}/{table_id}".format(
                base_id = c.AIRTABLE_HIGH_PERFORMANCE_BASE_ID,
                table_id = c.AIRTABLE_API_LATEST_UPDATE_TABLE_ID
            )
        )
        return res.json().get("records", [])
    
    def patch_articles(self, articles_json):
        res = self.patch(
            "/v0/{base_id}/{table_id}".format(
                base_id = c.AIRTABLE_HIGH_PERFORMANCE_BASE_ID,
                table_id = c.AIRTABLE_ALL_CONTENT_TABLE_ID
            ),
            json=articles_json
        )
        return res.json().get("records", [])
    
    def patch_latest_updates(self, updates_json):
        res = self.patch(
            "/v0/{base_id}/{table_id}".format(
                base_id = c.AIRTABLE_HIGH_PERFORMANCE_BASE_ID,
                table_id = c.AIRTABLE_API_LATEST_UPDATE_TABLE_ID
            ),
            json=updates_json
        )
        return res.json().get("records", [])
    
    def get_keepers_no_flurries(self, fields):
        res = self.get(
            "/v0/{base_id}/{table_id}?view={view_id}&fields%5B%5D={fields}".format(
                base_id = c.AIRTABLE_HIGH_PERFORMANCE_BASE_ID,
                table_id = c.AIRTABLE_ALL_CONTENT_TABLE_ID,
                view_id = c.AIRTABLE_KEEPERS_NO_FLURRIES_VIEW_ID,
                fields='&fields%5B%5D='.join(fields)
            )
        )
        return res.json().get("records", [])