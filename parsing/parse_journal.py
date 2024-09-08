import argparse
import requests
from bs4 import BeautifulSoup
import pandas as pd


def parse_html_to_csv(urls, csv_file):
    data = {"source": [], "target": []}

    for url in urls:
        try:
            response = requests.get(url)
            response.raise_for_status()  # Проверка, что запрос успешен

            # Парсим HTML с помощью BeautifulSoup
            soup = BeautifulSoup(response.content, "html.parser")

            # Извлекаем необходимую информацию
            manskiy_div = soup.find("div", class_="box visible")
            russkiy_div = soup.find(
                "div",
                class_="field field-name-field-body-russian field-type-text-with-summary field-label-hidden",
            )
            print(manskiy_div)
            if not manskiy_div or not russkiy_div:
                print(f"Не удалось найти нужные элементы на странице {url}")
                continue

            # Получаем тексты
            source_text = " ".join(
                [p.get_text(strip=True) for p in manskiy_div.find_all("p")]
            )
            target_text = " ".join(
                [p.get_text(strip=True) for p in russkiy_div.find_all("p")]
            )

            data["source"].append(source_text)
            data["target"].append(target_text)

            print(f"Успешно обработан URL: {url}")
        except Exception as e:
            print(f"Ошибка при обработке URL {url}: {e}")

    # Формируем DataFrame
    df = pd.DataFrame(data)

    # Сохраняем в CSV
    df.to_csv(csv_file, mode="a", index=False, header=False, encoding="utf-8")


def generate_urls(no_first_max: int, no_second_min: int):
    base_url = "https://www.khanty-yasang.ru/luima-seripos/no-{}-{}"
    urls = []

    for issue in range(no_second_min, no_second_min + no_first_max):
        urls.append(base_url.format(issue - no_second_min + 1, issue))

    return urls


def main():
    parser = argparse.ArgumentParser(
        description="Parse HTML from multiple URLs and save specific data to a CSV file."
    )
    parser.add_argument("--csv_file", type=str, help="Output CSV file path")
    parser.add_argument("--no-first-max", type=int)
    parser.add_argument("--no-second-min", type=int)
    args = parser.parse_args()

    # Генерируем URL и вызываем функцию для парсинга и сохранения данных
    urls = generate_urls(args.no_first_max, args.no_second_min)
    parse_html_to_csv(urls, args.csv_file)

    print(f"Данные успешно сохранены в {args.csv_file}")


if __name__ == "__main__":
    main()
