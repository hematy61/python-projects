import asyncio
from pyppeteer import launch
from PyPDF2 import PdfMerger


async def remove_elements(page, selectors):
    """
    Remove specified elements from the page.

    Parameters:
    page (pyppeteer.page.Page): The page to remove elements from.
    selectors (list): A list of CSS selectors for the elements to remove.
    """
    for selector in selectors:
        await page.evaluate(f"""document.querySelector('{selector}')?.remove();""")


async def export_to_pdf(url, output_path):
    """
    Export a webpage to a PDF file.

    Parameters:
    url (str): The URL of the webpage to export.
    output_path (str): The path where the PDF file will be saved.
    """
    selectors_to_remove = ['nav', 'header', 'div.hero.hero--home.grad', 'div.docs-nav-bar', 'main div.article-banner',
                           'main div.article-header', 'aside.toc', 'aside.toc', 'footer', 'div.lower-footer']  # Example selectors
    browser = await launch()
    page = await browser.newPage()

    # Set the viewport to a standard desktop size
    await page.setViewport({"width": 2400, "height": 1024})
    await page.goto(url, {'waitUntil': 'networkidle0'})

    # Remove specified elements
    await remove_elements(page, selectors_to_remove)

    # await page.emulateMedia('print')  # Ensure print styles are applied
    await page.pdf({
        'path': output_path,
        'width': '1600px',
        'height': '1024px',
        'printBackground': True  # Ensure backgrounds are included
        # You can remove 'format': 'A4' if using custom dimensions
    })
    await browser.close()


async def export_urls_to_pdfs(urls):
    """
    Export multiple webpages to PDF files.

    Parameters:
    urls (list): A list of URLs of the webpages to export.
    """
    for index, url in enumerate(urls):
        print(f"Exporting {url} to PDF...")
        await export_to_pdf(url, f"output_{index}.pdf")
    print("Export completed.")


def read_urls_from_file(file_path):
    """
    Read URLs from a file.

    Parameters:
    file_path (str): The path of the file to read URLs from.

    Returns:
    list: A list of URLs.
    """
    with open(file_path, 'r') as file:
        return [line.strip() for line in file.readlines()]


def merge_pdfs(paths, output_path):
    """
    Merge multiple PDF files into one.

    Parameters:
    paths (list): A list of paths of the PDF files to merge.
    output_path (str): The path where the merged PDF file will be saved.
    """
    merger = PdfMerger()
    for path in paths:
        merger.append(path)
    merger.write(output_path)
    merger.close()


# Main script execution
file_path = 'results.txt'
urls = read_urls_from_file(file_path)

# Asynchronous event loop for Pyppeteer tasks
asyncio.get_event_loop().run_until_complete(export_urls_to_pdfs(urls))

# Merge PDFs after all URLs have been exported
# Adjust based on the number of URLs
pdf_files = [f"output_{i}.pdf" for i in range(len(urls))]
merge_pdfs(pdf_files, "merged_output.pdf")
