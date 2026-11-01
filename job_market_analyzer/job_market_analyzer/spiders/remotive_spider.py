import scrapy
import json
from job_market_analyzer.items import JobItem

class RemotiveSpider(scrapy.Spider):
    name = "remotive"

    def start_requests(self):
        url = "https://remotive.com/api/remote-jobs?category=software-dev"
        yield scrapy.Request(url, self.parse_api)

    def parse_api(self, response):
        data = json.loads(response.text)

        jobs = data.get("jobs", [])

        self.logger.info(f"Found {len(jobs)} jobs")

        for job in jobs:
            item = JobItem()

            item["titre"] = job.get("title")
            item["entreprise"] = job.get("company_name")
            item["localisation"] = job.get("candidate_required_location")
            item["date_publication"] = job.get("publication_date")
            item["description"] = job.get("description")
            item["source"] = "remotive"

            yield item