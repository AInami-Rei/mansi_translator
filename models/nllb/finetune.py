import torch
import lightning as L
from lightning.pytorch.cli import LightningCLI

torch.set_float32_matmul_precision("medium")


class MyLightningCLI(LightningCLI):
    def add_arguments_to_parser(self, parser):
        parser.link_arguments(
            "model.init_args.model_name_or_path", "data.init_args.model_name_or_path"
        )
        parser.link_arguments("model.init_args.ckpt_path", "data.init_args.ckpt_path")


if __name__ == "__main__":
    cli = MyLightningCLI(
        model_class=L.LightningModule,
        datamodule_class=L.LightningDataModule,
        subclass_mode_model=True,
        subclass_mode_data=True,
    )
