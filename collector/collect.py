import csv
import os
import pathlib
from urllib.parse import urljoin

import fire
import requests
from bs4 import BeautifulSoup
from frictionless import Package


class Collect:
    @staticmethod
    def run():
        base_dir = pathlib.Path(__file__).absolute().parent.parent
        data_file = os.path.join(base_dir, "data", "datapackage.json")
        package = Package(data_file)
        resource = package.get_resource("content-pages")
        for row in resource.read_rows():
            try:
                resp = requests.get(row["url"])
                resp.raise_for_status()
                soup = BeautifulSoup(resp.text, "html.parser")

                # fixup relative css hrefs to be absolute
                for link in soup.find_all("link", attrs={"rel": "stylesheet"}):
                    href = urljoin(row["url"], link["href"])
                    link["href"] = href

                # remove js and forms
                for remove in ["script", "form"]:
                    for item in soup.find_all(remove):
                        item.decompose()

                # remove meta tags apart from encoding
                for m in soup.find_all("meta"):
                    if (
                        m.get("charset") is None
                        and m.get("content") != "text/html; charset=utf-8"
                    ):
                        m.decompose()

                # gov.uk page that was tested had a specific aria attr
                # with dynamic id attached which changes and can be ignored for diffs
                labelled_ids = []
                for tag in soup():
                    if tag.attrs.get("aria-labelledby"):
                        labelled_ids.append(tag.attrs.get("aria-labelledby"))
                        del tag.attrs["aria-labelledby"]
                for id in labelled_ids:
                    for element in soup.find_all(id=id):
                        del element["id"]

                for tag in soup.find_all(class_="attachment embedded"):
                    del tag["id"]

                html = soup.prettify()
                out = os.path.join(base_dir, "collected", f"{row['id']}.html")
                with open(out, "w") as html_file:
                    html_file.write(html)
            except requests.HTTPError as e:
                print(f"Error getting {row['url']}")
                print(e)


if __name__ == "__main__":
    fire.Fire(Collect)
