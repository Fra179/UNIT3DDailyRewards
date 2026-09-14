# UNIT3DDailyRewards

A small script that automatically claims the daily reward from
[UNIT3D](https://github.com/HDInnovations/UNIT3D-Community-Edition) based torrent
trackers. Optionally sends a notification for each claim via
[Apprise](https://github.com/caronc/apprise).

## How it works

1. For each tracker you want to claim from, you save a `curl` command in a
   `.txt` file inside a directory of your choice.
2. The script parses each file into a `Website`, then automatically discovers
   every currently running event on that tracker's event list page — no need
   to configure events individually.
3. For each event found, it opens the claim page to grab the CSRF token and
   POSTs the claim.
4. A success/error notification is sent through Apprise (if configured), including
   the prize obtained for each claimed event.

## Installation

Requires Python >= 3.11. Using [uv](https://docs.astral.sh/uv/):

```bash
uv sync
```

Or with pip:

```bash
pip install apprise requests uncurl
```

## Setup

### Curl commands

Create a directory (e.g. `websites/`) and add **one `.txt` file per website** (not
per event — every currently running event on that website is discovered and
claimed automatically). The file name (without `.txt`) is used as the tracker
name in logs and notifications.

The content of each `.txt` file must be the **Copy as cURL** copy of a logged-in
request to that website. Only the domain, cookies and `User-Agent` header are
actually used, so the request can be taken from any page on the site — the
**homepage is preferred** since it's simple and always available.

To get it:

1. Log in to the tracker and open any page (the homepage is preferred).
2. Open your browser's dev tools → Network tab.
3. Reload the page, right-click the document request and choose
   **Copy → Copy as cURL**.
4. Paste it into `websites/<tracker-name>.txt`.

The command must include your session cookies and `User-Agent` header.

### Notifications (optional)

Create an `apprise-config.txt` file in the working directory with one Apprise
URL per line. Lines starting with `#` are ignored. If the file is missing,
notifications are simply skipped.

```
# Example
discord://webhook_id/webhook_token
tgram://bot_token/chat_id
```

## Usage

```bash
uv run python main.py --directory websites
```

Options:

| Flag | Description |
| --- | --- |
| `-d`, `--directory` | Directory containing the curl command `.txt` files (required) |
| `--dry-run` | Print what would be claimed without sending any claim |
| `--log-level` | Logging level: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL` (default: `INFO`) |

### Scheduling

Run it once a day with cron, e.g.:

```cron
0 9 * * * cd /path/to/UNIT3DDailyRewards && uv run python main.py -d websites
```

## Disclaimer

This tool automates a normal user action. Make sure automated claiming does not
violate the rules of the trackers you use it with.
