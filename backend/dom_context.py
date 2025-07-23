# dom_context.py — Extract DOM snippets + XPaths in real-time

from bs4 import BeautifulSoup
import requests

def get_runtime_dom_data(page_url: str, element_descriptor: str = "") -> str:
    """
    Fetches page HTML and returns XPath and outerHTML of elements matching descriptor.
    If descriptor is empty, returns the full page DOM.
    """
    try:
        resp = requests.get(page_url, timeout=5)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        if element_descriptor:
            elements = soup.find_all(attrs={"id": element_descriptor}) or soup.find_all(class_=element_descriptor)
        else:
            elements = soup.find_all()
        contexts = []
        for el in elements[:5]:  # limit to first 5
            xpath = _get_xpath(el)
            html = str(el)[:500]  # limit length
            contexts.append(f"XPath: {xpath}\nHTML: {html}")
        return "\n\n".join(contexts) or "No matching elements found."
    except Exception as e:
        return f"[Error fetching DOM: {e}]"

def _get_xpath(element) -> str:
    path = []
    el = element
    while el and el.name:
        siblings = el.find_previous_siblings(el.name)
        index = len(siblings) + 1
        path.insert(0, f"/{el.name}[{index}]")
        el = el.parent
    return "".join(path)
