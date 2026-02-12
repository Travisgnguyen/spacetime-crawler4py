import re
from urllib.parse import urlparse, urljoin, urldefrag
from bs4 import BeautifulSoup

def scraper(url, resp):
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]


def extract_next_links(url, resp):
    # Implementation required.

    links = []

    # Only process successful responses
    if resp.status != 200:
        return links

    if not resp.raw_response or not resp.raw_response.content:
        return links

    try:
        content = resp.raw_response.content
        soup = BeautifulSoup(content, "html.parser")

        for tag in soup.find_all("a", href=True):
            href = tag.get("href")

            # Convert relative URLs to absolute
            absolute = urljoin(resp.url, href)

            # Remove fragments (#section)
            absolute, _ = urldefrag(absolute)

            links.append(absolute)

    except Exception:
        return []

    return links


def is_valid(url):
    try:
        parsed = urlparse(url)

        # Only allow http/https
        if parsed.scheme not in {"http", "https"}:
            return False

        # ----------------------------
        # REQUIRED DOMAIN RESTRICTION
        # ----------------------------
        allowed_domains = (
            ".ics.uci.edu",
            ".cs.uci.edu",
            ".informatics.uci.edu",
            ".stat.uci.edu"
        )

        if not any(parsed.netloc.endswith(domain) for domain in allowed_domains):
            return False

        # ----------------------------
        # TRAP DETECTION
        # ----------------------------

        # Too many query parameters (calendar/search traps)
        if parsed.query.count("=") > 5:
            return False

        # Extremely long URLs
        if len(url) > 200:
            return False

        # Too many path segments
        if len(parsed.path.split("/")) > 10:
            return False

        # ----------------------------
        # FILE EXTENSION FILTER
        # ----------------------------

        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$",
            parsed.path.lower()
        )

    except TypeError:
        return False
