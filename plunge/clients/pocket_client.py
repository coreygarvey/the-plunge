from .base_client import BaseClient
import constants as c

class PocketService(BaseClient):
    def __init__(self, base_url):
        super().__init__(base_url, '')
        self.headers = {
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "X-Accept": "application/json"
        }
    
    def get_plunge_articles(self):
        res = self.post(
            "/v3/get",
            data = {
                "consumer_key": c.POCKET_CONSUMER_KEY,
                "access_token": c.POCKET_ACCESS_TOKEN,
                "tag": "plunge",
                "detailType": "complete",
                "since": c.POCKET_LATEST_UPDATED_UNIX,
                "count": 200
            }
        )
        return res.json()