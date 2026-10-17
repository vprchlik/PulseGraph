# NYC 311: the source's stated terms and the time basis of `created_date`

Recorded on 2026-10-16 for Study 3 (`PROTOCOL.md`, dated addition of 2026-10-16, item 7), which requires NYC
Open Data's terms to be recorded before publication and `created_date` to be a floating timestamp in New York
local time. Every request was anonymous: no app token, no credential.

## The dataset's metadata

| Item | As read |
|---|---|
| URL | `https://data.cityofnewyork.us/api/views/erm2-nwe9.json` |
| Read at | 2026-10-16 07:44:21 UTC; HTTP 200 in 0.28 s; 25,591 bytes; SHA-256 `b3a22b46e0919d3e945c7b15d7d203e9f43016bf3ef6aefa9a36d835edce93c5` |
| Dataset | `erm2-nwe9`, titled "311 Service Requests from 2020 to Present"; owner NYC OpenData; agency Office of Technology and Innovation (OTI); provenance official; updated daily by automation; made public 2011-10-18; publication date 2025-12-23; rows last updated 2026-10-16 01:37:53 UTC |
| License | none stated: the `license` and `licenseId` fields are empty |
| Attribution | "311", with no attribution link |
| Terms of use | no terms-of-use link anywhere in the metadata |
| `created_date` | "Created Date": data type `calendar_date`, render type `calendar_date`, displayed as date and time; described as the date the service request was created; no time zone stated |

One sentence from the dataset's description bears on publication: "However the data does not reveal any
personally identifying information about the customer who made the request."

The description also links a page on the dataset's recent changes and the 2010 to 2019 dataset; neither was
read. The 2024 inventory was captured from the same identifier on 2026-09-14; its year and the context window,
2025-09-01 to 2026-06-02, both fall within the dataset's stated span of 2020 to present.

## The terms page

The metadata names no terms page, so none was read: the context pull was confined to `data.cityofnewyork.us`,
and no request went to another host. NYC Open Data's own terms of use are not linked from this dataset's
metadata and remain to be read and recorded here before any NYC 311 count, or any figure derived from the
counts, is published.

## The time basis of `created_date`

`calendar_date` is Socrata's floating timestamp: a date and time with no time zone. That is the type the
registration requires. The metadata does not say which local time the values are in. The captures of the
context pull speak to it:

- Every one of the 2,959,469 captured values has the form `YYYY-MM-DDTHH:MM:SS.mmm`, with no offset or zone.
- On the spring-forward Sunday, 2026-03-08, when 02:00 to 02:59 does not occur in New York, the hour holds
  1 request, against 197 and 225 on the Sundays before and after.
- On the fall-back Sunday, 2025-11-02, when 01:00 to 01:59 occurs twice in New York, the hour holds 796
  requests, against 528 and 339 on the Sundays before and after.
- The hour with the fewest requests falls between 03:00 and 05:59 on 251 of the 275 days.

| Sunday | Requests | 00:00 to 00:59 | 01:00 to 01:59 | 02:00 to 02:59 | 03:00 to 03:59 |
|---|---:|---:|---:|---:|---:|
| 2025-10-26 | 11,585 | 706 | 528 | 352 | 290 |
| 2025-11-02 (fall-back) | 9,467 | 612 | 796 | 225 | 167 |
| 2025-11-09 | 8,187 | 506 | 339 | 232 | 198 |
| 2026-03-01 | 9,139 | 387 | 335 | 197 | 193 |
| 2026-03-08 (spring-forward) | 11,107 | 595 | 330 | 1 | 228 |
| 2026-03-15 | 9,737 | 467 | 301 | 225 | 148 |

The values behave as New York wall-clock time with daylight saving time, which is what the census assumes
when it counts requests by New York calendar day. The single request at 02:xx on 2026-03-08 is a value the
source holds; the census counts it on that day like any other.

## The terms page, 2026-10-17

The author approved one request for NYC Open Data's terms of use, to the site's overview page, with one
redirect to be followed only within `cityofnewyork.us`. One anonymous GET was sent, with no redirect followed
automatically, no app token and no credential:

| Item | As read |
|---|---|
| URL | `https://opendata.cityofnewyork.us/overview/` |
| Read at | 2026-10-17 03:14:24 UTC; HTTP 301 in 0.34 s; 162 bytes; SHA-256 `9e17cb15dd75bbbd5dbb984eda674863c3b10ab72613cf8a39a00c3e11a8492a` |
| Response | the server's "301 Moved Permanently" page, with no terms text |
| Redirect target | `https://www.nyc.gov/opendata/get-started/what-is-open-data-` |

The page has moved to `www.nyc.gov`, outside `cityofnewyork.us`, so the redirect was not followed and no other
request was sent. NYC Open Data's terms of use are therefore still not recorded here. They remain to be read at
their current address, and recorded in this file, before any NYC 311 count or any figure derived from the
counts is published.

The author then approved two further requests on `www.nyc.gov`, to read the page at its new address and to follow
one redirect there. One anonymous GET was sent:

| Item | As read |
|---|---|
| URL | `https://www.nyc.gov/opendata/get-started/what-is-open-data-` |
| Read at | 2026-10-17 03:44:18 UTC; HTTP 403 in 0.09 s; 432 bytes; SHA-256 `c3cc7e3d6e2fc7996c9403576fb62822b4637a15abf4e1f1506fbd4b18fd750c` |
| Response | the content network's "Access Denied" page, with no terms text and no redirect |

The site refused the scripted request. The second request was not sent, since there was no redirect to follow and the
same request would meet the same refusal. NYC Open Data's terms of use remain unrecorded here.

The author then approved up to three page reads on `www.nyc.gov` in a desktop browser, following the site's links to
its terms of use. Two pages were read, and both loaded in the browser where the scripted request had been refused.
Each page's text (the browser's rendering of the page body) is saved with the SHA-256 of its UTF-8 bytes, computed in
the page:

| Read at (UTC) | URL | Page title | Text bytes | SHA-256 of the text |
|---|---|---|---|---|
| 2026-10-17 04:48:40 | `https://www.nyc.gov/opendata/get-started/what-is-open-data-` | What is Open Data? - NYC Open Data | 3,785 | `433b0ce547a647e05397df3fa167498d6977c51fd795c934032ca0dbcadfe297` |
| 2026-10-17 04:49:11 | `https://www.nyc.gov/main/terms-of-use` | Terms of Use - nyc.gov | 12,888 | `a67866a03e142fcb43459e92a40b139bcb6b2e20dcbce20fc91216869669aeb0` |

The NYC Open Data page has no terms section of its own. It names the program's basis as New York City's Open Data Law
(Title 23, Chapter 5 of the Administrative Code), under which agency data are open by default. Its footer links the
city website's terms of use, the second page. The law itself is hosted outside `www.nyc.gov` and was not read.

What the terms of use say, in brief:

- **Scope:** they govern NYC.gov and all its subpages, and using the site is agreeing to them.
- **Use:** only for lawful purposes. The listed prohibitions include disrupting the site or its servers and altering
  or deleting its content.
- **Intellectual property:**
  - trademarks and service marks belong to their owners;
  - the other materials on NYC.gov, and their selection and arrangement, are the City's property, with all rights
    reserved;
  - permission to use City intellectual property is requested from the relevant agency.
- **Links** to other sites imply no approval or endorsement by the City.
- **No warranty:** the site and its materials are distributed "as is" and "as available", with no warranty of
  accuracy, completeness or currency. The City is not responsible for damages arising from their use.
- **The rest:** New York law governs; the City may change the terms at any time without notice; nothing on the site is
  legal advice.

The terms say nothing specific about NYC Open Data datasets: no license, no attribution requirement, and no rule on
analyzing them or publishing figures derived from them. These pages do not settle whether the intellectual-property
clause reaches datasets served from `data.cityofnewyork.us`. The dataset's own metadata states no license and gives
the attribution "311".

The study's records name the source as NYC Open Data, dataset `erm2-nwe9`, and claim no endorsement by the City.
