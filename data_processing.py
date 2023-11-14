import csv, os

__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))

cities = []
with open(os.path.join(__location__, 'Cities.csv')) as f:
    rows = csv.DictReader(f)
    for r in rows:
        cities.append(dict(r))

countries = []
with open(os.path.join(__location__, 'Countries.csv')) as f:
    rows = csv.DictReader(f)
    for r in rows:
        countries.append(dict(r))

players = []
with open(os.path.join(__location__, 'Players.csv')) as f:
    rows = csv.DictReader(f)
    for r in rows:
        players.append(dict(r))

teams = []
with open(os.path.join(__location__, 'Teams.csv')) as f:
    rows = csv.DictReader(f)
    for r in rows:
        teams.append(dict(r))

titanic = []
with open(os.path.join(__location__, 'Titanic.csv')) as f:
    rows = csv.DictReader(f)
    for r in rows:
        titanic.append(dict(r))


class DB:
    def __init__(self):
        self.database = []

    def insert(self, table):
        self.database.append(table)

    def search(self, table_name):
        for table in self.database:
            if table.table_name == table_name:
                return table
        return None


import copy


class Table:
    def __init__(self, table_name, table):
        self.table_name = table_name
        self.table = table

    def join(self, other_table, common_key):
        joined_table = Table(self.table_name + '_joins_' + other_table.table_name, [])
        for item1 in self.table:
            for item2 in other_table.table:
                if item1[common_key] == item2[common_key]:
                    dict1 = copy.deepcopy(item1)
                    dict2 = copy.deepcopy(item2)
                    dict1.update(dict2)
                    joined_table.table.append(dict1)
        return joined_table

    def filter(self, condition):
        filtered_table = Table(self.table_name + '_filtered', [])
        for item1 in self.table:
            if condition(item1):
                filtered_table.table.append(item1)
        return filtered_table

    def __is_float(self, element):
        if element is None:
            return False
        try:
            float(element)
            return True
        except ValueError:
            return False

    def aggregate(self, function, aggregation_key):
        temps = []
        for item1 in self.table:
            if self.__is_float(item1[aggregation_key]):
                temps.append(float(item1[aggregation_key]))
            else:
                temps.append(item1[aggregation_key])
        return function(temps)

    def select(self, attributes_list):
        temps = []
        for item1 in self.table:
            dict_temp = {}
            for key in item1:
                if key in attributes_list:
                    dict_temp[key] = item1[key]
            temps.append(dict_temp)
        return temps

    def __str__(self):
        return self.table_name + ':' + str(self.table)

    def pivot_table(self, keys: list, values: list, agg_funcs: list):
        unique_data_set = {tuple((key, item[key])
                                 for key in keys) for item in self.table}
        sorted_data = sorted([dict(item) for item in unique_data_set], key=lambda x: tuple(
            x[key] for key in reversed(keys)))
        temps = []
        for item in sorted_data:
            filtered = self
            agg = []
            for key in item:
                filtered = filtered.filter(lambda x: x[key] == item[key])
            for x, y in enumerate(values):
                agg.append(filtered.aggregate(agg_funcs[x], y))
            temps.append([list(item.values()), agg])
        return reversed(temps)


table1 = Table('cities', cities)
table2 = Table('countries', countries)
table3 = Table('players', players)
table4 = Table('teams', teams)
table5 = Table('titanic', titanic)
my_DB = DB()
my_DB.insert(table1)
my_DB.insert(table2)
my_DB.insert(table3)
my_DB.insert(table4)
my_DB.insert(table5)
my_table1 = my_DB.search('cities')
my_table2 = my_DB.search('countries')
my_table3 = my_DB.search('players')
my_table4 = my_DB.search('teams')
my_table5 = my_DB.search('titanic')
table2 = my_table1.join(my_table2, 'country')
football = my_DB.search('players').join(my_DB.search('teams'), 'team')

# What player on a team with “ia” in the team name
# played less than 200 minutes and made more than 100 passes?
# Select to display the player surname, team, and position
my_table3_filtered = my_table3.filter(lambda x: 'ia' in x['team']).filter(lambda x: float(x['minutes']) < 200). \
    filter(lambda x: float(x['passes']) > 100)
for i in my_table3_filtered.table:
    print(f"Name: {i['surname']:<13} Team: {i['team']:<10} Position: {i['position']:<10}")
print()

# The average number of games played for teams ranking below 10 versus teams ranking above or equal 10
my_table4_filtered1 = my_table4.filter(lambda x: int(x['ranking']) < 10)
print(f"Average number of game (ranking below 10): "
      f"{my_table4_filtered1.aggregate(lambda x: sum(x) / len(x), 'games'):.2f}")
my_table4_filtered2 = my_table4.filter(lambda x: int(x['ranking']) >= 10)
print(f"Average number of game (ranking above or equal 10): "
      f"{my_table4_filtered2.aggregate(lambda x: sum(x) / len(x), 'games'):.2f}")
print()

# The average number of passes made by forwards versus by midfielders
my_table3_filtered1 = my_table3.filter(lambda x: x['position'] == 'forward')
print(f"Average number of passes made by forwards: "
      f"{my_table3_filtered1.aggregate(lambda x: sum(x) / len(x), 'passes'):.2f}")
my_table3_filtered2 = my_table3.filter(lambda x: x['position'] == 'midfielder')
print(f"Average number of passes made by midfielders: "
      f"{my_table3_filtered2.aggregate(lambda x: sum(x) / len(x), 'passes'):.2f}")
print()

# The average fare paid by passengers in the first class versus in the third class
my_table5_filtered1 = my_table5.filter(lambda x: x['class'] == '1')
print(f"Average fare paid by passengers in the first class: "
      f"{my_table5_filtered1.aggregate(lambda x: sum(x) / len(x), 'fare'):.2f}")
my_table5_filtered2 = my_table5.filter(lambda x: x['class'] == '3')
print(f"Average fare paid by passengers in the third class: "
      f"{my_table5_filtered2.aggregate(lambda x: sum(x) / len(x), 'fare'):.2f}")
print()

# The survival rate of male versus female passengers
my_table5_filteredMy = my_table5.filter(lambda x: x['gender'] == 'M').filter(lambda x: x['survived'] == 'yes')
my_table5_filteredMn = my_table5.filter(lambda x: x['gender'] == 'M')
print(f"The survival rate of male: "
      f"{len(my_table5_filteredMy.table) / len(my_table5_filteredMn.table):.2f}")
my_table5_filteredFy = my_table5.filter(lambda x: x['gender'] == 'F').filter(lambda x: x['survived'] == 'yes')
my_table5_filteredFn = my_table5.filter(lambda x: x['gender'] == 'F')
print(f"The survival rate of female: "
      f"{len(my_table5_filteredFy.table) / len(my_table5_filteredFn.table):.2f}")

print('Pivot table sorted by embarked,gender, class and aggregated by min fare, max fare, average fare, and count:')
result1 = my_table5.pivot_table(['embarked', 'gender', 'class'], ['fare', 'fare', 'fare', 'last'], [
    lambda x: min(x), lambda x: max(x), lambda x: sum(x) / len(x), lambda x: len(x)])
[print(i) for i in result1]
print('')

print('Pivot table sorted by position and aggregated by average passes, and average shots:')
result2 = football.pivot_table(['position'], ['passes', 'shots'],
                          [lambda x: sum(x) / len(x), lambda x: len(x), lambda x: sum(x) / len(x), lambda x: len(x)])
[print(i) for i in result2]
print('')

print('Pivot table sorted by coastline and eu by average temp, min latitude, max latitude:')
result3 = table2.pivot_table(['coastline', 'EU'], ['temperature', 'latitude', 'latitude'],
                                    [lambda x: sum(x) / len(x), lambda x: min(x), lambda x: max(x)])
[print(i) for i in result3]
print('')

table4 = Table('titanic', titanic)
my_DB.insert(table4)
my_table4 = my_DB.search('titanic')
my_pivot = my_table4.pivot_table(['embarked', 'gender', 'class'], ['fare', 'fare', 'fare', 'last'], [lambda x: min(x), lambda x: max(x), lambda x: sum(x)/len(x), lambda x: len(x)])
# print("Test filter: only filtering out cities in Italy")
# my_table1_filtered = my_table1.filter(lambda x: x['country'] == 'Italy')
# print(my_table1_filtered)
# print()
#
# print("Test select: only displaying two fields, city and latitude, for cities in Italy")
# my_table1_selected = my_table1_filtered.select(['city', 'latitude'])
# print(my_table1_selected)
# print()
#
# print("Calculting the average temperature without using aggregate for cities in Italy")
# temps = []
# for item in my_table1_filtered.table:
#     temps.append(float(item['temperature']))
# print(sum(temps)/len(temps))
# print()
#
# print("Calculting the average temperature using aggregate for cities in Italy")
# print(my_table1_filtered.aggregate(lambda x: sum(x)/len(x), 'temperature'))
# print()
#
# print("Test join: finding cities in non-EU countries whose temperatures are below 5.0")
# my_table2 = my_DB.search('countries')
# my_table3 = my_table1.join(my_table2, 'country')
# my_table3_filtered = my_table3.filter(lambda x: x['EU'] == 'no').filter(lambda x: float(x['temperature']) < 5.0)
# print(my_table3_filtered.table)
# print()
# print("Selecting just three fields, city, country, and temperature")
# print(my_table3_filtered.select(['city', 'country', 'temperature']))
# print()
#
# print("Print the min and max temperatures for cities in EU that do not have coastlines")
# my_table3_filtered = my_table3.filter(lambda x: x['EU'] == 'yes').filter(lambda x: x['coastline'] == 'no')
# print("Min temp:", my_table3_filtered.aggregate(lambda x: min(x), 'temperature'))
# print("Max temp:", my_table3_filtered.aggregate(lambda x: max(x), 'temperature'))
# print()
#
# print("Print the min and max latitude for cities in every country")
# for item in my_table2.table:
#     my_table1_filtered = my_table1.filter(lambda x: x['country'] == item['country'])
#     if len(my_table1_filtered.table) >= 1:
#         print(item['country'], my_table1_filtered.aggregate(lambda x: min(x), 'latitude'), my_table1_filtered.aggregate(lambda x: max(x), 'latitude'))
# print()