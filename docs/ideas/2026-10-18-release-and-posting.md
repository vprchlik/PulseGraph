# The release and the two postings: the checklist for the day

Written 2026-10-18 07:29 UTC. The author uploads and posts in person; this page lists what he uploads, in order,
what each form asks for, and what he pastes back so that the tree can record it. Two postings are due: the
Study 1 report on Zenodo by **2026-10-24**, and the three-study paper on Zenodo and to TMLR by **2026-10-31**. Both
say their numbers regenerate from files that only the GitHub release will publish, so the release comes first.
The files and their hashes are in `reports/release/ASSETS.md`; the posting route was decided on 2026-10-13
(`docs/PLAN.md`, "Open with the author", item 1) and the Zenodo steps were first written in
`docs/ideas/2026-10-11-report-link-title-abstract.md`. No page was re-read for this checklist (no network): where a
form's labels are named they are as the record has them and may differ on the day.

## The order of the day

1. Commit and push the release preparation. The tag below is made on that commit.
2. On this machine, check the files to upload: `.\.venv\Scripts\python.exe reports\release\verify_assets.py
   data\release` prints six lines starting `OK` and exits 0.
3. The GitHub release: tag, title, the six assets in the order below, publish. Paste back the release page's URL.
4. Download the six assets back from the release page into an empty folder, `downloads\`, and run
   `.\.venv\Scripts\python.exe reports\release\verify_assets.py downloads`; paste back its six lines. This shows
   that GitHub serves the bytes `ASSETS.md` lists.
5. The tree records the URLs in the next commit: the URL column of `ASSETS.md` and the "Release" line of
   `README.md`'s first screen.
6. By 2026-10-24, the report on Zenodo as version 1, with its DOI reserved first and printed in the PDF. Paste back
   the record's URL, the version DOI and the concept DOI.
7. By 2026-10-31, the paper on Zenodo as version 2 of the same record, then the TMLR submission through OpenReview.
   Paste back the version 2 DOI and the OpenReview submission's URL or number.

## 1. The GitHub release

On `https://github.com/vprchlik/PulseGraph`, "Releases", then "Draft a new release".

- **Tag:** `assets-2026-10-18`, new, on `main` at the pushed commit of step 1 (the tag names the day the assets were
  built and hashed, the date on `ASSETS.md`).
- **Title:** `Saved forecasts and target signals of the three studies (assets of 2026-10-18)`.
- **Description,** to paste:

  > The files the documents' numbers trace to that are not in the tree: Study 1's results file, the 1,049
  > whole-series checkpoints of the Study 2 and Study 3 runs, and the npm and NYC 311 target signals. Their sizes,
  > SHA-256 values, places in the tree and the commands that then regenerate the numbers are in
  > `reports/release/ASSETS.md`; `reports/release/verify_assets.py` checks a download and unpacks the
  > checkpoints. Data statements and licences: the same page, section "Licences". npm is a registered trademark of
  > npm, Inc.

- **Not** a pre-release.
- **The assets, in upload order,** all from `data\release\` (550,927,259 bytes in all; each under the 2 GiB per-file
  limit). `results.parquet` goes first because the report, due first, depends on it alone:

  | Order | File | Bytes | For |
  |---:|---|---:|---|
  | 1 | `results.parquet` | 433,172,286 | Study 1: the report and the paper |
  | 2 | `study2-npm-targets-signals.parquet` | 105,460 | Study 2 on npm |
  | 3 | `study3-nyc311-targets-signals.parquet` | 91,655 | Study 3 on NYC 311 |
  | 4 | `study2-npm-run-2026-10-15-checkpoints.zip` | 25,249,139 | Study 2 on npm |
  | 5 | `study3-nyc311-run-2026-10-17-checkpoints.zip` | 38,676,505 | Study 3 on NYC 311 |
  | 6 | `study2-synthetic-2026-10-15-checkpoints.zip` | 53,632,214 | Study 2, the synthetic grid |

  `data\release\assets.json` and `data\release\.gitignore` are working files of the build and are not uploaded.
- **What to paste back:** the release page's URL. Each asset's link should then read
  `https://github.com/vprchlik/PulseGraph/releases/download/assets-2026-10-18/<file>`; the six URLs
  are checked against that pattern before they are written into `ASSETS.md`.

## 2. Zenodo, the Study 1 report (version 1, by 2026-10-24)

Sign in to Zenodo (GitHub sign-in works) and start a new upload.

1. **Reserve the DOI** before uploading anything (the record calls the step "Reserve DOI"). Put it into
   `paper/main.tex` where it is marked (`\reportdoi`, "DOI to be filled on posting day") and build the final PDF.
2. **The file:** the report's PDF, built from `paper/main.tex`.
3. **Resource type:** Publication, Report.
4. **Title:** *Zero-shot foundation models on sparse daily GitHub star counts: a registered re-evaluation after an
   audit* (`paper/SUMMARY.md`, "Title").
5. **Abstract:** the paragraph under "Abstract" in `paper/SUMMARY.md`, as it stands on the day.
6. **Creator:** Victor Prchlik.
7. **Licence:** Creative Commons Attribution 4.0 International (CC BY 4.0).
8. **Publication date:** the day of posting.
9. **Related identifiers:**
   - the repository, `https://github.com/vprchlik/PulseGraph`, as "is supplemented by";
   - the protocol's registration commit, `https://github.com/vprchlik/PulseGraph/commit/5f01769b6be4c32814befdd7cc3395b6dcc386ed`;
   - the release of step 1, `https://github.com/vprchlik/PulseGraph/releases/tag/assets-2026-10-18`, as "is
     supplemented by".
10. **Publish.** Paste back the record's URL, its DOI (version 1) and the concept DOI that covers every version.

The assets stay on the GitHub release, with the record pointing to it, so that each file has one copy and one hash
(recommended). Zenodo can also hold them for durability; that is the author's choice, and if taken the six go on the
paper's version 2 record with their SHA-256 values unchanged.

## 3. Zenodo, the paper (version 2, by 2026-10-31)

On the report's record, "New version"; version 2 gets its own DOI under the same concept DOI.

1. **Reserve the DOI**, put it into `paper/paper.tex` where it is marked (`\reportdoi`), build the final PDF.
2. **The file:** the paper's PDF, built from `paper/paper.tex`.
3. **Resource type:** Publication, Preprint.
4. **Title and abstract:** from `paper/PAPER-SUMMARY.md` **as it stands on the day**; re-read that file before
   pasting, since it was still being revised on 2026-10-18. As of this writing the title is *Size, not occurrence:
   what zero-shot foundation models add on sparse daily counts*.
5. **Creator, licence, publication date:** as for version 1.
6. **Related identifiers:** the repository; the three registration commits,
   `https://github.com/vprchlik/PulseGraph/commit/5f01769b6be4c32814befdd7cc3395b6dcc386ed` (Study 1),
   `https://github.com/vprchlik/PulseGraph/commit/df55867c982dfe2bb6e1152ec8ae93e3cd228c45` (Study 2) and
   `https://github.com/vprchlik/PulseGraph/commit/3357d779db28cffa4048e7e333fd02b9434b4b6d` (Study 3); the release
   of step 1. Zenodo links version 1 itself.
7. **Publish.** Paste back the version 2 DOI.

## 4. TMLR, through OpenReview (by 2026-10-31)

What the record says about TMLR (`docs/ideas/2026-10-11-report-link-title-abstract.md`;
`docs/research/2026-10-17-paper-shape-review.md`, Part D, from TMLR's acceptance criteria, FAQ and reviewer guide
read on 2026-10-17):

- Submission is through OpenReview, with no fee and no arXiv requirement, and a prior preprint is allowed, so
  Zenodo version 2 can come first.
- Two acceptance criteria: claims supported by accurate and convincing evidence, the more important, and interest
  to some of the journal's audience. Novelty is not required, and a gap between claim and evidence may be closed by
  narrowing the claim.
- A main body of up to twelve pages gets two weeks of review, a longer one four; the journal aims at a decision about
  nine weeks after submission and asks for shorter manuscripts. By the word count of the review of 2026-10-18 the
  body is about 12.8 pages, 13.8 if the two full-page tables count as a page each; the cut is the author's.
- The Reproducibility Certification is for reproductions of other published work and does not fit this paper.

What the record does not say, to be read on TMLR's and OpenReview's pages before the upload:

- **Anonymity.** Whether the submitted PDF must be anonymized. TMLR is generally described as reviewing
  double-blind; if so, the submitted PDF cannot carry the author's name, the repository's URL, the Zenodo DOI or the
  author's statement (`paper/shared/author-statement.tex`, which `paper/paper.tex` includes) as they stand, and an
  anonymized build is needed beside the Zenodo one. This is the item most likely to change the day's work.
- **The style file.** TMLR's LaTeX style and its effect on the page count (not checked, as the review of
  2026-10-18 says).
- **The form.** The OpenReview fields (abstract length, keywords, any declarations), supplementary material, and
  the OpenReview profile the submitting author needs.

Paste back the submission's URL or number.

## 5. After the postings: what changes in the tree

- `reports/release/ASSETS.md`: the URL column (six links) and the "Release" line; `README.md`: the "Release" and
  "DOI" lines of the first screen. These are written from the pasted values in the next commit.
- `paper/check_numbers.py` asserts that `README.md` contains "to be filled" (line 581) and that the paper says the
  results file "is to be published as a GitHub release asset" (line 582). Once the URL and the DOI are filled in,
  the paper's sentences and the checker change in the same commit, or the checker fails. The paper's sentences on
  release assets also say the aggregated daily counts are to be released as assets; they are committed in the tree
  instead (`reports/study2-npm/panel/daily_counts.csv`, `reports/study3-nyc311/panel/daily_counts.csv`), and the
  target signals are assets.
- `docs/STATE.md` and `docs/PLAN.md`: the release, the DOIs and the submission, in the same commit.

## What could not be verified

- No page of GitHub, Zenodo, TMLR or OpenReview was opened for this checklist. The 2 GiB per-file limit of a GitHub
  release, Zenodo's labels ("Reserve DOI", "New version", the resource types) and TMLR's requirements are as the
  record or general knowledge has them, dated where the record dates them.
- Whether TMLR requires an anonymized submission, its style file and its form: not in the record (section 4).
- That GitHub serves the uploaded bytes unchanged is checked only by step 4, after the upload.
