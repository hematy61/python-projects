import requests
from urllib.parse import urlparse, urljoin, urlunparse
from bs4 import BeautifulSoup


def normalize_url(url):
    """
    Remove URL fragment and query.

    Parameters:
    url (str): The URL to be normalized.

    Returns:
    str: The normalized URL without query and fragment.

    Example:
    >>> normalize_url("https://example.com/path?query=1#fragment")
    'https://example.com/path'
    """
    parsed_url = urlparse(url)
    return urlunparse(parsed_url._replace(query="", fragment=""))


def is_subpath(base_url, url):
    """
    Check if the url is a subpath of the base_url.

    Parameters:
    base_url (str): The base URL to check against.
    url (str): The URL to check.

    Returns:
    bool: True if the URL is a subpath of the base URL, False otherwise.

    Example:
    >>> is_subpath("https://example.com", "https://example.com/path")
    True
    >>> is_subpath("https://example.com", "https://example.com")
    True
    >>> is_subpath("https://example.com", "https://example.com/path?query=1#fragment")
    True
    >>> is_subpath("https://example.com", "https://example.org")
    False
    """
    return url.startswith(base_url)


def get_subpaths(base_url, max_urls=30):
    """
    Get all subpaths of a given base URL up to a maximum number of URLs.

    Parameters:
    base_url (str): The base URL to find subpaths for.
    max_urls (int, optional): The maximum number of URLs to find. Defaults to 30.

    Returns:
    set: A set of all found subpaths.
    """
    visited_urls = set()
    urls_to_visit = {base_url}
    all_urls = set()

    while urls_to_visit and len(all_urls) < max_urls:
        current_url = urls_to_visit.pop()
        normalized_url = normalize_url(current_url)

        # Skip URLs that are not subpaths of the base URL
        if not is_subpath(base_url, normalized_url):
            continue

        # Skip already visited normalized URLs
        if normalized_url in visited_urls:
            continue

        try:
            response = requests.get(current_url, timeout=5)
            soup = BeautifulSoup(response.content, "html.parser")

            for link in soup.find_all("a", href=True):
                href = link["href"]
                full_url = urljoin(current_url, href)
                normalized_full_url = normalize_url(full_url)
                if normalized_full_url not in visited_urls and is_subpath(
                    base_url, normalized_full_url
                ):
                    urls_to_visit.add(full_url)
                    all_urls.add(normalized_full_url)

            visited_urls.add(normalized_url)
        except requests.RequestException as e:
            print(f"Failed to access {current_url}: {e}")
        except Exception as e:
            print(f"An error occurred: {e}")
    return all_urls


# Replace 'https://test.come/doc' with the base URL you're interested in
# Adjust max_urls as needed
base_url = "https://test.com/doc"
max_urls = 500
subpaths = get_subpaths(base_url, max_urls=max_urls)

# Write the results to a file
with open("results.txt", "w") as f:
    for path in subpaths:
        f.write(path + "\n")
