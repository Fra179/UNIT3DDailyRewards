import logging
import re
from urllib.parse import urlsplit

import requests

from website import Website

class MissingCSRFTokenError(Exception):
    def __init__(self, message="CSRF token not found in the claim page."):
        self.message = message
        super().__init__(self.message)

class WrongStatusCodeError(Exception):
    def __init__(self, status_code, message="Unexpected status code received."):
        self.status_code = status_code
        self.message = f"{message} Status code: {status_code}"
        super().__init__(self.message)


class RewardsClaimer:
    def __init__(self, website: Website, dry_run: bool = False):
        self.website = website
        self.dry_run = dry_run
        self.logger = logging.getLogger(__name__)

        self.session = requests.Session()

        domain = urlsplit(website.base_url).netloc
        for name, value in website.cookies.items():
            self.session.cookies.set(name, value, domain=domain, path="/")

        self.session.headers.update({"User-Agent": website.user_agent})

    def _get(self, url, **query_params):
        """
        Perform a GET request to the specified path on the website.

        Args:
            url: The URL to send the GET request to.
            **query_params: Optional query parameters to include in the request.

        Returns:
            The response from the GET request.
        """
        return self.session.get(url, params=query_params)

    def _post(self, url, **data):
        """
        Perform a POST request to the specified path on the website.

        Args:
            url: The URL to send the POST request to.
            **data: The data to include in the POST request.
        """
        return self.session.post(url, data=data)
    
    def __dry_claim(self):
        print(f"Dry run: Would claim reward from {self.website.name} at {self.website.claim_url}")

    def __real_claim(self):
        """
        Claim the reward from the specified website.

        Raises:
            MissingCSRFTokenError: If the CSRF token is not found in the claim page.
            WrongStatusCodeError: If the response status code is not as expected.
        """

        # get the crsf token from the claim page
        response = self._get(self.website.claim_page_url)
        if response.status_code != 200:
            raise WrongStatusCodeError(response.status_code)

        # extract the csrf token from the meta "crsf-token" tag in the HTML
        reg = re.compile(r'<meta name="csrf-token" content="(.*?)" />')
        match = reg.search(response.text)

        if not match:
            raise MissingCSRFTokenError()

        csrf_token = match.group(1)

        # submit the claim
        response = self._post(self.website.claim_url, _token=csrf_token)

        if response.status_code not in [200, 302]:  # Assuming 200 OK or 302 Found are valid responses
            raise WrongStatusCodeError(response.status_code)

    def claim_reward(self):
        """
        Claim the reward from the website. If dry_run is True, it will only print the action without performing it.
        """
        if self.dry_run:
            self.__dry_claim()
        else:
            self.__real_claim()