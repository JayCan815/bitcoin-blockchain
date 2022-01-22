from socket import *
import re
from re import search


serverPort = 10001


def isClientPayer(message):
    print(message)
    print(message.find("A"))
    indexOfAccount = int(message.find("A"))
    if indexOfAccount == 0:
        return True
    return False


def checkIfTxIsAvailable(transaction):
    print("checkIfTxIsAvailable")
    file = open("Unconfirmed_T.txt", "r")
    ledger = file.read().splitlines()
    for line in ledger:
        print(line, transaction)
        if line.find(transaction) != -1:
            file.close()
            return True
    file.close()
    return False


def creditConfirmedBalance(transaction):
    # account is the first 8 chars of transaction string
    accountToCharge = transaction[:8]
    # amount to charge is last 8 chars
    amountInHex = transaction[16:]
    # adding 0x to convert to proper hex
    amountInHex = "0x" + amountInHex
    print("Charging account:", accountToCharge)
    print("Amount due in hex:", amountInHex)
    accountA1Balance = ""
    accountA2Balance = ""
    confirmedA1Balance = ""
    confirmedA2Balance = ""
    index = 1
    file = open("ClientABalance.txt", "r")
    ledger = file.read().splitlines()
    file.close()
    for line in ledger:
        # if re.search("[0-9A-Za-z]", line) is None:
        #     break
        # first line always has Account A1
        if index == 1:
            accountA1Balance = line
            # confirmed balance is last 8 chars of string
            confirmedA1Balance = accountA1Balance[18:]
            confirmedA1Balance = "0x" + confirmedA1Balance
        # second line is always Account A2
        if index == 2:
            accountA2Balance = line
            confirmedA2Balance = accountA2Balance[18:]
            confirmedA2Balance = "0x" + confirmedA2Balance
        index = index + 1

    # subtract amount from respective confirmed account balance and then write back both accounts to file
    if accountToCharge == "A0000001":
        confirmedA1Balance = int(confirmedA1Balance, 16) - int(amountInHex, 16) - 2
        confirmedA1Balance = hex(confirmedA1Balance)
        confirmedA1Balance = confirmedA1Balance[2:]
        confirmedA1Balance = prependZeros(confirmedA1Balance)
        ledger = open("ClientABalance.txt", "w")
        accountA1Balance = accountA1Balance[:18]
        accountA1Balance = accountA1Balance + confirmedA1Balance
        ledger.writelines([accountA1Balance + "\n", accountA2Balance + "\n"])
        ledger.close()

    if accountToCharge == "A0000002":
        confirmedA2Balance = int(confirmedA2Balance, 16) - int(amountInHex, 16) - 2
        confirmedA2Balance = hex(confirmedA2Balance)
        confirmedA2Balance = confirmedA2Balance[2:]
        confirmedA2Balance = prependZeros(confirmedA2Balance)
        ledger = open("ClientABalance.txt", "w")
        accountA2Balance = accountA2Balance[:18]
        accountA2Balance = accountA2Balance + confirmedA2Balance
        ledger.writelines([accountA1Balance + "\n", accountA2Balance + "\n"])
        ledger.close()


def removeTransactionFromUnconfirmed(transaction):
    transactions = []
    file = open("Unconfirmed_T.txt", "r")
    ledger = file.read().splitlines()
    for line in ledger:
        if re.search("[0-9A-Za-z]", line) is None:
            print("empty line removed")
        transactions.append(line)
    file.close()

    file = open("Unconfirmed_T.txt", "r+")
    file.truncate(0)
    file.close()

    print("Transactions read from Unconfirmed_T.txt:", transactions)

    ledger = open("Unconfirmed_T.txt", "w")
    # loop through transactions read from file, write each tx back to Unconfirmed_T.txt unless it is a match
    # for the tx we are processing, in which case we skip writing this tx back to file.
    transactionFound = False # flag will prevent us removing more than one tx
    for tx in transactions:
        if search(transaction, tx) and not transactionFound:
            print("transaction found in Unconfirmed.txt, removing transaction...")
            transactionFound = True
        else:
            ledger.write(tx + "\n")
    ledger.close()


def appendTransactionToConfirmed(transaction):
    print("in append fn")
    file = open("Confirmed_T.txt", "r")
    lines = file.read().splitlines()
    file.close()
    # if the document is empty, then we write to file
    # otherwise we append
    if len(lines) == 0:
        writeToFile = open("Confirmed_T.txt", "w")
        writeToFile.write(transaction + "\n")
        writeToFile.close()
    else:
        print("writing...")
        appendToFile = open("Confirmed_T.txt", "a")
        appendToFile.write(transaction + "\n")
        appendToFile.close()


def prependZeros(hexAmount):
    numOfZerosToAdd = len(hexAmount)
    numOfZerosToAdd = 8 - numOfZerosToAdd

    while not numOfZerosToAdd == 0:
        hexAmount = "0" + hexAmount
        numOfZerosToAdd = numOfZerosToAdd - 1
    return str(hexAmount.upper())


def debitAccounts(transaction):
    # getting account to debit
    accountToDebit = transaction[8:16]
    # getting amount to debit
    amountToDebit = transaction[16:]
    amountToDebit = "0x" + amountToDebit
    file = open("ClientABalance.txt", "r")
    accountBalances = file.read().splitlines()
    file.close()
    a1Balance = accountBalances[0]
    a2Balance = accountBalances[1]

    if accountToDebit == "A0000001":
        unconfirmedBalance = a1Balance[9:17]
        unconfirmedBalance = "0x" + unconfirmedBalance
        newUnconfirmedBalance = int(unconfirmedBalance, 16) + int(amountToDebit, 16)
        newUnconfirmedBalance = hex(newUnconfirmedBalance)
        newUnconfirmedBalance = newUnconfirmedBalance[2:]
        newUnconfirmedBalance = prependZeros(newUnconfirmedBalance)
        confirmedBalance = a1Balance[18:]
        confirmedBalance = "0x" + confirmedBalance
        newConfirmedBalance = int(confirmedBalance, 16) + int(amountToDebit, 16)
        newConfirmedBalance = hex(newConfirmedBalance)
        newConfirmedBalance = newConfirmedBalance[2:]
        newConfirmedBalance = prependZeros(newConfirmedBalance)
        ledger = open("ClientABalance.txt", "w")
        a1Balance = accountToDebit + ":" + newUnconfirmedBalance + ":" + newConfirmedBalance
        ledger.write(a1Balance + "\n")
        ledger.write(a2Balance + "\n")
        ledger.close()
        print("Account:", accountToDebit, "amount credited in decimal:", int(amountToDebit, 16), "new account balance:", a1Balance)
    if accountToDebit == "A0000002":
        unconfirmedBalance = a2Balance[9:17]
        unconfirmedBalance = "0x" + unconfirmedBalance
        newUnconfirmedBalance = int(unconfirmedBalance, 16) + int(amountToDebit, 16)
        newUnconfirmedBalance = hex(newUnconfirmedBalance)
        newUnconfirmedBalance = newUnconfirmedBalance[2:]
        newUnconfirmedBalance = prependZeros(newUnconfirmedBalance)
        confirmedBalance = a2Balance[18:]
        confirmedBalance = "0x" + confirmedBalance
        newConfirmedBalance = int(confirmedBalance, 16) + int(amountToDebit, 16)
        newConfirmedBalance = hex(newConfirmedBalance)
        newConfirmedBalance = newConfirmedBalance[2:]
        newConfirmedBalance = prependZeros(newConfirmedBalance)
        ledger = open("ClientABalance.txt", "w")
        a2Balance = accountToDebit + ":" + newUnconfirmedBalance + ":" + newConfirmedBalance
        ledger.write(a1Balance + "\n")
        ledger.write(a2Balance + "\n")
        ledger.close()
        print("Account:", accountToDebit, "amount credited in decimal:", int(amountToDebit, 16), "new account balance:", a2Balance)


def transactionHandler(transactions):
    numOfTransactions = len(transactions)
    print("Number of incoming transactions:", numOfTransactions)
    # loop through each tx in our list and handle each one
    if(numOfTransactions == 4):
        while not numOfTransactions == 0:
            # select first element in list and then delete
            transaction = transactions[0]
            del(transactions[0])
            # check if client is payer in this transaction
            isPayer = isClientPayer(transaction)
            print(isPayer)
            if isPayer:
                # make sure Tx is in Unconfirmed_Txt
                isTxAvailable = checkIfTxIsAvailable(transaction)
                print(isTxAvailable, transaction)
                if not isTxAvailable:
                    print("Warning transaction is invalid, client will not be charged for this transaction:", transaction)
                    numOfTransactions = numOfTransactions - 1
                else:
                    # reduce confirmed balance by tx amount
                    creditConfirmedBalance(transaction)

                    # remove tx from unconfirmed.txt
                    removeTransactionFromUnconfirmed(transaction)

                    # append to confirmedTx.txt
                    appendTransactionToConfirmed(transaction)
                    # do this at the end of each iteration
                    numOfTransactions = numOfTransactions - 1
            # payee flow else
            else:
                # debit unconfirmed and confirmed accounts
                debitAccounts(transaction)
                # append transaction to Confirmed_T
                appendTransactionToConfirmed(transaction)
                numOfTransactions = numOfTransactions - 1


# main driver for program
def serverDriver():
    serverSocket = socket(AF_INET, SOCK_DGRAM)
    serverSocket.bind(('', serverPort))
    print('The server is ready to receive')
    while True:
        message, clientAddress = serverSocket.recvfrom(2048)
        # each transaction is 24 chars long, divide to get # of tx
        numOfTransactions = len(message) / 24
        numOfTransactions = int(numOfTransactions)
        # stripping extra chars from socket message
        message = str(message)
        message = message[2:]
        lastIndex = len(message) - 1
        message = message[0:lastIndex]
        # each transaction gets pushed onto a list
        transactions = []
        # transactions come in one long string, so we parse the first 24 chars recursively to extract each tx
        while not numOfTransactions == 0:
            transaction = message[:24]
            transactions.append(transaction)
            message = message[24:]
            numOfTransactions = numOfTransactions - 1
        # handles the transaction flow
        transactionHandler(transactions)

serverDriver()