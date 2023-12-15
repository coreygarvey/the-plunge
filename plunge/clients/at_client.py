from .base_client import BaseClient


class AirTableService(BaseClient):
    def __init__(self, base_url, auth):
        super().__init__(base_url, auth)
    
    def get_keepers_no_flurries(self, fields):
        res = self.get(
            "/v0/appaXjqrpTbMpOdm0/tbl5yEjuPWGg5jC5J?view=viwZfY7ctFDmmAX0U&fields%5B%5D={fields}".format(fields='&fields%5B%5D='.join(fields))
        )
        return res.json().get("records", [])