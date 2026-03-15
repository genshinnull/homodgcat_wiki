from fasthtml.common import *
from monsterui.all import *


def build_base_text(
    lang: str,
    ui: dict,
    value: str,
    paged: str,
    book: str,
    letter: str,
):
    readable_name = " - ".join([name for name in [paged, book, letter] if name])
    return Div(
        P(readable_name, cls=TextT.primary),
        P(value, cls="whitespace-pre-line"),
        cls="space-y-1",
    )


def build_text_key(lang: str, ui: dict, key: str | list[str], i: int):
    if isinstance(key, list) and len(key) > 1:
        return (
            P(ui["RESULT_TEXT_EXPAND_KEY"][lang].format(len(key))),
            UkIconLink("expand", data_uk_toggle=f"target: #modal-{i}", cls=AT.primary),
            Modal(
                ", ".join(key),
                id=f"modal-{i}",
                footer=ModalCloseButton(
                    cls=[
                        "absolute top-3 right-3",
                        ButtonT.destructive,
                    ]
                ),
            ),
        )
    else:
        key = key[0]
        return P(key, cls="uk-codespan")


def build(text_list: list[dict], lang: str, ui: dict, ungrouped: bool, lang_comp: bool):
    results = []
    for i, text in enumerate(text_list):
        text_content = []
        text_content.append(
            build_base_text(
                lang, ui, text["value"], text["Paged"], text["Book"], text["Letter"]
            )
        )
        if lang_comp:
            text_content.append(
                build_base_text(
                    lang,
                    ui,
                    text["value_right"],
                    text["Paged_right"],
                    text["Book_right"],
                    text["Letter_right"],
                )
            )
        results.append(
            Li(
                DivHStacked(
                    P(text["type"], cls=TextT.bold),
                    build_text_key(lang, ui, text["key"], i),
                ),
                *text_content,
                cls="space-y-1",
            )
        )
    return Ul(*results, cls=ListT.divider)
