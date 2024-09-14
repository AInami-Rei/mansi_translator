import os
import re
import sys
import json
import random
import pickle
import importlib
import unicodedata

from typing import Dict

from tqdm import tqdm

import numpy as np
import pandas as pd

import torch
import lightning as L
from torch.utils.data import Dataset, DataLoader

from transformers import AutoTokenizer

from sacremoses import MosesPunctNormalizer



class MachineTranslationDataset(Dataset):
    def __init__(
        self,
        tokenizer: AutoTokenizer,
        file_path: str = None,
    ):
        self.LANGS = [('ru', 'rus_Cyrl'), ('mans', "kaz_Cyrl")]
        self.tokenizer = tokenizer
        self.mpn = MosesPunctNormalizer(lang="en")
        self.mpn.substitutions = [
            (re.compile(r), sub) for r, sub in self.mpn.substitutions
        ]
        self.data = pd.read_csv(file_path)

    def __len__(self):
        return self.data.shape[0]

    def __getitem__(self, i):
        (first_lang, first_lang_tag), (second_lang, second_lang_tag) = random.sample(self.LANGS, 2)
        sample = self.data.iloc[i]

        data = self._tokenize(
            text=sample[first_lang],
            lang=first_lang
        )
        label = self._tokenize(
            text=sample[second_lang],
            lang=second_lang,
            target_flag=True
        )

        return {
            "data": data,
            "label": label,
            "data_text": self.preproc(sample[first_lang]),
            "label_text": self.preproc(sample[second_lang]),
            "first_lang": first_lang,
            "second_lang": second_lang,
            "first_lang_tag": first_lang_tag,
            "second_lang_tag": second_lang_tag
        }

    def _tokenize(self, text: str, lang: str, target_flag=False):
        self.tokenizer.src_lang = lang
        # fix constant valuess
        data = self.tokenizer(
            self.preproc(text),
            return_tensors="pt",
            padding="max_length",
            truncation=True,
            max_length=512
        )
        if target_flag:
            data.input_ids[data.input_ids == self.tokenizer.pad_token_id] = -100

        return data
        
    def get_non_printing_char_replacer(self, line, replace_by: str = " "):
        non_printable_map = {
            ord(c): replace_by
            for c in (chr(i) for i in range(sys.maxunicode + 1))
            # same as \p{C} in perl
            # see https://www.unicode.org/reports/tr44/#General_Category_Values
            if unicodedata.category(c) in {"C", "Cc", "Cf", "Cs", "Co", "Cn"}
        }

        return line.translate(non_printable_map)

    def preproc(self, text: list):
        clean = self.mpn.normalize(text)
        clean = self.get_non_printing_char_replacer(clean)
        # replace 𝓕𝔯𝔞𝔫𝔠𝔢𝔰𝔠𝔞 by Francesca
        clean = unicodedata.normalize("NFKC", clean)
        return clean
