import functools
import json
import os

import polars as pl
from fasthtml.common import *
from monsterui.all import *

import alert
import home
import query_dialog

TALK_DATA_DIR = os.environ["TALK_DATA_DIR"]
CURR_VER = os.environ["CURR_VER"]
MAX_RESULTS = 1000
CACHE_MAX_AGE = 600
Langs = str_enum("Langs", *os.environ["LANGS"].split(","))

with open("localization.json") as f:
    UI = json.loads(f.read())

TALK_DATA = {}
for lang in Langs:
    talk_data_path = (
        f"{TALK_DATA_DIR}/GI_Talk_{lang}.parquet"
        if TALK_DATA_DIR.startswith("http")
        else Path(TALK_DATA_DIR) / f"GI_Talk_{lang}.parquet"
    )
    TALK_DATA[lang] = (
        pl.read_parquet(talk_data_path)
        .with_columns(
            talkRoleIdName=pl.when(pl.col.talkRoleType == "TALK_ROLE_PLAYER")
            .then(pl.lit(UI["SPEAKER"]["TALK_ROLE_PLAYER"][lang]))
            .when(pl.col.talkRoleType == "TALK_ROLE_MATE_AVATAR")
            .then(pl.lit(UI["SPEAKER"]["TALK_ROLE_MATE_AVATAR"][lang]))
            .when(
                pl.col.talkRoleIdName.str.contains(
                    r"^\#\{REALNAME\[ID\(1\)\|\w+\(\w+\)\]\}$"
                )
            )
            .then(pl.lit(UI["SPEAKER"]["REALNAME_ID_1"][lang]))
            .when(
                pl.col.talkRoleIdName.str.contains(
                    r"^\#\{REALNAME\[ID\(2\)\|\w+\(\w+\)\]\}$"
                )
            )
            .then(pl.lit(UI["SPEAKER"]["REALNAME_ID_2"][lang]))
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

app = FastHTML(hdrs=Theme.blue.headers())


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
        *home.build(lang, UI, list(Langs), CURR_VER),
        HttpHeader("Cache-Control", f"max-age={CACHE_MAX_AGE}"),
    )


@app.route("/{lang}/q/dialog_keyword", methods="GET")
@functools.lru_cache
def query_dialog_keyword(
    lang: Langs, speaker: str, content: str, new: bool = False, regex: bool = False
):
    if not speaker and not content:
        return (
            alert.build("error", UI["ALERT"]["EMPTY"][lang]),
            HttpHeader("Cache-Control", f"max-age={CACHE_MAX_AGE}"),
        )
    query_lf = TALK_DATA[lang]
    assert isinstance(query_lf, pl.LazyFrame)
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
        qeury_df = query_lf.collect()
    except pl.exceptions.ComputeError as e:
        return (
            alert.build("error", str(e)),
            HttpHeader("Cache-Control", f"max-age={CACHE_MAX_AGE}"),
        )
    assert isinstance(qeury_df, pl.DataFrame)
    result_len = len(qeury_df)
    if result_len == 0:
        return (
            alert.build("error", UI["ALERT"]["NONE"][lang]),
            HttpHeader("Cache-Control", f"max-age={CACHE_MAX_AGE}"),
        )
    elif result_len < MAX_RESULTS:
        return (
            alert.build("success", UI["ALERT"]["SUCCESS"][lang].format(result_len)),
            query_dialog.build_keyword_result(qeury_df.to_dicts(), lang, UI),
            HttpHeader("Cache-Control", f"max-age={CACHE_MAX_AGE}"),
        )
    else:
        return (
            alert.build(
                "warning",
                UI["ALERT"]["OVERFLOW"][lang].format(MAX_RESULTS, result_len),
            ),
            query_dialog.build_keyword_result(
                qeury_df.limit(MAX_RESULTS).to_dicts(), lang, UI
            ),
            HttpHeader("Cache-Control", f"max-age={CACHE_MAX_AGE}"),
        )


@app.route("/{lang}/q/dialog_collection", methods="GET")
@functools.lru_cache
def query_dialog_collection(
    lang: Langs,
    id: int | None = None,
    talkId: int | None = None,
    questId: int | None = None,
):
    query_lf = TALK_DATA[lang]
    assert isinstance(query_lf, pl.LazyFrame)
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
    return (
        query_dialog.build_collection_result(
            query_df.rows_by_key("talkId", named=True)
        ),
        HttpHeader("Cache-Control", f"max-age={CACHE_MAX_AGE}"),
    )


serve()
