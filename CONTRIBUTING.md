# Contributing to NCR Ride Bookings Analysis

Thanks for your interest in contributing! 🎉

## Ways to contribute

* 🐛 **Report bugs** — open an issue using the *Bug report* template
* 💡 **Suggest features** — open an issue using the *Feature request* template
* 📊 **Improve the analysis** — new KPIs, better charts, deeper insights
* 🧹 **Code quality** — refactors, tests, documentation
* 📖 **Docs** — typos, clarifications, new sections in the README

## Getting started

1. **Fork** the repository and **clone** your fork.
2. Create a branch from `main`:

   ```bash
   git checkout -b feat/your-feature-name
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Make your changes in `analysis_script.py` (the notebook imports from it).
5. Test the full pipeline on your dataset:

   ```bash
   python analysis_script.py --data /path/to/ncr_ride_bookings.csv
   ```

6. Commit with a clear, conventional message:

   ```
   feat: add peak-hour KPI
   fix: correct profit calculation for incomplete rides
   docs: document cancellation-rate definition
   ```

7. Push your branch and open a **pull request** against `main`.

## Pull request guidelines

* Keep PRs small and focused — one logical change per PR.
* Use the pull request template and fill in every section.
* Reference any related issue (e.g. `Fixes #3`).
* If your change affects numbers shown in the README ("Key Insights"),
  re-run the pipeline and update them.
* Don't commit data files (`*.csv`) or generated outputs (`outputs/`) —
  they are gitignored.

## Style notes

* Python follows standard [PEP 8](https://peps.python.org/pep-0008/) style.
* Keep functions small and single-purpose, as the existing pipeline does.
* Document any analytical assumption in the code (`CONFIG` comments) —
  assumptions must always be explicit.

## Reporting issues

Use the issue templates in `.github/ISSUE_TEMPLATE/`. For security
vulnerabilities, do **not** open a public issue — see [SECURITY.md](SECURITY.md).

## Code of conduct

By participating in this project you agree to uphold our
[Code of Conduct](CODE_OF_CONDUCT.md).
