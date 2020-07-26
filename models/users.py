from models.database import Database
from models.quotes import Quote
from models.encryption_ import Encrypt, Decrypt
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime


class User(object):

    COLLECTION = "Users"

    def __init__(self,
                 name,
                 email,
                 username,
                 password,
                 current_sessions=[],
                 about=None,
                 totalQuotes=0,
                 totalDownloads=0,
                 _id=None):

        self.name = name
        self.totalQuotes = totalQuotes
        self.username = username
        self.email = email
        self.password = User.set_password(password)
        self.current_sessions = current_sessions
        self.about = about
        self.totalDownloads = totalDownloads
        self._id = _id

    @staticmethod
    def set_password(password):
        return generate_password_hash(password, method='pbkdf2:sha512')

    @staticmethod
    def checkUser(username, password, signUp=False, email=False):
        """
            This function takes username and password
            Returns if one of the following is the Case

                Case 1 : if user is not found = None
                Case 2 : if user is found 
                    a) if password is correct = True
                    b) if password is incorrect = False
        """

        if email:
            result = Database.find(collection=User.COLLECTION,
                                   query={"email": username})
        else:
            result = Database.find(collection=User.COLLECTION,
                                   query={"username": username})

        if signUp:
            if result:
                return User.getUser(result)
            return result

        if result:
            if check_password_hash(result.get("password"), password):
                return result
            else:
                return False

    def saveUser(self):
        """
            Inserts User into the collection
            Returns -1 if User Exists in Users Collection
        """
        if User.checkUser(username=self.username,
                          password=self.password, signUp=True):
            return False

        Database.insert(collection=User.COLLECTION,
                        data=self.toJson())
        return True

    def getUserInfo(self):
        """
            Converts User object to Json Object
            Adds 'created_at' attribute by using '_id'

            Returns Json Object 
        """
        userData = self.toJson()
        userData['created_at'] = Database.created_at(self._id)

        return userData

    @staticmethod
    def createSession(jsonObj):
        """
            Creates a new user session and updates current user document 
            in User Collection

            Returns New User Session
        """

        newSession = Encrypt(str(datetime.utcnow()))
        newSession = [i.decode('utf-8') for i in newSession]

        if jsonObj['current_sessions'] is None:
            jsonObj['current_sessions'] = newSession
        else:
            jsonObj['current_sessions'].append(newSession)

        Database.update(collection=User.COLLECTION,
                        query={'_id': jsonObj['_id']}, update_query=jsonObj)

        # print('updating Database for new session')
        return newSession[0]

    @staticmethod
    def getUserBySession(current_session, logout=False):
        """
            Finds User using Current Session

                If Found:
                    Returns User Object
                Else:
                    Returns None

        """
        result = Database.find_multi(
            collection=User.COLLECTION,
            SearchField='current_sessions', items=[current_session])

        if result:
            return User.getUserByID(result.get('_id'), logout=logout)

    @staticmethod
    def verifySession(current_session):
        return Database.find_multi(collection=User.COLLECTION,
                                   SearchField='current_sessions',
                                   items=[current_session])

    @staticmethod
    def getUserByID(_id, logout=False):
        usr = Database.find(collection=User.COLLECTION, query={'_id': _id})
        if usr:
            usr.pop('password', None)
            # if not logout:
            #     usr.pop('current_sessions', None)
        return usr

    @staticmethod
    def sessionCreatedAt(current_session):
        """ 
            Decrypts the session for cookie

            if session is real, 
                Returns datetime object
            else
                Returns None
        """
        result = User.verifySession(current_session)
        if result:
            result = result.get('current_sessions')
            current_session_encoded = current_session.encode('utf-8')
            key = 0
            for k in result:
                if current_session in k:
                    key = k[1]
                    break
            if key:
                time = Decrypt(enMessage=current_session_encoded,
                               key=key.encode('utf-8'))
                return datetime.strptime(time, '%Y-%m-%d %H:%M:%S.%f')

    @staticmethod
    def removeSession(current_session):
        """
            Removes a user session provided from the argument 
            and updates current user document in User Collection

            Returns None
        """
        usr = User.getUserBySession(current_session, logout=True)

        for session in usr.get('current_sessions'):
            if current_session in session:
                ele = session

        usr['current_sessions'].remove(ele)

        Database.update(collection=User.COLLECTION,
                        query={'_id': usr.get('_id')}, update_query=usr)

    def toJson(self):
        """
            Converts User object to json
            (mostly for saving and accessing user)

        """
        return {"name": self.name,
                "email": self.email,
                "username": self.username,
                "totalQuotes": self.totalQuotes,
                "password": self.password,
                "current_sessions": self.current_sessions,
                "about": self.about,
                "totalDownloads": self.totalDownloads}

    @staticmethod
    def getUserByUsername(username, usr=None):
        if not usr:
            usr = Database.find(collection=User.COLLECTION,
                                query={'username': username})
            if usr:
                usr.pop('password', None)
                usr.pop('current_sessions', None)
                usr.update({'createdAt': Database.created_at(usr['_id'])})
                print('user found!')
                return usr

            print('user not found!')
            return None

        return usr

    @staticmethod
    def getQuotes(_id):
        """
            Returns Quotes uploaded by the User
        """
        return Quote.GetQuotesByUserID(_id)

    @staticmethod
    def getQuotebyQuoteID(quoteID):
        """
            Returns Quote uploaded by the User
            By Using Quote ID
        """
        q = Quote.GetByQuoteID(quoteID)
        if q:
            userID = q.get('userID')
            usr = User.getUserByID(userID)
            if usr:
                q.update(
                    {'name': usr.get('name'),
                     'username': usr.get('username')})
                return q
        else:
            return None

    @staticmethod
    def updateUserInfo(user, _id):
        return Database.update(collection=User.COLLECTION,
                               query={'_id': _id}, update_query=user)

    @staticmethod
    def deleteUser(_id):
        """
            Deletes User from Users Collection
        """
        return Database.delete(collection=User.COLLECTION,
                               query={"_id": _id})

    @staticmethod
    def deleteAllUsers():
        """
            Deletes All Users from Users Collection
            Returns Number of Users Deleted
        """
        return Database.delete_all(collection=User.COLLECTION,
                                   query={})

    @classmethod
    def getUser(cls, json):
        """
            Takes json object as input and 
            Returns User Object
        """
        return cls(**json)

    @staticmethod
    def getUsers():
        """
            Returns all users present in the 
            Users Collection
        """
        return Database.find_all(collection=User.COLLECTION,
                                 query={})

    @staticmethod
    def PostQuote(_cu, quote, quoteID):
        usr = User.verifySession(_cu)
        if usr:
            q = Quote(quote=quote,
                      quoteID=quoteID,
                      name = usr.get('name'),
                      userID=usr.get('_id'))
            q.saveQuote()

    @staticmethod
    def updatePosts(_cu, val=1):
        usr = User.verifySession(_cu)
        if usr:
            totalQuotes = usr.get('totalQuotes')
            totalQuotes += val
            usr.update({'totalQuotes': totalQuotes})
            Database.update(collection=User.COLLECTION,
                            query={"_id": usr.get('_id')},
                            update_query=usr)
            return True

    @staticmethod
    def changePassword(_id, password):

        usr = User.getUserByID(_id)
        if usr:
            usr.update({'password': User.set_password(password)})
            Database.update(collection=User.COLLECTION,
                            query={"_id": usr.get('_id')},
                            update_query=usr)
            return True
        else:
            print(usr)

    @staticmethod
    def changeUsername(_id, username):

        usr = User.getUserByID(_id)
        if usr:
            usr.update({'username': username})
            Database.update(collection=User.COLLECTION,
                            query={"_id": usr.get('_id')},
                            update_query=usr)
            return True

    @staticmethod
    def changeEmail(_id, email):
        usr = User.getUserByID(_id)
        if usr:
            usr.update({'email': email})
            Database.update(collection=User.COLLECTION,
                            query={"_id": usr.get('_id')},
                            update_query=usr)
            return True

    @staticmethod
    def changeAbout(_id, about):

        usr = User.getUserByID(_id)
        if usr:
            usr.update({'about': about})
            print(usr)
            Database.update(collection=User.COLLECTION,
                            query={"_id": usr.get('_id')},
                            update_query=usr)
            return True
        else:
            print(usr)

    @staticmethod
    def updateDownloads(_id, quoteID):
        usr = User.getUserByID(_id)
        if usr:
            usr.update({
            'totalDownloads': usr.get('totalDownloads')+1
            })
            Quote.updateQuoteData(quoteID, Download = True)
            User.updateUserInfo(usr, usr.get('_id'))

    @staticmethod
    def updateQuote(quote, quoteID):
        # print('calling updateQuoteData')
        return Quote.updateQuoteData(quoteID, quote)
