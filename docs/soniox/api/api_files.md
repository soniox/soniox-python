---
title: "soniox.api.files"
description: "Soniox Python SDK — soniox.api.files Reference"
keywords: "FilesAPI"
---

---

## FilesAPI

<a id="filesapi-constructor"></a>

### Constructor

```python
FilesAPI(client: SonioxClient)
```

**Parameters**

| Parameter | Type |
| ------ | ------ |
| `client` | `SonioxClient` |

**Returns**

`None`

<a id="filesapi-list"></a>

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

<a id="filesapi-list_all"></a>

### list_all()

```python
list_all(limit: int = 100) -> Generator[File, None, None]
```

Iterate through all uploaded files across all pages.

**Parameters**

| Parameter | Type |
| ------ | ------ |
| `limit` | `int` |

**Yields**

`Generator[File, None, None]`

File: The next file object from the API.

**Raises**

- `SonioxAPIError` When the API returns an error.

***

<a id="filesapi-get"></a>

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

<a id="filesapi-get_or_none"></a>

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

<a id="filesapi-delete"></a>

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

<a id="filesapi-delete_if_exists"></a>

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

<a id="filesapi-upload"></a>

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

<a id="filesapi-delete_all"></a>

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