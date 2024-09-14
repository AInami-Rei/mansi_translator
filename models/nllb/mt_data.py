import os
import json
import random
import pickle
import importlib

from typing import Dict

from tqdm import tqdm

import numpy as np

import torch
import lightning as L
from torch.utils.data import DataLoader

from transformers import NllbTokenizer


class DataModule(L.LightningDataModule):
    def __init__(
        self,
        dataset_class: str,
        train_data_path: str,
        val_data_path: str,
        test_data_path: str,
        model_name_or_path: str,
        batch_size: int,
        trained_spm_path: str,
        data_processing: bool = False,
        model_max_length: int = 512,
        num_workers: int = 16,
        ckpt_path: str = None,
    ):
        super().__init__()
        self.save_hyperparameters(ignore=["dataset_class"])

        self.tokenizer = self._initialize_tokenizer(model_name_or_path)
        self.dataset_class = self._get_class_from_string(dataset_class)
        self.pt_train_path = self._construct_pt_path(train_data_path)
        self.pt_val_path = self._construct_pt_path(val_data_path)
        self.pt_test_path = self._construct_pt_path(test_data_path)

    @staticmethod
    def _get_class_from_string(class_path: str):
        module_name, class_name = class_path.rsplit(".", 1)
        module = importlib.import_module(module_name)
        return getattr(module, class_name)

    def _initialize_tokenizer(self, model_name_or_path: str):
        tokenizer_path = (
            self.hparams.ckpt_path
            if (self.hparams.ckpt_path and os.path.isdir(self.hparams.ckpt_path))
            else model_name_or_path
        )
        return NllbTokenizer.from_pretrained(
            tokenizer_path,
            vocab_file=self.hparams.trained_spm_path,
            model_max_length=512,
            padding="max_length",
            truncation=True
        )

    def _construct_pt_path(self, data_path: str):
        """Construct the path for the processed dataset."""
        model_name_or_path = self.hparams.model_name_or_path.replace("/", "_")
        return data_path.replace(
            ".csv",
            f"_{model_name_or_path}_{self.hparams.model_max_length}.pt",
        )

    def prepare_data(self):
        """Prepare the dataset if not already prepared."""
        if self._all_data_prepared() and not self.hparams.data_processing:
            return

        self._process_and_save_dataset(self.pt_train_path, self.hparams.train_data_path)
        self._process_and_save_dataset(self.pt_val_path, self.hparams.val_data_path)
        self._process_and_save_dataset(self.pt_test_path, self.hparams.test_data_path)

    def _all_data_prepared(self):
        """Check if all required datasets are already prepared."""
        return (
            os.path.exists(self.pt_train_path)
            and os.path.exists(self.pt_val_path)
            and os.path.exists(self.pt_test_path)
        )

    def _process_and_save_dataset(self, pt_path: str, data_path: str):
        """Process the dataset and save it to the specified path."""
        if not os.path.exists(pt_path) or self.hparams.data_processing:
            dataset = self.dataset_class(file_path=data_path, tokenizer=self.tokenizer)
            torch.save(dataset, pt_path)

    def setup(self, stage: str):
        """Setup datasets for different stages."""
        if stage == "fit":
            self.train_dataset = torch.load(self.pt_train_path)
            self.val_dataset = torch.load(self.pt_val_path)
        elif stage == "validate":
            self.val_dataset = torch.load(self.pt_val_path)
        elif stage == "test":
            self.test_dataset = torch.load(self.pt_test_path)

    def train_dataloader(self):
        return self._create_dataloader(self.train_dataset, shuffle=True)

    def val_dataloader(self):
        return self._create_dataloader(self.val_dataset, shuffle=False)

    def test_dataloader(self):
        return self._create_dataloader(self.test_dataset, shuffle=False)

    def _create_dataloader(self, dataset, shuffle: bool):
        return DataLoader(
            dataset,
            shuffle=shuffle,
            batch_size=self.hparams.batch_size,
            num_workers=self.hparams.num_workers,
            pin_memory=True,
        )
