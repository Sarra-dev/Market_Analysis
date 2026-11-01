import scrapy
from job_market_analyzer.items import JobItem

class BaytITSpider(scrapy.Spider):
    name = "bayt_it"
    start_urls = [
        "https://www.bayt.com/en/tunisia/jobs/information-technology-jobs/"
    ]

    def parse(self, response):
        jobs = response.css("li[data-js-job]")
        for job in jobs:
            link = response.urljoin(job.css("h2 a::attr(href)").get())
            yield response.follow(link, callback=self.parse_job)

        next_page = response.css("a.pagination-next-link::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_job(self, response):
        item = JobItem()
        item["titre"] = response.css("h1::text").get(default="").strip()
        item["entreprise"] = response.css("a.t-default::text").get(default="").strip()
        item["localisation"] = response.css("span.t-mute.t-small::text").get(default="").strip()
        item["date_publication"] = response.css("div.t-mute span::text").get(default="").strip()

        # Job details often listed in a sidebar/table
        details = response.css("div.card-content ul li::text").getall()
        item["experience"] = next((d.strip() for d in details if "Experience" in d or "experience" in d), "")
        item["contrat"] = next((d.strip() for d in details if "Job Type" in d or "Contract" in d), "")

        item["description"] = " ".join(response.css("div.s-jobAdditionalDetails ::text").getall()).strip()
        item["competences"] = ", ".join(response.css("div.skills a::text").getall())
        item["source"] = "bayt"
        yield item