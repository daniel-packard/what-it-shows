# #4471: three problems, not one

The support desk merged 412 reports about dates into ticket #4471 and marked it known. Read by body and placed by tenant, they hold three problems. Each one is filed as an issue in this repo with its report count.

- `page/problems.svx`: the new kb page (signed, `src/routes/kb/incidents/4471/problems/+page.svx` in the kb).
- `site/kb/incidents/4471/problems.html`: the page as the desk sees it, rendered from the kb (`site/` is the whole static build).
- `kb/`: the kb export, unchanged except for the added page. Counts come from the desk's own `CauseTable`. `npm install && npx vite build` renders it.
- `split.py`: recounts the problems from the kb data: `python3 split.py kb`.
