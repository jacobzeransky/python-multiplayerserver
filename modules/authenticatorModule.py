#Python

import json

# module for authenicating/creating users
# backend 'database' are simple text files

class authenticatorModule():

    def __init__(self, file_n, adminf_n, event_q):
        self.fio = file_n
        self.admins = adminf_n
        tempf = open(self.fio, 'r')
        self.flist = json.load(tempf)
        tempf.close()
        self.events = event_q
       # self.events.put("{}".format(self.flist))
        self.events.put("AuthenticatorModule started on file \'{}\'".format(file_n))

    # checks if user exists, if it does check password as well
    def checkforuser(self, user_n):
        for user, password in self.flist:
            self.events.put("pass =? {}".format(str(password)))
            if str(user_n) == str(user):
                return {'r':True, 'p':password}
        return {'r':False, 'p':None}

    # authenticate user, make sure they exist first
    def authenicate(self, user_n, pass_w):
        pa, res = self.checkforuser(user_n).values()
        self.events.put("{} =? {} :: {}".format(str(pass_w), str(pa), res))
        if res and str(pass_w) == str(pa):
            # info is correct
            return 'c'
        elif res:
            # invalid password
            return 'i'
        # user not found
        return 'n'

    # creates new user if they do not already exist
    def createnewuser(self, user_n, pass_w):
        if self.checkforuser(user_n)['r']:
            # user already exists
            return 'e'

        self.flist.append((user_n, pass_w))
        return 's'

    # check if user can be logged in with admin privileges
    def checkadminstatus(self, user_n):
        tempf = open(self.admins, 'r')
        alist = json.load(tempf)
        tempf.close()

        for ads in alist:
            if str(user_n) == str(ads):
                return True
        return False
        
    def shutdown(self):
        tempf = open(self.fio, 'w')
        json.dump(self.flist, tempf)
        tempf.close()
        self.events.put("AuthenticatorModule shutdown")
        
