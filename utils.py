import re

from fasthtml.common import *
from fasthtml.components import Rp, Rt, Ruby
from monsterui.all import *


def build_alert(
    level: str,
    msg: str,
):
    cls = ["space-x-4", FlexT.center, "uk-alert"]
    match level:
        case "error":
            cls.append("uk-alert-destructive")
            icon = "triangle-alert"
        case "success":
            icon = "check"
        case "warning":
            icon = "triangle-alert"
    return DivHStacked(UkIcon(icon), P(msg), cls=cls)


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
