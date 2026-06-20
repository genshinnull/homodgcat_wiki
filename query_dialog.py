from fasthtml.common import *
from monsterui.all import *

import utils

HONEY_BASE_URL = "https://gensh.honeyhunterworld.com/{}_{}/?lang={}"
AMBER_BASE_URL = "https://gi.yatta.moe/{}/archive/quest/{}"


def build_base_dialog(
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
                talkRoleIdName = (
                    to_xml(
                        Span(
                            talkRoleIdName,
                            " ",
                            cls=[TextT.muted, TextT.normal, "whitespace-pre"],
                        )
                    )
                    + talkRoleName
                )
        else:
            talkRoleIdName = talkRoleName
    talk_speaker = []
    if talkRoleIdName:
        talk_speaker.append(
            P(NotStr(talkRoleIdName), cls=[TextT.bold, "text-wrap break-words"])
        )
    if talkTitle:
        talk_speaker.append(
            P(talkTitle, cls=[TextT.muted, TextT.xs, "text-wrap break-words"])
        )
    return (
        DivHStacked(
            P(id), P(type, cls=TextT.muted), cls=[TextT.xs, FlexT.wrap, "space-x-2"]
        ),
        DivHStacked(
            DivCentered(*talk_speaker, cls="") if talk_speaker else None,
            P(talkRoleType, cls=TextT.muted),
            cls="space-x-2",
        ),
        utils.build_text(talkContent) if talkContent else None,
    )


def build_collection_query_modal(
    lang: str,
    ui: dict,
    i: int,
    id: int | None = None,
    talkId: int | None = None,
    questId: int | None = None,
):
    if id:
        suffix = "-id"
        id = max(id - id % 100 - 100, 0)
        link_title = ui["RESULT_DIALOG_EXPAND_ID"][lang] + f" (id={id}-{id + 299})"
        hx_vals = {"id": id}
        modal_title = f"IDs {id}-{id + 299}"
    elif talkId:
        suffix = "-talkId"
        link_title = ui["RESULT_DIALOG_EXPAND_TALK"][lang]
        if talkId > 0:
            link_title += f" (talkId={talkId})"
        hx_vals = {"talkId": talkId}
        modal_title = f"TalkID {talkId}"
    elif questId:
        suffix = "-questId"
        link_title = ui["RESULT_DIALOG_EXPAND_QUEST"][lang] + f" (questId={questId})"
        hx_vals = {"questId": questId}
        modal_title = f"QuestID {questId}"
    modal = f"modal-{i}{suffix}"
    replace = f"replace-{i}{suffix}"
    return Li(
        A(
            link_title,
            data_uk_toggle=f"#{modal}",
            hx_get=f"/{lang}/q/dialog_collection",
            hx_vals=hx_vals,
            hx_target=f"#{replace}",
            hx_indicator="#q-dialog-collection-loading",
        ),
        Modal(
            ModalTitle(modal_title),
            DivCentered(
                data_uk_spinner="",
                id="q-dialog-collection-loading",
                cls=["loading", "htmx-indicator"],
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


def build_collection_query_external(
    lang: str,
    ui: dict,
    source: str,
    questId: int | None = None,
    chapterId: int | None = None,
    activityId: int | None = None,
):
    if questId:
        if source == "Project Amber":
            url = AMBER_BASE_URL.format(lang.lower(), questId)
        elif source == "Honey Impact":
            url = HONEY_BASE_URL.format("q", questId, lang)
        link_title = ui["RESULT_DIALOG_EXTERNAL_QUEST"][lang].format(source)
    elif chapterId:
        if source == "Project Amber":
            url = AMBER_BASE_URL.format(lang.lower(), chapterId)
        elif source == "Honey Impact":
            url = HONEY_BASE_URL.format("ch", chapterId, lang)
        link_title = ui["RESULT_DIALOG_EXTERNAL_CHAPTER"][lang].format(source)
    elif activityId:
        if source == "Honey Impact":
            url = HONEY_BASE_URL.format("e", activityId, lang)
        link_title = ui["RESULT_DIALOG_EXTERNAL_ACTIVITY"][lang].format(source)
    return Li(
        A(
            Span(UkIcon("external-link"), cls=AT.primary),
            link_title,
            href=url,
            target="_blank",
        )
    )


def build_keyword_result(dialogs: list[dict], lang: str, ui: dict):
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
            build_collection_query_modal(lang, ui, i, id=dialog["id"])
        ]
        if dialog["talkIdExpandable"]:
            talk_collection_triggers.append(
                build_collection_query_modal(lang, ui, i, talkId=dialog["talkId"])
            )
        if dialog["questId"]:
            if dialog["questIdExpandable"]:
                talk_collection_triggers.append(
                    build_collection_query_modal(lang, ui, i, questId=dialog["questId"])
                )
            talk_collection_triggers.append(
                build_collection_query_external(
                    lang, ui, source="Honey Impact", questId=dialog["questId"]
                )
            )
            if not dialog["chapterId"]:
                talk_collection_triggers.append(
                    build_collection_query_external(
                        lang, ui, source="Project Amber", questId=dialog["questId"]
                    )
                )
        if dialog["chapterId"]:
            talk_collection_triggers.append(
                build_collection_query_external(
                    lang, ui, source="Honey Impact", chapterId=dialog["chapterId"]
                )
            )
            talk_collection_triggers.append(
                build_collection_query_external(
                    lang, ui, source="Project Amber", chapterId=dialog["chapterId"]
                )
            )
        if dialog["activityId"]:
            talk_collection_triggers.append(
                build_collection_query_external(
                    lang, ui, source="Honey Impact", activityId=dialog["activityId"]
                )
            )
        results.append(
            Li(
                DivFullySpaced(
                    Div(
                        *build_base_dialog(
                            dialog["id"],
                            dialog["talkRoleIdName"],
                            dialog["talkRoleName"],
                            dialog["talkTitle"],
                            dialog["talkContent"],
                            dialog["talkRoleType"],
                            dialog["type"],
                        ),
                        P(
                            talk_collection_names,
                            cls=[TextT.muted, TextT.xs, "text-wrap break-words"],
                        )
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


def build_collection_result(talks: dict):
    results = []
    for talk in list(talks.values()):
        talk_dialogs = []
        for dialog in talk:
            talk_dialogs.append(
                Li(
                    *build_base_dialog(
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
    return Ul(
        *results,
        cls=ListT.striped,
    )
