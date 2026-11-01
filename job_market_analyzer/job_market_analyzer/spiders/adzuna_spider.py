import os
import scrapy
from dotenv import load_dotenv
import json
from job_market_analyzer.items import JobItem
import urllib.parse

load_dotenv()  

class AdzunaSpider(scrapy.Spider):
    name = "adzuna"

    APP_ID  = os.getenv("ADZUNA_APP_ID")
    APP_KEY = os.getenv("ADZUNA_APP_KEY")

    IT_KEYWORDS = [
        "data scientist", "data analyst", "machine learning engineer",
        "python developer", "devops engineer", "software engineer",
        "backend developer", "fullstack developer", "AI engineer",
        "data engineer", "cloud engineer", "cybersecurity", "frontend developer",
    ]

    COUNTRIES = {
        "gb": "United Kingdom",
        "us": "USA",
        "au": "Australia",
        "ca": "Canada",
        "de": "Germany",
    }

    RESULTS_PER_PAGE = 50
    MAX_TOTAL = 5000

    custom_settings = {
        "DOWNLOAD_DELAY": 1.5,
        "RANDOMIZE_DOWNLOAD_DELAY": True,
        "CONCURRENT_REQUESTS": 2,           # Lower to avoid rate limits
        "FEED_EXPORT_ENCODING": "utf-8-sig",
        "HTTPERROR_ALLOW_ALL": True,
        "USER_AGENT": "Mozilla/5.0 (compatible; JobMarketBot/1.0)",
        "DEFAULT_REQUEST_HEADERS": {          
        "Accept": "application/json",
        "Content-Type": "application/json",
    },
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.APP_ID or not self.APP_KEY:
            raise ValueError(
                "Missing ADZUNA_APP_ID / ADZUNA_APP_KEY. Add them to your .env file."
            )
        self.total_scraped = 0

    async def start(self):
        for country_code, country_name in self.COUNTRIES.items():
            for keyword in self.IT_KEYWORDS:
                if self.total_scraped >= self.MAX_TOTAL:
                    return
                yield scrapy.Request(
                    url=self._build_url(country_code, keyword, page=1),
                    callback=self.parse,
                    errback=self.errback,
                    meta={
                        "country_code": country_code,
                        "country_name": country_name,
                        "keyword": keyword,
                        "page": 1,
                    }
                )

    def _build_url(self, country_code, keyword, page):
        # FIX 1: Use + instead of %20 for spaces (Adzuna prefers this)
        encoded = keyword.replace(" ", "+")
        
        # FIX 2: Build params dict and let urllib encode it cleanly
        params = {
            "app_id": self.APP_ID,
            "app_key": self.APP_KEY,
            "results_per_page": self.RESULTS_PER_PAGE,
            "what": encoded,
            "sort_by": "date",
            "content-type": "application/json",
            
        }
        query_string = "&".join(f"{k}={v}" for k, v in params.items())
        url = f"https://api.adzuna.com/v1/api/jobs/{country_code}/search/{page}?{query_string}"
        self.logger.debug(f"Built URL: {url}")
        return url

    def parse(self, response):
        self.logger.debug(f"Response preview: {response.text[:200]}")
        if response.status != 200:
            self.logger.error(
                f"HTTP {response.status} | {response.meta['country_name']} | "
                f"'{response.meta['keyword']}' | URL: {response.url}\n"
                f"Response body: {response.text[:500]}"
            )
            return

        try:
            data = json.loads(response.text)
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON error at {response.url}: {e}\nBody: {response.text[:200]}")
            return

        results = data.get("results", [])
        total_available = data.get("count", 0)

        self.logger.info(
            f"✅ {response.meta['country_name']} | "
            f"'{response.meta['keyword']}' | "
            f"Page {response.meta['page']} | "
            f"{len(results)} jobs | "
            f"Available: {total_available} | "
            f"Scraped: {self.total_scraped}/{self.MAX_TOTAL}"
        )

        for job in results:
            if self.total_scraped >= self.MAX_TOTAL:
                return

            item = JobItem()
            item["titre"]      = job.get("title", "N/A").strip()
            item["entreprise"] = (job.get("company") or {}).get("display_name", "N/A").strip()

            area = (job.get("location") or {}).get("area", [])
            item["localisation"] = ", ".join(area[-2:]) if area else response.meta["country_name"]

            raw_date = job.get("created", "N/A")
            item["date_publication"] = raw_date[:10] if raw_date != "N/A" else "N/A"

            item["contrat"] = (
                job.get("contract_type")
                or job.get("contract_time")
                or "N/A"
            )

            title_lower = item["titre"].lower()
            if any(w in title_lower for w in ["senior", "lead", "principal", "sr.", "staff"]):
                item["experience"] = "Senior"
            elif any(w in title_lower for w in ["junior", "intern", "graduate", "jr.", "entry"]):
                item["experience"] = "Junior"
            elif any(w in title_lower for w in ["mid", "medior", "confirmed"]):
                item["experience"] = "Mid-level"
            else:
                item["experience"] = "N/A"

            item["description"] = (job.get("description") or "N/A").strip() or "N/A"
            item["competences"] = response.meta["keyword"]
            item["source"]      = f"Adzuna-{response.meta['country_name']}"

            yield item
            self.total_scraped += 1

        # Pagination
        page = response.meta["page"]
        pages_fetched = page * self.RESULTS_PER_PAGE
        if (
            len(results) == self.RESULTS_PER_PAGE
            and pages_fetched < total_available
            and self.total_scraped < self.MAX_TOTAL
            and page < 20  
        ):
            yield scrapy.Request(
                url=self._build_url(response.meta["country_code"], response.meta["keyword"], page + 1),
                callback=self.parse,
                errback=self.errback,
                meta={**response.meta, "page": page + 1}
            )

    async def errback(self, failure):
        self.logger.error(f"❌ Request failed: {failure.request.url} | {repr(failure.value)}")