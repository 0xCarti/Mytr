from PyPDF2 import PdfReader
import re


class pdf_handler:
    def __init__(self, file: str):
        self.filename = file
        self.reader = PdfReader(file)

    def import_venue_stock_items(self):
        si_code = re.compile('SI-\d{5}-\d{6}\s')
        suffix = re.compile('\d{6}\s\w+\s\$\d+.\d{2}')

        venue_stock_items = []

        for page in self.reader.pages:
            lines = page.extract_text().split("\n")
            for line in lines:
                if re.search(si_code, line):
                    line = re.sub(si_code, "", line)
                    line = re.split(suffix, line)[0]
                    venue_stock_items.append(line)

        return venue_stock_items


def import_idealpos_menu_items(self):
    code = re.compile('SI-\d{5}-\d{6}\s')
    suffix = re.compile('\d{6}\s\w+\s\$\d+.\d{2}')

    venue_stock_items = []

    for page in self.reader.pages:
        lines = page.extract_text().split("\n")
        for line in lines:
            print(line)


if __name__ == '__main__':
    pdf_handler = pdf_handler('stock_items_summary.pdf')
    venue_stock_items = pdf_handler.import_venue_stock_items()
    print(venue_stock_items)
