from fasthtml.common import *
from monsterui.all import *

import utils

WIKI_BASE_URL = "https://genshin-impact.fandom.com/wiki/{}"


def build_results(pairs: dict, q: str, lang: str, target_lang: str):
    results = []
    for pair in pairs:
        results.append(
            Li(
                Div(
                    Span(
                        pair["page_category_type"],
                        cls=(TextT.meta, "justify-self-start"),
                    ),
                    Div(
                        utils.build_text(pair[lang]),
                        P(pair[target_lang]),
                        cls="text-center",
                    ),
                    A(
                        Span(UkIcon("external-link"), cls=AT.primary),
                        href=WIKI_BASE_URL.format(pair["page_title"]),
                        target="_blank",
                        cls="justify-self-end",
                    ),
                    cls="grid items-center w-full",
                    style="grid-template-columns: 1fr auto 1fr;",
                ),
            )
        )
    return Ul(*results, cls=ListT.striped)
