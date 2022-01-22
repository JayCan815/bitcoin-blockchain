import sys
from socket import *
import re
# Global Variables
clientMenuDispatcher = {}  # used to invoke functions
serverName = "192.168.254.45"
serverPort = 20000
clientSocket = socket(AF_INET, SOCK_DGRAM)

def getUnconfirmedBalance(account):
    ledger = open("ClientBBalance.txt", "r")
    accountB1Balance = ""
    accountB2Balance = ""
    index = 1
    for line in ledger:
        if index == 1:
            accountB1Balance = line
        index = index + 1
        accountB2Balance = line
    ledger.close()

    if account == "B0000001":
        indexToParseTo = accountB1Balance.find(":")
        temp = accountB1Balance[indexToParseTo+1:]
        indexToParseTo = temp.find(":")
        b1UnconfirmedBalance = temp[:indexToParseTo]
        b1UnconfirmedBalance = "0x" + b1UnconfirmedBalance
        b1UnconfirmedBalance = int(b1UnconfirmedBalance, 16)
        return b1UnconfirmedBalance
    if account == "B0000002":
        indexToParseTo = accountB2Balance.find(":")
        temp = accountB2Balance[indexToParseTo+1:]
        indexToParseTo = temp.find(":")
        b2UnconfirmedBalance = temp[:indexToParseTo]
        b2UnconfirmedBalance = "0x" + b2UnconfirmedBalance
        b2UnconfirmedBalance = int(b2UnconfirmedBalance, 16)
        return b2UnconfirmedBalance


def doesAmountExceedBalance(txAmount, balance):
    txAmount = int(txAmount) + 2
    if txAmount > int(balance):
        return True
    return False


def appendUnconfirmedTx(accounFrom, accountTo, unconfirmedTx):
    unconfirmedTx = hex(unconfirmedTx)
    unconfirmedTx = unconfirmedTx.upper()
    parsedHex = unconfirmedTx[2:]
    numOfZerosToPrepend = 8 - len(parsedHex)
    while not numOfZerosToPrepend == 0:
        parsedHex = "0" + parsedHex
        numOfZerosToPrepend = numOfZerosToPrepend - 1
    unconfirmedTx = accounFrom + accountTo + parsedHex
    ledger = open("Unconfirmed_T.txt", "a")
    ledger.write("\n" + unconfirmedTx)
    ledger.close()
    print("unconfirmedTx written to text file:", unconfirmedTx)
    return unconfirmedTx

def clientMenu():
    print("Client Menu")
    print("1. Enter a new transaction.")
    print("2. Current Account(s) balance.")
    print("3. View unconfirmed transactions.")
    print("4. View last X amount of confirmed transactions.")
    print("5. Print the blockchain.")
    print("6. Exit")
    userSelection = input()
    validSelection = re.findall("[1-6]", userSelection)
    if len(validSelection) == 0:
        print("Invalid selection please try again\n\n")
        clientMenu()
    validSelection = range(1, 7)
    if int(userSelection) not in validSelection:
        print("Invalid selection please try again\n\n")
        clientMenu()

    functionIndex = str(userSelection)
    clientMenuDispatcher[functionIndex]()

def reduceUnconfirmedBalance(account, amount):
    print("reduceUnconfirmedBalance function", " account:", account, " amount:", amount)
    ledger = open("ClientBBalance.txt", "r+")
    index = 1
    accountB1Balance = ""
    accountB2Balance = ""
    for line in ledger:
        if index == 1:
            accountB1Balance = line
        if index == 2:
            accountB2Balance = line
        index = index + 1
    ledger.truncate(0)
    ledger.close()

    if account == "B0000001":
        print(accountB1Balance)
        accountName = accountB1Balance[:8]
        unconfirmedBalance = accountB1Balance[9:17]
        confirmedBalance = accountB1Balance[18:]
        print("unconfirmedBalance:", unconfirmedBalance, "confirmedBalance:", confirmedBalance)

        unconfirmedBalance = "0x" + unconfirmedBalance
        unconfirmedBalance = int(unconfirmedBalance, 16)
        print("unconfirmedBalance in decimal:", unconfirmedBalance)
        print(amount)
        unconfirmedBalance = unconfirmedBalance - amount - 2
        print("unconfirmedBalance after subtracting amount: ", unconfirmedBalance)

        unconfirmedBalance = hex(unconfirmedBalance)
        unconfirmedBalance = unconfirmedBalance[2:]
        numOfZerosToPrePend = 8 - len(unconfirmedBalance)
        while not numOfZerosToPrePend == 0:
            unconfirmedBalance = "0" + unconfirmedBalance
            numOfZerosToPrePend = numOfZerosToPrePend - 1
        unconfirmedBalance = unconfirmedBalance.upper()
        print("unconfirmedBalance after prepending 0's:", unconfirmedBalance)
        transactions = []
        transactions.append(unconfirmedBalance)

        accountB1Balance = accountName + ":" + unconfirmedBalance + ":" + confirmedBalance
        print("accountBalance after adjusted unconfirmed balance:", accountB1Balance)
        ledger = open("ClientBBalance.txt", "w")
        ledger.write(accountB1Balance)
        ledger.write(accountB2Balance)
        ledger.close()

    if account == "B0000002":
        accountName = accountB2Balance[:8]
        unconfirmedBalance = accountB2Balance[10:17]
        confirmedBalance = accountB2Balance[18:]
        print("unconfirmedBalance: ", unconfirmedBalance, "confirmedBalance", confirmedBalance)

        unconfirmedBalance = "0x" + unconfirmedBalance
        unconfirmedBalance = int(unconfirmedBalance, 16)
        print("unconfirmedBalance in decimal:", unconfirmedBalance)
        unconfirmedBalance = unconfirmedBalance - amount - 2
        print("unconfirmedBalance after subtracting amount: ", unconfirmedBalance)

        unconfirmedBalance = hex(unconfirmedBalance)
        unconfirmedBalance = unconfirmedBalance[2:]
        numOfZerosToPrePend = 8 - len(unconfirmedBalance)
        while not numOfZerosToPrePend == 0:
            unconfirmedBalance = "0" + unconfirmedBalance
            numOfZerosToPrePend = numOfZerosToPrePend - 1
        unconfirmedBalance = unconfirmedBalance.upper()
        print("unconfirmedBalance after prepending 0's:", unconfirmedBalance)
        transactions = []
        transactions.append(unconfirmedBalance)

        accountB2Balance = accountName + ":" + unconfirmedBalance + ":" + confirmedBalance
        print("accountBalance after adjusted unconfirmed balance:", accountB2Balance)
        ledger = open("ClientBBalance.txt", "w")
        ledger.write(accountB1Balance)
        ledger.write(accountB2Balance)
        ledger.close()

def newTransaction():
    accountTo = ""
    accountFrom = ""
    print("Select account to pay from")
    print("1. Account B0000001")
    print("2. Account B0000002")
    userInput = int(input())
    if userInput == 1:
        accountFrom = "B0000001"
    if userInput == 2:
        accountFrom = "B0000002"

    print("Select account to pay to")
    print("1. Account A0000001")
    print("2. Account A0000002")
    userInput = int(input())

    if userInput == 1:
        accountTo = "A0000001"
    if userInput == 2:
        accountTo = "A0000002"

    amountInDecimal = int(input("Please enter amount to pay in decimal: "))

    # get unconfirmed account balance
    accountBalance = getUnconfirmedBalance(accountFrom)
    print("accountBalance", accountBalance)
    # make sure amount they are attempting to pay with, does not exceed their account balance
    amountExceeded = doesAmountExceedBalance(amountInDecimal, accountBalance)
    if amountExceeded:
        print("\n\n\nAmount exceeds account balance, please try again.")
        newTransaction()

    # reduce unconfirmed balance by transaction amount
    reduceUnconfirmedBalance(accountFrom, amountInDecimal)
    print("Tx:", accountFrom, " pays ", accountTo, " the amount of ", amountInDecimal, " BC")

    # append transaction to Unconfirmed_Txt
    unconfirmedTx = appendUnconfirmedTx(accountFrom, accountTo, amountInDecimal)

    # send tx to full node
    clientSocket.sendto(unconfirmedTx.encode(), (serverName, serverPort))

def viewBalance():
    ledger = open("ClientBBalance.txt", "r")
    accountB1Balance = ""
    accountB2Balance = ""
    index = 1
    for line in ledger:
        if index == 1:
            accountB1Balance = line
        if index == 2:
            accountB2Balance = line
        index = index + 1

    print(accountB1Balance)
    print(accountB2Balance)
    clientMenu()


def viewUnconfrimedTx():
    ledger = open("Unconfirmed_T.txt", "r")
    for line in ledger:
        print(line)
    ledger.close()
    clientMenu()

def viewLastXTxs():
    file = open("Confirmed_T.txt", "r")
    lines = file.read().splitlines()
    file.close()

    numOfTx = input("Enter X amount of tx's to view: ")
    numOfTx = int(numOfTx)
    if len(lines) == 0:
        print("No confirmed tx's yet")
        clientMenu()
    while numOfTx > 0:
        for line in lines:
            print(line)
            numOfTx = numOfTx - 1
    clientMenu()

def printBlockChain():
    print("\n\nprintBlockChain function")
    clientMenu()

def exitProgram():
    print("Exiting program...")
    sys.exit(0)

# initialize our dispatcher
clientMenuDispatcher = {
    "1": newTransaction,
    "2": viewBalance,
    "3": viewUnconfrimedTx,
    "4": viewLastXTxs,
    "5": printBlockChain,
    "6": exitProgram
}

while True:
    clientMenu()
