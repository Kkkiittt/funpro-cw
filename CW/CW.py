import datetime
import json
import sys
import csv
import msvcrt

BLACK = "\033[40m;37m"  
WHITE = "\033[107;30m"  
RESET = "\033[0m"
WIDTH=120
IDATE=datetime.datetime(1,1,1,1)

manage_flag=True
see_flag=True
use_csv=True

transactions=[]

def safe_ex(meth, arg):
    try:
        if arg==None:
            meth()
        else:
            meth(arg)
    except Exception as e:
        print(f"An error occurred: {e}")
        input("Press Enter to continue...")

def read_key():
    ch = msvcrt.getch()
    if ch == b"\r":
        return "enter"
    elif ch == b"\xe0":  
        ch2 = msvcrt.getch()
        if ch2 == b"H":
            return "up"
        elif ch2 == b"P":
            return "down"
        elif ch2 == b"K":
            return "left"
        elif ch2 == b"M":
            return "right"
    return None  

def change_theme(theme):
    if theme == "b":
        sys.stdout.write(BLACK)
    elif theme == "w":
        sys.stdout.write(WHITE)
    else:
        sys.stdout.write(RESET)

def choose(menu: list, header:str=''):
    ind = 0
    n = len(menu)
    l=max(len(item[0]) for item in menu)
    iden=' ' * ((WIDTH - l - 2) // 2)
    #l=(l+1)//2*2
    while True:
        sys.stdout.write("\033c")
        if header:
            change_theme("w")
            print(header.center(WIDTH, ' '))
            change_theme("r")
        print(iden+'+'+'-' * (l) + '+')
        for i in range(n):
            print(iden, end='|')
            if i == ind:
                change_theme("w")
            print(str(menu[i][0]).center(l, ' '),end='')
            change_theme("r")
            print('|')
            print(iden + '+'+'-' * (l) + '+')
        key=read_key()
        if key == "up":
            ind = (ind - 1) % n
        elif key == "down":
            ind = (ind + 1) % n
        elif key == "enter":
            change_theme("r")
            safe_ex(menu[ind][1], menu[ind][2])
            break

class transaction:
    positive = False
    amount=0.0
    date=datetime.datetime.now()
    category=""
    note=""

    def __init__(self, positive: bool, amount: float, date: datetime, note: str, category:str):
        self.positive = positive
        self.amount = amount
        self.date = date
        self.note = note
        self.category = category

    def __str__(self):
        return f"{'+' if self.positive else '-'}${self.amount:.2f} on {self.date.strftime('%Y-%m-%d')}: {self.note} [{self.category}]"

def add_transaction():
    sys.stdout.write("\033c")
    print("Add Transaction")
    amount=0.0
    while amount==0.0:
        try:
            amount = float(input("Enter amount: ").strip())
            if amount == 0.0:
                print("Amount must be non-zero.")
        except ValueError:
            print("Invalid amount. Please enter a numeric value.")
    positive= (amount > 0)
    amount=abs(amount)
    date=IDATE
    while date==IDATE:
        date_str = input("Enter date (YYYY-MM-DD) or leave blank for today: ").strip()
        if date_str:
            try:
                date = datetime.datetime.strptime(date_str, '%Y-%m-%d')
            except ValueError:
                print("Invalid date format. Please use YYYY-MM-DD.")
        else:
            date = datetime.datetime.now()
    note = input("Enter note: ").strip()
    category= input("Enter category or leave blank for default one: ").strip().capitalize()
    category = category if category else "Expense" if not positive else "Income"
    tr=transaction(positive, amount, date, note, category)
    change_theme("w")
    print(tr)
    change_theme("r")
    sure=input("Save this transaction? (y/n): ").strip().lower()
    if sure != 'y':
        input("Transaction cancelled. Press Enter to continue...")
        return
    transactions.append(tr)
    input("Transaction added! Press Enter to continue...")

def show_transactions():
    sys.stdout.write("\033c")
    data=[]
    categories=set(t.category for t in transactions)
    fil_cat=input("Filter by category? (y/n): ").strip().lower()=='y'
    if fil_cat:
        change_theme("w")
        print(f"(Existing categories: {" ".join(categories)})")
        change_theme("r")
        print("Type space separated categories to see: ")
        cats=list(map(lambda x:x.strip().capitalize(), input().split()))
        fil_cats=[ct for ct in categories if ct in cats]
        data=sorted([t for t in transactions if t.category in fil_cats], key=lambda x:x.date, reverse=True)
    else:
        data=sorted(transactions, key=lambda x:x.date, reverse=True)

    print("Transactions:".center(WIDTH))
    change_theme("w")
    for t in data:
        print(str(t).center(WIDTH))
    change_theme("r")
    input("Press Enter to continue...")

def date_time_serializer(obj):  
    if isinstance(obj, datetime.datetime):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

def save_transactions_csv():
    with open("transactions.csv", 'w', newline='') as f:
        wrt = csv.writer(f)
        wrt.writerow(['positive', 'amount', 'date', 'note', 'category'])
        wrt.writerows([[t.positive, t.amount, t.date.isoformat(), t.note, t.category] for t in transactions])

def save_transactions_json():
    with open("transactions.json", "w") as f:
        json.dump([t.__dict__ for t in transactions], f, default=date_time_serializer)

def save_transactions():
    if use_csv:
        save_transactions_csv()
    else:
        save_transactions_json()

def load_transactions_csv():
    global transactions
    try:
        with open("transactions.csv", 'r') as f:
            rdr = csv.DictReader(f)
            transactions = [transaction(row['positive']=='True', float(row['amount']), datetime.datetime.fromisoformat(row['date']), row['note'], row['category']) for row in rdr]
    except:
        transactions = []

def load_transactions_json():
    global transactions
    try:
        with open("transactions.json", "r") as f:
            data=json.load(f)
            transactions = [transaction(d['positive'], d['amount'], datetime.datetime.fromisoformat(d['date']), d['note'], d['category']) for d in data]
    except:
        transactions = []

def load_transactions():
    if use_csv:
        load_transactions_csv()
    else:
        load_transactions_json()

def balance():
    balance=0.0
    for t in transactions:
        if t.positive:
            balance+=t.amount
        else:
            balance-=t.amount
    return balance

def show_summary():
    sys.stdout.write("\033c")
    fr=IDATE
    to=IDATE
    exact=(input("Enter exact time period for summar?(y/n):").strip().lower()=='y')
    if exact:
        print("Show summary from which date?")
        while fr==IDATE:
            fr_str = input("Enter 'from' date (YYYY-MM-DD) or leave blank for no limit: ").strip()
            if fr_str:
                try:
                    fr = datetime.datetime.strptime(fr_str, '%Y-%m-%d')
                except ValueError:
                    print("Invalid date format. Please use YYYY-MM-DD.")
            else:
                fr=-1
        print("Show summary to which date?")
        while to==IDATE:
            to_str = input("Enter 'to' date (YYYY-MM-DD) or leave blank for no limit: ").strip()
            if to_str:
                try:
                    to = datetime.datetime.strptime(to_str, '%Y-%m-%d')
                except ValueError:
                    print("Invalid date format. Please use YYYY-MM-DD.")
            else:
                to=-1
    else:
        days=-1
        while days<0:
            try:
                days_inp=input("Enter number of days to look back for summary (leave blank for month): ").strip()
                if days_inp:
                    days= int(days_inp)
                else:
                    days=30

                if days<0:
                    print("Number of days must be non-negative.")
            except:
                print("Please enter a valid integer.")
        to=datetime.datetime.now()
        fr=to - datetime.timedelta(days=days)

    if fr!=-1 and to!=-1 and fr>to:
        fr, to = to, fr

    neg,pos=0.0,0.0
    for t in transactions:
        if fr!=-1 and t.date<fr:
            continue
        if to!=-1 and t.date>to:
            continue
        if t.positive:
            pos+=t.amount
        else:   
            neg+=t.amount
    change_theme("w")
    print(f"Summary{f' from {fr.strftime('%Y-%m-%d')}' if fr!=-1 else ''}{f' to {to.strftime('%Y-%m-%d')}' if to!=-1 else ''}{'for all time' if fr==to==-1 else ''}:".center(WIDTH))
    print(f"Total Positive: ${pos:.2f}".center(WIDTH))
    print(f"Total Negative: -${neg:.2f}".center(WIDTH))
    print(f"Total activity: ${(pos-neg):.2f}".center(WIDTH))
    change_theme("r")
    input("Press Enter to continue...")

def canc_manage():
    global manage_flag
    manage_flag=False

def canc_see():
    global see_flag
    see_flag=False

def manage_transaction(trans):
    global manage_flag
    manage_flag=True
    menu = [
        ("Edit Transaction", edit_transaction, trans),
        ("Delete Transaction", delete_transaction, trans),
        ("Back", canc_manage, None)
    ]
    while manage_flag:
        choose(menu, str(trans))

def edit_transaction(trans):
    def change_amount(trans):
        amount=0.0
        while amount==0.0:
            try:
                amount = float(input("Enter new amount: ").strip())
                if amount == 0.0:
                    print("Amount must be non-zero.")
            except ValueError:
                print("Invalid amount. Please enter a numeric value")
        positive= (amount > 0)
        amount=abs(amount)
        trans.amount=amount
        trans.positive=positive
        input("Amount updated. Press Enter to continue...")
    def change_date(trans):
        date=IDATE
        while date==IDATE:
            date_str = input("Enter new date (YYYY-MM-DD): ").strip()
            try:
                date = datetime.datetime.strptime(date_str, '%Y-%m-%d')
            except ValueError:
                print("Invalid date format. Please use YYYY-MM")
        trans.date=date
        input("Date updated. Press Enter to continue...")
    def change_note(trans):
        note=input("Enter new note: ").strip()
        trans.note=note
        input("Note updated. Press Enter to continue...")
    def change_category(trans):
        category=input("Enter new category: ").strip().capitalize()
        trans.category=category
        input("Category updated. Press Enter to continue...")
    menu=[
        ("Change Amount", change_amount, trans),
        ("Change Date", change_date, trans),
        ("Change Note", change_note, trans),
        ("Change Category", change_category, trans),
        ("Back", lambda:0, None)
        ]
    choose(menu, str(trans))

def delete_transaction(trans):
    global transactions
    sys.stdout.write("\033c")
    sure=input("Are you sure you want to delete this transaction? (y/n): ").strip().lower()
    if sure != 'y':
        return
    transactions.remove(trans)
    input("Transaction Removed. Press Enter to continue...")

def see_transactions_manage():
    global see_flag
    see_flag=True
    while see_flag:
        menu = [(str(t), manage_transaction, t) for t in sorted(transactions, reverse=True, key=lambda x:x.date)]+[("Back", canc_see, None)]
        choose(menu, "Select a transaction to manage:")

def exit_program():
    save_transactions()
    sys.stdout.write(RESET)
    sys.exit(0)

def pipeline():
    menu = [
        ("Add Transaction", add_transaction, None),
        ("Show Transactions", show_transactions, None),
        ("Manage Transactions", see_transactions_manage, None),
        ("Show Summary", show_summary, None),
        ("Exit", exit_program, None)
    ]
    choose(menu, f"Balance: {balance()}")

def choose_csv():
    use_csv=True

def choose_json():
    use_csv=False

if __name__ == "__main__":
    
    try:
        choose([("Use JSON storage", choose_json, None),("Use CSV storage", choose_csv, None)], "Choose storage format (json recommended):")
        load_transactions()
        while True:
            pipeline()
    except:
        save_transactions()