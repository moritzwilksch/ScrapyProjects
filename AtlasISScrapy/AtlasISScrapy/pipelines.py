# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy.exporters import CsvItemExporter, JsonItemExporter
import sqlite3

class AtlasisscrapyPipeline:
    def open_spider(self, spider):
        self.json_file = open("ISExport.json", 'w+b')
        # self.csv_file = open("ISExport.csv", 'w+b')

        self.json_exporter = JsonItemExporter(self.json_file)
        # self.csv_exporter = CsvItemExporter(self.csv_file)

        self.json_exporter.start_exporting()
        # self.csv_exporter.start_exporting()

    def close_spider(self, spider):
        self.json_exporter.finish_exporting()
        # self.csv_exporter.finish_exporting()

        self.json_file.close()
        # self.csv_file.close()


    def process_item(self, item, spider):
        self.json_exporter.export_item(item)
        # self.csv_exporter.export_item(item)
        return item


class ScrapyToSQLPipeline:
    def __init__(self):
        self.connection = sqlite3.connect("ISDatabase.db")
        self.cursor = self.connection.cursor()
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS isdata
            (
                id INTEGER PRIMARY KEY, 
                stadtteil VARCHAR(128),
                name VARCHAR(128),
                link VARCHAR(512),
                privatehh INTEGER,
                commercials INTEGER,
                residentsage VARCHAR(10),
                durationofresidence VARCHAR(10),
                families VARCHAR(10),
                singles VARCHAR(10)
            )
            """
        )

    def process_item(self, item, spider):
        self.cursor.execute("SELECT * FROM isdata WHERE link LIKE ?", (item['link'], ))
        result = self.cursor.fetchone()
        if result:
            print("Item already in DB!")
        else:
            self.cursor.execute(
                """
                INSERT INTO isdata (stadtteil, name, link, privatehh, commercials, residentsage, durationofresidence, families, singles)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    item['stadtteil'],
                    item['name'],
                    item['link'],
                    item['demographics']['privateHouseholds'],
                    item['demographics']['commercials'],
                    item['demographics']['residentsAge'],
                    item['demographics']['durationOfResidence'],
                    item['demographics']['families'],
                    item['demographics']['singles']
                )
            )
            self.connection.commit()
        return item