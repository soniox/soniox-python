from __future__ import annotations

import os

from soniox import SonioxClient
from soniox.types.api import Model


def _format_model(model: Model) -> str:
    target = model.translation_targets
    has_translation = bool(target or model.one_way_translation or model.two_way_translation)
    languages = ", ".join(lang.code for lang in model.languages[:3])
    translation_note = "supports translation" if has_translation else "no translation"
    return f"{model.id} ({model.transcription_mode}, {translation_note}, languages={languages}...)"


def main() -> None:
    api_key = os.environ.get("SONIOX_API_KEY")
    if not api_key:
        raise SystemExit("Please set SONIOX_API_KEY to run the models example.")

    with SonioxClient(api_key=api_key) as client:
        models_response = client.models.list()
        print(f"Discovered {len(models_response.models)} models:")
        for model in models_response.models[:5]:
            print(f" - {_format_model(model)}")

        first_model = models_response.models[0]
        if first_model.translation_targets:
            print(f"\nTranslation targets for {first_model.id}:")
            for target in first_model.translation_targets:
                print(f"  - {target.target_language} (from {target.source_languages})")


if __name__ == "__main__":
    main()
