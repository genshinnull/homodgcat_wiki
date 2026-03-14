import re

from fasthtml.common import *
from monsterui.all import *


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


def build_collection_query_trigger(
    lang: str,
    ui: dict,
    i: int,
    id: int | None = None,
    talkId: int | None = None,
    questId: int | None = None,
):
    if id:
        suffix = "-id"
        link_title = ui["RESULT_DIALOG_EXPAND_ID"][lang] + f" (id={id}±100)"
        hx_vals = {"id": id}
        modal_title = f"IDs {id - 100} - {id + 100}"
    elif talkId:
        suffix = "-talkId"
        link_title = ui["RESULT_DIALOG_EXPAND_TALK"][lang] + f" (talkId={talkId})"
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
                Loading(
                    htmx_indicator=True,
                    id="q-dialog-collection-loading",
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
            build_collection_query_trigger(lang, ui, i, id=dialog["id"])
        ]
        if talkId := dialog["talkId"]:
            talk_collection_triggers.append(
                build_collection_query_trigger(lang, ui, i, talkId=talkId)
            )
        if questId := dialog["questId"]:
            talk_collection_triggers.append(
                build_collection_query_trigger(lang, ui, i, questId=questId)
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
