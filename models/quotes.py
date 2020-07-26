from datetime import datetime
from models.database import Database
from uuid import uuid4
import pymongo


class Quote(object):
    COLLECTION = 'Quotes'

    def __init__(
            self,
            quote,
            name,
            userID,
            quoteID,
            totalDownloads = 0,
            _id=None):

        self.quote = quote
        self.name = name
        self.quoteID = quoteID
        self.userID = userID
        self.totalDownloads = totalDownloads
        self._id = _id

    def toJson(self):
        return {
            'quote': self.quote,
            'name':self.name,
            'userID': self.userID,
            'totalDownloads': self.totalDownloads,
            'quoteID': self.quoteID
        }

    def saveQuote(self):
        """
            This Method Saves Quote object in Quotes Collection
        """
        Database.insert(collection=Quote.COLLECTION,
                        data=self.toJson())

    @staticmethod
    def GetByQuoteID(quoteID):
        JsonQuote = Database.find(
            collection=Quote.COLLECTION, query={'quoteID': quoteID})
        print(quoteID)
        if JsonQuote:
            JsonQuote.update(
                {'created_at': Database.created_at(JsonQuote.get('_id'))})

        return JsonQuote

    @staticmethod
    def GetAllQuotes(query={}, skip_=0, limit_=0, sortField=None):
        return list(Database.find_all(
            collection=Quote.COLLECTION,
            query=query, skip_=skip_, limit_=limit_, sortField=sortField))

    @staticmethod
    def GetQuotesByUserID(userID):
        """
            Finds all Quotes with category provided in the argument
            Returns the cursor (for iterating the Quotes Collection)
        """
        return Database.find_all(collection=Quote.COLLECTION,
                                 query={'userID': userID})

    @staticmethod
    def removeByQuoteID(quoteID):
        """ 
            Deletes Document by quoteID 
            in Quotes Collectionon

            Returns Number of Quotes Deleted
        """
        return Database.delete(collection=Quote.COLLECTION,
                               query={'quoteID': quoteID})

    @staticmethod
    def removeAllQuotesOfUser(userID):
        """ 
            Deletes All Documents by username
            in Quotes Collection

            Returns Number of Quotes Deleted

        """
        # Useful while user wants to delete his profile
        return Database.delete_all(collection=Quote.COLLECTION,
                                   query={"userID": userID})

    @staticmethod
    def removeAllQuotes():
        """ 
            Deletes All Documents in Quotes Collection
            Returns Number of Quotes Deleted
        """
        result = Database.delete_all(collection=Quote.COLLECTION,
                                     query={})
        return result

    @staticmethod
    def updateQuoteData(quoteID, quote=None, Download=None):
        """
            Updates quote of Quote (in json)
            In Quote Collection

            If quote is updated:
                Returns True
            else:
                Returns None
        """
        print('updateQuoteData being called')
        quote_ = Quote.GetByQuoteID(quoteID)
        if quote_:
            print('Quote found!')
            if quote:
                quote_.update({'quote': quote})
                print('updating quote')

            if Download:
                totalD = quote_.get('totalDownloads', 0)
                quote_.update({'totalDownloads': totalD + 1})
                print('updating downloads')

            Database.update(collection=Quote.COLLECTION,
                            query={'quoteID': quoteID},
                            update_query=quote_)
            return True
        print('Quote not found!')
