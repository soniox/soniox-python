---
title: soniox.api.async_files
description: Description for async_files
keywords: annotations, AsyncGenerator, Path, TYPE_CHECKING, BinaryIO, SonioxNotFoundError, File, GetFilesPayload, GetFilesResponse, UploadFilePayload, ensure_success, normalize_file, parse_async_response, AsyncSonioxClient, AsyncFilesAPI
---


---

## Class `AsyncFilesAPI`

### Attributes

- **_client**: 

### `__init__`

#### Signature

```python
__init__(client: AsyncSonioxClient) -> None
```

#### Parameters

- **self** (None): 

- **client** (AsyncSonioxClient): 

#### Returns

None

### `list`

List uploaded files.

Performs a GET request to ``/files`` with optional pagination.

Raises:
    SonioxAPIError: When the API returns an error.

#### Signature

```python
list(limit: int = 100, cursor: str | None = None) -> GetFilesResponse
```

#### Parameters

- **self** (None): 

- **limit** (int): 

- **cursor** (str | None): 

#### Returns

GetFilesResponse

### `list_all`

Iterate through all uploaded files across all pages.

Yields:
    File: The next file object from the API.

Raises:
    SonioxAPIError: When the API returns an error.

#### Signature

```python
list_all(limit: int = 100) -> AsyncGenerator[File, None]
```

#### Parameters

- **self** (None): 

- **limit** (int): 

#### Returns

AsyncGenerator[File, None]

### `get`

Retrieve a file by ID.

Performs a GET request to ``/files/{file_id}``.

Raises:
    SonioxAPIError: When the API returns an error.

#### Signature

```python
get(file_id: str) -> File
```

#### Parameters

- **self** (None): 

- **file_id** (str): 

#### Returns

File

### `get_or_none`

Retrieve a file by ID.

Returns ``None`` if the file does not exist.

Raises:
    SonioxAPIError: When the API returns an error.

#### Signature

```python
get_or_none(file_id: str) -> File | None
```

#### Parameters

- **self** (None): 

- **file_id** (str): 

#### Returns

File | None

### `delete`

Delete a file by ID.

Performs a DELETE request to ``/files/{file_id}``.

Raises:
    SonioxAPIError: When the API returns an error.

#### Signature

```python
delete(file_id: str) -> None
```

#### Parameters

- **self** (None): 

- **file_id** (str): 

#### Returns

None

### `delete_if_exists`

Delete a file by ID if it exists.

Ignores missing files.

Raises:
    SonioxAPIError: When the API returns an error.

#### Signature

```python
delete_if_exists(file_id: str) -> None
```

#### Parameters

- **self** (None): 

- **file_id** (str): 

#### Returns

None

### `upload`

Upload a file.

Performs a multipart POST request to ``/files``.

Raises:
    SonioxAPIError: When the API returns an error.

#### Signature

```python
upload(file: BinaryIO | bytes | Path | str, *, filename: str | None = None, client_reference_id: str | None = None) -> File
```

#### Parameters

- **self** (None): 

- **file** (BinaryIO | bytes | Path | str): 

- **filename** (str | None): 

- **client_reference_id** (str | None): 

#### Returns

File

### `delete_all`

Delete all files.

Iterates through all pages and deletes each file. Stops and raises on the first failed deletion.

Raises:
    SonioxAPIError: When the API returns an error.

#### Signature

```python
delete_all(limit: int = 100) -> None
```

#### Parameters

- **self** (None): 

- **limit** (int): 

#### Returns

None