# Recruiter-Facing Repository Checklist

Use this before adding the repository to a CV or application.

## Highest Priority

- [ ] README opens with the business problem, not a technology list
- [ ] Add 3–5 dashboard / email screenshots under `docs/images/`
- [ ] Embed the strongest screenshot near the top of README
- [ ] Clearly state that all published data is synthetic / fabricated
- [ ] Remove any real customer names, phone numbers, outlet IDs or confidential source files
- [ ] Make sure the repository can be understood in under 60 seconds
- [ ] Add the exact command required to run the project
- [ ] Add a `requirements.txt` generated from the actual project environment
- [ ] Remove unused notebooks, duplicate exports and temporary files
- [ ] Verify all links in README

## GitHub About Section

Recommended description:

> Retail activation intelligence for 60 promoter-led stores — Python analytics, funnel diagnostics, availability intelligence and automated weekly reporting.

Recommended topics:

`python` `pandas` `data-analytics` `business-intelligence` `retail-analytics` `automation` `data-visualization` `html-email` `google-cloud-run`

## Repository Structure

Prefer:

```text
README.md
data/sample/
src/
outputs/
docs/
notebooks/
scripts/
requirements.txt
.gitignore
```

Avoid a root directory containing many unrelated CSV, XLSX, PNG and HTML files.

## Screenshots To Add

1. Executive Control Tower
2. Conversion & Shopper Intelligence
3. Availability & SKU Intelligence
4. Outlet Opportunity Engine
5. Weekly Performance Flash

Crop screenshots tightly and avoid showing local file paths, browser tabs or personal information.

## Code Hygiene

- [ ] Functions have clear names
- [ ] No hard-coded passwords / API keys
- [ ] No absolute local paths
- [ ] Configuration values are separated from business logic
- [ ] Repeated calculations are centralised
- [ ] Comments explain *why*, not every obvious line
- [ ] Remove dead / experimental code
- [ ] Include a small sample dataset that lets someone understand the input format

## Storytelling

A recruiter should be able to answer these after reading the README:

- What business problem was solved?
- What data was available?
- What did the candidate personally build?
- What KPIs were defined?
- What insights / actions does the solution produce?
- What tools were used?
- How is the workflow automated?
- What are the limitations?

## Nice-To-Have

- [ ] Architecture diagram
- [ ] KPI dictionary
- [ ] Data dictionary
- [ ] Short GIF or dashboard walkthrough
- [ ] One-command runner
- [ ] Tests for KPI calculations
- [ ] GitHub Actions smoke test
- [ ] License, if you want others to reuse the code
- [ ] Pin the repository to the GitHub profile
- [ ] Add a social preview image
