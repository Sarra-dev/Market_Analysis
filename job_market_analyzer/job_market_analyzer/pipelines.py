import csv
import os
import hashlib
import psycopg2
from scrapy.utils.project import get_project_settings  # ✅ ADD THIS IMPORT


class DeduplicatedCSVPipeline:

    FILE_PATH = "adzuna_jobs.csv"

    FIELDS = [
        "titre", "entreprise", "localisation",
        "date_publication", "experience", "contrat",
        "description", "competences", "source"
    ]

    def open_spider(self, spider):
        self.existing_keys = set()
        self.new_count = 0

        if os.path.exists(self.FILE_PATH):
            with open(self.FILE_PATH, "r", encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    key = self._make_key(row)
                    self.existing_keys.add(key)
            spider.logger.info(f"📂 Loaded {len(self.existing_keys)} existing jobs from CSV")

        file_exists = os.path.exists(self.FILE_PATH)
        self.file = open(self.FILE_PATH, "a", newline="", encoding="utf-8-sig")
        self.writer = csv.DictWriter(self.file, fieldnames=self.FIELDS, extrasaction="ignore")

        if not file_exists:
            self.writer.writeheader()

    def process_item(self, item, spider):
        key = self._make_key(dict(item))
        if key in self.existing_keys:
            spider.logger.debug(f"⏭️  Duplicate skipped: {item.get('titre')}")
            return item
        self.writer.writerow(dict(item))
        self.file.flush()
        self.existing_keys.add(key)
        self.new_count += 1
        spider.logger.debug(f"✅ Saved: {item.get('titre')} @ {item.get('entreprise')}")
        return item

    def close_spider(self, spider):
        self.file.close()
        spider.logger.info(f"🏁 Done — {self.new_count} new jobs added to {self.FILE_PATH}")

    def _make_key(self, row: dict) -> str:
        raw = "|".join([
            (row.get("titre") or "").strip().lower(),
            (row.get("entreprise") or "").strip().lower(),
            (row.get("date_publication") or "").strip(),
        ])
        return hashlib.md5(raw.encode()).hexdigest()


class PostgresPipeline:

    def open_spider(self, spider):
        os.environ['PGCLIENTENCODING'] = 'UTF8'

        db = spider.crawler.settings.get('DATABASE')

        if not db:
            spider.logger.error("❌ DATABASE not found in settings.py — check your config")
            self.conn = None
            self.cur = None
            return

        try:
            self.conn = psycopg2.connect(
                host=db['host'],
                port=db['port'],
                dbname=db['dbname'],
                user=db['user'],
                password=db['password'],
                options="-c client_encoding=UTF8"
            )
            self.cur = self.conn.cursor()
            spider.logger.info("✅ PostgreSQL connected successfully")
            spider.logger.info(f"   Connected to: {db['host']}:{db['port']}/{db['dbname']} as {db['user']}")

            self.cur.execute("""
                CREATE TABLE IF NOT EXISTS jobs (
                    id               SERIAL PRIMARY KEY,
                    titre            TEXT,
                    entreprise       TEXT,
                    localisation     TEXT,
                    date_publication TEXT,
                    experience       TEXT,
                    contrat          TEXT,
                    description      TEXT,
                    competences      TEXT,
                    source           TEXT,
                    scraped_at       TIMESTAMP DEFAULT NOW(),
                    UNIQUE (titre, entreprise, date_publication)
                );
            """)
            self.conn.commit()
            spider.logger.info("✅ Table 'jobs' ready")

        except psycopg2.OperationalError as e:
            spider.logger.error(f"❌ PostgreSQL connection failed: {e}")
            spider.logger.error(f"   Attempted: {db['host']}:{db['port']}/{db['dbname']} as {db['user']}")
            spider.logger.error("   💡 Check: is PostgreSQL running? Is the port correct? Is the password correct?")
            self.conn = None
            self.cur = None

        except psycopg2.Error as e:
            spider.logger.error(f"❌ PostgreSQL error during setup: {e}")
            spider.logger.error(f"   pgcode: {e.pgcode} — pgerror: {e.pgerror}")
            if self.conn:
                self.conn.rollback()
            self.conn = None
            self.cur = None

        except Exception as e:
            spider.logger.error(f"❌ Unexpected error in PostgresPipeline.open_spider: {e}")
            self.conn = None
            self.cur = None

    def process_item(self, item, spider):
        if not self.conn:
            return item
        try:
            self.cur.execute("""
                INSERT INTO jobs (
                    titre, entreprise, localisation,
                    date_publication, experience, contrat,
                    description, competences, source
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (titre, entreprise, date_publication)
                DO NOTHING;
            """, (
                item.get('titre'),
                item.get('entreprise'),
                item.get('localisation'),
                item.get('date_publication'),
                item.get('experience'),
                item.get('contrat'),
                item.get('description'),
                item.get('competences'),
                item.get('source'),
            ))
            self.conn.commit()

            if self.cur.rowcount > 0:
                spider.logger.debug(f"🐘 PG saved: {item.get('titre')}")
            else:
                spider.logger.debug(f"⏭️  PG duplicate: {item.get('titre')}")

        except Exception as e:
            self.conn.rollback()
            spider.logger.error(f"❌ PG insert error: {e}")

        return item

    def close_spider(self, spider):
        if hasattr(self, 'cur') and self.cur:
            self.cur.close()
        if hasattr(self, 'conn') and self.conn:
            self.conn.close()
        spider.logger.info("🔌 PostgreSQL connection closed")