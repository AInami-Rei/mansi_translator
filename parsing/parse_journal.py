import argparse
import requests
from bs4 import BeautifulSoup
import pandas as pd
from pdf.scripts.book_1 import process_string, should_skip_string


def parse_html_to_csv(urls: list[str], csv_file: str):
    data = {"source": [], "target": []}

    for url in urls:
        try:
            response = requests.get(url)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, "html.parser")

            manskiy_div = soup.find("div", class_="box visible")
            russkiy_div = soup.find(
                "div",
                class_="field field-name-field-body-russian field-type-text-with-summary field-label-hidden",
            )
            if not manskiy_div or not russkiy_div:
                print(f"Не удалось найти нужные элементы на странице {url}")
                continue

            source_text = " ".join(
                [p.get_text(strip=True) for p in manskiy_div.find_all("p")]
            )
            target_text = " ".join(
                [p.get_text(strip=True) for p in russkiy_div.find_all("p")]
            )

            if not should_skip_string(source_text) and not should_skip_string(
                target_text
            ):
                data["source"].append(process_string(source_text))
                data["target"].append(process_string(target_text))

            print(f"Успешно обработан URL: {url}")
        except Exception as e:
            print(f"Ошибка при обработке URL {url}: {e}")

    df = pd.DataFrame(data)

    df.to_csv(csv_file, mode="a", index=False, header=False, encoding="utf-8")


def generate_urls(no_journal: list[int], count: int = 24):
    base_url = "https://www.khanty-yasang.ru/luima-seripos/no-{}-{}"
    urls = []

    for no_j in no_journal:
        for issue in range(no_j, no_j + count):
            urls.append(base_url.format(issue - no_j + 1, issue))

    return urls


def main():
    parser = argparse.ArgumentParser(
        description="Parse HTML from multiple URLs and save specific data to a CSV file."
    )
    parser.add_argument("--csv_file", type=str, help="Output CSV file path")
    args = parser.parse_args()
    no_journal = [
        1011,
        1043,
        1067,
        1091,
        1115,
        1139,
        1163,
        1187,
        1211,
        1235,
        1259,
        1283,
        1307,
    ]

    urls = generate_urls(no_journal)
    parse_html_to_csv(urls, args.csv_file)

    print(f"Данные успешно сохранены в {args.csv_file}")


if __name__ == "__main__":
    main()
