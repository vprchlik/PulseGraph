# npm data redistribution review: what the governing documents allow before publication

Documents read 2026-10-15 between 11:04 and 11:15 UTC. `PROTOCOL.md` (Study 2, "Domains, frame and
selection") requires data redistribution evidence before publication, and its provenance section says the
open source-redistribution checks must precede publication. This document is that check for npm. It reads
the terms that govern the npm public registry, its replication feed and its download-counts API, and
answers what the paper and the repository may publish from the frozen npm panel. It is a reading of public
documents, not legal advice. Sentences marked (judgment) are judgments; the rest reports what the documents
say. Quotations are at most one sentence. No request was made to the npm data endpoints for this review.

## What is to be published

From the record (`study/study2/npm_panel_status.json`, `reports/study2-npm/panel/`):

- **Already committed (2026-10-15, `e5321cd`):** `reports/study2-npm/panel/manifest.json` and
  `selection.json`. Each lists 9,998 complete candidates by package name (scope included), registry
  creation timestamp, registry revision identifier, SHA-256 of the captured metadata document, selection
  hash, stratum and the zero fraction of the last 90 context days; the 209 selected series; the capture
  evidence (URL, acquisition time, SHA-256 of each saved answer); the frame estimates. No maintainer
  name, e-mail, description or README text is in either file.
- **Not committed:** `data/raw/study2/npm/panel/context.parquet` (76,165 bytes; the daily download counts
  of the 209 series for 2025-09-01 to 2026-06-02); the 27,436 saved answers under
  `data/raw/study2/npm/captures/` and their ledger (URL, time, status, SHA-256; no headers, no
  credentials); the inventory of 4,486,927 names from the replication feed; the candidate-walk ledger.
  The 12,943 saved registry metadata documents contain maintainer names and e-mail addresses as the
  registry serves them.
- **To come:** the targets to 2026-08-31 for the 209 series, under the author's target-access approval.
- **The paper** will publish aggregate tables (per-package zero fractions, scores, paired tables) and may
  publish the daily counts of the 209 named packages as a dataset under CC BY 4.0.

The pull of 2026-10-14 00:23 UTC to 2026-10-15 01:57 UTC made 30,198 HTTP attempts: 12,943 to
`registry.npmjs.org`, 12,762 to `api.npmjs.org`, 4,493 to `replicate.npmjs.com`, spaced at least one
second apart, and at least three seconds from 2026-10-14 22:51 UTC. The download API answered 429 to
2,708 attempts; three 429 answers in a row stopped an invocation, which resumed later from the saved
captures. The approval was 36,000 requests and 13 hours.

## The documents read

| Document | Its own date | What it governs | Read |
|---|---|---|---|
| [npm Terms and Licenses](https://docs.npmjs.com/policies/terms/) (index) | none | Routes free use of `www.npmjs.com` and the public registry to the Open-Source Terms | 2026-10-15 |
| [npm Open-Source Terms](https://docs.npmjs.com/policies/open-source-terms) | "last updated ... March 10, 2022"; its source file last changed 2025-09-23 (legal contact e-mail) | The Website and the Public Registry at `registry.npmjs.org`, together "npm Open Source"; with paid services, "npm Services" | 2026-10-15 |
| [npm Replication and web crawler policy](https://docs.npmjs.com/policies/crawlers/) | none; added to the policies repository 2021-07-16, unchanged since 2022-03-01 | Crawling the website; replication of the registry | 2026-10-15 |
| [npm license](https://docs.npmjs.com/policies/npm-license/) (Artistic License 2.0 with npm's additional terms) | none | The npm software; one sentence on registry data | 2026-10-15 |
| [npm Privacy Policy](https://docs.npmjs.com/policies/privacy) | "took effect June 3, 2020" | What npm collects and publishes, including package metadata | 2026-10-15 |
| [npm Logos and Usage](https://docs.npmjs.com/policies/logos-and-usage) (trademark) | none | Use of the npm name and logos | 2026-10-15 |
| [npm/registry `download-counts.md`](https://github.com/npm/registry/blob/main/docs/download-counts.md) | last changed 2024-05-06 | The download-counts API at `api.npmjs.org`: endpoints, data source, limits | 2026-10-15 |
| [npm/registry `REGISTRY-API.md`](https://github.com/npm/registry/blob/main/docs/REGISTRY-API.md), [`REPLICATE-API.md`](https://github.com/npm/registry/blob/main/docs/REPLICATE-API.md), [README](https://github.com/npm/registry) | none; the README calls the repository "archived documentation" | The registry and replication endpoints | 2026-10-15 |
| [npm blog, how download counts work](https://blog.npmjs.org/post/92574016600/numeric-precision-matters-how-npm-download-counts-work.html) | 2014-07-22 | What a download is | 2026-10-15 |
| [npm blog, API rate limiting](https://blog.npmjs.org/post/164799520460/api-rate-limiting-rolling-out.html) | 2017-08-30; marked by npm as no longer applicable | Rate limiting of the registry APIs, 429 answers | 2026-10-15 |
| [npm blog, acceptable use](https://blog.npmjs.org/post/187698412060/acceptible-use.html) | 2019-09-13 | The five-million-requests-a-month line | 2026-10-15 |
| [GitHub Terms of Service](https://docs.github.com/en/site-policy/github-terms/github-terms-of-service) | effective 2026-04-27 | GitHub's Service; does not name npm | 2026-10-15 |
| [GitHub Terms for Additional Products and Features](https://docs.github.com/en/site-policy/github-terms/github-terms-for-additional-products-and-features) | effective 2026-08-27 | Has an "npm" section | 2026-10-15 |
| [GitHub Acceptable Use Policies](https://docs.github.com/en/site-policy/acceptable-use-policies/github-acceptable-use-policies) | none; source file last changed 2026-07-09 | Information usage restrictions, research use | 2026-10-15 |
| [GitHub General Privacy Statement](https://docs.github.com/en/site-policy/privacy-policies/github-general-privacy-statement) | effective 2026-04-27 | Does not name npm | 2026-10-15 |

The policy texts were read from their sources in the `npm/documentation` repository (licensed CC BY 4.0)
and the `github/docs` repository, with the rendered pages checked for the dates. The `npm/registry`
repository has no licence file.

## What the documents say

**Which terms govern which service.** The Open-Source Terms govern "https://www.npmjs.com (the Website)
as well as the 'npm Public Registry' at https://registry.npmjs.org (the Public Registry)". The CLI
documentation says use of the public registry is subject to the terms at `docs.npmjs.com/policies/terms`.
GitHub's Terms for Additional Products and Features list npm as an additional product and say "Acceptable
use of the npm registry is outlined in the open-source terms" and "The npm Terms of Use apply to your use
of npm." The GitHub Terms of Service and the GitHub Privacy Statement do not mention npm. Neither
`replicate.npmjs.com` nor `api.npmjs.org` is named in any terms document; the replication feed and the
download-counts API are documented publicly in `npm/registry`, and the Open-Source Terms define Public
APIs as "application programming interfaces that npm publicly documents or makes available for public
use". (judgment) The conservative reading treats all three hosts as npm Services under the Open-Source
Terms.

**Replication and automated access.** Acceptable Use item 9: "You will not automate access to, use, or
monitor the Website, such as with a web crawler ... You may replicate data from the Public Registry using
the Public APIs per this Agreement." The crawler policy: "npm's full public dataset is available via the
public registry", a full copy of all metadata can be had by CouchDB replication, and it "is acceptable
within our terms of use to download copies of tarballs for inspection or experimentation". The one-
request-per-second rule in that policy is for "experimental crawlers" of the website, and the ban it
reserves is for "high-velocity crawling of the npm website".

**Request volume.** Acceptable Use item 17: you will not "strain infrastructure of npm Services with an
unreasonable volume of requests"; the rule "is intentionally loose"; the one clear line is that five
million requests to npm Services in a single month by one party are not reasonable. The 2019 blog post
gives the same line. The 2017 post announced "more explicit rate-limiting for all registry apis", asked
clients to handle HTTP 429, and gave the download API's range caps (18 months per package; 128 packages
and 365 days in bulk); npm marks that post as no longer applicable. No document read states a requests-
per-minute quota for `api.npmjs.org`. Item 16: you will not "disable, avoid, or circumvent any security or
access restrictions of npm Services".

**Data about packages.** The privacy policy: "When you publish a package to the npm public registry ...
npm makes the package and metadata available to everyone, online", and the registry APIs are "special
software services that others use to copy data from the npm public registry". The npm license page: "Data
published to the npm registry is not part of npm itself, and is the sole property of the publisher." The
Open-Source Terms: "Your Content belongs to you. You decide whether and how to license it." Acceptable Use
item 4: "You will not copy or share any personally identifiable information of any other person without
their specific permission." Item 14: you will not remove "any marking indicating proprietary ownership
from any material got via npm Services". Package names and creation timestamps carry no such marking.

**Download counts.** `download-counts.md` describes a "public api that gives you download counts by
package and time range", built once a day from npm's own request logs. The 2014 post defines a download
as a count of HTTP 200 tarball responses, including mirrors, build servers and bots, and calls the counts
a directional indicator, not a user count. No document read states a licence, an attribution requirement,
an ownership claim or a reuse restriction for the counts. They are not "data published to the npm
registry" by a publisher; they are npm's own derived record of requests.

**Use restrictions on data.** The Open-Source Terms restrict two kinds of data: package security data
(Conditions item 4: "only for your own personal or internal business purposes", not to be provided to
others) and personal information (Acceptable Use item 4). Nothing else in the Terms, the crawler policy,
the licence page or the privacy policy restricts what may be done with registry metadata or download
counts once obtained, and nothing grants a licence to them either. Using the Public Registry "as a
general purpose database" is barred in Acceptable Content; that clause is about what may be published to
the registry.

**GitHub's policies, if they reach npm.** The Acceptable Use Policies, section 7: "Researchers may use
public, non-personal information from the Service for research purposes, only if any publications
resulting from that research are open access", "regardless of whether the information was scraped,
collected through our API, or obtained otherwise"; use must comply with the GitHub Privacy Statement;
information may not be used for spam. Section 6 bars reproducing, copying, selling or exploiting "any
portion of the Service" without written permission. "Service" is defined in the Terms of Service as the
applications, software, products and services provided by GitHub; npm is listed as an additional product
under the same Agreement. (judgment) Whether these sections bind use of npm data is not stated; if they
do, the research clause permits the planned use, since TMLR and Zenodo are open access, and a table of
counts is not a reproduction of the Service.

**Trademark.** The Logos and Usage policy allows nominative use: "it's perfectly OK to use 'npm' to refer
to npm, Inc., the npm client, npm code, and the npm public registry." Its general rules ask that the
public registry be called the "npm registry" or "npm public registry", that the operator be named "npm,
Inc.", and that materials referring to npm carry the notice "npm is a registered trademark of npm, Inc."
Logos need permission.

**Removal.** npm may remove packages (unpublish policy, licence page: data "may be removed or modified at
the sole discretion of the npm server administrators"). The privacy policy acknowledges that npm "can't
make everyone who has downloaded published package data or account data erase that data".

## The five questions

| Question | Answer | Clause |
|---|---|---|
| May aggregate statistics derived from the download counts (per-package zero fractions, scores, tables) be published? | Yes. No document restricts derived use of the counts; the only data-use restrictions are on security data and personal information. If GitHub's Acceptable Use Policies apply, the research clause requires open-access publication, which the plan meets. | Open-Source Terms, Conditions 4 and Acceptable Use 4 (the only restrictions); GitHub AUP section 7 (research, open access). Licence or attribution for the counts: not stated. |
| May the daily counts of 209 named packages be redistributed as a dataset, and under what attribution? | Not stated. No document grants a licence to the counts, claims ownership of them, or forbids redistributing them; replication of registry data through the public APIs is expressly allowed and the crawler policy calls the registry "npm's full public dataset". Attribution: not required by any document; the trademark notice applies if the npm name is used. (judgment) The conservative reading: redistribute with a data statement that names the source, the endpoint, the retrieval window and the absence of a stated licence, and apply CC BY 4.0 to the project's own selection, derived fields and documentation rather than asserting it over the counts as such. | Acceptable Use 9 (replication allowed); crawler policy ("full public dataset"); download-counts.md and the 2014 post (no licence stated); Logos and Usage (notice). |
| May package names and metadata (creation dates) be published? | Yes, for names and creation timestamps. The privacy policy says npm publishes package metadata "to everyone, online" and that the registry APIs exist for others to copy it; the licence page makes registry data the publisher's property, which bears on package contents and expressive metadata, not on a name or a timestamp. Maintainer names and e-mail addresses are personal information and stay out (Acceptable Use 4). Scoped names embed a user or organization name; these are public identifiers published by npm, and the manifest is already committed with them. | Privacy policy ("npm collects package data"; "How can I see what data is publicly available"); npm license page; Acceptable Use 4 and 14. |
| Is there any rate, use or purpose restriction the pull may have breached? | None identified. 30,198 attempts in about 26 hours is far under the one stated line (five million a month); the website was not crawled, so the one-request-per-second rule does not apply; replication through the public APIs is allowed; no purpose restriction covers research use. The download API answered 429 to 2,708 attempts; the client stopped on three in a row, resumed later, and widened its spacing to three seconds, which is the behaviour the 2017 announcement asks for. (judgment) Honouring 429 answers and resuming later is not circumvention under item 16, but the number of 429 answers shows the pull repeatedly reached npm's throttle, and the paper's data statement should say so. No requests-per-minute quota is documented, so "unreasonable" remains at npm's discretion. | Acceptable Use 9, 16, 17; crawler policy; 2017 and 2019 posts. |
| Does anything restrict publishing the capture hashes or request logs? | No. They are the project's own records of its requests: URL, time, status and SHA-256, with no headers, tokens or personal data. The npm privacy policy concerns data npm holds about users, not a user's record of its own requests. The response bodies are a different matter: the registry metadata documents contain maintainer names and e-mail addresses and stay out of the tree; the download-API bodies hold only counts. | Not stated anywhere; Acceptable Use 4 for the response bodies. |

## Recommendation (judgment)

What the paper and the repository may publish, and how:

1. **Aggregate tables, zero fractions, scores, paired tables, figures:** publish. Cite the npm download-
   counts API by its documentation URL, the retrieval window (2026-10-14 to 2026-10-15 UTC) and the
   context window; say that a download is a tarball request as npm counts it, including mirrors and bots,
   per npm's 2014 explanation.
2. **The 209 daily series as a dataset (context now; targets after the run):** publish, with the manifest,
   under CC BY 4.0 applied to the project's compilation (the selection, the derived fields, the
   documentation), and a data statement in the dataset and the paper: counts obtained from
   `api.npmjs.org/downloads/range` on the dates given; package names and creation timestamps from
   `registry.npmjs.org` and `replicate.npmjs.com`; npm, Inc. states no licence for the counts and its
   Open-Source Terms of 2022-03-10 contain no restriction on their redistribution; names are as the
   registry served them at acquisition and may since have been removed; the pull reached npm's rate
   limit 2,708 times and honoured it. Add the notice "npm is a registered trademark of npm, Inc." Use no
   npm logo. Call the service the "npm public registry" and the operator "npm, Inc."
3. **Package names and creation timestamps:** publish, as already committed in the manifest and
   selection files. Publish no maintainer name, e-mail, description or README text.
4. **The repository:** `context.parquet` (76 KB) may be committed as the aggregated daily-count dataset
   that `CONTRIBUTING.md` names, with its SHA-256 already in the manifest; the capture ledger (URL, time,
   status, hash) may be committed as evidence. The saved response bodies, the 4.49-million-name inventory
   and the candidate-walk ledger stay out of the tree as raw captures; if the inventory is needed for
   reproduction, it goes as a release asset with its checksum, as the protocol's provenance section
   provides.
5. **Stays out:** the registry metadata response bodies (maintainer personal data); any token or header;
   the per-version or per-user data the project never fetched.
6. **Where the terms are silent:** the counts' licence and attribution are not stated. The conservative
   course is the data statement above. A written answer from npm, Inc. (support or `legal-support@github.com`)
   confirming that the download counts may be redistributed would turn "not stated" into stated; no
   document read requires it, and the project may publish without it on the reading above. That is the
   author's call.
7. **Removal requests:** if a publisher asks that a package be removed from the dataset on privacy
   grounds, remove the name and keep the series under its selection hash; the protocol's exclusion
   ledger records it.

## What could not be verified

- No document read names `api.npmjs.org` or `replicate.npmjs.com`. That the Open-Source Terms govern
  them is the conservative reading, not a stated fact.
- Whether GitHub's Acceptable Use Policies bind use of npm data is not stated: the Terms for Additional
  Products place npm under the GitHub Agreement, but the Acceptable Use Policies define "Service" through
  the Terms of Service, which do not name npm. The research clause, if it applies, is permissive.
- No requests-per-minute quota for the download API is documented anywhere read; the 2017 announcement
  that promised documentation of limits is marked no longer applicable, and nothing replaced it in the
  documents read.
- The crawler policy and the registry documentation carry no dates of their own; the dates given are from
  the repositories' commit histories.
- The Open-Source Terms' rendered page shows the 2022-03-10 date; the source file changed on 2025-09-23
  to update the legal contact e-mail only, per the commit message, and that diff was not read.
- Precedents, not authority: ecosyste.ms republishes npm package metadata with download figures under
  CC BY-SA 4.0 (its footer, read 2026-10-15); Libraries.io's dumps of npm metadata on Zenodo are under
  CC BY-SA 4.0 (2020); the licence of Google's deps.dev BigQuery dataset could not be confirmed from its
  documentation. None of these states npm's position.
- This is a reading of public documents by the project, not legal advice; the governing law and dispute
  sections of the Open-Source Terms were not analysed.
