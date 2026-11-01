import re
import scrapy
from scrapy_playwright.page import PageMethod
from job_market_analyzer.items import JobItem
import urllib.parse

class IndeedSpider(scrapy.Spider):
    name = "indeed"

    IT_KEYWORDS = [
        "machine learning engineer",
        "data scientist",
        "data analyst",
        "python developer",
        "devops engineer",
        "software engineer",
        "backend developer",
        "fullstack developer",
        "AI engineer",
        "data engineer",
    ]

    # Block all non-essential resources — massive speed improvement
    BLOCK_RESOURCES = {"image", "media", "font", "stylesheet", "ping", "other"}

    PLAYWRIGHT_META = {
        "playwright": True,
        "playwright_page_goto_kwargs": {
            "wait_until": "domcontentloaded",
            "timeout": 60000,
        },
    }

    def _block_meta(self):
        """Playwright meta that blocks images/fonts/CSS to load faster."""
        return {
            **self.PLAYWRIGHT_META,
            "playwright_page_methods": [
                PageMethod(
                    "route",
                    "**/*",
                    lambda route: route.abort()
                    if route.request.resource_type in self.BLOCK_RESOURCES
                    else route.continue_(),
                ),
            ],
        }

    async def start(self):
        for keyword in self.IT_KEYWORDS:
            encoded = urllib.parse.quote(keyword)
            url = f"https://fr.indeed.com/emplois?q={encoded}&l=&start=0"
            yield scrapy.Request(
                url=url,
                meta={
                    **self.PLAYWRIGHT_META,
                    "playwright_page_methods": [
                        PageMethod("wait_for_selector", "div.job_seen_beacon", timeout=30000, state="attached"),
                        PageMethod("wait_for_timeout", 2000),
                    ],
                    "keyword": keyword,
                    "page_num": 0,
                    "job_count": 0,
                },
                callback=self.parse_listing,
                errback=self.errback,
            )

    def _clean_detail_url(self, href: str) -> str:
        """
        Convert any Indeed href to a clean viewjob URL.
        
        Handles:
          /viewjob?jk=abc123               → https://fr.indeed.com/viewjob?jk=abc123
          /rc/clk?jk=abc123&bb=...         → https://fr.indeed.com/viewjob?jk=abc123
          https://fr.indeed.com/viewjob... → unchanged
        """
        if not href:
            return None

        # Extract jk parameter from any URL format
        jk_match = re.search(r'[?&]jk=([a-f0-9]+)', href)
        if jk_match:
            jk = jk_match.group(1)
            return f"https://fr.indeed.com/viewjob?jk={jk}"

        # Fallback: prepend domain if relative
        if href.startswith("/"):
            return f"https://fr.indeed.com{href}"

        return href

    def parse_listing(self, response):
        self.logger.info(f"✅ Listing | Keyword: {response.meta['keyword']} | URL: {response.url}")

        jobs = response.css("div.job_seen_beacon")
        self.logger.info(f"Found {len(jobs)} job cards")

        if not jobs:
            self.logger.warning(f"⚠️ No cards! Snippet:\n{response.text[:600]}")
            return

        job_count = response.meta.get("job_count", 0)

        for job in jobs:
            raw_href = (
                job.css("h2.jobTitle a::attr(href)").get()
                or job.css("a.jcs-JobTitle::attr(href)").get()
            )
            detail_url = self._clean_detail_url(raw_href)

            titre = (
                job.css("h2.jobTitle a span[title]::attr(title)").get()
                or job.css("h2.jobTitle span[title]::attr(title)").get()
                or job.css("h2.jobTitle span::text").get()
                or job.css("a.jcs-JobTitle span::text").get()
                or "N/A"
            ).strip()

            entreprise = (
                job.css("span[data-testid='company-name']::text").get()
                or job.css("[class*='companyName']::text").get()
                or "N/A"
            ).strip()

            localisation = (
                job.css("div[data-testid='text-location']::text").get()
                or job.css("[class*='companyLocation']::text").get()
                or "N/A"
            ).strip()

            if detail_url:
                yield scrapy.Request(
                    url=detail_url,
                    meta={
                        **self.PLAYWRIGHT_META,
                        "playwright_page_methods": [
                            PageMethod(
                                "wait_for_selector",
                                "#jobDescriptionText",
                                timeout=30000,
                                state="attached",
                            ),
                            PageMethod("wait_for_timeout", 1500),
                        ],
                        "keyword": response.meta["keyword"],
                        "titre": titre,
                        "entreprise": entreprise,
                        "localisation": localisation,
                    },
                    callback=self.parse_detail,
                    errback=self.errback,
                )
                job_count += 1
            else:
                # No URL — yield card data only
                item = JobItem()
                item["titre"] = titre
                item["entreprise"] = entreprise
                item["localisation"] = localisation
                item["date_publication"] = "N/A"
                item["contrat"] = "N/A"
                item["experience"] = "N/A"
                item["description"] = "N/A"
                item["competences"] = response.meta["keyword"]
                item["source"] = "Indeed-FR"
                yield item

        # Pagination — up to 1000 jobs per keyword
        page_num = response.meta.get("page_num", 0)
        if job_count < 1000:
            next_href = response.css('a[data-testid="pagination-page-next"]::attr(href)').get()
            if next_href:
                next_url = f"https://fr.indeed.com{next_href}"
                self.logger.info(f"➡️ Page {page_num + 1} | Jobs queued: {job_count}")
                yield scrapy.Request(
                    url=next_url,
                    meta={
                        **self.PLAYWRIGHT_META,
                        "playwright_page_methods": [
                            PageMethod("wait_for_selector", "div.job_seen_beacon", timeout=30000, state="attached"),
                            PageMethod("wait_for_timeout", 2000),
                        ],
                        "keyword": response.meta["keyword"],
                        "page_num": page_num + 1,
                        "job_count": job_count,
                    },
                    callback=self.parse_listing,
                    errback=self.errback,
                )

    def parse_detail(self, response):
        self.logger.info(f"📄 Detail: {response.url}")

        item = JobItem()
        item["competences"] = response.meta["keyword"]
        item["source"] = "Indeed-FR"
        item["entreprise"] = response.meta.get("entreprise", "N/A")
        item["localisation"] = response.meta.get("localisation", "N/A")

        # ── TITRE ─────────────────────────────────────────────────────────────
        item["titre"] = (
            response.css("h1.jobsearch-JobInfoHeader-title span::text").get()
            or response.css("h1[class*='jobTitle'] span::text").get()
            or response.css("h1::text").get()
            or response.meta.get("titre", "N/A")
        ).strip()

        # ── DESCRIPTION ───────────────────────────────────────────────────────
        desc_texts = (
            response.css("#jobDescriptionText *::text").getall()
            or response.css(".jobsearch-JobComponent-description *::text").getall()
        )
        cleaned = [t.strip() for t in desc_texts if t.strip()]
        item["description"] = " ".join(cleaned) if cleaned else "N/A"

        # ── CONTRAT ───────────────────────────────────────────────────────────
        # Indeed FR renders contract type as chips under "Détails de l'emploi"
        item["contrat"] = (
            self._get_labeled_value(response, "Type de poste")
            or self._get_labeled_value(response, "Type de contrat")
            or response.css("div.css-u74ql7 button::text").get()
            or response.css("div.css-u74ql7 span::text").get()
            or response.css("[data-testid='attribute_snippet_testid']::text").get()
            or "N/A"
        ).strip()

        # ── DATE PUBLICATION ──────────────────────────────────────────────────
        item["date_publication"] = (
            response.css("span[data-testid='myJobsStateDate']::text").get()
            or response.css("p.css-1t92pv::text").get()
            or response.css("div.css-kyg8or span::text").get()
            or response.css("span.css-qvloho::text").get()
            or self._find_text_with_keywords(response, ["Publiée", "Postée", "Il y a"])
            or "N/A"
        ).strip()

        # ── EXPERIENCE ────────────────────────────────────────────────────────
        item["experience"] = (
            self._get_labeled_value(response, "Expérience")
            or self._get_labeled_value(response, "Niveau d'études")
            or self._get_labeled_value(response, "Niveau d'expérience")
            or "N/A"
        )

        yield item

    def _get_labeled_value(self, response, label: str) -> str | None:
        """
        Extract a value paired with a label in Indeed's job details section.
        
        Handles two DOM patterns:
          Pattern A (dt/dd):  <dt>Type de poste</dt><dd>Temps plein</dd>
          Pattern B (div):    <div><span>Type de poste</span><span>Temps plein</span></div>
        """
        label_lower = label.lower()

        # Pattern A — definition list
        for dt in response.css("dt"):
            if label_lower in (dt.css("::text").get() or "").lower():
                dd_texts = dt.xpath("following-sibling::dd[1]//text()").getall()
                val = " ".join(t.strip() for t in dd_texts if t.strip())
                if val:
                    return val

        # Pattern B — generic container (div, li, section)
        for el in response.css("div, li"):
            children_text = el.css("> *::text").getall()  # direct children only
            joined = " ".join(children_text)
            if label_lower in joined.lower():
                values = [
                    t.strip() for t in children_text
                    if t.strip() and label_lower not in t.lower()
                ]
                if values:
                    return values[0]

        return None

    def _find_text_with_keywords(self, response, keywords: list) -> str | None:
        """Scan all text nodes for one matching any keyword."""
        for text in response.css("*::text").getall():
            t = text.strip()
            if t and any(kw.lower() in t.lower() for kw in keywords):
                return t
        return None

    async def errback(self, failure):
        self.logger.error(f"❌ Failed: {failure.request.url} — {repr(failure.value)}")