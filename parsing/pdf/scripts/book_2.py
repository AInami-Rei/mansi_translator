import os
import fitz
import re

from parsing.pdf.utils import download_pdf, write_to_csv


BOOK_URL = "https://okrlib.ru/sites/default/files/docs/2019/11_05_16_medvezh_i_e_picheskie_pesni_mansi_vogulov_2016-0270.pdf"
INPUT_FILE_PATH = "/tmp/medvezhie_pesni.pdf"
OUTPUT_FILE_PATH = "/tmp/medvezhie_pesni.csv"
START_PAGE = 26
END_PAGE = 545


def get_key(string):
    return string.strip()


def get_block(text, from_i, to_i=None):
    """
    Парсит четверостишье между индексами.
    """
    string = text[from_i:to_i]
    block = []
    for line in string.split("\n"):
        line = line.strip()
        if not line:
            continue
        if line == '* * *':
            continue
        block.append(line)
    return block


def parse_pdf(file_path):
    document = fitz.open(file_path)
    untranslated = {}
    result = []
    pattern = re.compile(r"\d+ ")

    def append_block(key, block):
        if untranslated.get(key):
            result.extend(list(zip(untranslated[key], block)))
            del untranslated[key]
        else:
            untranslated[key] = block

    for page_num in range(START_PAGE - 1, END_PAGE):
        page = document.load_page(page_num)
        text = page.get_text()
        matches = [match for match in pattern.finditer(text)]
        if not matches:
            continue
        for i in range(len(matches) - 1):
            match = matches[i]
            key = get_key(match.group())
            block = get_block(text, match.end(), matches[i + 1].start())
            append_block(key, block)
        key = get_key(matches[-1].group())
        block = get_block(text, matches[-1].end())
        append_block(key, block)

    return result


def main():
    if not os.path.exists(INPUT_FILE_PATH):
        download_pdf(INPUT_FILE_PATH, BOOK_URL)
    result = parse_pdf(INPUT_FILE_PATH)
    write_to_csv(OUTPUT_FILE_PATH, result)
    print(f"Wrote {len(result)} rows to {OUTPUT_FILE_PATH}")


if __name__ == "__main__":
    main()
