from collections import defaultdict
from plumbum import cli
from pyfiglet import Figlet
from questionary import text, select, Choice
import datetime
import csv

def print_banner(text):
    print(Figlet(font="big").renderText(text))

class FridgeCatalog(cli.Application):
    items = {}
    add = cli.Flag(["a", "add"], help="When appended, allows user to add item to catalog.")
    delete = cli.Flag(["d", "delete"], help="When appended, allows user to delete item from catalog")

    def get_date(self):
        year = int(text("In what year does the food expire?").ask())
        month = int(text("In what month does the food expire?").ask())
        day = int(text("In what day does the food expire?").ask())
        return datetime.datetime(year, month, day)

    def update_file(self, file_name):
        with open(file_name, 'w', newline="") as data_file:
            data_writer = csv.writer(data_file, delimiter=",")
            for item_date, amount in self.items.items():
                item, date = item_date
                data_writer.writerow([item, amount, date.strftime("%Y") + " " + date.strftime("%m") + " " + date.strftime("%d")])

    def open_file(self, file_name):
        with open(file_name, newline="") as data_file:
            data_reader = csv.reader(data_file, delimiter=",")
            for line in data_reader:
                exp = line[2].split(" ")
                exp_date = datetime.datetime(int(exp[0]), int(exp[1]), int(exp[2]))
                print(line[0] + ": " + line[1] + f" item{'s' if line[1] != '1' else ''}" + " expires on " + exp_date.strftime("%x"))
                self.items[(line[0], exp_date)] = int(line[1])

    def main(self):
        print_banner("Fridge Catalog")
        self.open_file("data.csv")
        if self.add:
            item_name = text("What item do you want to add?").ask()
            item_num = text(f"What's the amount of {item_name} you want to add?").ask()
            expiration = self.get_date()
            if item_name != None and item_num != None and expiration != None:
                if (item_name, expiration) in self.items.keys():
                    self.items[(item_name, expiration)] += int(item_num)
                else:
                    self.items[(item_name, expiration)] = int(item_num)
            self.update_file("data.csv")
        if self.delete:
            item_name = select("What item do you want to remove?", choices=[Choice(title=item[0] + " expdate:" + item[1].strftime("%x"), value=item) for item in self.items.keys()]).ask()
            if item_name not in self.items:
                print("This item isn't in the catalog.")
                exit()
            item_num = text("How many of this item do you want to remove?").ask()
            if item_num != None:
                if self.items[item_name] - int(item_num) > 0:
                    self.items[item_name] -= int(item_num)
                else:
                    self.items.pop(item_name)
            self.update_file("data.csv")


if __name__ == "__main__":
    FridgeCatalog()

