import contextlib
import functools
import json
import logging
import os
import shutil

import fasthtml.core
import httpx
import polars as pl
from fasthtml.common import *
from monsterui.all import *

import alert
import home
import query_dialog
import query_text

pl.Config.set_engine_affinity("streaming")

Langs = str_enum("Langs", *os.environ["LANGS"].split(","))

globals = {}
ui = {}
talk_data = {}
text_data = {}


@contextlib.asynccontextmanager
async def lifespan(app):
    DATA_SRC = os.environ["DATA_SRC"]
    globals["CURR_VER"] = os.environ["CURR_VER"]
    CACHE_MAX_AGE = os.environ.get("CACHE_MAX_AGE", None)
    globals["cache_header"] = HttpHeader(
        "Cache-Control", f"max-age={CACHE_MAX_AGE}" if CACHE_MAX_AGE else "no-store"
    )
    globals["MAX_RESULTS"] = 1000
    globals["logger"] = logging.getLogger("uvicorn.info")
    with open("localization.json") as f:
        ui.update(json.loads(f.read()))
    data_dir = Path("data")
    shutil.rmtree(data_dir, ignore_errors=True)
    data_dir.mkdir()
    if (data_src_dir := Path(DATA_SRC)).is_dir():
        for lang in Langs:
            for data_type in ["Talk", "Text"]:
                shutil.copyfile(
                    data_src_dir / f"GI_{data_type}_{lang}.parquet",
                    data_dir / f"GI_{data_type}_{lang}.parquet",
                )
    else:
        for lang in Langs:
            for data_type in ["Talk", "Text"]:
                with open(data_dir / f"GI_{data_type}_{lang}.parquet", "wb") as f:
                    f.write(
                        httpx.get(f"{DATA_SRC}/GI_{data_type}_{lang}.parquet").content
                    )
    for lang in Langs:
        talk_data[lang] = pl.scan_parquet(data_dir / f"GI_Talk_{lang}.parquet")
        text_data[lang] = pl.scan_parquet(data_dir / f"GI_Text_{lang}.parquet")
    yield


app = FastHTML(
    default_hdrs=False,
    hdrs=[
        Theme.blue.headers(),
        fasthtml.core.htmxsrc,
        fasthtml.core.fhjsscr,
        fasthtml.charset,
    ],
    lifespan=lifespan,
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
        *home.build(lang, ui, list(Langs), globals["CURR_VER"]),
        globals["cache_header"],
    )


@app.route("/{lang}/q/dialog_keyword", methods="GET")
@functools.lru_cache
def query_dialog_keyword(
    lang: Langs, speaker: str, content: str, new: bool = False, regex: bool = False
):
    if not speaker and not content:
        return (alert.build("error", ui["ALERT_EMPTY"][lang]), globals["cache_header"])
    globals["logger"].info(f"Dialog query: {speaker=}, {content=}")
    query_lf = talk_data[lang]
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
    query_lf = query_lf.select(
        "id",
        "talkRoleIdName",
        "talkRoleName",
        "talkTitle",
        "talkContent",
        "talkRoleType",
        "talkId",
        "questId",
        "questIdName",
        "activityIdName",
        "chapterTitle",
        "chapterNum",
        "type",
        "talkIdExpandable",
        "questIdExpandable",
    )
    try:
        query_df = query_lf.collect()
    except pl.exceptions.ComputeError as e:
        return (alert.build("error", str(e)), globals["cache_header"])
    assert isinstance(query_df, pl.DataFrame)
    result_len = len(query_df)
    if result_len == 0:
        return (alert.build("error", ui["ALERT_NONE"][lang]), globals["cache_header"])
    elif result_len < globals["MAX_RESULTS"]:
        return (
            alert.build("success", ui["ALERT_SUCCESS"][lang].format(result_len)),
            query_dialog.build_keyword_result(query_df.to_dicts(), lang, ui),
            globals["cache_header"],
        )
    return (
        alert.build(
            "warning",
            ui["ALERT_OVERFLOW"][lang].format(globals["MAX_RESULTS"], result_len),
        ),
        query_dialog.build_keyword_result(
            query_df.limit(globals["MAX_RESULTS"]).to_dicts(), lang, ui
        ),
        globals["cache_header"],
    )


@app.route("/{lang}/q/dialog_collection", methods="GET")
@functools.lru_cache
def query_dialog_collection(
    lang: Langs,
    id: int | None = None,
    talkId: int | None = None,
    questId: int | None = None,
):
    query_lf = talk_data[lang]
    assert isinstance(query_lf, pl.LazyFrame)
    if id:
        query_lf = query_lf.filter(pl.col.id.is_between(id - 100, id + 100))
    elif talkId:
        query_lf = query_lf.filter(pl.col.talkId == talkId)
    elif questId:
        query_lf = query_lf.filter(pl.col.questId == questId)
    else:
        return Response(status_code=400)
    query_df = query_lf.select(
        "id",
        "talkRoleIdName",
        "talkRoleName",
        "talkTitle",
        "talkContent",
        "talkRoleType",
        "talkId",
        "type",
    ).collect()
    assert isinstance(query_df, pl.DataFrame)
    return (
        query_dialog.build_collection_result(
            query_df.rows_by_key("talkId", named=True)
        ),
        globals["cache_header"],
    )


@app.route("/{lang}/q/text", methods="GET")
@functools.lru_cache
def query_text_keyword(
    lang: Langs,
    key: str,
    value: str,
    lang_comp: str,
    no_textmap: bool = False,
    no_readable: bool = False,
    no_subtitle: bool = False,
    new: bool = False,
    regex: bool = False,
    ungrouped: bool = False,
):
    if (not key and not value) or (no_textmap and no_readable and no_subtitle):
        return (alert.build("error", ui["ALERT_EMPTY"][lang]), globals["cache_header"])
    globals["logger"].info(f"Text query: {key=}, {value=}")
    query_lf = text_data[lang]
    assert isinstance(query_lf, pl.LazyFrame)
    if new:
        query_lf = query_lf.filter(pl.col.v_from == pl.col.v_from.max())
    if key:
        if regex:
            query_lf = query_lf.filter(pl.col.key.str.contains(key))
        else:
            key = key.lower()
            query_lf = query_lf.filter(pl.col.keyLower.str.contains(key, literal=True))
    if value:
        if regex:
            query_lf = query_lf.filter(
                (pl.col.value.str.contains(value))
                | (pl.col.paged.str.contains(value))
                | (pl.col.book.str.contains(value))
                | (pl.col.letter.str.contains(value))
            )
        else:
            value = value.lower()
            query_lf = query_lf.filter(
                (pl.col.valueLower.str.contains(value, literal=True))
                | (pl.col.pagedLower.str.contains(value, literal=True))
                | (pl.col.bookLower.str.contains(value, literal=True))
                | (pl.col.letterLower.str.contains(value, literal=True))
            )
    if no_textmap:
        query_lf = query_lf.filter(pl.col.type != "TextMap")
    if no_readable:
        query_lf = query_lf.filter(pl.col.type != "Readable")
    if no_subtitle:
        query_lf = query_lf.filter(pl.col.type != "Subtitle")
    if lang_comp != "-":
        comp_df = text_data[lang_comp]
        if ungrouped:
            query_lf = (
                query_lf.join(comp_df, on=["type", "key"], how="left")
                .sort("value", "type")
                .select(
                    "type",
                    "key",
                    "value",
                    "value_right",
                    "paged",
                    "paged_right",
                    "book",
                    "book_right",
                    "letter",
                    "letter_right",
                    "k_from",
                    "kv_from",
                )
            )
        else:
            query_lf = (
                query_lf.join(comp_df, on=["type", "key"], how="left")
                .group_by(
                    "type",
                    "value",
                    "value_right",
                    "paged",
                    "paged_right",
                    "book",
                    "book_right",
                    "letter",
                    "letter_right",
                    "v_from",
                )
                .agg("key")
                .sort("value", "type")
                .select(
                    "type",
                    "key",
                    "value",
                    "value_right",
                    "paged",
                    "paged_right",
                    "book",
                    "book_right",
                    "letter",
                    "letter_right",
                    "v_from",
                )
            )
    else:
        if ungrouped:
            query_lf = query_lf.sort("value", "type").select(
                "type", "key", "value", "paged", "book", "letter", "k_from", "kv_from"
            )
        else:
            query_lf = (
                query_lf.group_by("type", "value", "paged", "book", "letter", "v_from")
                .agg("key")
                .sort("value", "type")
                .select("type", "key", "value", "paged", "book", "letter", "v_from")
            )
    try:
        query_df = query_lf.collect()
    except pl.exceptions.ComputeError as e:
        return (alert.build("error", str(e)), globals["cache_header"])
    assert isinstance(query_df, pl.DataFrame)
    result_len = len(query_df)
    if result_len == 0:
        return (alert.build("error", ui["ALERT_NONE"][lang]), globals["cache_header"])
    elif result_len < globals["MAX_RESULTS"]:
        return (
            alert.build("success", ui["ALERT_SUCCESS"][lang].format(result_len)),
            query_text.build_result(query_df.to_dicts(), lang, ui, lang_comp != "-"),
            globals["cache_header"],
        )
    else:
        return (
            alert.build(
                "warning",
                ui["ALERT_OVERFLOW"][lang].format(globals["MAX_RESULTS"], result_len),
            ),
            query_text.build_result(
                query_df.limit(globals["MAX_RESULTS"]).to_dicts(),
                lang,
                ui,
                lang_comp != "-",
            ),
            globals["cache_header"],
        )


serve(reload_includes=["*.py", "*.json"])
