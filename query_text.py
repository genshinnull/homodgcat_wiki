from fasthtml.common import *
from monsterui.all import *


def build(text_list: list[dict], lang: str, ui: dict):
    results = []
    for i, text in enumerate(text_list):
        results.append(Li(P(str(text)), Br()))
    return Ul(*results)
