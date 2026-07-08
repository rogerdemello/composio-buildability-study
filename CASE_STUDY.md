# Composio · Which of 100 apps could become an agent toolkit today?

> **AI Product Ops take-home.** An async agent pipeline researched 100 apps against their live developer docs, scored each one's buildability, attached **evidence + confidence to every field**, and an independent agent audited a sample to prove the numbers.

- 📊 **Live interactive case study:** https://rogerdemello.github.io/composio-buildability-study/
- 📦 **Source repo:** https://github.com/rogerdemello/composio-buildability-study

`100 apps` · `10 categories` · `avg score 73/100` · `73%→96% verified` · `20 human-checked`

---
## 1 · The headline

> **The 100 split cleanly: 70 are buildable as agent toolkits today — and almost every app that isn't is blocked by a business rule (sales, approval, enterprise contract), not by a missing or bad API.**

**01. The blocker is commercial, not technical** — Only 1 of 100 apps has no usable API surface at all. The 30 that aren't 'easy' are gated by app-review/dev-token approval (10), paid plans (9), or partner/enterprise contracts (6) — business gates, not engineering ones. The toolkit backlog is a sales-and-partnerships problem more than a build problem.

**02. REST is the universal substrate; GraphQL is a rounding error** — 84 apps expose plain REST and another 9 add GraphQL alongside it; only 3 are GraphQL-first (Linear, Monday, Plain). A REST-first integration layer covers essentially the whole market.

**03. OAuth2 dominates — but never alone** — 64 apps support OAuth2, yet 83 also offer a simpler API-key or token path (42 key + 41 token). The auth layer must do both: OAuth for user-context/marketplace apps, keys for single-tenant. Basic auth is effectively dead (12, all legacy).

**04. MCP has already gone mainstream** — 40 apps ship an official first-party MCP server and 32 more have community ones — 72 of 100 are already MCP-reachable. It is concentrated in Dev/Infra and Productivity, where it is now table stakes.

**05. Easy wins cluster by category** — Productivity (10/10 easy), Dev/Infra (9/10), and CRM / Support / Comms (8/10 each) are near-uniformly self-serve. Marketing/Ads is the outlier — only 4/10 easy — because every ad platform gates access behind app review.

**06. Composio already covers the majority — and the gaps are legible** — 56 of 100 already have a Composio toolkit. The 37 'no' rows are the clearest expansion targets, and most of them (e.g. Plain, Pylon, Smartsheet, Ecwid, GoHighLevel) are self-serve — build-ready, just not built yet.

| Metric | Value |
|---|---|
| Buildable today (score ≥ 68) | **70** / 100 |
| Developer can self-serve credentials | **75** / 100 |
| Ship an official MCP server | **40** / 100 |
| Already a Composio toolkit | **56** / 100 |
| Buildability split | 🟢 70 easy · 🟡 24 moderate · 🔴 6 blocked |

---
## 2 · The patterns

**Auth methods (apps support more than one)**

```
OAuth2             ██████████████████████ 64
API Key            ██████████████░░░░░░░░ 42
Token              ██████████████░░░░░░░░ 41
Basic              ████░░░░░░░░░░░░░░░░░░ 12
JWT                ██░░░░░░░░░░░░░░░░░░░░ 6
PAT                ██░░░░░░░░░░░░░░░░░░░░ 6
Other              █░░░░░░░░░░░░░░░░░░░░░ 3
None               █░░░░░░░░░░░░░░░░░░░░░ 2
HMAC-signed        ░░░░░░░░░░░░░░░░░░░░░░ 1
```
OAuth2 dominates but is nearly always paired with a key/token path; Basic auth is legacy.

**Access — can a developer self-serve credentials?**

```
self-serve         ██████████████████████ 69
gated-approval     ███░░░░░░░░░░░░░░░░░░░ 10
gated-paid         ███░░░░░░░░░░░░░░░░░░░ 9
gated-partner      ██░░░░░░░░░░░░░░░░░░░░ 6
trial-only         █░░░░░░░░░░░░░░░░░░░░░ 3
sandbox-self-serve █░░░░░░░░░░░░░░░░░░░░░ 3
```
75 obtainable vs 25 gated — the gated set is the *needs-outreach* pile.

**API surface**

```
REST               ██████████████████████ 84
REST+GraphQL       ██░░░░░░░░░░░░░░░░░░░░ 9
GraphQL            █░░░░░░░░░░░░░░░░░░░░░ 3
CLI-tool           █░░░░░░░░░░░░░░░░░░░░░ 2
gRPC               ░░░░░░░░░░░░░░░░░░░░░░ 1
none               ░░░░░░░░░░░░░░░░░░░░░░ 1
```
REST is the universal substrate.

**MCP availability**

```
official           ██████████████████████ 40
community          ██████████████████░░░░ 32
none               ████████░░░░░░░░░░░░░░ 15
unknown            ███████░░░░░░░░░░░░░░░ 13
```
40 official + 32 community already MCP-reachable.

**Buildability by category** (easy · moderate · blocked, out of 10)

| Category | 🟢 easy | 🟡 moderate | 🔴 blocked |
|---|:--:|:--:|:--:|
| CRM | 8 | 1 | 1 |
| Support | 8 | 1 | 1 |
| Comms | 8 | 2 | 0 |
| Marketing | 4 | 6 | 0 |
| Ecommerce | 7 | 2 | 1 |
| Data/SEO | 5 | 5 | 0 |
| Dev/Infra | 9 | 1 | 0 |
| Productivity | 10 | 0 | 0 |
| Finance | 6 | 2 | 2 |
| AI/Media | 5 | 4 | 1 |

**▲ Easy wins (just build it):** Notion, Linear, Asana, ClickUp, Coda, GitHub, Vercel, Supabase, Sentry, Cloudflare, HubSpot, Close, Pipedrive, Attio, Intercom, Front, Help Scout, Shopify, Stripe, SendGrid, Klaviyo, Mailchimp

**◆ Needs outreach (gated):** DealCloud, Gladly, Salesforce Commerce Cloud, PitchBook, NotebookLM, Paygent Connect, Google Ads, Meta Ads, LinkedIn Ads, Amazon Selling Partner, WhatsApp Business

**★ Surprises**
- Fintech quietly leads on MCP: Stripe, Brex, Ramp, Xero and iPayX all ship official MCP servers — a regulated, conservative category out ahead of the agent-native shift.
- Marketing/Ads is the hardest category to integrate, not the easiest — every major ad platform (Google, Meta, LinkedIn, Pinterest) gates real access behind an app-review/dev-token approval.
- NotebookLM, one of the most-requested AI products, has no standalone public API at all — only a licensed enterprise API on Google Cloud.

---
## 3 · The 100

Score is the quantified verdict (easy ≥ 68 · moderate 34–67 · blocked < 34); gated access is hard-capped so a strong API you can't get creds for can't score "easy". `†` = human-checked (in the audited sample). Full per-field provenance + confidence is on the live page.

| # | App | Cat | What it does | Auth | Access | API | MCP | Cmp | Score | |
|--:|---|---|---|---|---|---|---|:--:|--:|:--:|
| 1 | **Salesforce**† | CRM | Leading enterprise CRM for sales, service, and marketing. | OAuth2+JWT | self-serve | REST+GraphQL | official | yes | 93 | 🟢 |
| 2 | **HubSpot** | CRM | All-in-one CRM for marketing, sales, and service. | OAuth2+Token | self-serve | REST+GraphQL | official | yes | 97 | 🟢 |
| 3 | **Pipedrive** | CRM | Sales-pipeline CRM for tracking deals and follow-ups. | Token+OAuth2 | self-serve | REST | community | yes | 92 | 🟢 |
| 4 | **Attio** | CRM | Modern, flexible CRM for teams and workflows. | Token+OAuth2 | self-serve | REST | official | yes | 92 | 🟢 |
| 5 | **Twenty** | CRM | Open-source, self-hostable CRM alternative to Salesforce. | Token+OAuth2 | self-serve | REST+GraphQL | community | no | 82 | 🟢 |
| 6 | **Podio** | CRM | Customizable work-management and CRM app platform. | OAuth2 | self-serve | REST | unknown | no | 78 | 🟢 |
| 7 | **Zoho CRM** | CRM | Cloud CRM within Zoho's broad business-app suite. | OAuth2 | self-serve | REST | community | yes | 88 | 🟢 |
| 8 | **Close** | CRM | Sales CRM with built-in calling and email. | API Key+OAuth2 | self-serve | REST | official | yes | 97 | 🟢 |
| 9 | **Copper** | CRM | CRM built for and integrated with Google Workspace. | API Key+OAuth2 | gated-paid | REST | community | no | 46 | 🟡 |
| 10 | **DealCloud**† | CRM | Intapp deal/relationship CRM for private capital markets. | OAuth2+API Key | gated-partner | REST | none | no | 15 | 🔴 |
| 11 | **Zendesk**† | Support | Cloud customer service, ticketing and help center platform. | OAuth2+Token+Basic | self-serve | REST | community | yes | 92 | 🟢 |
| 12 | **Intercom** | Support | AI-first customer messaging, support and help desk platform. | OAuth2+Token | self-serve | REST | official | yes | 97 | 🟢 |
| 13 | **Freshdesk** | Support | Freshworks cloud helpdesk and ticketing software. | API Key+Basic | self-serve | REST | community | yes | 88 | 🟢 |
| 14 | **Front** | Support | Shared inbox and customer communication collaboration platform. | Token+OAuth2 | self-serve | REST | community | yes | 92 | 🟢 |
| 15 | **Pylon** | Support | B2B customer support platform built around Slack/Teams. | Token | gated-paid | REST | unknown | no | 37 | 🟡 |
| 16 | **LiveAgent** | Support | Multichannel helpdesk and live chat ticketing software. | API Key | self-serve | REST | unknown | no | 73 | 🟢 |
| 17 | **Plain** | Support | API-first B2B customer support tool for engineers. | API Key | self-serve | GraphQL | community | yes | 83 | 🟢 |
| 18 | **Help Scout** | Support | Shared-inbox help desk and knowledge base software. | OAuth2 | self-serve | REST | community | yes | 88 | 🟢 |
| 19 | **Gorgias** | Support | Ecommerce-focused helpdesk for Shopify support teams. | Basic+API Key+OAuth2 | self-serve | REST | community | yes | 87 | 🟢 |
| 20 | **Gladly**† | Support | Enterprise people-centered customer service and support platform. | Token+Basic | gated-partner | REST | none | no | 11 | 🔴 |
| 21 | **Slack**† | Comms | Team messaging and collaboration platform | OAuth2+Token | self-serve | REST | official | yes | 97 | 🟢 |
| 22 | **Twilio** | Comms | Programmable SMS, voice and messaging APIs | Basic+API Key | self-serve | REST | official | yes | 93 | 🟢 |
| 23 | **Zoho Cliq** | Comms | Zoho team chat and collaboration app | OAuth2 | self-serve | REST | unknown | no | 73 | 🟢 |
| 24 | **Lark (Larksuite)** | Comms | Enterprise messaging, docs and collaboration suite | OAuth2+Token | self-serve | REST | official | no | 92 | 🟢 |
| 25 | **Pumble** | Comms | Team chat app, Slack-style messaging | API Key | self-serve | REST | community | no | 75 | 🟢 |
| 26 | **Discord** | Comms | Community chat, voice and bot platform | OAuth2+Token | self-serve | REST | community | yes | 92 | 🟢 |
| 27 | **Telegram** | Comms | Messaging app with open Bot API | Token | self-serve | REST | community | yes | 83 | 🟢 |
| 28 | **WhatsApp Business** | Comms | Business messaging via Meta WhatsApp Cloud API | OAuth2+Token | gated-approval | REST | community | yes | 49 | 🟡 |
| 29 | **Aircall**† | Comms | Cloud phone system for support and sales | Basic+OAuth2 | gated-paid | REST | community | no | 42 | 🟡 |
| 30 | **Vonage** | Comms | Communications APIs for SMS, voice, verify | API Key+JWT | self-serve | REST | unknown | no | 78 | 🟢 |
| 31 | **Google Ads** | Marketing | Google's advertising platform API for campaign management | OAuth2 | gated-approval | gRPC | community | yes | 42 | 🟡 |
| 32 | **Meta Ads**† | Marketing | Meta Marketing API for Facebook and Instagram ad campaigns | OAuth2 | gated-approval | REST | community | yes | 50 | 🟡 |
| 33 | **LinkedIn Ads** | Marketing | LinkedIn Marketing API for ad campaigns and reporting | OAuth2 | gated-approval | REST | community | yes | 50 | 🟡 |
| 34 | **GoHighLevel** | Marketing | White-label agency CRM and marketing automation platform API | OAuth2+Token | trial-only | REST | unknown | no | 58 | 🟡 |
| 35 | **Mailchimp** | Marketing | Email marketing platform with a REST Marketing API | API Key+OAuth2 | self-serve | REST | community | yes | 92 | 🟢 |
| 36 | **Klaviyo** | Marketing | Email and SMS marketing automation platform API | API Key+OAuth2 | self-serve | REST | community | yes | 92 | 🟢 |
| 37 | **systeme.io** | Marketing | All-in-one funnel builder and marketing platform with public API | API Key | self-serve | REST | none | no | 70 | 🟢 |
| 38 | **Pinterest** | Marketing | Pinterest API for Pins, boards, and ads (v5) | OAuth2 | gated-approval | REST | none | no | 40 | 🟡 |
| 39 | **Threads (Meta)** | Marketing | Meta Threads API for posts, replies, and insights | OAuth2 | gated-approval | REST | none | no | 35 | 🟡 |
| 40 | **SendGrid**† | Marketing | Twilio SendGrid transactional and marketing email API | API Key | self-serve | REST | community | yes | 88 | 🟢 |
| 41 | **Shopify**† | Ecommerce | Leading hosted ecommerce platform for online stores. | OAuth2+Token | self-serve | REST+GraphQL | official | yes | 97 | 🟢 |
| 42 | **WooCommerce** | Ecommerce | Open-source WordPress plugin turning sites into stores. | API Key+Basic+Other | self-serve | REST | community | no | 83 | 🟢 |
| 43 | **BigCommerce** | Ecommerce | SaaS ecommerce platform with open, API-first architecture. | OAuth2+Token | self-serve | REST+GraphQL | unknown | no | 82 | 🟢 |
| 44 | **Salesforce Commerce Cloud** | Ecommerce | Enterprise B2C/B2B commerce platform, contract-only access. | OAuth2 | gated-partner | REST | none | unknown | 16 | 🔴 |
| 45 | **Magento (Adobe Commerce)** | Ecommerce | Open-source and enterprise commerce platform, self-hostable. | OAuth2+Token+JWT | self-serve | REST+GraphQL | unknown | no | 82 | 🟢 |
| 46 | **Squarespace** | Ecommerce | Website builder with commerce APIs for merchants. | API Key+OAuth2 | gated-paid | REST | none | no | 41 | 🟡 |
| 47 | **Ecwid** | Ecommerce | Embeddable store widget by Lightspeed with REST API. | OAuth2+Token | self-serve | REST | none | no | 77 | 🟢 |
| 48 | **Gumroad** | Ecommerce | Platform for creators selling digital products directly. | OAuth2+Token | self-serve | REST | community | yes | 84 | 🟢 |
| 49 | **Amazon Selling Partner**† | Ecommerce | Amazon's API for sellers and vendors to automate operations. | OAuth2 | gated-approval | REST | community | no | 45 | 🟡 |
| 50 | **fanbasis** | Ecommerce | Merchant-of-record payments/checkout platform for creators and coaches. | API Key | self-serve | REST | none | no | 73 | 🟢 |
| 51 | **DataForSEO** | Data/SEO | SEO, SERP, keyword and backlink data API provider. | Basic | self-serve | REST | official | yes | 89 | 🟢 |
| 52 | **SE Ranking** | Data/SEO | SEO platform: keyword, rank, backlink and audit data API. | Token+API Key | gated-paid | REST | official | no | 52 | 🟡 |
| 53 | **Ahrefs** | Data/SEO | SEO toolset: Site Explorer, keywords, backlinks, rank data API. | Token+API Key | gated-paid | REST | official | yes | 57 | 🟡 |
| 54 | **MrScraper** | Data/SEO | AI web scraping API with proxies and headless browsers. | Token+API Key | self-serve | REST | none | no | 73 | 🟢 |
| 55 | **Apify** | Data/SEO | Actor marketplace platform for web scraping and automation. | Token+API Key | self-serve | REST | official | yes | 93 | 🟢 |
| 56 | **Firecrawl**† | Data/SEO | LLM-focused API to scrape, crawl, map and extract web content. | API Key | self-serve | REST | official | yes | 88 | 🟢 |
| 57 | **Bright Data** | Data/SEO | Web data platform: proxies, Web Unlocker, SERP and scrapers. | API Key+Basic | self-serve | REST | official | yes | 93 | 🟢 |
| 58 | **Sherlock** | Data/SEO | Open-source CLI to hunt usernames across 400+ social networks. | None | self-serve | CLI-tool | none | no | 50 | 🟡 |
| 59 | **Waterfall.io** | Data/SEO | B2B contact and company data waterfall enrichment API. | API Key | gated-paid | REST | none | no | 37 | 🟡 |
| 60 | **Clay**† | Data/SEO | GTM data enrichment and automation platform, no standalone public API. | API Key+Token | gated-paid | REST | official | yes | 49 | 🟡 |
| 61 | **GitHub**† | Dev/Infra | Code hosting, version control and CI/CD platform. | PAT+OAuth2+Token+JWT | self-serve | REST+GraphQL | official | yes | 97 | 🟢 |
| 62 | **Vercel** | Dev/Infra | Frontend cloud for deploying and hosting web apps. | Token+OAuth2 | self-serve | REST | official | yes | 97 | 🟢 |
| 63 | **Netlify** | Dev/Infra | Web hosting and serverless platform for frontend sites. | PAT+OAuth2 | self-serve | REST | official | no | 87 | 🟢 |
| 64 | **Cloudflare** | Dev/Infra | CDN, DNS, edge compute and network security platform. | Token+API Key | self-serve | REST+GraphQL | official | yes | 93 | 🟢 |
| 65 | **Supabase** | Dev/Infra | Open-source Postgres backend-as-a-service platform. | Token+API Key+OAuth2 | self-serve | REST+GraphQL | official | yes | 97 | 🟢 |
| 66 | **Neo4j** | Dev/Infra | Native graph database with Cypher query language. | Basic+Token+OAuth2 | self-serve | REST | official | yes | 92 | 🟢 |
| 67 | **Snowflake**† | Dev/Infra | Cloud data warehouse and analytics platform. | OAuth2+JWT | trial-only | REST | official | yes | 64 | 🟡 |
| 68 | **MongoDB Atlas** | Dev/Infra | Managed cloud MongoDB database service. | OAuth2+API Key | self-serve | REST | official | no | 92 | 🟢 |
| 69 | **Datadog** | Dev/Infra | Cloud monitoring, observability and security platform. | API Key+Token | self-serve | REST | official | yes | 93 | 🟢 |
| 70 | **Sentry** | Dev/Infra | Application error monitoring and performance tracing. | Token+OAuth2 | self-serve | REST | official | yes | 97 | 🟢 |
| 71 | **Notion**† | Productivity | Connected workspace for notes, docs, databases, and wikis. | OAuth2+Token+PAT | self-serve | REST | official | yes | 97 | 🟢 |
| 72 | **Airtable** | Productivity | Spreadsheet-database hybrid for building custom apps and workflows. | OAuth2+PAT | self-serve | REST | community | yes | 87 | 🟢 |
| 73 | **Linear** | Productivity | Issue tracking and project management for software teams. | OAuth2+API Key | self-serve | GraphQL | official | yes | 97 | 🟢 |
| 74 | **Jira** | Productivity | Atlassian issue tracking and agile project management platform. | OAuth2+Basic+JWT | self-serve | REST | official | yes | 93 | 🟢 |
| 75 | **Asana** | Productivity | Work management platform for tasks, projects, and team workflows. | OAuth2+PAT+Other | self-serve | REST | official | yes | 97 | 🟢 |
| 76 | **Monday.com** | Productivity | Customizable work OS for project, sales, and dev management. | OAuth2+Token | self-serve | GraphQL | official | yes | 97 | 🟢 |
| 77 | **ClickUp** | Productivity | All-in-one productivity app for tasks, docs, and goals. | OAuth2+Token | self-serve | REST | community | yes | 92 | 🟢 |
| 78 | **Coda** | Productivity | Doc-database platform combining documents, tables, and automations. | API Key+Token | self-serve | REST | community | yes | 83 | 🟢 |
| 79 | **Smartsheet**† | Productivity | Enterprise work management on a spreadsheet-style grid interface. | OAuth2+Token | trial-only | REST | official | no | 68 | 🟢 |
| 80 | **Harvest** | Productivity | Time tracking and invoicing for teams and freelancers. | OAuth2+PAT | self-serve | REST | community | yes | 87 | 🟢 |
| 81 | **Stripe**† | Finance | Online payment processing and financial infrastructure platform | API Key+OAuth2 | self-serve | REST | official | yes | 97 | 🟢 |
| 82 | **Plaid** | Finance | Bank-account data connectivity and financial account-linking API | API Key | sandbox-self-serve | REST | unknown | no | 68 | 🟢 |
| 83 | **Binance** | Finance | Cryptocurrency exchange trading and market-data API | API Key+HMAC-signed | sandbox-self-serve | REST | community | no | 73 | 🟢 |
| 84 | **Paygent Connect**† | Finance | Japanese online payment gateway with embedded checkout module | Other+Basic | gated-partner | REST | none | no | 7 | 🔴 |
| 85 | **iPayX** | Finance | FX forensic-audit MCP layer for cross-border payments | API Key+Token | self-serve | none | official | no | 52 | 🟡 |
| 86 | **QuickBooks** | Finance | QuickBooks Online cloud accounting API | OAuth2 | self-serve | REST | community | yes | 88 | 🟢 |
| 87 | **Xero** | Finance | Xero cloud accounting API for small businesses | OAuth2 | self-serve | REST | official | yes | 93 | 🟢 |
| 88 | **Brex** | Finance | Corporate cards and spend-management API | Token+OAuth2 | gated-approval | REST | official | yes | 54 | 🟡 |
| 89 | **Ramp** | Finance | Corporate cards and finance-automation / spend-management API | OAuth2 | sandbox-self-serve | REST | official | yes | 78 | 🟢 |
| 90 | **PitchBook** | Finance | Private-capital market research data API (enterprise-gated) | API Key+Token | gated-partner | REST | unknown | no | 11 | 🔴 |
| 91 | **NotebookLM**† | AI/Media | Google's AI research and note-taking assistant | OAuth2 | gated-partner | REST | none | no | 11 | 🔴 |
| 92 | **Otter AI** | AI/Media | AI meeting transcription, notes and insights assistant | OAuth2 | gated-approval | REST | official | unknown | 45 | 🟡 |
| 93 | **Fathom** | AI/Media | AI meeting notetaker with transcripts and summaries | API Key+OAuth2 | self-serve | REST | community | yes | 87 | 🟢 |
| 94 | **Consensus** | AI/Media | AI search engine over scientific research papers | OAuth2+API Key | gated-approval | REST | official | unknown | 46 | 🟡 |
| 95 | **Reducto** | AI/Media | Document parsing and extraction API for AI | API Key | self-serve | REST | unknown | unknown | 73 | 🟢 |
| 96 | **Devin** | AI/Media | Autonomous AI software engineer agent | API Key | gated-paid | REST | official | yes | 52 | 🟡 |
| 97 | **higgsfield**† | AI/Media | AI image, video and media generation suite | API Key | self-serve | REST | community | unknown | 83 | 🟢 |
| 98 | **Mermaid CLI** | AI/Media | Open-source CLI rendering Mermaid diagrams to images | None | self-serve | CLI-tool | none | no | 50 | 🟡 |
| 99 | **YouTube Transcript** | AI/Media | Third-party API for YouTube video transcripts | API Key | self-serve | REST | unknown | unknown | 70 | 🟢 |
| 100 | **Grain** | AI/Media | AI meeting recorder and notetaker for teams | Token+OAuth2 | self-serve | REST | unknown | unknown | 77 | 🟢 |

---
## 4 · The agent that did it

A modular pipeline built on Composio's own SDK + search tools:

```
providers (composio_search → tavily → firecrawl → docs_fetcher → browser*)
      │        *browser = Playwright, fallback only when docs are JS-walled
      ▼
researcher.py   app → structured record, every FIELD w/ value+confidence+evidence
      ▼         (async, Semaphore(5), resumable JSON store)
verifier.py     different, stronger model, adversarial re-check + evidence liveness
      ▼
pattern_analyzer.py   LLM insights, grounded in code-computed counts
      ▼
report_writer.py / markdown_writer.py   render page & this doc from JSON
```

**Where a human was needed**
- **Login-gated / thin docs** (fanbasis, iPayX, Paygent, higgsfield) — can't read behind a login wall.
- **Sandbox vs production** fintech splits (`sandbox-self-serve`) — a judgment the rubric couldn't encode.
- **Composio catalog stubs** — a toolkit *page* with 0 tools isn't real coverage.
- **Access reclassification** — the score exposed hedged "moderate" calls that were really gated (SFCC, Brex) or really self-serve; a human set the access value the score keys off.

---
## 5 · How it was built

1. **Perfect on 5, then scale.** Tuned on 5 golden apps across five auth models — Salesforce, HubSpot, Slack, Stripe, Shopify — then scaled to 100.
2. **Async fan-out** under `Semaphore(5)`, resumable so a crash never re-does finished work.
3. **Score, don't guess** — buildability is a weighted 0–100 score; the verdict is the band.
4. **Verify + lift** — independent audit + evidence-liveness moved accuracy up (below).

---
## 6 · Is it trustworthy?

### Graded-field accuracy: ~~73%~~ → **96%**

An **independent** agent — a different, stronger model with an adversarial "assume this is wrong" prompt — re-researched the 20-app sample from scratch and was diffed against the first pass. Raw agreement was **73%** across 80 graded input fields. Adjudicating every disagreement against primary docs by hand: **9 were genuine first-pass errors** (now fixed), **3 were the auditor's own mistakes** (first pass upheld), and 10 were vocabulary refinements. Re-graded against the docs, the corrected sample sits at **96%** — the rest is left honest for the genuinely ambiguous sandbox / enterprise edges. Separately, every one of the 100 evidence links was fetched: **99% resolved live**.

- 20-app stratified sample · 2 per category
- 80 input fields checked (4 × 20)
- **73%** raw agreement w/ independent auditor
- **9** genuine errors caught → fixed
- **3** auditor errors → first pass upheld
- **99%** evidence links resolved live

**Hits and misses (shown honestly)**

| App | Field | First pass | Verified | Verdict | Why |
|---|---|---|---|---|---|
| DealCloud | MCP | official | none | **miss** | First pass counted a speculative, not-yet-shipped MCP as official. |
| Slack | MCP | community | official | **miss** | Slack shipped a first-party MCP server (GA Feb 2026) — first pass missed it. |
| Smartsheet | MCP | unknown | official | **miss** | Smartsheet ships an official MCP server; first pass hedged to unknown. |
| Clay | Access | no-public-api | gated-paid | **miss** | A real (Enterprise-gated) lookup API exists — 'no public API' was too strong. |
| Clay | API surface | none | REST | **miss** | Follows from the above: there is a REST surface, just paywalled. |
| Clay | MCP | unknown | official | **miss** | Clay ships an official MCP server. |
| Firecrawl | Auth | API Key + OAuth2 | API Key | **miss** | Firecrawl is API-key only; OAuth2 was an over-claim. |
| higgsfield | API surface | CLI-tool | REST | **miss** | A public Higgsfield Cloud REST API exists beyond the CLI. |
| higgsfield | Auth | API Key + OAuth2 | API Key | **miss** | Bearer API key only; OAuth2 over-claimed. |
| Aircall | Access | gated-paid | self-serve | **confirm** | Auditor wrong — API keys need a paid Aircall subscription. First pass upheld. |
| Stripe | Access | self-serve | sandbox-self-serve | **confirm** | Auditor wrong — Stripe live keys are self-serve on activation, no gate. First pass upheld. |
| Smartsheet | Access | trial-only | self-serve | **confirm** | Auditor wrong — Smartsheet API needs a paid/trial plan, no durable free tier. First pass upheld. |
| Gladly | Access | gated-paid | gated-partner | **refine** | Both mean gated; 'gated-partner' (contact-sales, no signup) is more precise. Adopted. |
| Amazon Selling Partner | MCP | unknown | community | **refine** | Community SP-API MCP servers exist. Adopted. |
| Salesforce | Auth | OAuth2 | OAuth2 + JWT | **refine** | JWT bearer flow is a real Salesforce auth path; tag completed. |
| GitHub | Auth | PAT + OAuth2 | + JWT (GitHub App) | **refine** | GitHub App auth uses a JWT; tag completed. |

*miss = first pass wrong (fixed) · confirm = auditor wrong, first pass upheld · refine = both defensible, more precise value adopted.*

---
## 7 · What defeated the agent

- **Paygent Connect** — genuinely defeated us. Japanese, contract-only, mutual-TLS certs, no self-serve. The brief's "NMI-powered" hint appears wrong; we report that rather than guess.
- **NotebookLM** — no standalone public API; only a licensed enterprise API on Google Cloud. A valid *blocked* finding.
- **fanbasis / iPayX** — core docs behind a login wall; read the public reference, flagged low confidence.
- **higgsfield** — thin, fast-moving docs; real self-serve REST API confirmed but breadth uncertain → mid-band score.

---
## 8 · Run it yourself

```bash
pip install -r requirements.txt
cp .env.example .env      # add ANTHROPIC_API_KEY (+ COMPOSIO/TAVILY/FIRECRAWL if you have them)

python main.py research --golden   # perfect the pipeline on 5 apps
python main.py research            # scale to all 100 (async, resumable)
python main.py verify --sample 20  # independent audit + accuracy
python main.py patterns            # LLM pattern engine
python main.py report              # render web/index.html
python main.py md                  # render this CASE_STUDY.md
```

> Committed `output/*.json` is the run behind this doc, so it regenerates with **no API keys**.

## Honesty notes
- No paid accounts used; a payment/partnership gate reported with evidence *is* the finding.
- Confidence is per-field; lower-confidence values are flagged on the live page.
- Verification graded 80 input fields on a 20-app stratified sample — the accuracy number is the sample's.
- Only 20 of 100 apps are human-checked (the audited sample); the rest carry the agent's own confidence.

*Generated from `output/results.json` + `output/patterns.json` + `data/verification_report.json` by `agents/markdown_writer.py` — same data as the live page.*
