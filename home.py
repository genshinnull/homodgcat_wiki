from fasthtml.common import *
from monsterui.all import *


def build(lang: str, ui: dict, langs: list[str], curr_ver: str):
    return (
        Title(ui["QUERY"]["TITLE"][lang]),
        NavBar(
            *[
                A(ui["PAGE"]["USE_LANG"][use_lang], href=f"/{use_lang.upper()}")
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
            H1(ui["QUERY"]["TITLE"][lang]),
            P(f"{ui['PAGE']['CURR_VER'][lang]}: {curr_ver}", cls=TextT.muted),
            Form(
                Grid(
                    LabelInput(
                        ui["QUERY"]["SPEAKER"][lang],
                        placeholder=ui["QUERY"]["SPEAKER_PLACEHOLDER"][lang],
                        id="speaker",
                        type="search",
                    ),
                    LabelInput(
                        ui["QUERY"]["CONTENT"][lang], id="content", type="search"
                    ),
                ),
                DivCentered(
                    DivHStacked(
                        Button(
                            DivHStacked(
                                UkIcon("search"),
                                P(ui["QUERY"]["SEARCH"][lang]),
                                cls="space-x-2",
                            ),
                            cls=ButtonT.primary,
                            hx_indicator="#query-keyword-loading",
                        ),
                        LabelCheckboxX(ui["QUERY"]["NEW"][lang], id="new"),
                        LabelCheckboxX(ui["QUERY"]["REGEX"][lang], id="regex"),
                    ),
                    Loading(htmx_indicator=True, id="query-keyword-loading"),
                ),
                hx_get=f"/{lang}/q/dialog_keyword",
                hx_target="#query-keyword-result",
            ),
            Grid(
                Div(
                    H4(ui["TIPS"]["TIPS"][lang]),
                    Accordion(
                        AccordionItem(
                            ui["TIPS"]["SPEAKER"][lang],
                            Ul(
                                Li(
                                    Code("TALK_ROLE_PLAYER"),
                                    " -> " + ui["SPEAKER"]["TALK_ROLE_PLAYER"][lang],
                                ),
                                Li(
                                    Code("TALK_ROLE_MATE_AVATAR"),
                                    " -> "
                                    + ui["SPEAKER"]["TALK_ROLE_MATE_AVATAR"][lang],
                                ),
                                Li(
                                    Code("{REALNAME[ID(1)]}"),
                                    " -> " + ui["SPEAKER"]["REALNAME_ID_1"][lang],
                                ),
                                Li(
                                    Code("{REALNAME[ID(2)]}"),
                                    " -> " + ui["SPEAKER"]["REALNAME_ID_2"][lang],
                                ),
                                cls=ListT.disc,
                            ),
                        ),
                        AccordionItem(
                            ui["TIPS"]["LIMITATION"][lang],
                            Ul(
                                Li(ui["TIPS"]["LIMITATION1"][lang]),
                                Li(ui["TIPS"]["LIMITATION2"][lang]),
                                cls=ListT.disc,
                            ),
                        ),
                    ),
                ),
                id="query-keyword-result",
                cls="w-full md:max-w-screen-md gap-3",
            ),
            P(
                ui["PAGE"]["FOOTER"][lang],
                cls=["relative bottom-0", TextT.muted, TextT.xs],
            ),
            cls="m-5 gap-5",
            cols_max=1,
        ),
        Meta(name="robots", content="noindex, nofollow"),
    )
