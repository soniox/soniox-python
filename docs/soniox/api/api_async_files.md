---
title: "soniox.api.async_files"
description: "Soniox Python SDK — soniox.api.async_files Reference"
keywords: "AsyncFilesAPI"
---

---

## AsyncFilesAPI

<a id="asyncfilesapi-constructor"></a>

### Constructor

```python
AsyncFilesAPI(client: AsyncSonioxClient)
```

**Parameters**

| Parameter | Type |
| ------ | ------ |
| `client` | `AsyncSonioxClient` |

**Returns**

`None`

<a id="asyncfilesapi-list"></a>

### list()

```python
list(limit: int = 100, cursor: str | None = None) -> GetFilesResponse
```

List uploaded files.

Performs a GET request to ``/files`` with optional pagination.

**Parameters**

| Parameter | Type |
| ------ | ------ |
| `limit` | `int` |
| `cursor` | `str \| None` |

**Returns**

`GetFilesResponse`

**Raises**

- `SonioxAPIError` When the API returns an error.

***

<a id="asyncfilesapi-list_all"></a>

### list_all()

```python
list_all(limit: int = 100) -> AsyncGenerator[File, None]
```

Iterate through all uploaded files across all pages.

**Parameters**

| Parameter | Type |
| ------ | ------ |
| `limit` | `int` |

**Yields**

`AsyncGenerator[File, None]`

File: The next file object from the API.

**Raises**

- `SonioxAPIError` When the API returns an error.

***

<a id="asyncfilesapi-get"></a>

### get()

```python
get(file_id: str) -> File
```

Retrieve a file by ID.

Performs a GET request to ``/files/{file_id}``.

**Parameters**

| Parameter | Type |
| ------ | ------ |
| `file_id` | `str` |

**Returns**

`File`

**Raises**

- `SonioxAPIError` When the API returns an error.

***

<a id="asyncfilesapi-get_or_none"></a>

### get_or_none()

```python
get_or_none(file_id: str) -> File | None
```

Retrieve a file by ID.

Returns ``None`` if the file does not exist.

**Parameters**

| Parameter | Type |
| ------ | ------ |
| `file_id` | `str` |

**Returns**

`File | None`

**Raises**

- `SonioxAPIError` When the API returns an error.

***

<a id="asyncfilesapi-delete"></a>

### delete()

```python
delete(file_id: str) -> None
```

Delete a file by ID.

Performs a DELETE request to ``/files/{file_id}``.

**Parameters**

| Parameter | Type |
| ------ | ------ |
| `file_id` | `str` |

**Returns**

`None`

**Raises**

- `SonioxAPIError` When the API returns an error.

***

<a id="asyncfilesapi-delete_if_exists"></a>

### delete_if_exists()

```python
delete_if_exists(file_id: str) -> None
```

Delete a file by ID if it exists.

Ignores missing files.

**Parameters**

| Parameter | Type |
| ------ | ------ |
| `file_id` | `str` |

**Returns**

`None`

**Raises**

- `SonioxAPIError` When the API returns an error.

***

<a id="asyncfilesapi-upload"></a>

### upload()

```python
upload(file: BinaryIO | bytes | Path | str, *, filename: str | None = None, client_reference_id: str | None = None) -> File
```

Upload a file.

Performs a multipart POST request to ``/files``.

**Parameters**

| Parameter | Type |
| ------ | ------ |
| `file` | `BinaryIO \| bytes \| Path \| str` |
| `filename` | `str \| None` |
| `client_reference_id` | `str \| None` |

**Returns**

`File`

**Raises**

- `SonioxAPIError` When the API returns an error.

***

<a id="asyncfilesapi-delete_all"></a>

### delete_all()

```python
delete_all(limit: int = 100) -> None
```

Delete all files.

Iterates through all pages and deletes each file. Stops and raises on the first failed deletion.

**Parameters**

| Parameter | Type |
| ------ | ------ |
| `limit` | `int` |

**Returns**

`None`

**Raises**

- `SonioxAPIError` When the API returns an error.