# dom_context.py

import difflib
from bs4 import BeautifulSoup
from lxml import etree
import os
import requests

def get_all_elements_with_xpath(html: str):
    soup = BeautifulSoup(html, "html.parser")
    dom = etree.HTML(str(soup))
    all_elements = dom.xpath("//*")
    results = []

    for el in all_elements:
        try:
            path = dom.getpath(el)
            text = el.text.strip() if el.text else ''
            tag = el.tag
            attrs = " ".join([f'{k}="{v}"' for k, v in el.attrib.items()])
            descriptor = f"{tag} {attrs} {text}".strip()
            results.append((descriptor, path))
        except Exception:
            continue
    return results

# dom_context.py

def get_runtime_dom_data(page_url: str, element_descriptor: str = "") -> dict:
    try:
        resp = requests.get(page_url, timeout=5)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        if not element_descriptor:
            return {"matches": [], "message": "No element descriptor provided."}

        elements = soup.find_all()
        matches = []

        for el in elements:
            desc = f"{el.name} {el.get('id', '')} {el.get('class', '')} {el.text.strip()[:30]}".strip()
            sim = difflib.SequenceMatcher(None, element_descriptor.lower(), desc.lower()).ratio()
            if sim > 0.2:
                matches.append((sim, _get_xpath(el), desc))

        matches.sort(reverse=True, key=lambda x: x[0])
        top3 = matches[:3]

        return {
            "matches": [
                {
                    "xpath": m[1],
                    "confidence": round(m[0] * 100, 2),
                    "descriptor": m[2]
                } for m in top3
            ]
        }
    except Exception as e:
        return {"matches": [], "message": f"[Error fetching DOM: {e}]"}

def _get_xpath(el) -> str:
    path = []
    while el and el.name:
        siblings = el.find_previous_siblings(el.name)
        index = len(siblings) + 1
        path.insert(0, f"{el.name}[{index}]")
        el = el.parent
    return "/" + "/".join(path)
