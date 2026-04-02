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
        P(readable_name, cls=[TextT.primary, "text-wrap break-words"])
        if readable_name
        else None,
        P(
            value,
            cls="whitespace-pre-line text-wrap break-words",
        ),
        cls="space-y-1",
    )


def build_text_key(lang: str, ui: dict, key: str | list[str], i: int):
    if isinstance(key, list):
        if len(key) == 1:
            key = key[0]
        else:
            return (
                A(
                    DivHStacked(
                        UkIcon("expand"),
                        P(
                            ui["RESULT_TEXT_EXPAND_KEY"][lang].format(len(key)),
                            cls=TextT.bold,
                        ),
                        cls="space-x-1",
                    ),
                    href="#",
                    data_uk_toggle=f"target: #modal-{i}",
                    cls=AT.text,
                ),
                Modal(
                    P(", ".join(key), cls="text-wrap break-all"),
                    id=f"modal-{i}",
                    footer=ModalCloseButton(
                        cls=[
                            "absolute top-3 right-3",
                            ButtonT.destructive,
                        ]
                    ),
                ),
            )
    return P(key, cls=[TextT.bold, "text-wrap break-all"])


def build_text_window(lang: str, ui: dict, k_from: str, kv_from: str, v_from: str):
    if v_from:
        return Div(
            P(
                ui["RESULT_TEXT_V_FROM"][lang],
                " ",
                CodeSpan(v_from),
                cls=[TextT.muted, TextT.xs, TextT.right],
            )
        )
    return Div(
        P(
            ui["RESULT_TEXT_K_FROM"][lang],
            " ",
            CodeSpan(k_from),
            cls=[TextT.muted, TextT.xs, TextT.right],
        ),
        P(
            ui["RESULT_TEXT_KV_FROM"][lang],
            " ",
            CodeSpan(kv_from),
            cls=[TextT.muted, TextT.xs, TextT.right],
        ),
    )


def build_result(text_list: list[dict], lang: str, ui: dict, lang_comp: bool):
    results = []
    for i, text in enumerate(text_list):
        text_content = []
        text_content.append(
            build_base_text(
                lang, ui, text["value"], text["paged"], text["book"], text["letter"]
            )
        )
        if lang_comp:
            text_content.append(
                build_base_text(
                    lang,
                    ui,
                    text["value_right"],
                    text["paged_right"],
                    text["book_right"],
                    text["letter_right"],
                )
            )
        results.append(
            Li(
                DivFullySpaced(
                    DivHStacked(
                        build_text_key(lang, ui, text["key"], i),
                        P(text["type"], cls=TextT.muted),
                        cls=[FlexT.wrap, "space-x-2"],
                    ),
                    build_text_window(
                        lang,
                        ui,
                        text.get("k_from"),
                        text.get("kv_from"),
                        text.get("v_from"),
                    ),
                ),
                *text_content,
                cls="space-y-1",
            )
        )
    return Ul(*results, cls=ListT.divider)
