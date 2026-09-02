import logging
from logging import getLevelNamesMapping
import argparse

import apprise
from claims import RewardsClaimer
from website import parse_websites_from_dir

def parse_arguments():
    levels = getLevelNamesMapping().keys()
    parser = argparse.ArgumentParser(description="Claim rewards from UNIT3D based trackers")
    parser.add_argument("-d", "--directory", type=str, required=True, help="Directory containing curl commands for websites")
    parser.add_argument("--dry-run", action="store_true", help="Perform a dry run without actually claiming rewards")
    parser.add_argument("--log-level", type=str, choices=levels, default="INFO", help="Set the logging level (default: INFO)")
    return parser.parse_args()

def setup_logging(log_level=logging.INFO):
    logging.basicConfig(level=log_level, format='%(asctime)s - %(levelname)s - %(message)s')

def setup_apprise_notifications():
    appr = apprise.Apprise()

    try:
        with open("apprise-config.txt", "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    appr.add(line)
    except FileNotFoundError:
        logging.warning("apprise_config.txt not found. Notifications will not be sent.")

    return appr

def main():
    args = parse_arguments()
    setup_logging(log_level=args.log_level)

    logger = logging.getLogger(__name__)

    websites = parse_websites_from_dir(args.directory)
    appr = setup_apprise_notifications()

    for website in websites:
        title = ""
        description = ""

        try:
            claim = RewardsClaimer(website, dry_run=args.dry_run)
            claim.claim_reward()

            title = f"Reward Claimed from {website.name}"
            description = f"Successfully claimed reward from {website.name}"

        except Exception as e:
            logger.error(f"Error occurred while requesting rewards for {website.name}: {e}")

            title = f"Error Claiming Reward from {website.name}"
            description = f"An error occurred while claiming reward from {website.name}: {e}"
        finally:
            appr.notify(title=title, body=description)

if __name__ == "__main__":
    main()