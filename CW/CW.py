import datetime
import json
import os
import sys
import msvcrt

BLACK = "\033[40m;37m"  
WHITE = "\033[107;30m"  
RESET = "\033[0m"
WIDTH=120
IDATE=datetime.datetime(1,1,1,1)

def safe_ex(meth):
    try:
        meth()
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

def choose(menu: list):
    ind = 0
    n = len(menu)
    l=max(len(item[0]) for item in menu)
    iden=' ' * ((WIDTH - l - 2) // 2)
    #l=(l+1)//2*2
    while True:
        sys.stdout.write("\033c")  
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
            menu[ind][1]()
            break

class transaction:
    positive = False
    amount=0.0
    date=datetime.datetime.now()
    note=""

    def __init__(self, positive: bool, amount: float, date: datetime, note: str):
        self.positive = positive
        self.amount = amount
        self.date = date
        self.note = note

    def __str__(self):
        return f"{'+' if self.positive else '-'}${self.amount:.2f} on {self.date.strftime('%Y-%m-%d')}: {self.note}"

transactions=[]

def add_transaction():
    sys.stdout.write("\033c")
    print("Add Transaction")
    pos_input = input("Is this a positive transaction? (y/n): ").strip().lower()
    positive = pos_input == 'y'
    amount=0.0
    while amount<=0.0:
        try:
            amount = float(input("Enter amount: ").strip())
            if amount <= 0.0:
                print("Amount must be positive.")
        except ValueError:
            print("Invalid amount. Please enter a numeric value.")
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
    transactions.append(transaction(positive, amount, date, note))
    input("Transaction added! Press Enter to continue...")

def show_transactions():
    sys.stdout.write("\033c")
    print("Transactions:")
    for t in sorted(transactions, key=lambda x:x.date):
        print(t)
    input("Press Enter to continue...")

def date_time_serializer(obj):
    if isinstance(obj, datetime.datetime):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

def save_transactions():
    with open("transactions.txt", "w") as f:
        json.dump([t.__dict__ for t in transactions], f, default=date_time_serializer)

def load_transactions():
    global transactions
    try:
        with open("transactions.txt", "r") as f:
            data=json.load(f)
            transactions = [transaction(d['positive'], d['amount'], datetime.datetime.fromisoformat(d['date']), d['note']) for d in data]
    except FileNotFoundError:
        transactions = []

def show_summary(fr=-1, to=-1):
    sys.stdout.write("\033c")
    balance=0.0
    for t in transactions:
        if t.positive:
            balance+=t.amount
        else:
            balance-=t.amount
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
    print(f"Summary{f' from {fr.strftime('%Y-%m-%d')}' if fr!=-1 else ''}{f' to {to.strftime('%Y-%m-%d')}' if to!=-1 else ''} {'for all time' if fr==to==-1 else ''}".strip()+":")
    print(f"Total Positive: ${pos:.2f}\nTotal Negative: ${neg:.2f}\nBalance: ${balance:.2f}")

load_transactions()

# add_transaction()
# save_transactions()

# load_transactions()
# show_transactions()
