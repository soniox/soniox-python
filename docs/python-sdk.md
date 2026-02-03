# API Reference

* [errors](#errors)
  * [SonioxError](#errors.SonioxError)
  * [SonioxValidationError](#errors.SonioxValidationError)
  * [SonioxAPIError](#errors.SonioxAPIError)
    * [from\_response](#errors.SonioxAPIError.from_response)
  * [SonioxAuthenticationError](#errors.SonioxAuthenticationError)
  * [SonioxInvalidRequestError](#errors.SonioxInvalidRequestError)
  * [SonioxNotFoundError](#errors.SonioxNotFoundError)
  * [SonioxConflictError](#errors.SonioxConflictError)
  * [SonioxRateLimitError](#errors.SonioxRateLimitError)
  * [SonioxServerError](#errors.SonioxServerError)
  * [InvalidWebhookSignatureError](#errors.InvalidWebhookSignatureError)
  * [SonioxRealtimeError](#errors.SonioxRealtimeError)
* [\_\_init\_\_](#__init__)
* [utils](#utils)
  * [stream\_audio](#utils.stream_audio)
  * [stream\_audio\_async](#utils.stream_audio_async)
  * [throttle\_audio](#utils.throttle_audio)
  * [throttle\_audio\_async](#utils.throttle_audio_async)
  * [render\_tokens](#utils.render_tokens)
  * [start\_audio\_thread](#utils.start_audio_thread)
  * [start\_keep\_alive\_thread](#utils.start_keep_alive_thread)
  * [keep\_alive\_async](#utils.keep_alive_async)
* [client](#client)
  * [SonioxClient](#client.SonioxClient)
    * [request](#client.SonioxClient.request)
    * [close](#client.SonioxClient.close)
  * [AsyncSonioxClient](#client.AsyncSonioxClient)
    * [request](#client.AsyncSonioxClient.request)
    * [aclose](#client.AsyncSonioxClient.aclose)
* [types](#types)
* [types.common](#types.common)
  * [Token](#types.common.Token)
* [types.webhooks](#types.webhooks)
  * [WebhookAuthConfig](#types.webhooks.WebhookAuthConfig)
  * [WebhookEvent](#types.webhooks.WebhookEvent)
* [types.realtime](#types.realtime)
  * [RealtimeEvent](#types.realtime.RealtimeEvent)
  * [RealtimeSTTConfig](#types.realtime.RealtimeSTTConfig)
  * [RealtimeControlType](#types.realtime.RealtimeControlType)
  * [RealtimeSessionOpenPayload](#types.realtime.RealtimeSessionOpenPayload)
  * [RealtimeSessionClosePayload](#types.realtime.RealtimeSessionClosePayload)
  * [RealtimeSessionFinishedPayload](#types.realtime.RealtimeSessionFinishedPayload)
  * [RealtimeSessionErrorPayload](#types.realtime.RealtimeSessionErrorPayload)
* [types.api](#types.api)
  * [ApiErrorValidationError](#types.api.ApiErrorValidationError)
  * [ApiError](#types.api.ApiError)
  * [GetFilesPayload](#types.api.GetFilesPayload)
  * [File](#types.api.File)
  * [GetFilesResponse](#types.api.GetFilesResponse)
  * [UploadFilePayload](#types.api.UploadFilePayload)
  * [GetTranscriptionsPayload](#types.api.GetTranscriptionsPayload)
  * [StructuredContextGeneralItem](#types.api.StructuredContextGeneralItem)
  * [StructuredContextTranslationTerm](#types.api.StructuredContextTranslationTerm)
  * [StructuredContext](#types.api.StructuredContext)
  * [TranslationConfig](#types.api.TranslationConfig)
  * [CreateTranscriptionPayload](#types.api.CreateTranscriptionPayload)
  * [CreateTranscriptionConfig](#types.api.CreateTranscriptionConfig)
  * [CreateTemporaryApiKeyPayload](#types.api.CreateTemporaryApiKeyPayload)
  * [CreateTemporaryApiKeyResponse](#types.api.CreateTemporaryApiKeyResponse)
  * [Language](#types.api.Language)
  * [TranslationTarget](#types.api.TranslationTarget)
  * [Model](#types.api.Model)
  * [GetModelsResponse](#types.api.GetModelsResponse)
  * [TranscriptionTranscript](#types.api.TranscriptionTranscript)
  * [Transcription](#types.api.Transcription)
  * [GetTranscriptionsResponse](#types.api.GetTranscriptionsResponse)
* [api](#api)
* [api.webhooks](#api.webhooks)
  * [SonioxWebhooksAPI](#api.webhooks.SonioxWebhooksAPI)
    * [verify\_signature](#api.webhooks.SonioxWebhooksAPI.verify_signature)
    * [unwrap](#api.webhooks.SonioxWebhooksAPI.unwrap)
    * [webhook\_payload](#api.webhooks.SonioxWebhooksAPI.webhook_payload)
* [api.files](#api.files)
  * [FilesAPI](#api.files.FilesAPI)
    * [list](#api.files.FilesAPI.list)
    * [get](#api.files.FilesAPI.get)
    * [get\_or\_none](#api.files.FilesAPI.get_or_none)
    * [delete](#api.files.FilesAPI.delete)
    * [delete\_if\_exists](#api.files.FilesAPI.delete_if_exists)
    * [upload](#api.files.FilesAPI.upload)
    * [delete\_all](#api.files.FilesAPI.delete_all)
* [api.async\_files](#api.async_files)
  * [AsyncFilesAPI](#api.async_files.AsyncFilesAPI)
    * [list](#api.async_files.AsyncFilesAPI.list)
    * [get](#api.async_files.AsyncFilesAPI.get)
    * [get\_or\_none](#api.async_files.AsyncFilesAPI.get_or_none)
    * [delete](#api.async_files.AsyncFilesAPI.delete)
    * [delete\_if\_exists](#api.async_files.AsyncFilesAPI.delete_if_exists)
    * [upload](#api.async_files.AsyncFilesAPI.upload)
    * [delete\_all](#api.async_files.AsyncFilesAPI.delete_all)
* [api.auth](#api.auth)
  * [AuthAPI](#api.auth.AuthAPI)
    * [create\_temporary\_api\_key](#api.auth.AuthAPI.create_temporary_api_key)
* [api.models](#api.models)
  * [ModelsAPI](#api.models.ModelsAPI)
    * [list](#api.models.ModelsAPI.list)
* [api.async\_webhooks](#api.async_webhooks)
* [api.\_utils](#api._utils)
  * [normalize\_file](#api._utils.normalize_file)
* [api.async\_auth](#api.async_auth)
  * [AsyncAuthAPI](#api.async_auth.AsyncAuthAPI)
    * [create\_temporary\_api\_key](#api.async_auth.AsyncAuthAPI.create_temporary_api_key)
* [api.async\_transcriptions](#api.async_transcriptions)
  * [AsyncTranscriptionsAPI](#api.async_transcriptions.AsyncTranscriptionsAPI)
    * [list](#api.async_transcriptions.AsyncTranscriptionsAPI.list)
    * [delete\_all](#api.async_transcriptions.AsyncTranscriptionsAPI.delete_all)
    * [create](#api.async_transcriptions.AsyncTranscriptionsAPI.create)
    * [get](#api.async_transcriptions.AsyncTranscriptionsAPI.get)
    * [get\_or\_none](#api.async_transcriptions.AsyncTranscriptionsAPI.get_or_none)
    * [delete](#api.async_transcriptions.AsyncTranscriptionsAPI.delete)
    * [delete\_if\_exists](#api.async_transcriptions.AsyncTranscriptionsAPI.delete_if_exists)
    * [destroy](#api.async_transcriptions.AsyncTranscriptionsAPI.destroy)
    * [get\_transcript](#api.async_transcriptions.AsyncTranscriptionsAPI.get_transcript)
    * [wait](#api.async_transcriptions.AsyncTranscriptionsAPI.wait)
    * [transcribe\_from\_url](#api.async_transcriptions.AsyncTranscriptionsAPI.transcribe_from_url)
    * [transcribe\_from\_file\_id](#api.async_transcriptions.AsyncTranscriptionsAPI.transcribe_from_file_id)
    * [transcribe\_from\_file](#api.async_transcriptions.AsyncTranscriptionsAPI.transcribe_from_file)
    * [transcribe](#api.async_transcriptions.AsyncTranscriptionsAPI.transcribe)
    * [transcribe\_file\_with\_webhook](#api.async_transcriptions.AsyncTranscriptionsAPI.transcribe_file_with_webhook)
    * [transcribe\_and\_wait](#api.async_transcriptions.AsyncTranscriptionsAPI.transcribe_and_wait)
    * [transcribe\_and\_wait\_with\_tokens](#api.async_transcriptions.AsyncTranscriptionsAPI.transcribe_and_wait_with_tokens)
* [api.async\_models](#api.async_models)
  * [AsyncModelsAPI](#api.async_models.AsyncModelsAPI)
    * [list](#api.async_models.AsyncModelsAPI.list)
* [api.transcriptions](#api.transcriptions)
  * [TranscriptionsAPI](#api.transcriptions.TranscriptionsAPI)
    * [list](#api.transcriptions.TranscriptionsAPI.list)
    * [delete\_all](#api.transcriptions.TranscriptionsAPI.delete_all)
    * [create](#api.transcriptions.TranscriptionsAPI.create)
    * [get](#api.transcriptions.TranscriptionsAPI.get)
    * [get\_or\_none](#api.transcriptions.TranscriptionsAPI.get_or_none)
    * [delete](#api.transcriptions.TranscriptionsAPI.delete)
    * [delete\_if\_exists](#api.transcriptions.TranscriptionsAPI.delete_if_exists)
    * [destroy](#api.transcriptions.TranscriptionsAPI.destroy)
    * [get\_transcript](#api.transcriptions.TranscriptionsAPI.get_transcript)
    * [wait](#api.transcriptions.TranscriptionsAPI.wait)
    * [transcribe\_from\_url](#api.transcriptions.TranscriptionsAPI.transcribe_from_url)
    * [transcribe\_from\_file\_id](#api.transcriptions.TranscriptionsAPI.transcribe_from_file_id)
    * [transcribe\_from\_file](#api.transcriptions.TranscriptionsAPI.transcribe_from_file)
    * [transcribe](#api.transcriptions.TranscriptionsAPI.transcribe)
    * [transcribe\_file\_with\_webhook](#api.transcriptions.TranscriptionsAPI.transcribe_file_with_webhook)
    * [transcribe\_and\_wait](#api.transcriptions.TranscriptionsAPI.transcribe_and_wait)
    * [transcribe\_and\_wait\_with\_tokens](#api.transcriptions.TranscriptionsAPI.transcribe_and_wait_with_tokens)
* [realtime](#realtime)
  * [AsyncRealtimeAPI](#realtime.AsyncRealtimeAPI)
  * [RealtimeAPI](#realtime.RealtimeAPI)
* [realtime.stt](#realtime.stt)
  * [RealtimeSTTSession](#realtime.stt.RealtimeSTTSession)
    * [\_\_init\_\_](#realtime.stt.RealtimeSTTSession.__init__)
    * [config](#realtime.stt.RealtimeSTTSession.config)
    * [\_\_enter\_\_](#realtime.stt.RealtimeSTTSession.__enter__)
    * [\_\_exit\_\_](#realtime.stt.RealtimeSTTSession.__exit__)
    * [close](#realtime.stt.RealtimeSTTSession.close)
    * [send\_byte\_chunk](#realtime.stt.RealtimeSTTSession.send_byte_chunk)
    * [send\_bytes](#realtime.stt.RealtimeSTTSession.send_bytes)
    * [send\_control\_message](#realtime.stt.RealtimeSTTSession.send_control_message)
    * [send\_finish](#realtime.stt.RealtimeSTTSession.send_finish)
    * [send\_keep\_alive](#realtime.stt.RealtimeSTTSession.send_keep_alive)
    * [send\_finalize](#realtime.stt.RealtimeSTTSession.send_finalize)
    * [recv\_bytes](#realtime.stt.RealtimeSTTSession.recv_bytes)
    * [parse\_event](#realtime.stt.RealtimeSTTSession.parse_event)
    * [last\_message](#realtime.stt.RealtimeSTTSession.last_message)
    * [receive\_event](#realtime.stt.RealtimeSTTSession.receive_event)
    * [receive\_events](#realtime.stt.RealtimeSTTSession.receive_events)
    * [handle\_events](#realtime.stt.RealtimeSTTSession.handle_events)
  * [RealtimeSTTClient](#realtime.stt.RealtimeSTTClient)
    * [\_\_init\_\_](#realtime.stt.RealtimeSTTClient.__init__)
    * [connect](#realtime.stt.RealtimeSTTClient.connect)
* [realtime.async\_stt](#realtime.async_stt)
  * [AsyncRealtimeSTTSession](#realtime.async_stt.AsyncRealtimeSTTSession)
    * [\_\_init\_\_](#realtime.async_stt.AsyncRealtimeSTTSession.__init__)
    * [config](#realtime.async_stt.AsyncRealtimeSTTSession.config)
    * [\_\_aenter\_\_](#realtime.async_stt.AsyncRealtimeSTTSession.__aenter__)
    * [\_\_aexit\_\_](#realtime.async_stt.AsyncRealtimeSTTSession.__aexit__)
    * [close](#realtime.async_stt.AsyncRealtimeSTTSession.close)
    * [send\_byte\_chunk](#realtime.async_stt.AsyncRealtimeSTTSession.send_byte_chunk)
    * [send\_bytes](#realtime.async_stt.AsyncRealtimeSTTSession.send_bytes)
    * [send\_control\_message](#realtime.async_stt.AsyncRealtimeSTTSession.send_control_message)
    * [send\_finish](#realtime.async_stt.AsyncRealtimeSTTSession.send_finish)
    * [send\_keep\_alive](#realtime.async_stt.AsyncRealtimeSTTSession.send_keep_alive)
    * [send\_finalize](#realtime.async_stt.AsyncRealtimeSTTSession.send_finalize)
    * [recv\_bytes](#realtime.async_stt.AsyncRealtimeSTTSession.recv_bytes)
    * [parse\_event](#realtime.async_stt.AsyncRealtimeSTTSession.parse_event)
    * [last\_message](#realtime.async_stt.AsyncRealtimeSTTSession.last_message)
    * [receive\_event](#realtime.async_stt.AsyncRealtimeSTTSession.receive_event)
    * [receive\_events](#realtime.async_stt.AsyncRealtimeSTTSession.receive_events)
    * [handle\_events](#realtime.async_stt.AsyncRealtimeSTTSession.handle_events)
  * [AsyncRealtimeSTTClient](#realtime.async_stt.AsyncRealtimeSTTClient)
    * [\_\_init\_\_](#realtime.async_stt.AsyncRealtimeSTTClient.__init__)
    * [connect](#realtime.async_stt.AsyncRealtimeSTTClient.connect)

<a id="errors"></a>

# errors

<a id="errors.SonioxError"></a>

## SonioxError Objects

```python
class SonioxError(Exception)
```

Base exception for the SDK.

<a id="errors.SonioxValidationError"></a>

## SonioxValidationError Objects

```python
class SonioxValidationError(SonioxError)
```

Raised when Pydantic input validation fails on the client side.

<a id="errors.SonioxAPIError"></a>

## SonioxAPIError Objects

```python
class SonioxAPIError(SonioxError)
```

Raised when the Soniox API replies with a non-2xx payload.

<a id="errors.SonioxAPIError.from_response"></a>

#### from\_response

```python
@classmethod
def from_response(cls, response: httpx.Response) -> SonioxAPIError
```

Parse an `httpx.Response` into a richer SDK error.

<a id="errors.SonioxAuthenticationError"></a>

## SonioxAuthenticationError Objects

```python
class SonioxAuthenticationError(SonioxAPIError)
```

Authentication failures (`401`/`403`).

<a id="errors.SonioxInvalidRequestError"></a>

## SonioxInvalidRequestError Objects

```python
class SonioxInvalidRequestError(SonioxAPIError)
```

Invalid request payloads (`400`).

<a id="errors.SonioxNotFoundError"></a>

## SonioxNotFoundError Objects

```python
class SonioxNotFoundError(SonioxAPIError)
```

Resource not found.

<a id="errors.SonioxConflictError"></a>

## SonioxConflictError Objects

```python
class SonioxConflictError(SonioxAPIError)
```

Conflict or invalid state (e.g., delete while processing).

<a id="errors.SonioxRateLimitError"></a>

## SonioxRateLimitError Objects

```python
class SonioxRateLimitError(SonioxAPIError)
```

Rate limit (429).

<a id="errors.SonioxServerError"></a>

## SonioxServerError Objects

```python
class SonioxServerError(SonioxAPIError)
```

5xx responses.

<a id="errors.InvalidWebhookSignatureError"></a>

## InvalidWebhookSignatureError Objects

```python
class InvalidWebhookSignatureError(SonioxError)
```

Raised when a webhook signature cannot be validated.

<a id="errors.SonioxRealtimeError"></a>

## SonioxRealtimeError Objects

```python
class SonioxRealtimeError(SonioxError)
```

Errors raised by realtime workflows.

<a id="__init__"></a>

# \_\_init\_\_

<a id="utils"></a>

# utils

<a id="utils.stream_audio"></a>

#### stream\_audio

```python
def stream_audio(file: Path | str | BinaryIO | bytes,
                 *,
                 chunk_size_bytes: int = 4 * 1024) -> Iterator[bytes]
```

Yield fixed-size chunks from an audio source.

Supports bytes, file paths, or binary streams and slices them into
`chunk_size_bytes` blocks for realtime transmission.

<a id="utils.stream_audio_async"></a>

#### stream\_audio\_async

```python
async def stream_audio_async(
        file: Path | str | BinaryIO | bytes,
        *,
        chunk_size_bytes: int = 4 * 1024) -> AsyncIterator[bytes]
```

Asynchronously yield fixed-size chunks from an audio source.

Mirrors `stream_audio` but produces an async iterator for later consumption.

<a id="utils.throttle_audio"></a>

#### throttle\_audio

```python
def throttle_audio(file: Path | str | BinaryIO | bytes,
                   *,
                   chunk_size_bytes: int = 4096,
                   delay_seconds: float = 0.0) -> Iterator[bytes]
```

Yield audio chunks at a regulated pace, optionally sleeping between yields.

<a id="utils.throttle_audio_async"></a>

#### throttle\_audio\_async

```python
async def throttle_audio_async(
        file: Path | str | BinaryIO | bytes,
        *,
        chunk_size_bytes: int = 32 * 1024,
        delay_seconds: float = 0.0) -> AsyncIterator[bytes]
```

Async counterpart of `throttle_audio`, yielding chunks with optional delay.

<a id="utils.render_tokens"></a>

#### render\_tokens

```python
def render_tokens(final_tokens: list[Token],
                  non_final_tokens: list[Token]) -> str
```

Build a human-friendly transcript from token metadata.

<a id="utils.start_audio_thread"></a>

#### start\_audio\_thread

```python
def start_audio_thread(session: RealtimeSTTSession,
                       chunks: bytes | Iterator[bytes],
                       *,
                       name: str | None = None,
                       daemon: bool = True) -> threading.Thread
```

Stream audio into the session on a background thread.

<a id="utils.start_keep_alive_thread"></a>

#### start\_keep\_alive\_thread

```python
def start_keep_alive_thread(
        session: RealtimeSTTSession,
        *,
        interval_seconds: float = 10.0,
        name: str | None = None,
        daemon: bool = True) -> tuple[threading.Thread, threading.Event]
```

Start a background thread that periodically sends keep-alives to the session.

**Returns**:

  A tuple of (thread, stop_event). Setting `stop_event` will stop the loop.

<a id="utils.keep_alive_async"></a>

#### keep\_alive\_async

```python
async def keep_alive_async(session: AsyncRealtimeSTTSession,
                           *,
                           interval_seconds: float = 10.0,
                           stop_event: asyncio.Event | None = None) -> None
```

Async helper that repeatedly sends keep-alive messages until told to stop.

<a id="client"></a>

# client

<a id="client.SonioxClient"></a>

## SonioxClient Objects

```python
class SonioxClient(_BaseSonioxClient)
```

Synchronous Soniox REST client exposing API namespaces via httpx.

<a id="client.SonioxClient.request"></a>

#### request

```python
def request(method: str,
            path: str,
            *,
            params: Mapping[str, Any] | None = None,
            json: Any | None = None,
            data: Mapping[str, Any] | None = None,
            files: Mapping[str, Any] | None = None) -> httpx.Response
```

Perform a request against the configured Soniox REST endpoint.

<a id="client.SonioxClient.close"></a>

#### close

```python
def close() -> None
```

Close the underlying HTTP transport.

<a id="client.AsyncSonioxClient"></a>

## AsyncSonioxClient Objects

```python
class AsyncSonioxClient(_BaseSonioxClient)
```

Asynchronous Soniox REST client exposing HTTP and realtime helpers.

<a id="client.AsyncSonioxClient.request"></a>

#### request

```python
async def request(method: str,
                  path: str,
                  *,
                  params: Mapping[str, Any] | None = None,
                  json: Any | None = None,
                  data: Mapping[str, Any] | None = None,
                  files: Mapping[str, Any] | None = None) -> httpx.Response
```

Perform a request against the configured Soniox REST endpoint.

<a id="client.AsyncSonioxClient.aclose"></a>

#### aclose

```python
async def aclose() -> None
```

Close any outstanding async HTTP connections.

<a id="types"></a>

# types

<a id="types.common"></a>

# types.common

<a id="types.common.Token"></a>

## Token Objects

```python
class Token(BaseModel)
```

Token metadata emitted during realtime streaming transcriptions.

<a id="types.webhooks"></a>

# types.webhooks

<a id="types.webhooks.WebhookAuthConfig"></a>

## WebhookAuthConfig Objects

```python
class WebhookAuthConfig(BaseModel)
```

Configuration for webhook authentication headers.

<a id="types.webhooks.WebhookEvent"></a>

## WebhookEvent Objects

```python
class WebhookEvent(BaseModel)
```

Basic webhook event metadata.

<a id="types.realtime"></a>

# types.realtime

<a id="types.realtime.RealtimeEvent"></a>

## RealtimeEvent Objects

```python
class RealtimeEvent(BaseModel)
```

Event payload received from the realtime STT websocket.

<a id="types.realtime.RealtimeSTTConfig"></a>

## RealtimeSTTConfig Objects

```python
class RealtimeSTTConfig(BaseModel)
```

Configuration for initiating a realtime transcription session.

<a id="types.realtime.RealtimeControlType"></a>

## RealtimeControlType Objects

```python
class RealtimeControlType(str, Enum)
```

Control messages that can be sent over a realtime session.

<a id="types.realtime.RealtimeSessionOpenPayload"></a>

## RealtimeSessionOpenPayload Objects

```python
class RealtimeSessionOpenPayload(BaseModel)
```

Event emitted when a realtime websocket session opens.

<a id="types.realtime.RealtimeSessionClosePayload"></a>

## RealtimeSessionClosePayload Objects

```python
class RealtimeSessionClosePayload(BaseModel)
```

Event emitted when a realtime websocket session closes.

<a id="types.realtime.RealtimeSessionFinishedPayload"></a>

## RealtimeSessionFinishedPayload Objects

```python
class RealtimeSessionFinishedPayload(BaseModel)
```

Event emitted when a realtime session finishes processing.

<a id="types.realtime.RealtimeSessionErrorPayload"></a>

## RealtimeSessionErrorPayload Objects

```python
class RealtimeSessionErrorPayload(BaseModel)
```

Event emitted when a realtime session reports an error.

<a id="types.api"></a>

# types.api

<a id="types.api.ApiErrorValidationError"></a>

## ApiErrorValidationError Objects

```python
class ApiErrorValidationError(BaseModel)
```

Details a single validation error reported by the Soniox API.

<a id="types.api.ApiError"></a>

## ApiError Objects

```python
class ApiError(BaseModel)
```

Structured representation of a non-2xx API response payload.

<a id="types.api.GetFilesPayload"></a>

## GetFilesPayload Objects

```python
class GetFilesPayload(BaseModel)
```

Parameters accepted by the file listing endpoint.

<a id="types.api.File"></a>

## File Objects

```python
class File(BaseModel)
```

Metadata describing an uploaded file in the Soniox API.

<a id="types.api.GetFilesResponse"></a>

## GetFilesResponse Objects

```python
class GetFilesResponse(BaseModel)
```

Paginated response returned when listing uploaded files.

<a id="types.api.UploadFilePayload"></a>

## UploadFilePayload Objects

```python
class UploadFilePayload(BaseModel)
```

Optional metadata supplied at upload time.

<a id="types.api.GetTranscriptionsPayload"></a>

## GetTranscriptionsPayload Objects

```python
class GetTranscriptionsPayload(BaseModel)
```

Parameters for listing transcription jobs.

<a id="types.api.StructuredContextGeneralItem"></a>

## StructuredContextGeneralItem Objects

```python
class StructuredContextGeneralItem(BaseModel)
```

Single general context key/value pair for transcription context.

<a id="types.api.StructuredContextTranslationTerm"></a>

## StructuredContextTranslationTerm Objects

```python
class StructuredContextTranslationTerm(BaseModel)
```

Defines a translation term mapping used in structured context.

<a id="types.api.StructuredContext"></a>

## StructuredContext Objects

```python
class StructuredContext(BaseModel)
```

Optional structured context provided to the transcription engine.

<a id="types.api.TranslationConfig"></a>

## TranslationConfig Objects

```python
class TranslationConfig(BaseModel)
```

Configuration describing how translation should be performed.

<a id="types.api.CreateTranscriptionPayload"></a>

## CreateTranscriptionPayload Objects

```python
class CreateTranscriptionPayload(BaseModel)
```

Payload sent to create an asynchronous transcription job.

<a id="types.api.CreateTranscriptionConfig"></a>

## CreateTranscriptionConfig Objects

```python
class CreateTranscriptionConfig(BaseModel)
```

Helper config used when building transcription payloads.

<a id="types.api.CreateTemporaryApiKeyPayload"></a>

## CreateTemporaryApiKeyPayload Objects

```python
class CreateTemporaryApiKeyPayload(BaseModel)
```

Payload for requesting a temporary API key (e.g., websocket).

<a id="types.api.CreateTemporaryApiKeyResponse"></a>

## CreateTemporaryApiKeyResponse Objects

```python
class CreateTemporaryApiKeyResponse(BaseModel)
```

Response data for a temp API key request.

<a id="types.api.Language"></a>

## Language Objects

```python
class Language(BaseModel)
```

Represents a supported language for transcription or translation.

<a id="types.api.TranslationTarget"></a>

## TranslationTarget Objects

```python
class TranslationTarget(BaseModel)
```

Describes translation targets offered by a model.

<a id="types.api.Model"></a>

## Model Objects

```python
class Model(BaseModel)
```

Describes a Soniox transcription model.

<a id="types.api.GetModelsResponse"></a>

## GetModelsResponse Objects

```python
class GetModelsResponse(BaseModel)
```

Response returned when listing available models.

<a id="types.api.TranscriptionTranscript"></a>

## TranscriptionTranscript Objects

```python
class TranscriptionTranscript(BaseModel)
```

Transcript data including the full text and tokens.

<a id="types.api.Transcription"></a>

## Transcription Objects

```python
class Transcription(BaseModel)
```

Represents a transcription job tracked by Soniox.

<a id="types.api.GetTranscriptionsResponse"></a>

## GetTranscriptionsResponse Objects

```python
class GetTranscriptionsResponse(BaseModel)
```

Paginated response for transcription listings.

<a id="api"></a>

# api

<a id="api.webhooks"></a>

# api.webhooks

<a id="api.webhooks.SonioxWebhooksAPI"></a>

## SonioxWebhooksAPI Objects

```python
class SonioxWebhooksAPI()
```

<a id="api.webhooks.SonioxWebhooksAPI.verify_signature"></a>

#### verify\_signature

```python
def verify_signature(headers: Headers,
                     *,
                     auth: WebhookAuthConfig | None = None) -> None
```

Verify a webhook signature from headers.

**Raises**:

- `InvalidWebhookSignatureError` - When the webhook signature cannot be validated.

<a id="api.webhooks.SonioxWebhooksAPI.unwrap"></a>

#### unwrap

```python
def unwrap(payload: str | bytes,
           headers: Headers,
           *,
           auth: WebhookAuthConfig | None = None) -> WebhookEvent
```

Validate and parse a webhook payload.

Returns a WebhookEvent.

**Raises**:

- `InvalidWebhookSignatureError` - When the webhook signature cannot be validated.

<a id="api.webhooks.SonioxWebhooksAPI.webhook_payload"></a>

#### webhook\_payload

```python
def webhook_payload(webhook_url: str,
                    *,
                    auth: WebhookAuthConfig | None = None) -> dict[str, str]
```

Return fields for webhook configuration when creating a transcription.

<a id="api.files"></a>

# api.files

<a id="api.files.FilesAPI"></a>

## FilesAPI Objects

```python
class FilesAPI()
```

<a id="api.files.FilesAPI.list"></a>

#### list

```python
def list(limit: int = 100, cursor: str | None = None) -> GetFilesResponse
```

List uploaded files.

Performs a GET request to ``/files`` with optional pagination.

**Raises**:

- `SonioxAPIError` - When the API returns an error.

<a id="api.files.FilesAPI.get"></a>

#### get

```python
def get(file_id: str) -> File
```

Retrieve a file by ID.

Performs a GET request to ``/files/{file_id}``.

**Raises**:

- `SonioxAPIError` - When the API returns an error.

<a id="api.files.FilesAPI.get_or_none"></a>

#### get\_or\_none

```python
def get_or_none(file_id: str) -> File | None
```

Retrieve a file by ID.

Returns ``None`` if the file does not exist.

**Raises**:

- `SonioxAPIError` - When the API returns an error.

<a id="api.files.FilesAPI.delete"></a>

#### delete

```python
def delete(file_id: str) -> None
```

Delete a file by ID.

Performs a DELETE request to ``/files/{file_id}``.

**Raises**:

- `SonioxAPIError` - When the API returns an error.

<a id="api.files.FilesAPI.delete_if_exists"></a>

#### delete\_if\_exists

```python
def delete_if_exists(file_id: str) -> None
```

Delete a file by ID if it exists.

Ignores missing files.

**Raises**:

- `SonioxAPIError` - When the API returns an error.

<a id="api.files.FilesAPI.upload"></a>

#### upload

```python
def upload(file: BinaryIO | bytes | Path | str,
           *,
           filename: str | None = None,
           client_reference_id: str | None = None) -> File
```

Upload a file.

Performs a multipart POST request to ``/files``.

**Raises**:

- `SonioxAPIError` - When the API returns an error.

<a id="api.files.FilesAPI.delete_all"></a>

#### delete\_all

```python
def delete_all(*, limit: int = 100) -> None
```

Delete all files.

Iterates through all pages and deletes each file.

**Raises**:

- `SonioxAPIError` - When the API returns an error.

<a id="api.async_files"></a>

# api.async\_files

<a id="api.async_files.AsyncFilesAPI"></a>

## AsyncFilesAPI Objects

```python
class AsyncFilesAPI()
```

<a id="api.async_files.AsyncFilesAPI.list"></a>

#### list

```python
async def list(limit: int = 100,
               cursor: str | None = None) -> GetFilesResponse
```

List uploaded files.

Performs a GET request to ``/files`` with optional pagination.

**Raises**:

- `SonioxAPIError` - When the API returns an error.

<a id="api.async_files.AsyncFilesAPI.get"></a>

#### get

```python
async def get(file_id: str) -> File
```

Retrieve a file by ID.

Performs a GET request to ``/files/{file_id}``.

**Raises**:

- `SonioxAPIError` - When the API returns an error.

<a id="api.async_files.AsyncFilesAPI.get_or_none"></a>

#### get\_or\_none

```python
async def get_or_none(file_id: str) -> File | None
```

Retrieve a file by ID.

Returns ``None`` if the file does not exist.

**Raises**:

- `SonioxAPIError` - When the API returns an error.

<a id="api.async_files.AsyncFilesAPI.delete"></a>

#### delete

```python
async def delete(file_id: str) -> None
```

Delete a file by ID.

Performs a DELETE request to ``/files/{file_id}``.

**Raises**:

- `SonioxAPIError` - When the API returns an error.

<a id="api.async_files.AsyncFilesAPI.delete_if_exists"></a>

#### delete\_if\_exists

```python
async def delete_if_exists(file_id: str) -> None
```

Delete a file by ID if it exists.

Ignores missing files.

**Raises**:

- `SonioxAPIError` - When the API returns an error.

<a id="api.async_files.AsyncFilesAPI.upload"></a>

#### upload

```python
async def upload(file: BinaryIO | bytes | Path | str,
                 *,
                 filename: str | None = None,
                 client_reference_id: str | None = None) -> File
```

Upload a file.

Performs a multipart POST request to ``/files``.

**Raises**:

- `SonioxAPIError` - When the API returns an error.

<a id="api.async_files.AsyncFilesAPI.delete_all"></a>

#### delete\_all

```python
async def delete_all(*, limit: int = 100) -> None
```

Delete all files.

Iterates through all pages and deletes each file.

**Raises**:

- `SonioxAPIError` - When the API returns an error.

<a id="api.auth"></a>

# api.auth

<a id="api.auth.AuthAPI"></a>

## AuthAPI Objects

```python
class AuthAPI()
```

<a id="api.auth.AuthAPI.create_temporary_api_key"></a>

#### create\_temporary\_api\_key

```python
def create_temporary_api_key(
        *,
        usage_type: TemporaryApiKeyUsageType = "transcribe_websocket",
        expires_in_seconds: int = 5 * 60,
        client_reference_id: str | None = None
) -> CreateTemporaryApiKeyResponse
```

Create a temporary API key.

Performs a POST request to ``/auth/temporary-api-key``.

**Raises**:

- `SonioxAPIError` - When the API returns an error.

<a id="api.models"></a>

# api.models

<a id="api.models.ModelsAPI"></a>

## ModelsAPI Objects

```python
class ModelsAPI()
```

<a id="api.models.ModelsAPI.list"></a>

#### list

```python
def list() -> GetModelsResponse
```

List available models.

Performs a GET request to ``/models``.

**Raises**:

- `SonioxAPIError` - When the API returns an error.

<a id="api.async_webhooks"></a>

# api.async\_webhooks

<a id="api._utils"></a>

# api.\_utils

<a id="api._utils.normalize_file"></a>

#### normalize\_file

```python
def normalize_file(file: BinaryIO | bytes | Path | str,
                   filename: str | None = None) -> tuple[BinaryIO, str, bool]
```

Return (file-like, filename, should_close) tuple for upload.

<a id="api.async_auth"></a>

# api.async\_auth

<a id="api.async_auth.AsyncAuthAPI"></a>

## AsyncAuthAPI Objects

```python
class AsyncAuthAPI()
```

<a id="api.async_auth.AsyncAuthAPI.create_temporary_api_key"></a>

#### create\_temporary\_api\_key

```python
async def create_temporary_api_key(
        *,
        usage_type: TemporaryApiKeyUsageType = "transcribe_websocket",
        expires_in_seconds: int = 5 * 60,
        client_reference_id: str | None = None
) -> CreateTemporaryApiKeyResponse
```

Create a temporary API key.

Performs a POST request to ``/auth/temporary-api-key``.

**Raises**:

- `SonioxAPIError` - When the API returns an error.

<a id="api.async_transcriptions"></a>

# api.async\_transcriptions

<a id="api.async_transcriptions.AsyncTranscriptionsAPI"></a>

## AsyncTranscriptionsAPI Objects

```python
class AsyncTranscriptionsAPI()
```

<a id="api.async_transcriptions.AsyncTranscriptionsAPI.list"></a>

#### list

```python
async def list(limit: int = 100,
               cursor: str | None = None) -> GetTranscriptionsResponse
```

List transcriptions.

Performs a GET request to ``/transcriptions`` with optional pagination.

**Raises**:

- `SonioxAPIError` - When the API returns an error.

<a id="api.async_transcriptions.AsyncTranscriptionsAPI.delete_all"></a>

#### delete\_all

```python
async def delete_all(*, limit: int = 100) -> None
```

Delete all transcriptions.

Iterates through all pages and deletes each transcription.

**Raises**:

- `SonioxAPIError` - When the API returns an error.

<a id="api.async_transcriptions.AsyncTranscriptionsAPI.create"></a>

#### create

```python
async def create(
        *,
        model: str = DEFAULT_MODEL,
        file_id: str | None = None,
        audio_url: str | None = None,
        client_reference_id: str | None = None,
        config: CreateTranscriptionConfig | None = None) -> Transcription
```

Create a transcription.

Performs a POST request to ``/transcriptions``.

**Raises**:

- `SonioxAPIError` - When the API returns an error.

<a id="api.async_transcriptions.AsyncTranscriptionsAPI.get"></a>

#### get

```python
async def get(transcription_id: str) -> Transcription
```

Retrieve a transcription by ID.

Performs a GET request to ``/transcriptions/{transcription_id}``.

**Raises**:

- `SonioxAPIError` - When the API returns an error.

<a id="api.async_transcriptions.AsyncTranscriptionsAPI.get_or_none"></a>

#### get\_or\_none

```python
async def get_or_none(transcription_id: str) -> Transcription | None
```

Retrieve a transcription by ID.

Returns ``None`` if the transcription does not exist.

**Raises**:

- `SonioxAPIError` - When the API returns an error.

<a id="api.async_transcriptions.AsyncTranscriptionsAPI.delete"></a>

#### delete

```python
async def delete(transcription_id: str) -> None
```

Delete a transcription by ID.

Performs a DELETE request to ``/transcriptions/{transcription_id}``.

**Raises**:

- `SonioxAPIError` - When the API returns an error.

<a id="api.async_transcriptions.AsyncTranscriptionsAPI.delete_if_exists"></a>

#### delete\_if\_exists

```python
async def delete_if_exists(transcription_id: str) -> None
```

Delete a transcription by ID if it exists.

Ignores missing transcriptions.

**Raises**:

- `SonioxAPIError` - When the API returns an error.

<a id="api.async_transcriptions.AsyncTranscriptionsAPI.destroy"></a>

#### destroy

```python
async def destroy(transcription_id: str) -> None
```

Delete a transcription and its associated uploaded file.

**Raises**:

- `SonioxAPIError` - When the API returns an error.

<a id="api.async_transcriptions.AsyncTranscriptionsAPI.get_transcript"></a>

#### get\_transcript

```python
async def get_transcript(transcription_id: str) -> TranscriptionTranscript
```

Retrieve the transcript for a transcription.

Performs a GET request to ``/transcriptions/{transcription_id}/transcript``.

**Raises**:

- `SonioxAPIError` - When the API returns an error.

<a id="api.async_transcriptions.AsyncTranscriptionsAPI.wait"></a>

#### wait

```python
async def wait(transcription_id: str,
               *,
               interval_sec: float = 5.0,
               timeout_sec: float | None = None) -> Transcription
```

Poll a transcription until it leaves the queued or processing state.

**Raises**:

- `SonioxAPIError` - When the API returns an error.
- `TimeoutError` - Waiting for the transcription to finish exceeded `timeout_sec`.

<a id="api.async_transcriptions.AsyncTranscriptionsAPI.transcribe_from_url"></a>

#### transcribe\_from\_url

```python
async def transcribe_from_url(
        *,
        model: str = DEFAULT_MODEL,
        audio_url: str,
        client_reference_id: str | None = None,
        config: CreateTranscriptionConfig | None = None) -> Transcription
```

Create a transcription from an audio URL.

**Raises**:

- `SonioxAPIError` - When the API returns an error.

<a id="api.async_transcriptions.AsyncTranscriptionsAPI.transcribe_from_file_id"></a>

#### transcribe\_from\_file\_id

```python
async def transcribe_from_file_id(
        *,
        model: str = DEFAULT_MODEL,
        file_id: str,
        client_reference_id: str | None = None,
        config: CreateTranscriptionConfig | None = None) -> Transcription
```

Create a transcription from an existing uploaded file.

**Raises**:

- `SonioxAPIError` - When the API returns an error.

<a id="api.async_transcriptions.AsyncTranscriptionsAPI.transcribe_from_file"></a>

#### transcribe\_from\_file

```python
async def transcribe_from_file(
        *,
        model: str = DEFAULT_MODEL,
        file: BinaryIO | bytes | Path | str,
        filename: str | None = None,
        client_reference_id: str | None = None,
        config: CreateTranscriptionConfig | None = None) -> Transcription
```

Upload a file and create a transcription from it.

**Raises**:

- `SonioxAPIError` - When the API returns an error.

<a id="api.async_transcriptions.AsyncTranscriptionsAPI.transcribe"></a>

#### transcribe

```python
async def transcribe(
        *,
        model: str = DEFAULT_MODEL,
        audio_url: str | None = None,
        file_id: str | None = None,
        file: BinaryIO | bytes | Path | str | None = None,
        filename: str | None = None,
        client_reference_id: str | None = None,
        config: CreateTranscriptionConfig | None = None) -> Transcription
```

Create a transcription from a file, file ID, or audio URL.

Validates mutually exclusive inputs before submission.

**Raises**:

- `SonioxAPIError` - When the API returns an error.
- `SonioxValidationError` - When the payload fails validation.

<a id="api.async_transcriptions.AsyncTranscriptionsAPI.transcribe_file_with_webhook"></a>

#### transcribe\_file\_with\_webhook

```python
async def transcribe_file_with_webhook(
        *,
        model: str = DEFAULT_MODEL,
        file: BinaryIO | bytes | Path | str,
        webhook_url: str,
        filename: str | None = None,
        client_reference_id: str | None = None,
        webhook_auth: WebhookAuthConfig | None = None,
        config: CreateTranscriptionConfig | None = None) -> Transcription
```

Upload a file, configure a webhook, and start transcription.

**Raises**:

- `SonioxAPIError` - When the API returns an error.

<a id="api.async_transcriptions.AsyncTranscriptionsAPI.transcribe_and_wait"></a>

#### transcribe\_and\_wait

```python
async def transcribe_and_wait(
        *,
        model: str = DEFAULT_MODEL,
        audio_url: str | None = None,
        file_id: str | None = None,
        file: BinaryIO | bytes | Path | str | None = None,
        filename: str | None = None,
        client_reference_id: str | None = None,
        delete_after: bool = False,
        wait_interval_sec: float = 5.0,
        wait_timeout_sec: float | None = None,
        config: CreateTranscriptionConfig | None = None) -> Transcription
```

Create a transcription and wait for completion.

Returns a Transcription object after it is completed. Optionally deletes
the transcription and the uploaded file after completion.

**Raises**:

- `SonioxAPIError` - When the API returns an error.
- `SonioxValidationError` - When the payload fails validation.
- `TimeoutError` - Waiting for the transcription to finish exceeded `timeout_sec`.

<a id="api.async_transcriptions.AsyncTranscriptionsAPI.transcribe_and_wait_with_tokens"></a>

#### transcribe\_and\_wait\_with\_tokens

```python
async def transcribe_and_wait_with_tokens(
    *,
    model: str = DEFAULT_MODEL,
    audio_url: str | None = None,
    file_id: str | None = None,
    file: BinaryIO | bytes | Path | str | None = None,
    filename: str | None = None,
    client_reference_id: str | None = None,
    delete_after: bool = False,
    wait_interval_sec: float = 5.0,
    wait_timeout_sec: float | None = None,
    config: CreateTranscriptionConfig | None = None
) -> TranscriptionTranscript
```

Create a transcription, wait for completion, and return the transcript.

Optionally deletes the transcription and uploaded file after completion.

**Raises**:

- `SonioxAPIError` - When the API returns an error.
- `SonioxValidationError` - When the payload fails validation.
- `TimeoutError` - Waiting for the transcription to finish exceeded `timeout_sec`.

<a id="api.async_models"></a>

# api.async\_models

<a id="api.async_models.AsyncModelsAPI"></a>

## AsyncModelsAPI Objects

```python
class AsyncModelsAPI()
```

<a id="api.async_models.AsyncModelsAPI.list"></a>

#### list

```python
async def list() -> GetModelsResponse
```

List available models.

Performs a GET request to ``/models``.

**Raises**:

- `SonioxAPIError` - When the API returns an error.

<a id="api.transcriptions"></a>

# api.transcriptions

<a id="api.transcriptions.TranscriptionsAPI"></a>

## TranscriptionsAPI Objects

```python
class TranscriptionsAPI()
```

<a id="api.transcriptions.TranscriptionsAPI.list"></a>

#### list

```python
def list(limit: int = 100,
         cursor: str | None = None) -> GetTranscriptionsResponse
```

List transcriptions.

Performs a GET request to ``/transcriptions`` with optional pagination.

**Raises**:

- `SonioxAPIError` - When the API returns an error.

<a id="api.transcriptions.TranscriptionsAPI.delete_all"></a>

#### delete\_all

```python
def delete_all(*, limit: int = 100) -> None
```

Delete all transcriptions.

Iterates through all pages and deletes each transcription.

**Raises**:

- `SonioxAPIError` - When the API returns an error.

<a id="api.transcriptions.TranscriptionsAPI.create"></a>

#### create

```python
def create(*,
           model: str = DEFAULT_MODEL,
           file_id: str | None = None,
           audio_url: str | None = None,
           client_reference_id: str | None = None,
           config: CreateTranscriptionConfig | None = None) -> Transcription
```

Create a transcription.

Performs a POST request to ``/transcriptions``.

**Raises**:

- `SonioxAPIError` - When the API returns an error.

<a id="api.transcriptions.TranscriptionsAPI.get"></a>

#### get

```python
def get(transcription_id: str) -> Transcription
```

Retrieve a transcription by ID.

Performs a GET request to ``/transcriptions/{transcription_id}``.

**Raises**:

- `SonioxAPIError` - When the API returns an error.

<a id="api.transcriptions.TranscriptionsAPI.get_or_none"></a>

#### get\_or\_none

```python
def get_or_none(transcription_id: str) -> Transcription | None
```

Retrieve a transcription by ID.

Returns ``None`` if the transcription does not exist.

**Raises**:

- `SonioxAPIError` - When the API returns an error.

<a id="api.transcriptions.TranscriptionsAPI.delete"></a>

#### delete

```python
def delete(transcription_id: str) -> None
```

Delete a transcription by ID.

Performs a DELETE request to ``/transcriptions/{transcription_id}``.

**Raises**:

- `SonioxAPIError` - When the API returns an error.

<a id="api.transcriptions.TranscriptionsAPI.delete_if_exists"></a>

#### delete\_if\_exists

```python
def delete_if_exists(transcription_id: str) -> None
```

Delete a transcription by ID if it exists.

Ignores missing transcriptions.

**Raises**:

- `SonioxAPIError` - When the API returns an error.

<a id="api.transcriptions.TranscriptionsAPI.destroy"></a>

#### destroy

```python
def destroy(transcription_id: str) -> None
```

Delete a transcription and its associated uploaded file.

**Raises**:

- `SonioxAPIError` - When the API returns an error.

<a id="api.transcriptions.TranscriptionsAPI.get_transcript"></a>

#### get\_transcript

```python
def get_transcript(transcription_id: str) -> TranscriptionTranscript
```

Retrieve the transcript for a transcription.

Performs a GET request to ``/transcriptions/{transcription_id}/transcript``.

**Raises**:

- `SonioxAPIError` - When the API returns an error.

<a id="api.transcriptions.TranscriptionsAPI.wait"></a>

#### wait

```python
def wait(transcription_id: str,
         *,
         interval_sec: float = 5.0,
         timeout_sec: float | None = None) -> Transcription
```

Poll a transcription until it leaves the queued or processing state.

**Raises**:

- `SonioxAPIError` - When the API returns an error.
- `TimeoutError` - Waiting for the transcription to finish exceeded `timeout_sec`.

<a id="api.transcriptions.TranscriptionsAPI.transcribe_from_url"></a>

#### transcribe\_from\_url

```python
def transcribe_from_url(
        *,
        model: str = DEFAULT_MODEL,
        audio_url: str,
        client_reference_id: str | None = None,
        config: CreateTranscriptionConfig | None = None) -> Transcription
```

Create a transcription from an audio URL.

**Raises**:

- `SonioxAPIError` - When the API returns an error.

<a id="api.transcriptions.TranscriptionsAPI.transcribe_from_file_id"></a>

#### transcribe\_from\_file\_id

```python
def transcribe_from_file_id(
        *,
        model: str = DEFAULT_MODEL,
        file_id: str,
        client_reference_id: str | None = None,
        config: CreateTranscriptionConfig | None = None) -> Transcription
```

Create a transcription from an existing uploaded file.

**Raises**:

- `SonioxAPIError` - When the API returns an error.

<a id="api.transcriptions.TranscriptionsAPI.transcribe_from_file"></a>

#### transcribe\_from\_file

```python
def transcribe_from_file(
        *,
        model: str = DEFAULT_MODEL,
        file: BinaryIO | bytes | Path | str,
        filename: str | None = None,
        client_reference_id: str | None = None,
        config: CreateTranscriptionConfig | None = None) -> Transcription
```

Upload a file and create a transcription from it.

**Raises**:

- `SonioxAPIError` - When the API returns an error.

<a id="api.transcriptions.TranscriptionsAPI.transcribe"></a>

#### transcribe

```python
def transcribe(
        *,
        model: str = DEFAULT_MODEL,
        audio_url: str | None = None,
        file_id: str | None = None,
        file: BinaryIO | bytes | Path | str | None = None,
        filename: str | None = None,
        client_reference_id: str | None = None,
        config: CreateTranscriptionConfig | None = None) -> Transcription
```

Create a transcription from a file, file ID, or audio URL.

Validates mutually exclusive inputs before submission.

**Raises**:

- `SonioxAPIError` - When the API returns an error.
- `SonioxValidationError` - When the payload fails validation.

<a id="api.transcriptions.TranscriptionsAPI.transcribe_file_with_webhook"></a>

#### transcribe\_file\_with\_webhook

```python
def transcribe_file_with_webhook(
        *,
        model: str = DEFAULT_MODEL,
        file: BinaryIO | bytes | Path | str,
        webhook_url: str,
        filename: str | None = None,
        client_reference_id: str | None = None,
        webhook_auth: WebhookAuthConfig | None = None,
        config: CreateTranscriptionConfig | None = None) -> Transcription
```

Upload a file, configure a webhook, and start transcription.

**Raises**:

- `SonioxAPIError` - When the API returns an error.

<a id="api.transcriptions.TranscriptionsAPI.transcribe_and_wait"></a>

#### transcribe\_and\_wait

```python
def transcribe_and_wait(
        *,
        model: str = DEFAULT_MODEL,
        audio_url: str | None = None,
        file_id: str | None = None,
        file: BinaryIO | bytes | Path | str | None = None,
        filename: str | None = None,
        client_reference_id: str | None = None,
        delete_after: bool = False,
        wait_interval_sec: float = 5.0,
        wait_timeout_sec: float | None = None,
        config: CreateTranscriptionConfig | None = None) -> Transcription
```

Create a transcription and wait for completion.

Returns a Transcription object after it is completed. Optionally deletes
the transcription and the uploaded file after completion.

**Raises**:

- `SonioxAPIError` - When the API returns an error.
- `SonioxValidationError` - When the payload fails validation.
- `TimeoutError` - Waiting for the transcription to finish exceeded `timeout_sec`.

<a id="api.transcriptions.TranscriptionsAPI.transcribe_and_wait_with_tokens"></a>

#### transcribe\_and\_wait\_with\_tokens

```python
def transcribe_and_wait_with_tokens(
    *,
    model: str = DEFAULT_MODEL,
    audio_url: str | None = None,
    file_id: str | None = None,
    file: BinaryIO | bytes | Path | str | None = None,
    filename: str | None = None,
    client_reference_id: str | None = None,
    delete_after: bool = False,
    wait_interval_sec: float = 5.0,
    wait_timeout_sec: float | None = None,
    config: CreateTranscriptionConfig | None = None
) -> TranscriptionTranscript
```

Create a transcription, wait for completion, and return the transcript.

Optionally deletes the transcription and uploaded file after completion.

**Raises**:

- `SonioxAPIError` - When the API returns an error.
- `SonioxValidationError` - When the payload fails validation.
- `TimeoutError` - Waiting for the transcription to finish exceeded `timeout_sec`.

<a id="realtime"></a>

# realtime

<a id="realtime.AsyncRealtimeAPI"></a>

## AsyncRealtimeAPI Objects

```python
class AsyncRealtimeAPI()
```

Entrypoint for async realtime helpers on AsyncSonioxClient.

<a id="realtime.RealtimeAPI"></a>

## RealtimeAPI Objects

```python
class RealtimeAPI()
```

Entrypoint for realtime helpers on SonioxClient.

<a id="realtime.stt"></a>

# realtime.stt

<a id="realtime.stt.RealtimeSTTSession"></a>

## RealtimeSTTSession Objects

```python
class RealtimeSTTSession()
```

Synchronous WebSocket session for a single real-time speech-to-text stream.

This class manages the full lifecycle of a real-time transcription session:
connecting to the WebSocket endpoint, streaming audio data, receiving events,
and gracefully closing the stream. A session is stateful and represents
exactly one streaming interaction with the Soniox realtime API.

Instances are designed to be used as context managers.

<a id="realtime.stt.RealtimeSTTSession.__init__"></a>

#### \_\_init\_\_

```python
def __init__(url: str, config: RealtimeSTTConfig) -> None
```

Create a new realtime STT session.

This does not open a network connection. The WebSocket connection
is established when entering the context manager.

**Arguments**:

  url:
  WebSocket URL for the realtime transcription endpoint.
  config:
  Configuration describing the audio format and transcription
  behavior for this session.

<a id="realtime.stt.RealtimeSTTSession.config"></a>

#### config

```python
@property
def config() -> RealtimeSTTConfig
```

Return the configuration used to initialize this session.

<a id="realtime.stt.RealtimeSTTSession.__enter__"></a>

#### \_\_enter\_\_

```python
def __enter__() -> RealtimeSTTSession
```

Open the WebSocket connection and start the realtime session.

The session configuration is sent immediately after connecting.
If any step fails, the connection is closed and a
SonioxRealtimeError is raised.

**Returns**:

  The active realtime session instance.
  

**Raises**:

  SonioxRealtimeError:
  If the WebSocket connection or session initialization fails.

<a id="realtime.stt.RealtimeSTTSession.__exit__"></a>

#### \_\_exit\_\_

```python
def __exit__(_exc_type: type[BaseException] | None,
             _exc_value: BaseException | None,
             _traceback: TracebackType | None) -> None
```

Close the realtime session and release network resources.

This method is called automatically when exiting the
context manager.

<a id="realtime.stt.RealtimeSTTSession.close"></a>

#### close

```python
def close() -> None
```

Gracefully close the realtime session.

Sends a final empty message to signal end-of-stream, then closes
the WebSocket connection. Calling this method multiple times is safe.

<a id="realtime.stt.RealtimeSTTSession.send_byte_chunk"></a>

#### send\_byte\_chunk

```python
def send_byte_chunk(chunk: bytes) -> None
```

Send a single chunk of raw audio bytes to the realtime stream.

The audio data must match the format declared in the session
configuration (sample rate, channels, encoding).

**Arguments**:

  chunk:
  Raw audio bytes to send.
  

**Raises**:

  SonioxRealtimeError:
  If the session is not connected or the send operation fails.

<a id="realtime.stt.RealtimeSTTSession.send_bytes"></a>

#### send\_bytes

```python
def send_bytes(chunks: bytes | Iterator[bytes]) -> None
```

Send audio data to the realtime stream.

This method accepts either a single bytes object or an iterator
yielding audio chunks. When an iterator is provided, a FINISH
control message is sent automatically after all chunks have
been transmitted.

**Arguments**:

  chunks:
  Audio data as raw bytes or an iterator of byte chunks.

<a id="realtime.stt.RealtimeSTTSession.send_control_message"></a>

#### send\_control\_message

```python
def send_control_message(control_type: RealtimeControlType) -> None
```

Send a control message to the realtime session.

Control messages modify the state of the stream, such as signaling
end-of-audio or requesting finalization.

**Arguments**:

  control_type:
  The type of control message to send.
  

**Raises**:

  SonioxRealtimeError:
  If the session is not connected or the message cannot be sent.

<a id="realtime.stt.RealtimeSTTSession.send_finish"></a>

#### send\_finish

```python
def send_finish() -> None
```

Signal that no more audio will be sent for this session.

<a id="realtime.stt.RealtimeSTTSession.send_keep_alive"></a>

#### send\_keep\_alive

```python
def send_keep_alive() -> None
```

Send a keep-alive message to prevent the session from timing out.

<a id="realtime.stt.RealtimeSTTSession.send_finalize"></a>

#### send\_finalize

```python
def send_finalize() -> None
```

Finalize all outstanding non-final tokens while keeping the session open.

Subsequent tokens will be delivered with `is_final=True`.

<a id="realtime.stt.RealtimeSTTSession.recv_bytes"></a>

#### recv\_bytes

```python
def recv_bytes() -> bytes
```

Receive a raw message from the WebSocket connection.

**Returns**:

  The received message as bytes. An empty bytes object indicates
  that the connection has been closed.

<a id="realtime.stt.RealtimeSTTSession.parse_event"></a>

#### parse\_event

```python
def parse_event(raw: str | bytes) -> RealtimeEvent
```

Parse a raw WebSocket message into a structured realtime event.

**Arguments**:

  raw:
  Raw message payload received from the server.
  

**Returns**:

  A validated RealtimeEvent instance.

<a id="realtime.stt.RealtimeSTTSession.last_message"></a>

#### last\_message

```python
@property
def last_message() -> RealtimeEvent | None
```

Return the most recently received realtime event, if any.

<a id="realtime.stt.RealtimeSTTSession.receive_event"></a>

#### receive\_event

```python
def receive_event() -> RealtimeEvent | None
```

Receive and parse the next realtime event from the server.

**Returns**:

  The next RealtimeEvent, or None if the connection has closed.
  

**Raises**:

  SonioxRealtimeError:
  If the session is not connected.

<a id="realtime.stt.RealtimeSTTSession.receive_events"></a>

#### receive\_events

```python
def receive_events() -> Iterator[RealtimeEvent]
```

Yield realtime events as they are received from the server.

Iteration stops automatically when the connection is closed.

<a id="realtime.stt.RealtimeSTTSession.handle_events"></a>

#### handle\_events

```python
def handle_events(handler: Callable[[RealtimeEvent], None]) -> None
```

Receive realtime events and dispatch them to a handler callback.

**Arguments**:

  handler:
  Callable invoked for each received RealtimeEvent.

<a id="realtime.stt.RealtimeSTTClient"></a>

## RealtimeSTTClient Objects

```python
class RealtimeSTTClient()
```

Factory for creating synchronous realtime speech-to-text sessions.

This class validates credentials and prepares session configuration,
but does not itself manage WebSocket connections.

<a id="realtime.stt.RealtimeSTTClient.__init__"></a>

#### \_\_init\_\_

```python
def __init__(client: SonioxClient) -> None
```

Create a realtime STT client bound to an existing API client.

**Arguments**:

  client:
  Parent Soniox client providing configuration and credentials.

<a id="realtime.stt.RealtimeSTTClient.connect"></a>

#### connect

```python
def connect(*,
            config: RealtimeSTTConfig,
            api_key: str | None = None) -> RealtimeSTTSession
```

Create a new realtime STT session.

The returned session is not connected until entered as a
context manager.

**Arguments**:

  config:
  Realtime transcription configuration.
  api_key:
  Optional API key override. If not provided, the client's
  default API key is used.
  

**Returns**:

  A new RealtimeSTTSession instance.
  

**Raises**:

  SonioxValidationError:
  If no API key is available.

<a id="realtime.async_stt"></a>

# realtime.async\_stt

<a id="realtime.async_stt.AsyncRealtimeSTTSession"></a>

## AsyncRealtimeSTTSession Objects

```python
class AsyncRealtimeSTTSession()
```

Asynchronous WebSocket session for a single real-time speech-to-text stream.

This class manages the full lifecycle of a real-time transcription session:
connecting to the WebSocket endpoint, streaming audio data, receiving events,
and gracefully closing the stream. A session is stateful and represents
exactly one streaming interaction with the Soniox realtime API.

Instances are designed to be used as async context managers.

<a id="realtime.async_stt.AsyncRealtimeSTTSession.__init__"></a>

#### \_\_init\_\_

```python
def __init__(url: str, config: RealtimeSTTConfig) -> None
```

Create a new realtime STT session.

This does not open a network connection. The WebSocket connection
is established when entering the async context manager.

**Arguments**:

  url:
  WebSocket URL for the realtime transcription endpoint.
  config:
  Configuration describing the audio format and transcription
  behavior for this session.

<a id="realtime.async_stt.AsyncRealtimeSTTSession.config"></a>

#### config

```python
@property
def config() -> RealtimeSTTConfig
```

Return the configuration used to initialize this session.

<a id="realtime.async_stt.AsyncRealtimeSTTSession.__aenter__"></a>

#### \_\_aenter\_\_

```python
async def __aenter__() -> AsyncRealtimeSTTSession
```

Open the WebSocket connection and start the realtime session.

The session configuration is sent immediately after connecting.
If any step fails, the connection is closed and a
SonioxRealtimeError is raised.

**Returns**:

  The active realtime session instance.
  

**Raises**:

  SonioxRealtimeError:
  If the WebSocket connection or session initialization fails.

<a id="realtime.async_stt.AsyncRealtimeSTTSession.__aexit__"></a>

#### \_\_aexit\_\_

```python
async def __aexit__(_exc_type: type[BaseException] | None,
                    _exc_value: BaseException | None,
                    _traceback: TracebackType | None) -> None
```

Close the realtime session and release network resources.

This method is called automatically when exiting the async
context manager.

<a id="realtime.async_stt.AsyncRealtimeSTTSession.close"></a>

#### close

```python
async def close() -> None
```

Gracefully close the realtime session.

Sends a final empty message to signal end-of-stream, then closes
the WebSocket connection. Calling this method multiple times is safe.

<a id="realtime.async_stt.AsyncRealtimeSTTSession.send_byte_chunk"></a>

#### send\_byte\_chunk

```python
async def send_byte_chunk(chunk: bytes) -> None
```

Send a single chunk of raw audio bytes to the realtime stream.

The audio data must match the format declared in the session
configuration (sample rate, channels, encoding).

**Arguments**:

  chunk:
  Raw audio bytes to send.
  

**Raises**:

  SonioxRealtimeError:
  If the session is not connected or the send operation fails.

<a id="realtime.async_stt.AsyncRealtimeSTTSession.send_bytes"></a>

#### send\_bytes

```python
async def send_bytes(chunks: bytes | AsyncIterator[bytes]) -> None
```

Send audio data to the realtime stream.

This method accepts either a single bytes object or an iterator
yielding audio chunks. When an iterator is provided, a
FINISH control message is sent automatically after all chunks
have been transmitted.

**Arguments**:

  chunks:
  Audio data as raw bytes or an iterator of byte chunks.

<a id="realtime.async_stt.AsyncRealtimeSTTSession.send_control_message"></a>

#### send\_control\_message

```python
async def send_control_message(control_type: RealtimeControlType) -> None
```

Send a control message to the realtime session.

Control messages modify the state of the stream, such as signaling
end-of-audio or requesting finalization.

**Arguments**:

  control_type:
  The type of control message to send.
  

**Raises**:

  SonioxRealtimeError:
  If the session is not connected or the message cannot be sent.

<a id="realtime.async_stt.AsyncRealtimeSTTSession.send_finish"></a>

#### send\_finish

```python
async def send_finish() -> None
```

Signal that no more audio will be sent for this session.

<a id="realtime.async_stt.AsyncRealtimeSTTSession.send_keep_alive"></a>

#### send\_keep\_alive

```python
async def send_keep_alive() -> None
```

Send a keep-alive message to prevent the session from timing out.

<a id="realtime.async_stt.AsyncRealtimeSTTSession.send_finalize"></a>

#### send\_finalize

```python
async def send_finalize() -> None
```

Finalize all outstanding non-final tokens while keeping the session open.

Subsequent tokens will be delivered with `is_final=True`.

<a id="realtime.async_stt.AsyncRealtimeSTTSession.recv_bytes"></a>

#### recv\_bytes

```python
async def recv_bytes() -> bytes
```

Receive a raw message from the WebSocket connection.

**Returns**:

  The received message as bytes. An empty bytes object indicates
  that the connection has been closed.

<a id="realtime.async_stt.AsyncRealtimeSTTSession.parse_event"></a>

#### parse\_event

```python
def parse_event(raw: str | bytes) -> RealtimeEvent
```

Parse a raw WebSocket message into a structured realtime event.

**Arguments**:

  raw:
  Raw message payload received from the server.
  

**Returns**:

  A validated RealtimeEvent instance.

<a id="realtime.async_stt.AsyncRealtimeSTTSession.last_message"></a>

#### last\_message

```python
@property
def last_message() -> RealtimeEvent | None
```

Return the most recently received realtime event, if any.

<a id="realtime.async_stt.AsyncRealtimeSTTSession.receive_event"></a>

#### receive\_event

```python
async def receive_event() -> RealtimeEvent | None
```

Receive and parse the next realtime event from the server.

**Returns**:

  The next RealtimeEvent, or None if the connection has closed.
  

**Raises**:

  SonioxRealtimeError:
  If the session is not connected.

<a id="realtime.async_stt.AsyncRealtimeSTTSession.receive_events"></a>

#### receive\_events

```python
async def receive_events() -> AsyncIterator[RealtimeEvent]
```

Yield realtime events as they are received from the server.

Iteration stops automatically when the connection is closed.

<a id="realtime.async_stt.AsyncRealtimeSTTSession.handle_events"></a>

#### handle\_events

```python
async def handle_events(
        handler: Callable[[RealtimeEvent], Awaitable[None]]) -> None
```

Receive realtime events and dispatch them to a handler callback.

**Arguments**:

  handler:
  Callable invoked for each received RealtimeEvent.

<a id="realtime.async_stt.AsyncRealtimeSTTClient"></a>

## AsyncRealtimeSTTClient Objects

```python
class AsyncRealtimeSTTClient()
```

Factory for creating asynchronous realtime speech-to-text sessions.

This class validates credentials and prepares session configuration,
but does not itself manage WebSocket connections.

<a id="realtime.async_stt.AsyncRealtimeSTTClient.__init__"></a>

#### \_\_init\_\_

```python
def __init__(client: AsyncSonioxClient) -> None
```

Create a realtime STT client bound to an existing API client.

**Arguments**:

  client:
  Parent Soniox client providing configuration and credentials.

<a id="realtime.async_stt.AsyncRealtimeSTTClient.connect"></a>

#### connect

```python
def connect(*,
            config: RealtimeSTTConfig,
            api_key: str | None = None) -> AsyncRealtimeSTTSession
```

Create a new realtime STT session.

The returned session is not connected until entered as an async
context manager.

**Arguments**:

  config:
  Realtime transcription configuration.
  api_key:
  Optional API key override. If not provided, the client's
  default API key is used.
  

**Returns**:

  A new AsyncRealtimeSTTSession instance.
  

**Raises**:

  SonioxValidationError:
  If no API key is available.

