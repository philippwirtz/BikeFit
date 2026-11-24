# BikeFit

- Result shape: `engine.py` results are read by `web/app.py` (`rescore`, `_summary`), `report.py` and `web/static/js/app.js` (`renderSide`). After adding an analysis mode, extend `tests/test_contract.py`.
- Reference repo `doniwirawan/bike-fit-analyzer` is PolyForm Shield, not open source. Take ideas, formulas and cited studies from it; write the code yourself. Sources for every target range live in `docs/RESEARCH.md`.
- Windows setup: `python -m venv .venv`, then `.venv\Scripts\pip install -r requirements.txt -r requirements-dev.txt`, then `.venv\Scripts\python -m pytest -q`. Run one `pip` at a time.
