import requests
from bs4 import BeautifulSoup
import argparse
import csv


def parse_elements(elements):
    parsed_data = []
    for element in elements:
        texts = element.find_all("td")

        for td in texts:
            for a in td.find_all("span"):
                a.decompose()

        target = texts[1].text.strip()
        source = texts[0].text.strip()
        parsed_data.append({"target": target, "source": source})
    return parsed_data


def parse_page(url: str):
    response = requests.get(url)
    html = response.text

    soup = BeautifulSoup(html, "html.parser")

    odd_elements = soup.find_all("tr", class_="odd")
    even_elements = soup.find_all("tr", class_="even")

    odd_data = parse_elements(odd_elements)
    even_data = parse_elements(even_elements)

    return odd_data, even_data


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-file", type=str, default="bible_mansi.csv")
    parser.add_argument(
        "--url-template",
        type=str,
        default="http://finugorbib.com/bible/mansi/41_Mar{idx}_ru.html",
    )
    args = parser.parse_args()

    data = []
    for idx in range(1, 17):
        if idx < 10:
            idx = f"0{idx}"
        url = args.url_template.format(idx=idx)
        print(f"Parsing {url}")
        odd_data, even_data = parse_page(url)
        data += odd_data + even_data

    with open(args.output_file, "w") as f:
        csvwriter = csv.writer(f)
        csvwriter.writerow(["source", "target"])
        for row in data:
            csvwriter.writerow([row["source"], row["target"]])


if __name__ == "__main__":
    main()
