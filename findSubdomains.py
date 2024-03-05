import requests
from urllib.parse import urlparse, urljoin, urlunparse
from bs4 import BeautifulSoup

def normalize_url(url):
    """Remove URL fragment and query."""
    parsed_url = urlparse(url)
    # Construct a normalized URL without query and fragment
    return urlunparse(parsed_url._replace(query="", fragment=""))

def is_subpath(base_url, url):
    """Check if the url is a subpath of the base_url."""
    return url.startswith(base_url)

def get_subpaths(base_url, max_urls=30):
    visited_urls = set()
    urls_to_visit = {base_url}
    all_urls = set()

    while urls_to_visit and len(all_urls) < max_urls:
        current_url = urls_to_visit.pop()
        normalized_url = normalize_url(current_url)
        if not is_subpath(base_url, normalized_url):
            continue  # Skip URLs that are not subpaths of the base URL

        if normalized_url in visited_urls:
            continue  # Skip already visited normalized URLs

        try:
            response = requests.get(current_url, timeout=5)  # Added timeout
            soup = BeautifulSoup(response.content, "html.parser")

            for link in soup.find_all("a", href=True):
                href = link['href']
                full_url = urljoin(current_url, href)
                normalized_full_url = normalize_url(full_url)
                if normalized_full_url not in visited_urls and is_subpath(base_url, normalized_full_url):
                    urls_to_visit.add(full_url)
                    all_urls.add(normalized_full_url)
            
            visited_urls.add(normalized_url)
        except requests.RequestException as e:
            print(f"Failed to access {current_url}: {e}")
        except Exception as e:
            print(f"An error occurred: {e}")

    return all_urls

# Replace 'http://www.test.com/doc' with the base URL you're interested in
# Adjust max_urls as needed
base_url = "https://test.come/doc"

max_urls = 500  # Example: set a maximum of 50 URLs to find
subpaths = get_subpaths(base_url, max_urls=max_urls)


with open("results.txt", "w") as f:
    f.write("")

for path in subpaths:
    # write the results in the results.txt file, if the file doesn't exist, it will be created,
    with open("results.txt", "a") as f:
        f.write(path + "\n")

