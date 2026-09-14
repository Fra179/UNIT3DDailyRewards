import logging
import re
from dataclasses import dataclass
import uncurl
from urllib.parse import urlsplit
from os import listdir, path

@dataclass
class Website:
    base_url: str
    cookies: dict[str, str]
    user_agent: str
    name: str = "Unnamed Website"

    @staticmethod
    def from_curl_command(command: str, name) -> 'Website':
        """
        Create a Website instance from a curl command.

        Args:
            command (str): The curl command as a string.

        Returns:
            Website: An instance of the Website class.
        """

        command = re.sub(r'\\\s*\n', ' ', command)
        curl_parsed = uncurl.parse_context(command)

        parsed_url = urlsplit(curl_parsed.url)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        user_agent = curl_parsed.headers.get('User-Agent', '')

        return Website(name=name, base_url=base_url, cookies=curl_parsed.cookies, user_agent=user_agent)

    def claim_url(self, event_id: int) -> str:
        """
        Construct the claim URL based on the base URL and event ID.

        Returns:
            str: The constructed claim URL.
        """
        return f"{self.base_url}/events/{event_id}/claims"

    def claim_page_url(self, event_id: int) -> str:
        """
        Construct the claim page URL based on the base URL and event ID.

        Returns:
            str: The constructed claim page URL.
        """
        return f"{self.base_url}/events/{event_id}/"

    @property
    def event_list_url(self) -> str:
        """
        Construct the event list URL based on the base URL.

        Returns:
            str: The constructed event list URL.
        """
        return f"{self.base_url}/events/"

    def __str__(self) -> str:
        _return = f"Website: {self.name}\n"
        _return += f"Base URL: {self.base_url}\n"
        _return += f"Event List URL: {self.event_list_url}\n"
        _return += f"Cookies: {self.cookies}\n"
        return _return

class Event:
    def __init__(self, event_id: int, name: str):
        self.event_id = event_id
        self.name = name

    def __str__(self) -> str:
        return f"Event ID: {self.event_id}, Name: {self.name}"

def parse_websites_from_dir(directory: str) -> list[Website]:
    """
    Parse all curl commands from text files in the specified directory and create Website instances.

    Args:
        directory (str): The path to the directory containing text files with curl commands.
    
    Returns:
        list[Website]: A list of Website instances.
    """
    websites = []
    for filename in listdir(directory):
        if filename.endswith('.txt'):
            with open(path.join(directory, filename), 'r') as f:
                curl_command = f.read()
            websites.append(Website.from_curl_command(curl_command, name=filename.replace('.txt', '')))
    return websites

def main():
    websites = parse_websites_from_dir('websites')
    for website in websites:
        print(website)

if __name__ == "__main__":
    main()