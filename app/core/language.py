from __future__ import annotations

SUPPORTED_LANGUAGES = ["fr", "ar", "tzm"]
DEFAULT_LANGUAGE = "fr"


def get_preferred_language(lang: str | None) -> str:
    if lang in SUPPORTED_LANGUAGES:
        return lang
    return DEFAULT_LANGUAGE


def _choose_localized_value(event_dict: dict, base_field: str, lang: str) -> str | None:
    if lang == "fr":
        return event_dict.get(f"{base_field}_fr") or event_dict.get(base_field)
    if lang == "ar":
        return (
            event_dict.get(f"{base_field}_ar")
            or event_dict.get(f"{base_field}_fr")
            or event_dict.get(base_field)
        )
    if lang == "tzm":
        return (
            event_dict.get(f"{base_field}_tam")
            or event_dict.get(f"{base_field}_fr")
            or event_dict.get(base_field)
        )
    return event_dict.get(base_field)


def localize_event(event_dict: dict, lang: str) -> dict:
    title_value = _choose_localized_value(event_dict, "title", lang)
    description_value = _choose_localized_value(event_dict, "description", lang)

    raw_fields = [
        "title_fr",
        "title_ar",
        "title_tam",
        "description_fr",
        "description_ar",
        "description_tam",
    ]

    localized_event = {
        key: value
        for key, value in event_dict.items()
        if key not in raw_fields
    }

    if title_value is not None:
        localized_event["title"] = title_value
    if any(field in event_dict for field in ["description", "description_fr", "description_ar", "description_tam"]):
        localized_event["description"] = description_value

    return localized_event


def localize_event_list(events: list[dict], lang: str) -> list[dict]:
    return [localize_event(event, lang) for event in events]
