import argparse
import os


class Options:
    def __init__(self):
        self.parser = argparse.ArgumentParser(description="parser for PyTorch-Style-Transfer")
        subparsers = self.parser.add_subparsers(title="subcommands", dest="subcommand")

        # evaluation args
        eval_arg = subparsers.add_parser("eval", help="parser for evaluation/stylizing arguments")
        eval_arg.add_argument("--ngf", type=int, default=128,
                              help="number of generator filter channels, default 128")
        eval_arg.add_argument("--content-image", type=str, required=True,
                              help="path to content image you want to stylize")
        eval_arg.add_argument("--style-image", type=str, default="images/9styles/candy.jpg",
                              help="path to style-image")
        eval_arg.add_argument("--content-size", type=int, default=512,
                              help="factor for scaling down the content image")
        eval_arg.add_argument("--style-size", type=int, default=512,
                              help="size of style-image, default is the original size of style image")
        eval_arg.add_argument("--style-folder", type=str, default="images/9styles/",
                              help="path to style-folder")
        eval_arg.add_argument("--output-image", type=str, default="output.jpg",
                              help="path for saving the output image")
        eval_arg.add_argument("--model", type=str, required=True,
                              help="saved model to be used for stylizing the image")
        eval_arg.add_argument("--cuda", type=int, default=1,
                              help="set it to 1 for running on GPU, 0 for CPU")
        eval_arg.add_argument("--vgg-model-dir", type=str, default="models/",
                              help="directory for vgg, if model is not present in the directory it is downloaded")

    def parse(self):
        return self.parser.parse_args()
