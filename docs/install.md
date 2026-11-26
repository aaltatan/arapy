# Installation

arapy needs Python 3.12 or newer. The core has no dependencies.

=== "uv"

    ```bash
    uv add arapy
    ```

=== "pip"

    ```bash
    pip install arapy
    ```

## Optional extras

Two features need third-party packages. They are imported only when you use them.

| Extra | Installs | Needed for |
| --- | --- | --- |
| `hijri` | `hijridate` | [`HijriDate`](guide/dates.md#hijridate) and `ArDate.to_hijri()` |
| `shape` | `arabic-reshaper`, `python-bidi` | [`shape()` and `reshape_only()`](guide/shape.md) |

=== "uv"

    ```bash
    uv add "arapy[hijri]"
    uv add "arapy[shape]"
    uv add "arapy[hijri,shape]"
    ```

=== "pip"

    ```bash
    pip install "arapy[hijri]"
    pip install "arapy[shape]"
    pip install "arapy[hijri,shape]"
    ```

Without the extra, the call raises `MissingExtraError`, which names the command to run:

```text
arapy.errors.MissingExtraError: This feature needs the 'hijri' extra.
Install it with: `pip install "arapy[hijri]"` or `uv add arapy[hijri]`
```

`MissingExtraError` is also an `ImportError`, so `except ImportError` catches it.

## Check the install

```python
import arapy

print(arapy.to_words(2026))  # ألفان وستة وعشرون
```
