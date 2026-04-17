# envdiff

A CLI tool to compare `.env` files across environments and flag missing or mismatched keys.

---

## Installation

```bash
pip install envdiff
```

Or install from source:

```bash
git clone https://github.com/yourname/envdiff.git
cd envdiff && pip install .
```

---

## Usage

Compare two `.env` files and see what's different:

```bash
envdiff .env.development .env.production
```

**Example output:**

```
Missing in .env.production:
  - DEBUG
  - LOCAL_DB_URL

Mismatched keys:
  ~ APP_PORT  (development: 3000 | production: 8080)

✔ All other keys match.
```

You can also compare multiple files at once:

```bash
envdiff .env.development .env.staging .env.production
```

Use `--keys-only` to suppress values and only show key differences:

```bash
envdiff .env.development .env.production --keys-only
```

Run `envdiff --help` for a full list of options.

---

## Why envdiff?

Keeping `.env` files in sync across environments is error-prone. `envdiff` makes it easy to catch missing variables before they cause issues in staging or production.

---

## License

MIT © [yourname](https://github.com/yourname)