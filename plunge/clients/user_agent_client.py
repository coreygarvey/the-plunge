from .base_client import BaseClient

import constants as c

USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:65.0) Gecko/20100101 Firefox/65.0"

class UserAgentService(BaseClient):
    def __init__(self):
        super().__init__('', '')
        self.headers = {"user-agent": USER_AGENT}
