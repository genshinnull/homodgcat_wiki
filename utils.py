import re

from fasthtml.common import *
from fasthtml.components import Rp, Rt, Ruby
from monsterui.all import *


def build_alert(
    level: str,
    msg: str,
):
    match level:
        case "error":
            alert_cls = AlertT.error
            alert_icon = "triangle-alert"
        case "success":
            alert_cls = AlertT.success
            alert_icon = "check"
        case "warning":
            alert_cls = AlertT.warning
            alert_icon = "triangle-alert"
    return Alert(
        DivHStacked(
            UkIcon(alert_icon),
            P(msg),
        ),
        cls=alert_cls,
    )


def convert_ruby(match: re.Match):
    return to_xml(Ruby(match.group(1), Rp("["), Rt(NotStr(match.group(2))), Rp("]")))


def convert_highlight(match: re.Match):
    return to_xml(Mark(match.group(1)))


def build_text(
    text: str,
):
    text = text.replace("\n", "<br>")
    for match in re.finditer(r"(.)\{RUBY\#\[\w\](.*?)\}", text):
        text = text.replace(match.group(0), convert_ruby(match))
    text = re.sub(r"<mark>(.*?)</mark>", convert_highlight, text)
    return P(NotStr(text), cls="text-wrap break-words")
