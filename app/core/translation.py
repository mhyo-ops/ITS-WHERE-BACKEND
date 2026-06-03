from __future__ import annotations

from argostranslate import package, translate

# Argos Translate generally provides translations via English as a pivot language.
# We install the direct packages that are available for fr<->en and en<->ar.
LANGUAGE_PAIRS = [
    ("fr", "en"),
    ("en", "ar"),
    ("ar", "en"),
    ("en", "fr"),
]


def download_packages() -> None:
    """
    Downloads translation models on first run.
    Safe to call on every startup — skips if already installed.
    Called once from main.py startup event.
    """
    package.update_package_index()
    available = package.get_available_packages()
    installed = [str(p) for p in package.get_installed_packages()]

    for from_code, to_code in LANGUAGE_PAIRS:
        pkg = next(
            (p for p in available if p.from_code == from_code and p.to_code == to_code),
            None,
        )
        if pkg is None:
            print(f"⚠️ No translation package available for {from_code}→{to_code}")
            continue
        if str(pkg) in installed:
            print(f"✅ Translation model {from_code}→{to_code} already installed")
            continue

        print(f"📦 Downloading translation model {from_code}→{to_code}...")
        package.install_from_path(pkg.download())
        print(f"✅ Installed {from_code}→{to_code}")


def _translate_direct(text: str, from_lang: str, to_lang: str) -> str | None:
    installed = translate.get_installed_languages()
    from_language = next((l for l in installed if l.code == from_lang), None)
    if not from_language:
        return None
    to_language = next((l for l in installed if l.code == to_lang), None)
    if not to_language:
        return None
    translation = from_language.get_translation(to_language)
    if not translation:
        return None
    return translation.translate(text)


def translate_text(text: str, from_lang: str, to_lang: str) -> str | None:
    """
    Translates text from from_lang to to_lang.
    Returns None if translation fails or pair not supported.
    Never raises — translation failure must not block event creation.
    """
    if from_lang == to_lang:
        return text

    try:
        direct = _translate_direct(text, from_lang, to_lang)
        if direct is not None:
            return direct

        # Some language pairs are only available via English as a pivot.
        if from_lang != "en" and to_lang != "en":
            pivot = _translate_direct(text, from_lang, "en")
            if pivot is None:
                return None
            return _translate_direct(pivot, "en", to_lang)

        return None
    except Exception:
        return None


def translate_event_fields(
    title: str | None,
    description: str | None,
    from_lang: str,
) -> dict[str, str]:
    """
    Given title and description in from_lang,
    returns dict with translations for the other language.

    If from_lang == "fr":
      returns {"title_ar": ..., "description_ar": ...}
    If from_lang == "ar":
      returns {"title_fr": ..., "description_fr": ...}
    If from_lang == "tzm":
      returns {} (no translation available, admin fills manually)

    Never returns None values in dict — omits key if translation failed.
    """
    result: dict[str, str] = {}
    if from_lang == "tzm":
        return result

    to_lang = "ar" if from_lang == "fr" else "fr"

    if title:
        translated_title = translate_text(title, from_lang, to_lang)
        if translated_title:
            result[f"title_{to_lang}"] = translated_title

    if description:
        translated_desc = translate_text(description, from_lang, to_lang)
        if translated_desc:
            result[f"description_{to_lang}"] = translated_desc

    return result
