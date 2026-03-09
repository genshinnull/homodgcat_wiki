from fasthtml.common import *
from monsterui.all import *


def build(
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
