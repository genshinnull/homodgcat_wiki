from fasthtml.common import *
from monsterui.all import *


def build_text_langs(lang: str, ui: dict, langs: list[str]):
    target_langs = langs.copy()
    target_langs.remove(lang)
    return (
        LabelSelect(
            Option(
                ui["LANG"][lang],
                value=lang,
                selected=True,
            ),
            *[Option(ui["LANG"][_lang], value=_lang) for _lang in target_langs],
            label=ui["QUERY_TEXT_TARGET_LANG"][lang],
            id="target_lang",
        ),
        LabelSelect(
            Option("-", value="", selected=True),
            *[Option(ui["LANG"][_lang], value=_lang) for _lang in langs],
            label=ui["QUERY_TEXT_COMP_LANG"][lang],
            id="comp_lang",
        ),
    )


def build_text_versions(lang: str, ui: dict, versions: list[str]):
    versions = versions.copy()
    max_ver = versions.pop(0)
    if len(max_ver) > 3:
        max_rel_ver = max_ver[:3]
        versions.remove(max_rel_ver)
        max_version_options = [
            Option(ui["QUERY_TEXT_LATEST_BETA"][lang].format(max_ver), value=max_ver),
            Option(
                ui["QUERY_TEXT_LATEST_LIVE"][lang].format(max_rel_ver),
                value=max_rel_ver,
                selected=True,
            ),
        ]
    else:
        max_version_options = [
            Option(
                ui["QUERY_TEXT_LATEST_LIVE"][lang].format(max_ver),
                value=max_ver,
                selected=True,
            )
        ]
    version_options = [Option(ver, value=ver) for ver in versions]
    return (
        LabelSelect(
            *max_version_options,
            *version_options,
            label=ui["QUERY_TEXT_TARGET_VER"][lang],
            searchable=True,
            id="target_ver",
        ),
        LabelSelect(
            Option(ui["QUERY_TEXT_MODE_DEFAULT"][lang], value="", selected=True),
            Option(ui["QUERY_TEXT_MODE_NEW_ONLY"][lang], value="new_only"),
            Option(
                ui["QUERY_TEXT_MODE_INCLUDE_DELETED"][lang], value="include_deleted"
            ),
            label=ui["QUERY_TEXT_MODE"][lang],
            id="mode",
        ),
    )


def build_talk_query(lang: str, ui: dict):
    return (
        Datalist(id="q-dialog-speaker"),
        Form(
            Grid(
                Div(
                    FormLabel(
                        Span(ui["QUERY_DIALOG_SPEAKER"][lang]),
                        UkIcon(
                            "info", uk_tooltip=ui["QUERY_DIALOG_SPEAKER_TOOLTIP"][lang]
                        ),
                        cls=[FlexT.inline, "space-x-2"],
                    ),
                    Input(
                        placeholder=ui["QUERY_DIALOG_SPEAKER_PLACEHOLDER"][lang],
                        id="speaker",
                        type="search",
                        list="q-dialog-speaker",
                        hx_get=f"/{lang}/q/dialog_speaker",
                        hx_trigger="getSpeakers",
                        hx_target="#q-dialog-speaker",
                        _=(
                            "on input empty #q-dialog-speaker "
                            "on compositionstart set :composing to true "
                            "on compositionend set :composing to false "
                            "on input debounced at 500ms"
                            " if"
                            "  my value is not empty"
                            "  and my value does not start with '<'"
                            "  and my value does not end with '>'"
                            "  and (:composing does not exist or :composing is false)"
                            " then send getSpeakers"
                        ),
                    ),
                    cls="space-y-2",
                ),
                LabelInput(
                    ui["QUERY_DIALOG_CONTENT"][lang],
                    id="content",
                    type="search",
                ),
            ),
            P(ui["QUERY_OPTIONS"][lang], cls=TextT.bold),
            Grid(
                LabelCheckboxX(ui["QUERY_REGEX"][lang], id="regex"),
                LabelCheckboxX(ui["QUERY_DIALOG_NEW"][lang], id="new"),
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
                data_uk_spinner="",
                id="q-dialog-keyword-loading",
                cls=["loading", "htmx-indicator"],
            ),
            cls="space-y-5",
            hx_get=f"/{lang}/q/dialog_keyword",
            hx_target="#q-main-result",
        ),
    )


def build_text_query(lang: str, ui: dict, langs: list[str], versions: list[str]):
    return (
        Form(
            Grid(
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
                        placeholder=ui["QUERY_TEXT_VALUE_PLACEHOLDER"][lang],
                        type="search",
                    ),
                ),
                Grid(
                    *build_text_langs(lang, ui, langs),
                    *build_text_versions(lang, ui, versions),
                    cols=2,
                ),
                cols=1,
            ),
            P(ui["QUERY_EXCLUDE"][lang], cls=TextT.bold),
            Grid(
                LabelCheckboxX("TextMap", id="no_textmap"),
                LabelCheckboxX("Readable", id="no_readable"),
                LabelCheckboxX("Subtitle", id="no_subtitle"),
                cols=3,
            ),
            P(ui["QUERY_OPTIONS"][lang], cls=TextT.bold),
            Grid(
                LabelCheckboxX(ui["QUERY_REGEX"][lang], id="regex"),
                LabelCheckboxX(ui["QUERY_TEXT_UNGROUPED"][lang], id="ungrouped"),
            ),
            DivCentered(
                Button(
                    UkIcon("search"),
                    P(ui["QUERY_SEARCH"][lang]),
                    cls=["space-x-2", ButtonT.primary],
                    hx_indicator="#q-text-loading",
                ),
            ),
            DivCentered(
                data_uk_spinner="",
                id="q-text-loading",
                cls=["loading", "htmx-indicator"],
            ),
            cls="space-y-5",
            hx_get=f"/{lang}/q/text",
            hx_target="#q-main-result",
        ),
    )


def build(lang: str, ui: dict, langs: list[str], curr_ver: str, versions: list[str]):
    return (
        Title(ui["PAGE_TITLE"][lang]),
        NavBar(
            *[A(ui["LANG"][_lang], href=f"/{_lang.upper()}") for _lang in langs],
            brand=A(
                DivCentered(
                    H4(Span("Homo", cls=TextT.primary), "DGCat"),
                    P(
                        "A Genshin Leakflow project",
                        cls=TextT.muted,
                    ),
                    cls="",
                ),
                href="https://t.me/GenshinLeakflow",
                target="_blank",
            ),
            mobile_icon=UkIcon("languages"),
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
                    Li(*build_talk_query(lang, ui)),
                    Li(*build_text_query(lang, ui, langs, versions)),
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
                            P(ui["TIPS_SPEAKER_DETAIL"][lang]),
                            Ul(
                                Li(
                                    Code("TALK_ROLE_PLAYER"),
                                    " -> ",
                                    Code(ui["SPEAKER_TALK_ROLE_PLAYER"][lang]),
                                ),
                                Li(
                                    Code("TALK_ROLE_MATE_AVATAR"),
                                    " -> ",
                                    Code(ui["SPEAKER_TALK_ROLE_MATE_AVATAR"][lang]),
                                ),
                                Li(
                                    Code("{REALNAME[ID(1)]}"),
                                    " -> ",
                                    Code(ui["SPEAKER_REALNAME_ID_1"][lang]),
                                ),
                                Li(
                                    Code("{REALNAME[ID(2)]}"),
                                    " -> ",
                                    Code(ui["SPEAKER_REALNAME_ID_2"][lang]),
                                ),
                                cls=ListT.disc,
                            ),
                        ),
                        AccordionItem(
                            ui["TIPS_LIMITATION"][lang],
                            Ul(
                                Li(ui["TIPS_LIMITATION1"][lang]),
                                Li(ui["TIPS_LIMITATION2"][lang]),
                                Li(ui["TIPS_LIMITATION3"][lang]),
                                cls=ListT.disc,
                            ),
                        ),
                    ),
                ),
                id="q-main-result",
                cls="w-full md:max-w-screen-md gap-3",
            ),
            DivCentered(
                P(ui["PAGE_FOOTER"][lang]),
                P(
                    "Live data from ",
                    A(
                        "Dimbreath",
                        href="https://github.com/DimbreathBot/AnimeGameData",
                        target="_blank",
                        cls=AT.muted,
                    ),
                    " · ",
                    "Beta data from ",
                    A(
                        "Kuroo",
                        href="https://gitlab.com/GuraFoundation/YuanShenResources",
                        target="_blank",
                        cls=AT.muted,
                    ),
                    " and ",
                    A(
                        "Gen",
                        href="https://gitlab.com/R4nggaa/anime-book",
                        target="_blank",
                        cls=AT.muted,
                    ),
                ),
                cls=["relative bottom-0", TextT.muted, TextT.xs],
            ),
            cls="m-5 gap-5",
            cols_max=1,
        ),
        Meta(name="robots", content="noindex, nofollow"),
        Meta(
            name="viewport",
            content="user-scalable=no, width=device-width, initial-scale=1.0, maximum-scale=1.0",
        ),
    )
