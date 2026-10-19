# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

It also applies to Claude Cowork sessions opened on this folder. If you are Claude Cowork, read the whole file; the "AI usage documentation" section in particular applies to you.

## What this repository is

The final project for MINE-4101 Ciencia de Datos Aplicada (Universidad de los Andes, semester 2026-20): a data science project for a real organization, following the ASUM-DM methodology and delivered as a data product. It is a coursework repository, not a software package. As of October 2026 it holds mostly scaffolding (environment, docs, and the first delivery's report, video and data-understanding notebook skeletons) plus the export of the data to a parquet file; no analysis or product code exists yet.

- `Proyecto Final.pdf` is the project statement and the source of truth for requirements and grading weights.
- `TODO.md` is the checklist derived from it, one section per delivery. Tick items there as work is completed.
- Deadlines: first delivery Sunday 18 October 2026, 11:59 PM; final delivery Sunday 29 November 2026, 11:59 PM.

## Conventions

- **Everything committed to the repo is written in Spanish**: README, reports, notebook prose, slides, code comments in config files. The team and graders are Spanish speakers.
- **Team member names** are listed in `README.md` under "Integrantes". Use exactly those names, in that order, on every deliverable and artifact (reports, slides, videos).
- The repository is graded directly and must be **public and self-contained**, so treat anything committed as published.
- **Do not name the municipality.** The dataset is cadastral data for a real Colombian municipality. In everything written for the project (repo files, reports, slides, video scripts, charts, notebook outputs, commit messages) refer to it only as "un municipio colombiano": no name, no department or municipality codes, no source file names that contain it. The user will decide whether to name it in the final deliverable; until they say so, do not.
- **Visual identity:** everything the project produces (reports, videos, slides, notebook charts, the data product's UI) follows the Universidad de los Andes identity: yellow, black and white, sans-serif type. Read `identidad/README.md` before designing anything visual; it summarizes the institutional manual (colors, typography, logo and legal-text rules) and lists where the style is already implemented.

## Requirements from the statement that shape the work

- The data product needs at least 3 of: ML model, REST API (or equivalent), web/mobile app, dashboard.
- Scripts and notebooks must run without errors in a clearly specified order. Document that order in the README when adding them.
- The README must cover: team members, scope, conclusions (insights), repository organization, run instructions and dependencies.
- **A separate markdown file must declare where AI was used** (implementation, interpretation, documentation), listing tools, the most relevant prompts or the general workflow. See "AI usage documentation" below.
- Each delivery includes an executive PDF report (single column, Arial 12, max 6 pages for the first delivery and 12 for the final, no cover page or table of contents) and a YouTube video (max 6 and 12 minutes). Slides must be committed to the repo. The final report is incremental: it includes the first delivery's results, adjusted to the feedback received.
- The final delivery requires at least three ML algorithms with several hyperparameter sets, a train/validation/test split with a distribution check, and a log of at least three stakeholder interactions.

## AI usage documentation

The statement requires declaring where AI was used, so every AI-assisted session on this project is logged. This applies equally to **Claude Code** and **Claude Cowork**: the user works with both at the same time, alternating turns between them within one work session, Claude Code mostly for implementation in the repo and Claude Cowork mostly for knowledge-focused work and for improving their own understanding of the course topics. Whichever you are, the logging rules below are yours to follow.

Two files, with different audiences:

- `USO_DE_IA.borrador.md` is the private, detailed log. It is gitignored, so it exists only on the user's machine. This is where you log.
- `USO_DE_IA.md` is the curated summary that is committed and graded. Never log into it session by session. Update it only when asked, by summarizing the draft under its existing headings.

### Logging rules for `USO_DE_IA.borrador.md`

- **Log without being asked.** Before you finish a turn in which you produced, changed or explained something for this project, add or update your entry. A session that only answered a trivial question about the tooling does not need one.
- **What counts for Claude Cowork:** explanations of course or project topics, research, drafting or reviewing report text and slides, interpreting results, and preparing stakeholder material all count, even when no file in the repo changes. Record the topic, what you produced or explained, and which activity in `TODO.md` it informs.
- **Structure:** dates in ascending order (`## AAAA-MM-DD`). Under each date, one section per **work session**, numbered within the day. A work session is one sitting in which the user may alternate turns between Claude Code and Claude Cowork, so it is a single shared section for both tools: `### Sesión N — Claude Code + Claude Cowork` (name only one tool if only one took part). Steps are numbered in the order they happened across both tools, and each step title ends with the tool that did it: `#### Paso N — Título corto (Claude Code)` or `(Claude Cowork)`. The template is in the HTML comment at the top of the file; follow its fields exactly.
- **Joining the current work session:** by default, add your step to the last section of today's date, even if the other tool started it, and continue its step numbering. If your tool is not yet in that section's title or in its "Herramienta y modelo" field, add it there. Start a new section only when there is none for today or the user says a new work session has started; if you cannot tell, ask.
- **Category:** tag every step as `Implementación`, `Interpretación de resultados`, `Documentación` or `Aprendizaje`. The first three are the headings of the curated file; `Aprendizaje` is for sessions that only build the user's understanding.
- **Prompts are copied verbatim**, in the language the user typed them. Everything else is written in Spanish.
- **Be factual about verification:** say what was tested and what was not, and mark anything that is your own judgement rather than something from the sources.
- **Leave `Revisión humana` for the user** unless they tell you what they reviewed or changed.
- **Append only.** The other tool writes to the same file between your turns: re-read the file immediately before writing, add your step after the last step of the current work session, and never reorder, renumber or rewrite steps you did not create. The only exception is adding your tool to the section title and "Herramienta y modelo" field, as described above.
- **Re-read before editing any file.** Because the two tools alternate on the same working copy, a file you read in an earlier turn may have changed. This applies to repo files as well as to this log.
- If the file is missing, recreate it with the same header and template comment before logging, and make sure it is still listed in `.gitignore`.

## Python environment

Python 3.12, one environment for data analysis, notebooks and the delivery videos (built with Manim Community).

```bash
uv sync                                   # create/update .venv from uv.lock
uv run jupyter lab                        # notebooks
uv run manim render -ql <file.py> <Scene> # low-quality preview render; -qh for final quality
uv run manim checkhealth                  # verify the manim install
```

There are no tests, linter or build step configured.

### How the dependency files relate

The environment must install identically with uv, pip or conda, so four files move together:

1. `pyproject.toml` declares dependencies (lower bounds only). `[tool.uv] package = false`: the repo is not an installable package.
2. `uv.lock` holds the exact, cross-platform resolution.
3. `requirements.txt` is **generated** from the lock for pip and conda users. Never edit it by hand.
4. `environment.yml` installs five native packages from conda-forge (`pycairo`, `manimpango`, `moderngl`, `glcontext`, `argon2-cffi-bindings`) and everything else via `pip -r requirements.txt`. Their versions are pinned to match `requirements.txt` exactly so pip treats them as already satisfied instead of compiling them.

To add or upgrade a dependency:

```bash
uv add <package>
uv export --format requirements-txt --no-hashes --no-emit-project -o requirements.txt
```

Then, if any of the five native packages changed version in `requirements.txt`, update the same pin in `environment.yml`. Commit all four files together.

Things that are deliberate and should not be "fixed":

- `setuptools<81` is pinned because `ydata-profiling` imports `pkg_resources`, which newer setuptools removed.
- `requires-python` is capped below 3.14 because `ydata-profiling` does not support it.
- `cryptography<49` is a uv constraint (not a direct dependency): newer versions ship no wheels for Intel macOS.
- Teammates work on Windows, macOS and Linux, on x64 and ARM. Before adding a dependency with compiled code, check it ships wheels for those platforms. The README no longer documents per-platform setup.

## Deliverables

Each delivery has its own folder (`entrega-1/` now; the final one should mirror it), with its own README:

- `reporte/reporte.tex` is the executive report, one section per statement activity, with the statement's requirements and grading weights as comments. Build with `latexmk reporte.tex` from that folder (LuaLaTeX, set in `.latexmkrc`). The compiled `reporte.pdf` is committed; LaTeX build files are gitignored.
- Page styling (cover, yellow header band, section headings, links, the `destacado` highlight box) lives in `identidad/estilo-reporte.tex`, shared by both deliveries; change the look there, not in each report. It avoids packages missing from a default Fedora TeX Live (for example `tcolorbox` skins), since teammates compile on different systems.
- The cover page counts toward the page limit and the statement recommends against cover pages, so since 17 October 2026 the first delivery uses `\portadafalse` in `reporte.tex`: a compact title block on page 1 instead of the cover (no logo, professors or date). `\portadatrue` brings the cover back.
- The logo may only be used unmodified, in color on white only, and with the legal text, as the cover does. Do not put it on the yellow band, recolor it, or create a project logo.
- The statement requires Arial 12. The template falls back to a metric-compatible font and emits a warning when Arial is missing, which is the default on Linux. The user's machine has had Arial since 12 October 2026 (Microsoft core fonts in `/usr/share/fonts/msttcore/`), but a teammate's may not. Never report a PDF as final without checking `pdffonts` shows Arial, and check the page count against the limit with `pdfinfo`.
- `notebooks/06-entendimiento-de-los-datos.ipynb` is the notebook for activity 6 (exploratory analysis and data quality). Its stages follow the exploration process from the course's EDA slides; stages 1 to 7 hold the analysis, with shared helpers in `entrega-1/notebooks/utilidades_eda.py` (including a quality log, `BitacoraCalidad`, whose table is stage 6.3), and the interpretation cells and the stage 8 conclusions are written. It reads `datos/predios/predios.parquet`, which is gitignored (it still identifies the municipality) and is built from the pruned database as `datos/predios/README.md` explains. Stage 2 splits it into three tables (`predios`, `construcciones`, `unidades`) and defines `COLUMNAS_RESERVADAS`: columns whose values never appear in an output. Notebooks are committed with their outputs, so no cell output may show personal data or anything that identifies the municipality (stage 2 of the notebook lists what that covers). Charts use `identidad/graficas.mplstyle`, loaded in the notebook's first stage; do not call `sns.set_theme()` after it. After changing a notebook, re-run it top to bottom with the command in the root README, which also lists the run order.
- `video/video_entrega_N.py` is the manim video; `video/guion.md` (the script the members read) and `video/diapositivas.pptx`/`.pdf` (the slides the statement requires in the repo) are generated from it and must not be edited by hand.

## Videos (manim + Gemini TTS)

**Read `herramientas_video/README.md` before creating or changing a video.** It is the full workflow (ported from another project of the user's where it is proven), the anatomy of a video file, the content rules and the known manim pitfalls. The essentials:

- Run everything from the repository root. Manim writes to `media/` there, which is gitignored; final videos go to YouTube.
- The narration lives in the video file as `self.narrar((text, action), ..., quien=DANIEL)` calls on `EscenaNarrada` (`herramientas_video/escena.py`). Each call is one step of the script and one slide. `quien` assigns the text to a team member, which sets the prototype voice, the on-screen speaker label and the attribution in `guion.md`.
- Voice is prototyped with Gemini TTS through Vertex AI, configured in `.env` at the root (gitignored; `.env.template` documents it). Never print, commit or copy the contents of `.env`. In the end each member reads their own part; the TTS voice is not the final audio.
- Draft mute first, then add voice:

  ```bash
  VOZ_SERVICIO=silencio uv run manim -ql entrega-1/video/video_entrega_1.py <Escena>   # mute draft, no API calls
  uv run python -m herramientas_video.guion entrega-1/video/video_entrega_1.py        # regenerate guion.md: duration vs limit, time per member
  uv run manim -qh --fps 30 entrega-1/video/video_entrega_1.py VideoCompleto           # with voice; spends API quota
  uv run python -m herramientas_video.diapositivas entrega-1/video/video_entrega_1.py # slides
  uv run python -m herramientas_video.revisar_voz "fragmento"                          # transcribe a cached clip
  ```

- Voice clips are cached in `media/voiceovers/` by exact text, voice and model: changing a comma regenerates the clip. Do not run two voiced renders at once (they share `cache.json`). Regenerate `guion.md` whenever the narration changes.
- After a mute draft, look at frames (the README shows the ffmpeg contact-sheet command) for text running off screen or overlapping elements before spending quota on voice.
- `revisar_voz` is an automatic transcription. If you rely on it, tell the user that nobody has listened to the video.
- The statement requires all four members to take part with similar speaking time and caps the video at 6 minutes (first delivery) or 12 (final): check both in `guion.md`.
- Text on screen uses `Text` (no LaTeX needed); `Tex` and `MathTex` need a LaTeX installation. ffmpeg is not required to render.

## `course-contents/`

Local-only reference material from the course (slides, syllabus, schedule, tutorial notebooks with their datasets). Everything in it is gitignored except `course-contents/README.md`, which documents what the folder should contain and which slide deck supports which project activity. Use the material to ground methodology choices in what the course teaches, and never commit it or copy its datasets elsewhere in the repo. It may be absent or incomplete on a given machine.
