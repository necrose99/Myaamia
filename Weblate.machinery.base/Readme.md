# Weblate.machinery.base

Local Weblate + LibreTranslate deployment tooling for Algic/Algonquian
language research and revival efforts (Myaamia and cognate languages).
Part of the broader [necrose99/Myaamia](https://github.com/necrose99/Myaamia)
corpus/NLP work.

## Why `just`, not Docker

```
sudo apt install just
```

`just` is a command runner — think `make`, but without Makefile's tab
sensitivity and recipe quirks. The `weblate.justfile` here drives a bare
Debian venv install rather than Weblate's own `docker-compose.yaml`.

Docker Compose is the officially documented path and works fine for a
normal deployment. For *this* use case — repeatedly hot-patching a local
Django/Weblate install with unsupported Algic language codes — it gets in
the way:

- Testing a hot patch means rebuilding/restarting containers each time,
  which is slower and more prone to breaking than editing a venv's
  `settings.py` directly.
- The Compose setup wants a hardcoded admin password baked in at
  first-run, and it's awkward to rotate afterward. The venv install's
  `weblate createadmin --update` is a one-liner and easy to script.

## Hardware targets

Anything from a Raspberry Pi 5 (3–4GB+ RAM) up to a retired Dell
OptiPlex works. Also runs fine under Debian on WSL, or bare metal Debian.
This is intentionally low-stakes hardware — it's a research box, not
production infrastructure.

## The elephant in the room

Patching Weblate/Django's language tables outside upstream support is a
hack. It voids the warranty, so to speak, until Algic languages are more
officially supported upstream. Assume:

- The `justfile`'s base install steps (`apt-deps`, `venv`, `configure`,
  `migrate`, `createadmin`, `celery`) will get you a working, safe Weblate
  instance.
- The `patch-algic-codes` hot fix (`add_algic_languages.py`) *works*, but
  is brittle. It can crash, or in the worst case, corrupt your
  `settings.py` enough that Weblate won't start.

**Here be dragons, sea monsters, and the occasional gremlin that eats
your work.** Treat the hot-patch step as experimental every time you run
it — always assume it might not survive an upstream Weblate/Django
version bump.

## Backups — always

**Always back up your work before running the hot fix, and periodically
while doing research.**

- Weblate has built-in git integration — your translations/TMX work can
  be committed and pushed like any other git repo, or exported and
  copied to a USB drive / your home folder.
- If you're on Btrfs, take a filesystem snapshot right after a fresh
  install — once with a bare Weblate (pre-hot-patch) and once with this
  environment fully set up. That gives you a clean rollback point on
  either side of the risky step.
  - Migrating an ext4 Debian or Raspberry Pi OS install to Btrfs, and
    using `snapper` (GUI or CLI) for snapshot management, is well
    documented — a wiki/search away.
- Worst case: nuke and pave, rerun the `justfile` from scratch. That's
  the whole point of scripting the install — recovery should be boring.

## Extending the justfile

The `justfile` is meant to be added to, not treated as final. Planned/
suggested additions:

- **LibreTranslate** — add its own install/run recipes after the Weblate
  section, so it can sit alongside Weblate as a local machine-translation
  backend.
- **Rust LT engine** — for machine translation, can be wired in as an
  additional recipe once you've decided on the specific engine/binding.

## Status

Experimental, best-effort, local/LAN research use only. Not upstream-
supported. Not production-hardened.
