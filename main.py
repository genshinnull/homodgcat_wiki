import functools
import json
import os
import re

import polars as pl
from fasthtml.common import *
from monsterui.all import *

QUERY_MAX_RESULTS = 1000
CACHE_MAX_AGE = 600

Langs = str_enum("Langs", *os.environ["LANGS"].split(","))

TALK_DATA_DIR = os.environ["TALK_DATA_DIR"]
CURR_VER = os.environ["CURR_VER"]

app = FastHTML(hdrs=Theme.blue.headers())

with open("text.json") as f:
    TEXT = json.loads(f.read())

talk_data = {}
for lang in Langs:
    talk_data_path = (
        f"{TALK_DATA_DIR}/GI_Talk_{lang}.parquet"
        if TALK_DATA_DIR.startswith("http")
        else Path(TALK_DATA_DIR) / f"GI_Talk_{lang}.parquet"
    )
    talk_data[lang] = (
        pl.read_parquet(talk_data_path)
        .with_columns(
            talkRoleIdName=pl.when(pl.col.talkRoleType == "TALK_ROLE_PLAYER")
            .then(pl.lit(TEXT["SPEAKER"]["TALK_ROLE_PLAYER"][lang]))
            .when(pl.col.talkRoleType == "TALK_ROLE_MATE_AVATAR")
            .then(pl.lit(TEXT["SPEAKER"]["TALK_ROLE_MATE_AVATAR"][lang]))
            .when(
                pl.col.talkRoleIdName.str.contains(
                    r"^\#\{REALNAME\[ID\(1\)\|\w+\(\w+\)\]\}$"
                )
            )
            .then(pl.lit(TEXT["SPEAKER"]["REALNAME_ID_1"][lang]))
            .when(
                pl.col.talkRoleIdName.str.contains(
                    r"^\#\{REALNAME\[ID\(2\)\|\w+\(\w+\)\]\}$"
                )
            )
            .then(pl.lit(TEXT["SPEAKER"]["REALNAME_ID_2"][lang]))
            .otherwise(pl.col.talkRoleIdName)
        )
        .with_columns(
            talkRoleIdNameLower=pl.col.talkRoleIdName.str.to_lowercase(),
            talkRoleNameLower=pl.col.talkRoleName.str.to_lowercase(),
            talkTitleLower=pl.col.talkTitle.str.to_lowercase(),
            talkContentLower=pl.col.talkContent.str.to_lowercase(),
        )
        .lazy()
    )


@app.route("/{lang}", methods="GET")
@functools.cache
def get_home(lang: str | None):
    if not lang:
        return Redirect(f"/{list(Langs)[0]}")
    if lang not in Langs:
        if (lang_upper := lang.upper()) in Langs:
            return Redirect(f"/{lang_upper}")
        raise HTTPException(status_code=404)
    return (
        Title(TEXT["QUERY"]["TITLE"][lang]),
        NavBar(
            *[
                A(TEXT["PAGE"]["USE_LANG"][use_lang], href=f"/{use_lang.upper()}")
                for use_lang in Langs
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
            H1(TEXT["QUERY"]["TITLE"][lang]),
            P(f"{TEXT['PAGE']['CURR_VER'][lang]}: {CURR_VER}", cls=TextT.muted),
            Form(
                Grid(
                    LabelInput(
                        TEXT["QUERY"]["SPEAKER"][lang],
                        placeholder=TEXT["QUERY"]["SPEAKER_PLACEHOLDER"][lang],
                        id="speaker",
                        type="search",
                    ),
                    LabelInput(
                        TEXT["QUERY"]["CONTENT"][lang], id="content", type="search"
                    ),
                ),
                DivCentered(
                    DivHStacked(
                        Button(
                            DivHStacked(
                                UkIcon("search"),
                                P(TEXT["QUERY"]["SEARCH"][lang]),
                                cls="space-x-2",
                            ),
                            cls=ButtonT.primary,
                            hx_indicator="#query-keyword-loading",
                        ),
                        LabelCheckboxX(TEXT["QUERY"]["NEW"][lang], id="new"),
                        LabelCheckboxX(TEXT["QUERY"]["REGEX"][lang], id="regex"),
                    ),
                    Loading(htmx_indicator=True, id="query-keyword-loading"),
                ),
                hx_get=f"/{lang}/query_keyword",
                hx_target="#query-keyword-result",
            ),
            Grid(
                Div(
                    H4(TEXT["TIPS"]["TIPS"][lang]),
                    Accordion(
                        AccordionItem(
                            TEXT["TIPS"]["SPEAKER"][lang],
                            Ul(
                                Li(
                                    Code("TALK_ROLE_PLAYER"),
                                    " -> " + TEXT["SPEAKER"]["TALK_ROLE_PLAYER"][lang],
                                ),
                                Li(
                                    Code("TALK_ROLE_MATE_AVATAR"),
                                    " -> "
                                    + TEXT["SPEAKER"]["TALK_ROLE_MATE_AVATAR"][lang],
                                ),
                                Li(
                                    Code("{REALNAME[ID(1)]}"),
                                    " -> " + TEXT["SPEAKER"]["REALNAME_ID_1"][lang],
                                ),
                                Li(
                                    Code("{REALNAME[ID(2)]}"),
                                    " -> " + TEXT["SPEAKER"]["REALNAME_ID_2"][lang],
                                ),
                                cls=ListT.disc,
                            ),
                        ),
                        AccordionItem(
                            TEXT["TIPS"]["LIMITATION"][lang],
                            Ul(
                                Li(TEXT["TIPS"]["LIMITATION1"][lang]),
                                Li(TEXT["TIPS"]["LIMITATION2"][lang]),
                                cls=ListT.disc,
                            ),
                        ),
                    ),
                ),
                id="query-keyword-result",
                cls="w-full md:max-w-screen-md gap-3",
            ),
            P(
                TEXT["PAGE"]["FOOTER"][lang],
                cls=["relative bottom-0", TextT.muted, TextT.xs],
            ),
            cls="m-5 gap-5",
            cols_max=1,
        ),
        HttpHeader("Cache-Control", f"max-age={CACHE_MAX_AGE}"),
        Meta(name="robots", content="noindex, nofollow"),
        Meta(property="og:title", content="HomoDGCat"),
        Meta(property="og:description", content="A Genshin Leakflow Project"),
    )


@app.route("/{lang}/query_keyword", methods="GET")
@functools.lru_cache
def query_keyword(
    lang: Langs, speaker: str, content: str, new: bool = False, regex: bool = False
):
    if speaker or content:
        query_lf = talk_data[lang]
        if new:
            query_lf = query_lf.filter(pl.col.new)
        if speaker:
            if regex:
                query_lf = query_lf.filter(
                    pl.col.talkRoleIdName.str.contains(speaker)
                    | (pl.col.talkRoleName.str.contains(speaker))
                    | (pl.col.talkTitle.str.contains(speaker))
                )
            else:
                speaker = speaker.lower()
                query_lf = query_lf.filter(
                    (pl.col.talkRoleIdNameLower.str.contains(speaker, literal=True))
                    | (pl.col.talkRoleNameLower.str.contains(speaker, literal=True))
                    | (pl.col.talkTitleLower.str.contains(speaker, literal=True))
                )
        if content:
            if regex:
                query_lf = query_lf.filter(pl.col.talkContent.str.contains(content))
            else:
                content = content.lower()
                query_lf = query_lf.filter(
                    pl.col.talkContentLower.str.contains(content, literal=True)
                )
        try:
            query_df = query_lf.collect()
            assert isinstance(query_df, pl.DataFrame)
            result_len = len(query_df)
            if result_len == 0:
                alert_icon = "triangle-alert"
                alert_msg = TEXT["ALERT"]["NONE"][lang]
                alert_cls = AlertT.error
            elif result_len < QUERY_MAX_RESULTS:
                alert_icon = "check"
                alert_msg = TEXT["ALERT"]["SUCCESS"][lang].format(result_len)
                alert_cls = AlertT.success
            else:
                alert_icon = "triangle-alert"
                alert_msg = TEXT["ALERT"]["OVERFLOW"][lang].format(
                    QUERY_MAX_RESULTS, result_len
                )
                alert_cls = AlertT.warning
                query_df = query_df.limit(QUERY_MAX_RESULTS)
            if alert_cls != AlertT.error:
                return (
                    Alert(DivHStacked(UkIcon(alert_icon), P(alert_msg)), cls=alert_cls),
                    KeywordQueryResults(lang, query_df.to_dicts()),
                    HttpHeader("Cache-Control", f"max-age={CACHE_MAX_AGE}"),
                )
        except pl.exceptions.ComputeError as e:
            alert_icon = "triangle-alert"
            alert_msg = str(e)
            alert_cls = AlertT.error
    else:
        alert_icon = "triangle-alert"
        alert_msg = TEXT["ALERT"]["EMPTY"][lang]
        alert_cls = AlertT.error
    return Alert(DivHStacked(UkIcon(alert_icon), P(alert_msg)), cls=alert_cls)


@app.route("/{lang}/query_collection", methods="GET")
@functools.lru_cache
def query_collection(
    lang: Langs,
    id: int | None = None,
    talkId: int | None = None,
    questId: int | None = None,
):
    query_lf = talk_data[lang]
    if id:
        query_lf = query_lf.filter(pl.col.id.is_between(id - 100, id + 100))
    elif talkId:
        query_lf = query_lf.filter(pl.col.talkId == talkId)
    elif questId:
        query_lf = query_lf.filter(pl.col.questId == questId)
    else:
        return Response(status_code=400)
    query_df = query_lf.collect()
    assert isinstance(query_df, pl.DataFrame)
    results = []
    talks = query_df.rows_by_key("talkId", named=True)
    for talk in list(talks.values()):
        talk_dialogs = []
        for dialog in talk:
            talk_dialogs.append(
                Li(
                    *BaseDialog(
                        dialog["id"],
                        dialog["talkRoleIdName"],
                        dialog["talkRoleName"],
                        dialog["talkTitle"],
                        dialog["talkContent"],
                        dialog["talkRoleType"],
                        dialog["type"],
                    )
                )
            )
        results.append(Ul(*talk_dialogs, cls=ListT.divider))
    return (
        Ul(
            *results,
            cls=ListT.striped,
        ),
        HttpHeader("Cache-Control", f"max-age={CACHE_MAX_AGE}"),
    )


def BaseDialog(
    id: int,
    talkRoleIdName: str,
    talkRoleName: str,
    talkTitle: str,
    talkContent: str,
    talkRoleType: str,
    type: str,
):
    if talkRoleName:
        if talkRoleIdName:
            if talkRoleIdName != talkRoleName:
                talkRoleIdName += " -> " + talkRoleName
        else:
            talkRoleIdName = talkRoleName
    talk_speaker = []
    if talkRoleIdName:
        talk_speaker.append(P(talkRoleIdName, cls=TextT.bold))
    if talkTitle:
        talk_speaker.append(P(talkTitle, cls=(TextT.muted, TextT.xs)))
    return (
        DivHStacked(P(id), P(type, cls=TextT.muted), cls=[TextT.xs, "space-x-4"]),
        DivHStacked(
            DivCentered(*talk_speaker, cls="") if talk_speaker else None,
            P(talkRoleType, cls=TextT.muted),
        ),
        P(re.sub(r"\\n", "\n", talkContent), cls="whitespace-pre-line")
        if talkContent
        else None,
    )


def CollectionQueryTrigger(
    lang: Langs,
    i: int,
    id: int | None = None,
    talkId: int | None = None,
    questId: int | None = None,
):
    if id:
        suffix = "-id"
        link_title = TEXT["RESULT"]["EXPAND_ID"][lang] + f" (id={id}±100)"
        hx_vals = {"id": id}
        modal_title = f"IDs {id - 100} - {id + 100}"
    elif talkId:
        suffix = "-talkId"
        link_title = TEXT["RESULT"]["EXPAND_TALK"][lang] + f" (talkId={talkId})"
        hx_vals = {"talkId": talkId}
        modal_title = f"TalkID {talkId}"
    elif questId:
        suffix = "-questId"
        link_title = TEXT["RESULT"]["EXPAND_QUEST"][lang] + f" (questId={questId})"
        hx_vals = {"questId": questId}
        modal_title = f"QuestID {questId}"
    modal = f"modal-{i}{suffix}"
    replace = f"replace-{i}{suffix}"
    return Li(
        A(
            link_title,
            data_uk_toggle=f"#{modal}",
            hx_get=f"/{lang}/query_collection",
            hx_vals=hx_vals,
            hx_target=f"#{replace}",
            hx_indicator="#query-collection-loading",
        ),
        Modal(
            ModalTitle(modal_title),
            DivCentered(
                Loading(
                    htmx_indicator=True,
                    id="query-collection-loading",
                )
            ),
            Div(id=replace),
            footer=ModalCloseButton(
                cls=[
                    "absolute top-3 right-3",
                    ButtonT.destructive,
                ]
            ),
            id=modal,
        ),
    )


def KeywordQueryResults(lang: Langs, dialogs: list[dict]):
    results = []
    for i, dialog in enumerate(dialogs):
        talk_collection_names = []
        chapter = None
        if chapterTitle := dialog["chapterTitle"]:
            if chapterNum := dialog["chapterNum"]:
                chapter = ": ".join([chapterNum, chapterTitle])
            else:
                chapter = chapterTitle
        for collection_name in [
            dialog["questIdName"],
            dialog["activityIdName"],
            chapter,
        ]:
            if collection_name:
                talk_collection_names.append(collection_name)
        if talk_collection_names:
            talk_collection_names = " - ".join(talk_collection_names)
        talk_collection_triggers = [
            CollectionQueryTrigger(lang=lang, i=i, id=dialog["id"])
        ]
        if talkId := dialog["talkId"]:
            talk_collection_triggers.append(
                CollectionQueryTrigger(lang=lang, i=i, talkId=talkId)
            )
        if questId := dialog["questId"]:
            talk_collection_triggers.append(
                CollectionQueryTrigger(lang=lang, i=i, questId=questId)
            )
        results.append(
            Li(
                DivFullySpaced(
                    Div(
                        *BaseDialog(
                            dialog["id"],
                            dialog["talkRoleIdName"],
                            dialog["talkRoleName"],
                            dialog["talkTitle"],
                            dialog["talkContent"],
                            dialog["talkRoleType"],
                            dialog["type"],
                        ),
                        P(talk_collection_names, cls=[TextT.muted, TextT.xs])
                        if talk_collection_names
                        else None,
                    ),
                    Div(
                        A(UkIcon("circle-chevron-down"), cls=AT.primary),
                        DropDownNavContainer(*talk_collection_triggers),
                    ),
                )
            ),
        )
    return Ul(
        *results,
        cls=ListT.divider,
    )


serve()
