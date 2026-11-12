# Pic-to-List

Read the full project brief in `pic-to-list-codex-prompt.md` when it is available. Check uncertain API details against the provider's current documentation before implementing and record confirmed details in the README.

## Milestone workflow

Work through the milestones in order. Run the current milestone's acceptance checks, record the result here, summarize it to the user, and wait for their go-ahead before starting the next milestone. The user handles commits and pushes. Ask before adding a paid service, adding a dependency beyond `requests` or `pytest`, or changing the inventory CSV format.

Use Ximilar's Free plan only. If Ximilar returns a plan or trial error, stop and report it to the user.

## Milestones

- [x] **M1 — Offline mock pipeline.** `python -m pictolist run tests/fixtures/photos --mock` produced both CSVs with zero API calls. `pytest` passed all 14 tests.
- [ ] **M2 — Ximilar client and identification cache.** Verify the API contract and test Collectibles access with one photo first. For acceptance, identify or queue each of three real photos and confirm a second run makes zero API calls. The user has created a Ximilar account. Awaiting their go-ahead.
- [ ] **M3 — TCGCSV pricing.** Cache daily TCGCSV data and join it to the export. Manually spot-check market and listing prices for three cards.
- [ ] **M4 — CLI and documentation polish.** Add dry-run, improve errors, and finish setup and import instructions. Run the mock pipeline from a fresh clone using the README.
- [ ] **M5a — Eval harness and gold set.** Use about 30 user-labeled photos. Verify that `pytest evals/` prints a score table and record the baseline in the README.
- [ ] **M5b — Orchestrator and corrective retry.** Measure recovered low-confidence cards against the gold set. Keep the simple path as the default if the retry recovers none.
- [ ] **M5c — Catalog grounding and MCP tools.** Verify the Riftbound catalog check in the pipeline and exercise the tools with MCP Inspector.
