from fasthtml.common import *
from monsterui.all import *


def build(lang: str, ui: dict, langs: list[str], curr_ver: str):
    langs_for_comp = ["-", *langs.copy()]
    langs_for_comp.remove(lang)
    return (
        Title(ui["PAGE_TITLE"][lang]),
        NavBar(
            *[
                A(ui["PAGE_USE_LANG"][use_lang], href=f"/{use_lang.upper()}")
                for use_lang in langs
            ],
            brand=A(
                DivCentered(
                    H4("HomoDGCat"),
                    P("A Genshin Leakflow Project", cls=TextT.muted),
                    cls="",
                ),
                href="https://t.me/GenshinLeakflow",
                target="_blank",
            ),
        ),
        DivCentered(
            H1(ui["PAGE_TITLE"][lang]),
            P(f"{ui['PAGE_CURR_VER'][lang]}: {curr_ver}", cls=TextT.muted),
            Container(
                TabContainer(
                    Li(A(ui["QUERY_TAB_DIALOG"][lang], href="#")),
                    Li(A(ui["QUERY_TAB_TEXT"][lang], href="#")),
                    uk_switcher="connect: #q-tabs",
                    alt=True,
                ),
                Ul(
                    Li(
                        Form(
                            Grid(
                                LabelInput(
                                    ui["QUERY_DIALOG_SPEAKER"][lang],
                                    placeholder=ui["QUERY_DIALOG_SPEAKER_PLACEHOLDER"][
                                        lang
                                    ],
                                    id="speaker",
                                    type="search",
                                ),
                                LabelInput(
                                    ui["QUERY_DIALOG_CONTENT"][lang],
                                    id="content",
                                    type="search",
                                ),
                            ),
                            DivCentered(
                                Grid(
                                    LabelCheckboxX(ui["QUERY_NEW"][lang], id="new"),
                                    LabelCheckboxX(ui["QUERY_REGEX"][lang], id="regex"),
                                ),
                            ),
                            DivCentered(
                                Button(
                                    UkIcon("search"),
                                    P(ui["QUERY_SEARCH"][lang]),
                                    cls=[
                                        "space-x-2",
                                        ButtonT.primary,
                                    ],
                                    hx_indicator="#q-dialog-keyword-loading",
                                ),
                            ),
                            DivCentered(
                                Loading(
                                    htmx_indicator=True,
                                    id="q-dialog-keyword-loading",
                                )
                            ),
                            cls="space-y-5",
                            hx_get=f"/{lang}/q/dialog_keyword",
                            hx_target="#q-main-result",
                        ),
                    ),
                    Li(
                        Form(
                            Grid(
                                LabelInput(
                                    ui["QUERY_TEXT_KEY"][lang],
                                    placeholder=ui["QUERY_TEXT_KEY_PLACEHOLDER"][lang],
                                    id="key",
                                    type="search",
                                ),
                                LabelInput(
                                    ui["QUERY_TEXT_VALUE"][lang],
                                    id="value",
                                    placeholder=ui["QUERY_TEXT_VALUE_PLACEHOLDER"][
                                        lang
                                    ],
                                    type="search",
                                ),
                                LabelSelect(
                                    Options(
                                        *langs_for_comp,
                                        selected_idx=0,
                                    ),
                                    label=ui["QUERY_TEXT_LANG_COMP"][lang],
                                    id="lang-comp",
                                ),
                                LabelSelect(
                                    Options("TextMap", "Readable", "Subtitle"),
                                    label=ui["QUERY_TEXT_EXCLUDE"][lang],
                                    id="exclude",
                                    multiple=True,
                                    placeholder="-",
                                ),
                                cols_max=2,
                            ),
                            DivCentered(
                                Grid(
                                    LabelCheckboxX(ui["QUERY_NEW"][lang], id="new"),
                                    LabelCheckboxX(ui["QUERY_REGEX"][lang], id="regex"),
                                    LabelCheckboxX(
                                        ui["QUERY_TEXT_UNGROUPED"][lang], id="ungrouped"
                                    ),
                                ),
                            ),
                            DivCentered(
                                Button(
                                    UkIcon("search"),
                                    P(ui["QUERY_SEARCH"][lang]),
                                    cls=[
                                        "space-x-2",
                                        ButtonT.primary,
                                    ],
                                    hx_indicator="#q-text-loading",
                                ),
                            ),
                            DivCentered(
                                Loading(
                                    htmx_indicator=True,
                                    id="q-text-loading",
                                )
                            ),
                            cls="space-y-5",
                            hx_get=f"/{lang}/q/text",
                            hx_target="#q-main-result",
                        ),
                    ),
                    id="q-tabs",
                    cls="uk-switcher",
                ),
                cls="w-4/5 md:max-w-screen-md gap-3 space-y-3",
            ),
            Grid(
                Div(
                    H4(ui["TIPS_TITLE"][lang]),
                    Accordion(
                        AccordionItem(
                            ui["TIPS_SPEAKER"][lang],
                            Ul(
                                Li(
                                    Code("TALK_ROLE_PLAYER"),
                                    " -> " + ui["SPEAKER_TALK_ROLE_PLAYER"][lang],
                                ),
                                Li(
                                    Code("TALK_ROLE_MATE_AVATAR"),
                                    " -> " + ui["SPEAKER_TALK_ROLE_MATE_AVATAR"][lang],
                                ),
                                Li(
                                    Code("{REALNAME[ID(1)]}"),
                                    " -> " + ui["SPEAKER_REALNAME_ID_1"][lang],
                                ),
                                Li(
                                    Code("{REALNAME[ID(2)]}"),
                                    " -> " + ui["SPEAKER_REALNAME_ID_2"][lang],
                                ),
                                cls=ListT.disc,
                            ),
                        ),
                        AccordionItem(
                            ui["TIPS_LIMITATION"][lang],
                            Ul(
                                Li(ui["TIPS_LIMITATION1"][lang]),
                                Li(ui["TIPS_LIMITATION2"][lang]),
                                cls=ListT.disc,
                            ),
                        ),
                    ),
                ),
                id="q-main-result",
                cls="w-full md:max-w-screen-md gap-3",
            ),
            P(
                ui["PAGE_FOOTER"][lang],
                cls=["relative bottom-0", TextT.muted, TextT.xs],
            ),
            cls="m-5 gap-5",
            cols_max=1,
        ),
        Meta(name="robots", content="noindex, nofollow"),
    )
