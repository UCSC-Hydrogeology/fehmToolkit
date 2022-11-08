import argparse

from fehmtk.command_line_interface import add_fehmtk_subparsers


def test_parser():
    parser = argparse.ArgumentParser()
    subparsers = add_fehmtk_subparsers(parser)
    for name, command in subparsers.choices.items():
        assert command.get_default('_name') == name
        assert callable(command.get_default('_func'))
