import random

from database.orm import Theme
from generators.config import session


def choose_theme(boost_name: str, boost_amount: int = 150):
    themes = session.query(Theme).all()

    weights = [theme.probability for theme in themes]

    for i, theme in enumerate(themes):
        if theme.name == boost_name:
            weights[i] += boost_amount
            break

    return random.choices(themes, weights=weights, k=1)[0]
