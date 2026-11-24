# BikeFit

- Result shape: `engine.py` results are read by `web/app.py` (`rescore`, `_summary`), `report.py` and `web/static/js/app.js` (`renderSide`). After adding an analysis mode, extend `tests/test_contract.py`.
- Reference repo `doniwirawan/bike-fit-analyzer` is PolyForm Shield, not open source. Take ideas, formulas and cited studies from it; write the code yourself. Sources for every target range live in `docs/RESEARCH.md`.
- Windows setup: `python -m venv .venv`, then `.venv\Scripts\pip install -r requirements.txt -r requirements-dev.txt`, then `.venv\Scripts\python -m pytest -q`. Run one `pip` at a time.
- Translations: user-facing text goes through `t(lang, "English template", **kw)` (Python, catalog `src/locale_de.py`) or `t("…", {…})` (JS, catalog `src/web/static/js/locale-de.js`). Plain static strings in the UI are translated by the DOM observer in `i18n.js`, so only strings with values in them need `t()`. `tests/test_fitcalc.py` fails when a Python template has no German entry.
- Fit calculations (`src/fitcalc.py`) are derived at score time from the stored track, so they also work for old fits; `engine.MODEL_VERSION` invalidates the cached model in `result['fit_model']`.
