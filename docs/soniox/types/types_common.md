---
title: soniox.types.common
description: Description for common
keywords: annotations, BaseModel, ConfigDict, Token
---


---

## Class `Token`

Token metadata emitted during realtime streaming transcriptions.

### Attributes

- **model_config**: 

- **text**: The transcribed text.

- **start_ms**: Start time in milliseconds relative to audio start.

- **end_ms**: End time in milliseconds relative to audio start.

- **confidence**: Confidence score (0.0 to 1.0).

- **is_final**: Whether this is a finalized token.

- **speaker**: Speaker identifier (if diarization enabled).

- **translation_status**: Translation status of this token.

- **language**: Detected language code (if language identification enabled).

- **source_language**: Source language for translated tokens.