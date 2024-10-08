import os
from typing import Optional
from collections import OrderedDict

from tqdm import tqdm

import clearml

import torch
import lightning as L

from peft import LoraConfig, get_peft_model
import transformers
from transformers import (
    AutoModelForSeq2SeqLM,
    AutoModel,
    AutoTokenizer,
    NllbTokenizer,
    get_scheduler,
)

from transformers.optimization import Adafactor

import sacrebleu

class MachineTranslationModel(L.LightningModule):
    def __init__(
        self,
        model_name_or_path: str,
        model_max_length: int,
        task_name: str,
        split_name: str,
        tokenizer_path: str,
        trained_spm_path: str,
        embed_resizing: bool = False,
        add_lora: bool = True,
        ckpt_path: Optional[str] = None,
        warmup_ratio: float = 0.1,
        lora_r: int = 64,
        lora_alpha: int = 64,
        lora_dropout: float = 0.1,
        learning_rate: float = 5e-5,
        scheduler_type: str = "linear",
        config_file: Optional[str] = None,
        project_name: str = "AITH/MachineTranslation"
    ):
        super().__init__()
        self.save_hyperparameters(
            ignore=["project_name", "task_name", "config_file", "_class_path"]
        )

        self.clearml_logger = self._init_clearml_task(
            project_name,
            task_name,
            config_file,
            model_name_or_path,
            split_name,
        )

        tokenizer_model_config = self._configure_model()
        self.model, self.tokenizer = tokenizer_model_config["model"], tokenizer_model_config["tokenizer"]

        self._register_external_params()

        self.training_step_outputs = []
        self.validation_step_outputs = []
        self.ru = []
        self.mans = []
        self.rus_translated = []
        self.mansi_translated = []

    def _init_clearml_task(
        self,
        project_name,
        task_name,
        config_file,
        model_name_or_path,
        split_name,
    ):
        task = clearml.Task.init(
            project_name=project_name, task_name=f"{task_name}"
        )
        if config_file:
            task.connect_configuration(config_file)
        task.add_tags(
            [f"context_{self.hparams.model_max_length}", model_name_or_path, split_name]
        )
        return task.get_logger()

    def _register_external_params(self):
        for name, param in self.model.named_parameters():
            self.register_parameter(name.replace(".", "_"), param)

    
    def _configure_model(self):     
        model = AutoModelForSeq2SeqLM.from_pretrained(
            self.hparams.model_name_or_path, torch_dtype=torch.bfloat16
        )
        if self.hparams.embed_resizing:
            tokenizer_old = AutoTokenizer.from_pretrained(
                self.hparams.model_name_or_path
            )
            tokenizer = NllbTokenizer.from_pretrained(
                self.hparams.model_name_or_path,
                vocab_file=self.hparams.trained_spm_path,
                return_tensors="pt",
                model_max_length=512,
                padding=True,
                truncation=True
            )
            print(f"Old vocab_size: {len(tokenizer_old)},\nnew vocab size: {len(tokenizer)}")
            added_vocab = set(tokenizer.get_vocab()).difference(set(tokenizer_old.get_vocab()))

            model.resize_token_embeddings(len(tokenizer))
            for t in tqdm(added_vocab):
                tt = tokenizer_old(t, add_special_tokens=False).input_ids
                if len(tt) == 0:
                    tt = [tokenizer_old.unk_token_id]
                idx = tokenizer.convert_tokens_to_ids(t)
                model.model.shared.weight.data[idx] = model.model.shared.weight.data[tt].mean(0)

        else:
            tokenizer = NllbTokenizer.from_pretrained(
                self.hparams.model_name_or_path,
                vocab_file=self.hparams.trained_spm_path,
                return_tensors="pt",
                model_max_length=512,
                padding=True,
                truncation=True
            )
            
        if self.hparams.add_lora:
            model = self._apply_lora(model)
            model = self._load_checkpoint_weights(model)
            model.print_trainable_parameters()

        return {
            "model": model,
            "tokenizer": tokenizer
        }

    def _load_checkpoint_weights(self, model):
        ckpt_path = self.hparams.ckpt_path
        if ckpt_path:
            if os.path.isdir(ckpt_path):
                print(
                    f"\nLoading weights from HuggingFace Transformers checkpoint: {ckpt_path}"
                )
                model = AutoModelForSeq2SeqLM.from_pretrained(ckpt_path, torch_dtype=torch.bfloat16)
            else:
                print(
                    f"\nLoading weights from Pytorch Lightning checkpoint: {ckpt_path}"
                )
                model_states = OrderedDict(
                    {
                        original_states[0]: value
                        for original_states, value in zip(
                            model.named_parameters(),
                            torch.load(ckpt_path)["state_dict"].values(),
                        )
                    }
                )
                model.load_state_dict(model_states)
        return model

    def _apply_lora(self, model):
        lora_config = LoraConfig(
            r=self.hparams.lora_r,
            lora_alpha=self.hparams.lora_alpha,
            lora_dropout=self.hparams.lora_dropout,
            target_modules=[
                "q_proj",
                "k_proj",
                "v_proj",
                "o_proj",
                "gate_proj",
                "up_proj",
                "down_proj",
            ],
        )
        return get_peft_model(model, lora_config)

    def _compute_grad_norm(self, norm_type: int = 2):
        total_norm = 0.0
        for p in self.model.parameters():
            if p.grad is not None:
                param_norm = p.grad.data.norm(norm_type)
                total_norm += param_norm.item() ** norm_type
        total_norm = total_norm ** (1.0 / norm_type)

        return total_norm

    def training_step(self, batch, batch_idx):
        batch_size = batch["data"].input_ids.shape[0]

        reshaped_batch = {
            key: {matrix_key: value.view(batch_size, -1) for matrix_key, value in matrix.items()}
            for key, matrix in batch.items() if key in ["data", "label"]
        }
        
        loss = self.model(**reshaped_batch["data"], labels=reshaped_batch["label"]["input_ids"]).loss
        self.training_step_outputs.append(loss.item())
        self._log_metrics(batch_idx, loss)
        return loss

    def validation_step(self, batch, batch_idx):
        batch_size = batch["data"].input_ids.shape[0]

        reshaped_batch = {
            key: {matrix_key: value.view(batch_size, -1) for matrix_key, value in matrix.items()}
            for key, matrix in batch.items() if key in ["data", "label"]
        }
        
        loss = self.model(**reshaped_batch["data"], labels=reshaped_batch["label"]["input_ids"]).loss
        self.validation_step_outputs.append(loss.item())
        self.log(
            "val_loss", loss, sync_dist=True, prog_bar=True, add_dataloader_idx=True
        )
        return loss

    def test_step(self, batch, batch_idx):
        batch_size = batch["data"].input_ids.shape[0]

        reshaped_batch = {
            key: {matrix_key: value.view(batch_size, -1) for matrix_key, value in matrix.items()}
            for key, matrix in batch.items() if key in ["data", "label"]
        }
        
        loss = self.model(**reshaped_batch["data"], labels=reshaped_batch["label"]["input_ids"]).loss
        # self._store_test_step_outputs(batch)

        return loss

    def _translate(
        text, src_lang='rus_Cyrl', tgt_lang='kaz_Cyrl', 
        a=32, b=3, max_input_length=512, num_beams=4, **kwargs
    ):
        """Turn a text or a list of texts into a list of translations"""
        tokenizer.src_lang = src_lang
        tokenizer.tgt_lang = tgt_lang
        inputs = self.tokenizer(
            text, return_tensors='pt', padding=True, truncation=True, 
            max_length=512
        )
        result = self.model.generate(
            **inputs.to(model.device),
            forced_bos_token_id=tokenizer.convert_tokens_to_ids(tgt_lang),
            max_new_tokens=int(a + b * inputs.input_ids.shape[1]),
            num_beams=num_beams, **kwargs
        )
        return tokenizer.batch_decode(result, skip_special_tokens=True)

    def _log_metrics(self, batch_idx, loss):
        lr = self.trainer.lr_scheduler_configs[0].scheduler.optimizer.param_groups[0][
            "lr"
        ]

        self.clearml_logger.report_scalar(
            title="Learning rate",
            series="lr",
            iteration=self.global_step,
            value=lr,
        )
        self.clearml_logger.report_scalar(
            title="Batch Loss",
            series="train_batch_loss",
            iteration=self.global_step,
            value=loss.item(),
        )
        self.clearml_logger.report_scalar(
            title="Batch Loss",
            series="grad_norm",
            iteration=self.global_step,
            value=self._compute_grad_norm(),
        )

    # def _store_test_step_outputs(self, batch: dict):
    #     if batch["first_lang"] == "ru":
    #         self.ru.append(batch["data_text"])
    #         self.mans.append(batch["label_text"])
    #         self.mansi_translated.append(self._translate(batch["data_text"],
    #                                                      src_lang=batch["first_lang_tag"],
    #                                                      tgt_lang=batch["second_lang_tag"]))
    #         self.rus_translated.append(self._transalte(batch["label_text"],
    #                                                    src_lang=batch["second_lang_tag"],
    #                                                    tgt_lang=batch["first_lang_tag"]))

    #     else:
    #         self.ru.append(batch["label_text"])
    #         self.mans.append(batch["data_text"])
    #         self.mansi_translated.append(self._translate(batch["label_text"],
    #                                                      src_lang=batch["second_lang_tag"],
    #                                                      tgt_lang=batch["first_lang_tag"]))
    #         self.rus_translated.append(self._transalte(batch["data_text"],
    #                                                    src_lang=batch["first_lang_tag"],
    #                                                    tgt_lang=batch["second_lang_tag"]))

    def on_train_epoch_end(self) -> None:
        mean_loss = sum(self.training_step_outputs) / len(self.training_step_outputs)
        self.log("loss", mean_loss, sync_dist=True)
        self.clearml_logger.report_scalar(
            title="Loss",
            series="End of epoch train_loss",
            iteration=self.global_step,
            value=mean_loss,
        )
        self.training_step_outputs.clear()

    def on_validation_epoch_end(self) -> None:
        mean_loss = sum(self.validation_step_outputs) / len(
            self.validation_step_outputs
        )
        self.log("val_loss", mean_loss, sync_dist=True)
        self._log_end_of_epoch_metrics(mean_loss)
        self.validation_step_outputs.clear()

    def _log_end_of_epoch_metrics(self, mean_loss):
        self.clearml_logger.report_scalar(
            title="Loss",
            series="Validation loss",
            iteration=self.global_step,
            value=mean_loss,
        )
        if self.training_step_outputs:
            cur_train_mean_loss = sum(self.training_step_outputs) / len(
                self.training_step_outputs
            )
            self.clearml_logger.report_scalar(
                title="Loss",
                series="Current train_loss",
                iteration=self.global_step,
                value=cur_train_mean_loss,
            )

    def on_test_epoch_end(self) -> None:
        bleu_calc = sacrebleu.BLEU()
        chrf_calc = sacrebleu.CHRF(word_order=2)  # this metric is called ChrF++

        self._log_chrf(
            russian_chrf=chrf_calc.corpus_score(self.rus_translated, [self.ru]),
            mans_chrf=chrf_calc.corpus_score(self.mansi_translated, [self.mans])
        )
        self._log_bleu(
            russian_bleu=bleu_calc.corpus_score(self.rus_translated, [self.ru]),
            mansi_bleu=bleu_calc.corpus_score(self.mansi_translated, [self.mans])
        )

        self.ru.clear()
        self.rus_translated.clear()
        self.mans.clear()
        self.mansi_translated.clear()

    def _log_chrf(self, russian_chrf: float, mans_chrf: float):
        self.clearml_logger.report_scalar(
            title="CHRF",
            series="Russian ChrF++",
            iteration=self.global_step,
            value=russian_chrf,
        )
        self.clearml_logger.report_scalar(
            title="CHRF",
            series="Mansi ChrF++",
            iteration=self.global_step,
            value=mans_chrf
        )

    def _log_bleu(self, russian_bleu: float, mans_bleu: float):
        self.clearml_logger.report_scalar(
            title="Bleu",
            series="Russian BLEU",
            iteration=self.global_step,
            value=russian_bleu_value,
        )
        self.clearml_logger.report_scalar(
            title="Bleu",
            series="Mansi BLEU",
            iteration=self.global_step,
            value=mans_bleu_value,
        )

    def configure_optimizers(self):
        optimizer = Adafactor(
            [p for p in self.model.parameters() if p.requires_grad],
            scale_parameter=False,
            relative_step=False,
            lr=self.hparams.learning_rate,
            weight_decay=1e-3,
        )
        num_training_steps = self.trainer.estimated_stepping_batches
        warmup_steps = int(num_training_steps * self.hparams.warmup_ratio)
        print(f"Training steps: {num_training_steps}, warmup steps: {warmup_steps}")
        lr_scheduler = {
            "scheduler": get_scheduler(
                name=self.hparams.scheduler_type,
                optimizer=optimizer,
                num_warmup_steps=warmup_steps,
                num_training_steps=num_training_steps,
            ),
            "name": "learning_rate",
            "interval": "step",
            "frequency": 1,
        }
        return {"optimizer": optimizer, "lr_scheduler": lr_scheduler}
