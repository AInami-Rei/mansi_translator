import os
import fitz
import re

from parsing.pdf.utils import download_pdf, write_to_csv


BOOK_URL = "https://ouipiir.ru/sites/default/files/pesni_hulimsunt.pdf"
INPUT_FILE_PATH = "/tmp/pesni_hulimsunt.pdf"
OUTPUT_FILE_PATH = "/tmp/pesni_hulimsunt.csv"
START_PAGE = 5
END_PAGE = 46


# частный диапазон юникода из шрифтов, используемых в пдф
# не нашел ничего по ним, поэтому просто сделал маппинг на символы
# из расширенной кириллицы
non_standart_chars_mapping = {
    '\uf521': 'ы̄',  # https://en.wikipedia.org/wiki/Yery_with_macron и тд
    '\uf518': 'О̄',
    '\uf512': 'Ё̄',
    '\uf50f': 'а̄',
    '\uf50e': 'А̄',
    '\uf513': 'ё̄',
    '\uf529': 'я̄',
    '\uf523': 'э̄',
    '\uf522': 'Э̄',
    '\uf528': 'Я̄',
    '\uf52d': 'ю̄',
    '\uf511': 'е̄',
    '\uf519': 'о̄',
}

non_standart_chars = set()


def extract_non_standart_unicode_chars(string):
    pattern = re.compile(r'[\uE000-\uF8FF]')
    matches = pattern.findall(string)
    non_standart_chars.update(set(matches))


def process_string(string):
    string = string.strip()
    for char in non_standart_chars_mapping.keys():
        string = string.replace(char, non_standart_chars_mapping[char])
    return string


def should_skip_string(string):
    if string.strip() == "":
        return True
    if re.match(r'^\d+$', string):
        return True
    return False


def parse_pdf(file_path):
    document = fitz.open(file_path)
    result = []
    start_pattern = r"\d\."
    first_strings = []
    second_strings = []
    last_match = None
    is_parsing_first_strings = True

    def append_result():
        to_append = list(zip(first_strings, second_strings))
        if to_append:
            result.extend(to_append)

    for page_num in range(START_PAGE - 1, END_PAGE):
        page = document.load_page(page_num)
        text = page.get_text()
        match = re.search(start_pattern, text)
        if match:
            # мы в начале стиха
            text = text[match.end():]
            if not last_match or match.group() != last_match.group():
                # мы в начале нового стиха
                is_parsing_first_strings = True
                last_match = match
                append_result()
                first_strings = []
                second_strings = []
            else:
                # мы в начале перевода стиха
                is_parsing_first_strings = False
        # мы продолжаем читать стих
        extract_non_standart_unicode_chars(text)
        strings = text.split("\n")
        strings = [
            process_string(string) for string in strings
            if not should_skip_string(string)
        ]
        if is_parsing_first_strings:
            first_strings.extend(strings)
        else:
            second_strings.extend(strings)

    append_result()

    return result


def main():
    if not os.path.exists(INPUT_FILE_PATH):
        download_pdf(INPUT_FILE_PATH, BOOK_URL)
    result = parse_pdf(INPUT_FILE_PATH)
    write_to_csv(OUTPUT_FILE_PATH, result)
    print(f"Wrote {len(result)} rows to {OUTPUT_FILE_PATH}")
    not_mapped_chars = non_standart_chars - non_standart_chars_mapping.keys()
    if not_mapped_chars:
        print(f"Non standart chars without mapping: {not_mapped_chars}")


if __name__ == "__main__":
    main()
