import datetime
import json
import os
from pathlib import Path

import requests
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from models import *
from settings import *


class RequestJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, (datetime.date, datetime.datetime)):
            return o.isoformat()
        if isinstance(o, AbstractDataObject):
            return o.__dict__
        return o


class MambuAPI:
    def __init__(self):
        self.postman_collection_fp = (
            Path(".")
            / "postman_collections"
            / "RazerHackathon.postman_collection.json"
        )
        with open(self.postman_collection_fp, "r") as f:
            self.api_collections = json.load(f)

        self.auth = ("Team33", "pass10D1917C11")
        self.username = "team33"
        _res_branch_id = self.get_branch_id().json()
        self.branch_id = _res_branch_id["encodedKey"]
        self.json_encoder = RequestJSONEncoder()

        self.db_engine = create_engine(DATABASE_URI)
        self.db = scoped_session(sessionmaker(bind=self.db_engine))

    def get_id_document(self):
        """Testing"""
        url = self.api_collections["item"][0]["request"]["url"]["raw"]
        res = requests.get(url, auth=self.auth)
        return res

    def get_branch_id(self):
        """init-ing the branch id"""
        raw_string = self.api_collections["item"][2]["request"]["url"]["raw"]
        url = raw_string.replace("{{username}}", self.username)
        res = requests.get(url, auth=self.auth)

        return res

    def create_client(
        self,
        first_name,
        last_name,
        nirc,
        address,
        country_of_birth,
        razerID='',
        preferred_lang="ENGLISH",
        notes="Enjoys playing RPG",
    ):
        """Create client"""
        payload = {
            "client": {
                "firstName": first_name,
                "lastName": last_name,
                "preferredLanguage": preferred_lang,
                "notes": notes,
                "assignedBranchKey": self.branch_id,
            },
            "idDocuments": [
                {
                    "identificationDocumentTemplateKey": "8a8e867271bd280c0171bf7e4ec71b01",
                    "issuingAuthority": "Immigration Authority of Singapore",
                    "documentType": "NRIC/Passport Number",
                    "validUntil": "2021-09-12",
                    "documentId": nirc,
                }
            ],
            "addresses": [],
            "customInformation": [
                {"value": country_of_birth, "customFieldID": "countryOfBirth"},
                {"value": razerID, "customFieldID": "razerID"},
            ],
        }
        data_str = self.json_encoder.encode(payload)
        headers = {
            "Content-type": "application/json",
            "Authorization": "Basic VGVhbTMzOnBhc3MxMEQxOTE3QzEx",
        }
        url = self.api_collections["item"][3]["request"]["url"]["raw"]

        res = requests.post(
            url, data=data_str, auth=self.auth, headers=headers
        )
        if res.status_code == requests.codes.ok or requests.codes.created:
            mambu_client_id = res.json()["client"]["encodedKey"]
            client = Client(
                first_name=first_name,
                last_name=last_name,
                mambu_client_id=mambu_client_id,
            )
            self.db.add(client)
            self.db.commit()
        else:
            print(f'Status code: {res.status_code}')
        return res

    def create_current_acc(
        self,
        client_id,
        over_draft_limit=0,
        over_draft_interest=5,
        interest_rate=1.25,
    ):
        """Create a current acc for a client id"""
        payload = {
            "savingsAccount": {
                "name": "Digital Account",
                "accountHolderType": "CLIENT",
                "accountHolderKey": client_id,
                "accountState": "APPROVED",
                "productTypeKey": "8a8e878471bf59cf0171bf6979700440",
                "accountType": "CURRENT_ACCOUNT",
                "currencyCode": "SGD",
                "allowOverdraft": "true",
                "overdraftLimit": over_draft_limit,
                "overdraftInterestSettings": {
                    "interestRate": over_draft_interest
                },
                "interestSettings": {"interestRate": interest_rate},
            }
        }
        data_str = self.json_encoder.encode(payload)
        headers = {
            "Content-type": "application/json",
            "Authorization": "Basic VGVhbTMzOnBhc3MxMEQxOTE3QzEx",
        }
        url = self.api_collections["item"][4]["request"]["url"]["raw"]

        res = requests.post(
            url, data=data_str, auth=self.auth, headers=headers
        )
        mambu_acc_id = res.json()["savingsAccount"]["encodedKey"]
        client = (
            self.db.query(Client)
            .filter(Client.mambu_client_id == client_id)
            .all()[0]
        )
        client.add_account(mambu_acc_id)
        return res

    def deposit(self, account_id, amount):
        """Deposit an amount to an account"""
        payload = {
            "amount": amount,
            "notes": "Deposit into savings account",
            "type": "DEPOSIT",
            "method": "bank",
            "customInformation": [
                {
                    "value": "unique identifier for receipt",
                    "customFieldID": "IDENTIFIER_TRANSACTION_CHANNEL_I",
                }
            ],
        }
        data_str = self.json_encoder.encode(payload)
        headers = {
            "Content-type": "application/json",
            "Authorization": "Basic VGVhbTMzOnBhc3MxMEQxOTE3QzEx",
        }
        raw_string = self.api_collections["item"][5]["request"]["url"]["raw"]
        url = raw_string.replace("{{accountId}}", account_id)
        res = requests.post(
            url, data=data_str, auth=self.auth, headers=headers
        )

        return res

    def transfer(self, account_id, target_account_id, amount):
        """Transfer an amount from an acc to another """
        payload = {
            "type": "TRANSFER",
            "amount": amount,
            "notes": "Transfer to Expenses Account",
            "toSavingsAccount": target_account_id,
            "method": "bank",
        }
        raw_string = self.api_collections["item"][6]["request"]["url"]["raw"]
        url = raw_string.replace("{{accountId}}", account_id)
        data_str = self.json_encoder.encode(payload)
        headers = {
            "Content-type": "application/json",
            "Authorization": "Basic VGVhbTMzOnBhc3MxMEQxOTE3QzEx",
        }
        res = requests.post(
            url, data=data_str, auth=self.auth, headers=headers
        )

        return res

    def get_all_transactions(self, account_id):
        """Get all transactions from an account id"""
        raw_string = self.api_collections["item"][7]["request"]["url"]["raw"]
        url = raw_string.replace("{{accountId}}", account_id)

        res = requests.get(url, auth=self.auth)
        return res

    def get_account(self, account_id):
        """Get account information from an account id"""
        raw_string = self.api_collections["item"][9]["request"]["url"]["raw"]
        url = raw_string.replace("{{accountId}}", account_id)

        res = requests.get(url, auth=self.auth)
        return res


if __name__ == "__main__":
    test = MambuAPI()
