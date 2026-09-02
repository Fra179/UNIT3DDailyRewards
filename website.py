import logging
import re
from dataclasses import dataclass
import uncurl
from urllib.parse import urlsplit
from os import listdir, path

@dataclass
class Website:
    base_url: str
    claim_page_url: str
    event_id: int
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

        claim_page_url = curl_parsed.url
        parsed_url = urlsplit(curl_parsed.url)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        event_id = parsed_url.path.split('/')[-1]  # Assuming the event_id is the last part of the path
        user_agent = curl_parsed.headers.get('User-Agent', '')

        return Website(name=name, base_url=base_url, claim_page_url=claim_page_url, event_id=int(event_id), cookies=curl_parsed.cookies, user_agent=user_agent)

    @property
    def claim_url(self) -> str:
        """
        Construct the claim URL based on the base URL and event ID.

        Returns:
            str: The constructed claim URL.
        """
        return f"{self.base_url}/events/{self.event_id}/claims"

    def __str__(self) -> str:
        _return = f"Website: {self.name}\n"
        _return += f"Base URL: {self.base_url}\n"
        _return += f"Claim Page URL: {self.claim_page_url}\n"
        _return += f"Event ID: {self.event_id}\n"
        _return += f"Cookies: {self.cookies}\n"
        _return += f"Claim URL: {self.claim_url}\n"
        return _return


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