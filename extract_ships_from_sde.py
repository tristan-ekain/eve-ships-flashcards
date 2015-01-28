"""Reads all ships and some of their basic attributes from the CCP SDE dump, and writes them into a CSV file."""

import csv
import io
import sqlite3
import shutil

import constants as const

# Terminology
#
# Skinned ship:
#   This term refers to a ship that differs from its "unskinned" sibling only in its looks, but not in its attributes.


# Blacklist
SKINNED_SHIPS = frozenset([
    'Police Pursuit Comet', # variant of Federation Navy Comet
    "Goru's Shuttle",       # variant of the Caldari Shuttle
    ])

# Whitelist for ships that would be incorrectly flagged as skinned ships.
NOT_SKINNED_SHIPS = frozenset([
    'Miasmos Quafe Ultra Edition'
    ])

ATTRIBUTE_METALEVEL = 633
ATTRIBUTE_META_GROUP_ID = 1692
ATTRIBUTE_TECH_LEVEL = 422

TECH_LEVEL_TO_STRING = {
    1: 'Tech I',
    2: 'Tech II',
    3: 'Tech III'
    }


class Ship:

    type_name = None
    type_id = None
    group_name = None
    race = None
    meta_level = 0
    tech_level = 0
    meta_group = None
    base_type = None
    market_group = None
    parent_market_group = None


class ShipsRetriever:

    races_by_id = {}
    shipsById = {}
    meta_types_by_id = {} # contains dicts with keys 'parentTypeID' and 'metaGroupName'

    all_ships_by_id = {}   

    def retrieve(self, db_file):
        self.con = sqlite3.connect(db_file)
        with self.con:
            self.con.row_factory = sqlite3.Row
            
            self.fetch_races()
            self.fetch_meta_types()
            self.fetch_ships()
        self.con = None
        return self.all_ships_by_id.values()
        

    def fetch_races(self):
        for row in self.con.execute('SELECT raceId, raceName from chrRaces'):
            self.races_by_id[row['raceId']] = row['raceName']

    def fetch_meta_types(self):
        for row in self.con.execute(
            '''
            SELECT typeID, parentTypeID, metaGroupName
            FROM invMetaTypes
            JOIN invMetaGroups ON invMetaTypes.metaGroupID = invMetaGroups.metaGroupID
            '''):
            self.meta_types_by_id[row['typeID']] = { 'parentTypeID': row['parentTypeID'], 'metaGroupName': row['metaGroupName'] }

    def fetch_ships(self):
        query = '''
            SELECT invGroups.groupName, invTypes.typeName, invTypes.typeID, invTypes.raceID
            FROM invGroups
            JOIN invTypes ON invGroups.groupID = invTypes.groupID
            WHERE invGroups.categoryID = 6 -- 6 = ships
            AND invTypes.published = 1
            '''

        ships = {}

        for row in self.con.execute(query):
            ship = Ship()
            ship.type_name = row['typeName']
            ship.type_id = row['typeID']
            ship.group_name = row['groupName']
            ship.race = self.races_by_id[row['raceID']]
            
            ships[row['typeID']] = ship

        # Add further information
        for ship in ships.values():
            # Meta Level
            meta_level = self.get_attribute(ship.type_id, ATTRIBUTE_METALEVEL);
            ship.meta_level = int(meta_level)

            # Tech Level
            tech_level = self.get_attribute(ship.type_id, ATTRIBUTE_TECH_LEVEL)
            ship.tech_level = int(tech_level)
            
            # Meta Group
            try:
                meta_type = self.meta_types_by_id[ship.type_id]
                ship.meta_group = meta_type['metaGroupName']
                ship.base_type = ships[meta_type['parentTypeID']].type_name
            except KeyError:
                pass
				
            if ship.meta_group is None:
                # Ships that are not based on another hull don't have a meta group; we need to use the tech level instead.
                # Just always using the tech level doesn't work for faction ships.
                ship.meta_group = TECH_LEVEL_TO_STRING.get(tech_level)

            if ship.meta_group is None:
                # If we still don't know the meta group, use a string that makes the problem obvious.
                ship.meta_group = 'UNKNOWN'

            # Market Group
            market_groups = self.con.execute(
                '''
                SELECT g1.marketGroupName, g2.marketGroupName
                FROM invTypes
                JOIN invMarketGroups AS g1 ON invTypes.marketGroupID = g1.marketGroupID
                JOIN invMarketGroups AS g2 ON g1.parentGroupID = g2.marketGroupID
                WHERE invTypes.typeID=:typeID
                ''',
                { 'typeID': ship.type_id }
            ).fetchone()

            if market_groups is not None:
                ship.market_group = market_groups[0]
                ship.parent_market_group = market_groups[1]

        self.all_ships_by_id = ships

    def get_attribute(self, type_id, attribute_id):
        value = self.con.execute(
            'SELECT COALESCE(valueFloat, valueInt) AS value FROM dgmTypeAttributes WHERE typeID=:typeID AND attributeID=:attributeID',
            { 'typeID': type_id, 'attributeID': attribute_id }
            ).fetchone()[0]
        return value
            

class ShipTraits:

    @staticmethod
    def is_skinned_ship(ship):
        if ship.type_name in NOT_SKINNED_SHIPS:
            return False

        # Normal faction ships have a meta level > 0
        if ship.meta_group == 'Faction' and ship.meta_level == 0:
            return True

        name = ship.type_name

        if name.endswith('Edition'):
            return True

        if name in SKINNED_SHIPS:
            return True

        return False

    @staticmethod
    def is_unreleased_ship(ship):
        if ship.type_name.startswith('?'):
            return True

        return False    

    
def write_csv(ships, filename):
    sorted_ships = sorted(ships, key=lambda ship: ship.type_name)
    
    with open(filename, 'w') as file:
        c = csv.writer(file, delimiter=',', lineterminator='\n')
        c.writerow([const.CSV_COL_SHIP, const.CSV_COL_SHIP_CLASS, const.CSV_COL_META_GROUP, const.CSV_COL_TECH_LEVEL, const.CSV_COL_META_LEVEL,
                    const.CSV_COL_HULL, const.CSV_COL_RACE, const.CSV_COL_MARKET_GROUP, const.CSV_COL_TYPE_ID, const.CSV_COL_IGNORE])
            
        for ship in sorted_ships:
            filter_ship = ShipTraits.is_unreleased_ship(ship) or ShipTraits.is_skinned_ship(ship)
            c.writerow([
                    ship.type_name,
                    ship.group_name,
                    ship.meta_group,
                    ship.tech_level,
                    ship.meta_level,
                    ship.base_type,
                    ship.race,
                    ship.market_group,
                    ship.type_id,
                    'TRUE' if filter_ship else 'FALSE'
                ])

        
if __name__ == '__main__':
    r = ShipsRetriever()
    ships = r.retrieve(str(const.DATA_PATH / 'eve.sqlite'))

    if not const.OUTPUT_PATH.exists(): const.OUTPUT_PATH.mkdir()
    write_csv(ships, str(const.OUTPUT_PATH / 'ships.csv'))
