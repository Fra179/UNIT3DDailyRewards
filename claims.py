from website import Website, Event
from urllib.parse import urlsplit
from typing import Optional
import requests
import logging
import re

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
    
    def __dry_claim(self, event: Event) -> None:
        print(f"Dry run: Would claim reward from {self.website.name} at {self.website.claim_url(event.event_id)} for event '{event.name}' (ID: {event.event_id})")

    def __real_claim(self, event: Event) -> Optional[str]:
        """
        Claim the reward from the specified website.

        Raises:
            MissingCSRFTokenError: If the CSRF token is not found in the claim page.
            WrongStatusCodeError: If the response status code is not as expected.
        """

        # get the crsf token from the claim page
        response = self._get(self.website.claim_page_url(event.event_id))
        if response.status_code != 200:
            raise WrongStatusCodeError(response.status_code)

        # extract the csrf token from the meta "crsf-token" tag in the HTML
        reg = re.compile(r'<meta name="csrf-token" content="(.*?)" />')
        match = reg.search(response.text)

        if not match:
            raise MissingCSRFTokenError()

        csrf_token = match.group(1)

        # submit the claim
        response = self._post(self.website.claim_url(event.event_id), _token=csrf_token)

        if response.status_code not in [200, 302]:  # Assuming 200 OK or 302 Found are valid responses
            raise WrongStatusCodeError(response.status_code)

        prize_messaage = r"<i class=\"events__prize-message\">\s*(.*?)\s*</i>"
        response_message_matches = re.findall(prize_messaage, response.text)[::-1]

        if not response_message_matches:
            return None
        
        last_prize = next(filter(lambda x: x.strip() != "Check back later!", response_message_matches), None)
        return last_prize

    def _list_events(self) -> list[Event]:
        """
        List all events available on the website.

        Returns:
            list[Event]: A list of Event instances representing the available events.
        """
        response = self._get(self.website.event_list_url)
        if response.status_code != 200:
            raise WrongStatusCodeError(response.status_code)

        # Event IDs are in the format /events/<event_id>
        event_id_pattern = re.compile(rf'<a href="{self.website.base_url}/events/(\d+)">\s*(.*?)\s*</a>')

        events = []
        for match in event_id_pattern.finditer(response.text):
            event_id = int(match.group(1))
            event_name = match.group(2).strip()
            events.append(Event(event_id=event_id, name=event_name))

        return events


    def claim_rewards(self) -> list[tuple[Event, Optional[str]]]:
        """
        Claim the reward from the website. If dry_run is True, it will only print the action without performing it.

        Returns:
            list[tuple[Event, Optional[str]]]: A list of tuples, each containing an Event instance and the corresponding prize message (or None if no prize message was found or if it was a dry run).
        """

        events = self._list_events()

        results = []

        for event in events:
            if self.dry_run:
                prize_message = self.__dry_claim(event) # type: ignore[func-returns-value] # It's expected behaviour for the dry claim to return None
            else:
                prize_message = self.__real_claim(event)
                
            results.append((event, prize_message))

        return results