import csv
import requests


def download_pdf(file_path, url):
    response = requests.get(url)
    with open(file_path, "wb") as file:
        file.write(response.content)


def write_to_csv(file_path, result):
    with open(file_path, "w") as f:
        csvwriter = csv.writer(f, quoting=csv.QUOTE_NONNUMERIC)
        csvwriter.writerow(["source", "target"])
        for source, target in result:
            csvwriter.writerow([source, target])
