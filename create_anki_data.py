"""Creates a CSV file that Anki can import, and copies the ship images to an output folder.

This script reads the CSV file created by the 'create_ship_list' script, and transforms it into a format that can then be imported into Anki.
"""

import csv
import shutil
from pathlib import Path

import constants as const


class AnkiDataBuilder:

    def __init__(self, ship_list_file):
        self.ships = self.read_ships_csv(ship_list_file)

    def read_ships_csv(self, filename):
        with open(filename, 'r') as file:
            reader = csv.DictReader(file)

            # Remove all ships that have 'IGNORE' set to True.
            ships = list(filter(lambda row: row[const.CSV_COL_IGNORE] != 'TRUE', reader))
            return ships
       

    def dump(self, anki_file):
        self.path = Path('./anki')
        if not self.path.exists(): self.path.mkdir()
        
        self.write_csv()
        self.copy_images()

    def write_csv(self, filename):
        with open(filename, 'w') as file:

            c = csv.writer(file, delimiter='\t', lineterminator='\n')
            # Add '#' to first field, so Anki treats the line as a comment line.
            c.writerow(['# Type ID', 'Ship', 'Ship Type', 'Meta Group', 'Hull', 'Race', 'Image', 'Category Tag'])

            for ship in self.ships:
                c.writerow([
                    ship[const.CSV_COL_TYPE_ID],
                    ship[const.CSV_COL_SHIP],
                    ship[const.CSV_COL_SHIP_CLASS],
                    ship[const.CSV_COL_META_GROUP],
                    ship[const.CSV_COL_HULL],
                    ship[const.CSV_COL_RACE],
                    '<img src="%s.png">' % ship[const.CSV_COL_TYPE_ID],
                    'type:' + ship[const.CSV_COL_SHIP_CLASS].replace(' ', '_'),
                    ])


    def copy_images(self, from_dir, to_dir):
        for ship in self.ships:
            filename = "%s.png" % ship[const.CSV_COL_TYPE_ID]
            shutil.copyfile(str(Path(from_dir) / filename), str(Path(to_dir) / filename))


if __name__ == '__main__':
    DIR = const.OUTPUT_PATH / 'anki'
    if not DIR.exists(): DIR.mkdir()
    IMAGE_DIR = DIR / 'collection.media'
    if not IMAGE_DIR.exists(): IMAGE_DIR.mkdir()
    

    b = AnkiDataBuilder(str(const.OUTPUT_PATH / 'ships.csv'))
    b.write_csv(str(DIR / 'anki.csv'))
    b.copy_images(str(const.DATA_PATH / 'Renders'), str(IMAGE_DIR))

