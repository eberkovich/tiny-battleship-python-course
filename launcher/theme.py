from __future__ import annotations

from dataclasses import dataclass


Color = tuple[int, int, int]

DARK_THEME_NAME = "dark"
LIGHT_THEME_NAME = "light"
DEFAULT_THEME_NAME = DARK_THEME_NAME


@dataclass(frozen=True)
class ThemePalette:
    background: Color
    panel: Color
    card: Color
    card_active: Color
    content_card: Color
    note_background: Color
    recap_background: Color
    recap_border: Color
    code_background: Color
    code_text: Color
    text: Color
    muted: Color
    accent: Color
    button: Color
    button_hover: Color
    button_disabled: Color
    button_text: Color
    success: Color
    error: Color
    gold: Color
    article: Color
    question: Color
    project: Color
    summary: Color
    progress_idle: Color


DARK_THEME = ThemePalette(
    background=(15, 23, 39),
    panel=(25, 37, 59),
    card=(34, 49, 75),
    card_active=(43, 74, 111),
    content_card=(40, 59, 88),
    note_background=(29, 43, 65),
    recap_background=(31, 52, 72),
    recap_border=(72, 151, 163),
    code_background=(17, 29, 49),
    code_text=(205, 231, 246),
    text=(239, 245, 255),
    muted=(174, 191, 211),
    accent=(63, 190, 181),
    button=(48, 105, 152),
    button_hover=(61, 129, 184),
    button_disabled=(67, 77, 93),
    button_text=(239, 245, 255),
    success=(67, 180, 113),
    error=(224, 102, 102),
    gold=(238, 190, 72),
    article=(91, 155, 213),
    question=(165, 122, 214),
    project=(234, 143, 74),
    summary=(164, 139, 219),
    progress_idle=(70, 84, 105),
)

LIGHT_THEME = ThemePalette(
    background=(220, 233, 239),
    panel=(216, 231, 239),
    card=(249, 252, 253),
    card_active=(213, 237, 243),
    content_card=(250, 253, 254),
    note_background=(238, 245, 247),
    recap_background=(230, 244, 247),
    recap_border=(69, 145, 157),
    code_background=(24, 39, 58),
    code_text=(218, 239, 248),
    text=(27, 43, 58),
    muted=(93, 111, 126),
    accent=(22, 145, 142),
    button=(42, 116, 166),
    button_hover=(52, 136, 190),
    button_disabled=(155, 166, 174),
    button_text=(249, 252, 255),
    success=(38, 140, 80),
    error=(190, 68, 68),
    gold=(190, 132, 14),
    article=(45, 111, 174),
    question=(126, 78, 184),
    project=(194, 91, 31),
    summary=(112, 78, 178),
    progress_idle=(92, 112, 126),
)

THEMES = {
    DARK_THEME_NAME: DARK_THEME,
    LIGHT_THEME_NAME: LIGHT_THEME,
}
