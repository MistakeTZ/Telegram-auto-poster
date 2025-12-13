import logging
from os.path import join


def get_prompt(name: str, folder: str = "expressions", **kwargs):
    with open(join(folder, f"{name}.txt"), encoding="utf-8") as file:
        expression = file.read()
    logging.debug("Loaded prompt: %s", expression)

    if kwargs:
        logging.debug("Prompt variables: %s", kwargs)
        return expression.format(**kwargs)
    return expression
