
import psycopg2
from psycopg2.extras import execute_values

class HotelDataPipeline:
    def open_spider(self, spider):
        self.connection = psycopg2.connect(
            host=spider.settings.get("POSTGRES_HOST"),
            database=spider.settings.get("POSTGRES_DB"),
            user=spider.settings.get("POSTGRES_USER"),
            password=spider.settings.get("POSTGRES_PASSWORD")
        )
        self.cursor = self.connection.cursor()
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS hotels (
                name TEXT,
                url TEXT UNIQUE,
                location TEXT,
                description TEXT,
                facilities TEXT[],
                image_urls TEXT[]
            );
        """)
        self.connection.commit()

        self.buffer = []
        self.buffer_size = 100
        self.test_mode = spider.settings.getbool("TEST_MODE")

    def process_item(self, item, spider):
        if self.test_mode:
            try:
                self.cursor.execute("""
                    INSERT INTO hotels (name, url, location, description, facilities, image_urls)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT DO NOTHING;
                """, (
                    item["name"],
                    item["url"],
                    item["location"],
                    item["description"],
                    item["facilities"],
                    item["image_urls"]
                ))
                self.connection.commit()
            except Exception as e:
                spider.logger.error(f"[DB ERROR] Insert failed for {item['name']}: {e}")
        else:
            row = (
                item["name"],
                item["url"],
                item["location"],
                item["description"],
                item["facilities"],
                item["image_urls"]
            )
            self.buffer.append(row)

            if len(self.buffer) >= self.buffer_size:
                self.flush_buffer(spider)

        return item

    def flush_buffer(self, spider):
        try:
            execute_values(
                self.cursor,
                """
                INSERT INTO hotels (name, url, location, description, facilities, image_urls)
                VALUES %s
                ON CONFLICT DO NOTHING;
                """,
                self.buffer
            )
            self.connection.commit()
            self.buffer.clear()
        except Exception as e:
            spider.logger.error(f"[DB ERROR] Batch insert failed: {e}")

    def close_spider(self, spider):
        if not self.test_mode and self.buffer:
            self.flush_buffer(spider)
        self.cursor.close()
        self.connection.close()
