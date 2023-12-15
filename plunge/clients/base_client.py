from requests import Session

class BaseClient(Session):
    def __init__(self, base_url, auth, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.headers.update(
            {
                "authorization": "Bearer " + auth,
                "accept": "application/json",
                "content-type": "application/json",
            }
        )
        self.verify = False
        self.base_url = base_url
    
    def get(self, url, **kwargs):
        res = super().get(self.base_url + url, **kwargs)
        res.raise_for_status()
        return res
    
    def get_no_base(self, url, **kwargs):
        res = super().get(url, **kwargs)
        res.raise_for_status()
        return res
    
    def post(self, url, **kwargs):
        res = super().post(self.base_url + url, **kwargs)
        res.raise_for_status()
        return res
    
    def put(self, url, **kwargs):
        res = super().put(self.base_url + url, **kwargs)
        res.raise_for_status()
        return res
    
    def patch(self, url, **kwargs):
        res = super().patch(self.base_url + url, **kwargs)
        res.raise_for_status()
        return res