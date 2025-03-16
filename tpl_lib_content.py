#!/usr/bin/env python
import sys, os, string, sqlite3, getopt
from pathlib import Path
import tpl_settings
import comm_functions

class Lib_Content():

    def __init__(self):
        # file_id_dict  key: file_id   value: file_name
        # word_id_dict  key: word      value: word_id
        # tpl_content   key: word_id   values: file_ids
        self.file_id_dict = {}
        self.word_counter = 0
        self.word_id_dict = {}
        self.tpl_content = {}     
        self.file_storage = ""
        self.Settings = tpl_settings.Settings()

    # topic: files
    def set_file_dict(self, path):
       counter = 0
       for root, directories, files in os.walk(path):
           for name in files:
               counter = counter + 1
               self.file_id_dict[counter] = os.path.join(root,name)
       print ("... number of files: ", len(self.file_id_dict))
  
    def get_num_files(self):           return len(self.file_id_dict)
    def get_file_dict(self):           return self.file_id_dict
    def get_file_list(self):           return self.file_id_dict.values()
    def get_file_ids(self):            return sorted(self.file_id_dict.keys())
    def get_file_name(self, file_id):  return self.file_id_dict[file_id]

    def get_file_ids_tuple_list(self): 
        return_list = []
        for file_id in self.get_file_ids():
            return_list.append( ( file_id, self.get_file_name(file_id) ) )
        return len(tuple(return_list)), tuple(return_list)



    def set_file_storage(self):
        path_obj = Path(os.path.join(os.getcwd(),"t2"))
        print (path_obj)
        path_obj.parent.mkdir(exist_ok=True)
        # parents=True, exist_ok=True
        self.file_storage = path_obj
 

    def get_file_storage(self):
        return self.file_storage


    # topic: words
    def get_word_counter(self):        return len(self.word_id_dict)
    def get_num_words(self):           return len(self.word_id_dict)
 
    def add_words(self, word_list, file_id):
        for w in word_list:
            if w in self.word_id_dict:
                word_id = self.get_word_id(w)
                self.add_tpl_content(word_id, file_id)
            else:
                word_counter = self.get_word_counter() + 1
                self.word_id_dict[w] = word_counter
                self.add_tpl_content(word_counter, file_id)

    def get_word_id(self, w): return self.word_id_dict[w]
    def get_word_dict(self):  return self.word_id_dict

    def get_word_ids_tuple_list(self):
        return_list = []
        for key in sorted(self.word_id_dict.keys()):
                return_list.append(  ( str(self.word_id_dict[key]), str(key) ) )
        return len(tuple(return_list)), tuple(return_list)
        
    def clean_up_word_list(self, line_list):
        file_line_string = "".join(line_list)
        trans_table = file_line_string.maketrans("()[]{}.,:;+-*/=_!?<>#@~|^`%&$\n\'\"\\\t\r", \
                                       "                                   "  )
        q1 = file_line_string.translate(trans_table)
        file_line_string = q1.upper( )
        return  list(set(file_line_string.split(" ")))

    def reduce_word_list(self, line_list):
        return_list = []
        for w in line_list:
            if comm_functions.check_word_criteria(w) == 0:
                return_list.append(w)
        return return_list

    # topic: tpl content
    def add_tpl_content(self, word_id, file_id):
        if word_id in self.tpl_content:
            self.tpl_content[word_id].append(file_id)
        else:
            self.tpl_content[word_id] = [file_id]

    def set_tpl_content(self):
        # go through all files
        for i, file_id in enumerate(self.get_file_ids()):
            if i % 100 == 0:
                print (i)

            file_name = self.get_file_name(file_id)

            if i > 2800 and i < 2900:
                print (file_name)

            splitext_tuple = os.path.splitext(file_name)
            # get content of file
            if len(splitext_tuple) >= 1:
                if splitext_tuple[1] == ".dat"  or  splitext_tuple[1] == ".bdf":
                    with open(file_name, 'r') as file_in:
                        try:
                            line_list = file_in.readlines()
                            cleaned = self.clean_up_word_list(line_list)
                            reduced = self.reduce_word_list(cleaned)
                            # print ("num reduced words in file  ", file_id, file_name, "  :  ", len(reduced))
                            self.add_words(reduced, file_id)
                        except:
                            line_list = []
                            self.add_words(["problems_to_read_file"], file_id)
        print ( "tpl content length: ", len(self.get_word_dict()), len(self.get_file_dict()), len(self.get_tpl_content()) )

    def get_tpl_content(self):    return self.tpl_content

    def get_tpl_ids_tuple_list(self):
        return_list = []
        for key in sorted(self.tpl_content.keys()):
            for entry in self.tpl_content[key]:
                return_list.append( (key, entry) )
        return len(tuple(return_list)), tuple(return_list)
    



    # topic: sqlite database
    def create_database(self):
        status = 0
        # create database
        con = sqlite3.connect('tpl_database.db')
        # file ids
        with con:
            cur = con.cursor()
            cur.execute("DROP TABLE IF EXISTS file_ids;")
            cur.execute("CREATE TABLE file_ids(id INT, name TEXT)")
            cur.executemany("INSERT INTO file_ids VALUES(?, ?)", self.get_file_ids_tuple_list()[1])
        # word ids
        with con:
            cur = con.cursor()
            cur.execute("DROP TABLE IF EXISTS word_ids;")
            cur.execute("CREATE TABLE word_ids(id INT, word TEXT)")
            cur.executemany("INSERT INTO word_ids VALUES(?, ?)", self.get_word_ids_tuple_list()[1])
        # tpl content
            cur = con.cursor()
            cur.execute("DROP TABLE IF EXISTS tpl_ids;")
            cur.execute("CREATE TABLE tpl_ids(id INT, tpl INT)")
            cur.executemany("INSERT INTO tpl_ids VALUES(?, ?)", self.get_tpl_ids_tuple_list()[1])        
        # close database
        con.close()
        # check length of file ids, word ids, tpl ids for information or warning issues
        if self.get_file_ids_tuple_list()[0] == 0 or \
            self.get_word_ids_tuple_list()[0] == 0 or \
            self.get_tpl_ids_tuple_list()[0] == 0:
            print ("WARNING: any record length for creating database is zero")
            print ("         problem creating proper database, please check content")
            print ("         of directory that is used for creating of database.")
            status = -1
        return status




    def search_in_database(self, and_list, not_list):
        status = 0
        and_ids = [ [], [] ]
        not_ids = [ [], [] ]
        num_files = 0
        return_list = []
        # open database
        db_connection = sqlite3.connect('tpl_database.db')
        cur = db_connection.cursor() 

        # search in database or printout error message
        try: 
            # get word ids from database for and_list and not_list
            print ("get word ids ...")
            cur.execute("SELECT * FROM " + 'word_ids' + ";")
            rows = cur.fetchall()
            for word in and_list:
                for entry in rows:
                    if word == entry[1]:
                        and_ids[0].append(entry[0])
                        and_ids[1].append(entry[1])
            for word in not_list:
                for entry in rows:
                    if word == entry[1]:
                        not_ids[0].append(entry[0])
                        not_ids[1].append(entry[1])                         
            # print ("and_ids: ", and_ids)
            # print ("not_ids: ", not_ids)
    
            # get according files
            print ("get according files ...")
            cur.execute("SELECT * FROM " + 'tpl_ids' + ";")
            rows = cur.fetchall()
            store = []
            files = []
            
            # anding
            print (" anding ...")
            print (and_ids)
            for i, word_id in enumerate(and_ids[0]):
                # print (" ", files, store)
                for entry in rows:
                    if entry[0] == word_id:
                        files.append(entry[1])
                    num_files = len(files)
                # boolean operation: intersection
                if i >= 1:
                    files = list(set(store) & set(files))
                    # files = list(set.intersection(*[set(x) for x in [store, files]]))
                    # word_string = and_ids[1][i].ljust(10," ")
                    # n1_string = str(num_files).ljust(5)
                    # n2_string = str(len(files)).ljust(5)
                    print (and_ids[1][i], num_files, len(files))
                    store = []
                else: 
                    # word_string = and_ids[1][i].ljust(10," ")
                    # n1_string = str(num_files).ljust(5)
                    print (and_ids[1][i],num_files, len(files))
                store = list(set(files))
                # print (i, len(and_ids[1]), files)
                if i < len(and_ids[1])-1:
                    files = []
                # print (files)
            # not
            print (" not ...")
            store = []
            for i, word_id in enumerate(not_ids[0]):
                num_files = len(files)
                for entry in rows:
                    if entry[0] == word_id:
                        store.append(entry[1])
                for file_id in store:
                    if file_id in files:
                        files.remove(file_id)
                store = []
                # word_string = not_ids[1][i].ljust(10," ")
                # n1_string = str(num_files).ljust(5)
                # n2_string = str(len(files)).ljust(5)
                print (not_ids[1][i], num_files, len(files))
                
            # file names
            cur.execute("SELECT * FROM " + 'file_ids' + ";")
            rows = cur.fetchall()
            print (" list of files: ", len(files))
            for i, entry in enumerate(rows):
                if entry[0] in files:
                    print (" (",str(i+1), ")   ", entry[1])   
                    return_list.append(entry[1])     
            db_connection.close()
            return status, return_list     
        except:
            db_connection.close()
            status = -1
            return_list = []
            print ("ERROR: problem searching database, check location of database")
            return status, return_list       



    # topic: debug
    def get_debug_printout(self, data_type, detail):
        return_list = []
        return_list.append(data_type + "\n")
        if data_type == "MEM":
            return_list.append( str(self.get_num_files())  + "  " + str(self.get_num_words()) )
            if detail == True:
                for key in sorted(self.file_id_dict.keys()):
                    return_list.append(str(key) + "  " + str(self.file_id_dict[key]))
                for key in sorted(self.word_id_dict.keys()):
                    return_list.append(str(key) + "  " + str(self.word_id_dict[key]))
                for key in sorted(self.tpl_content.keys()):
                    return_list.append(str(key) + "  " + str(self.tpl_content[key]))
        if data_type == "FILE_ID":
            for key in sorted(self.file_id_dict.keys()):
                return_list.append(str(key) + "  " + str(self.file_id_dict[key]))
        if data_type == "DB":    
            db_connection = sqlite3.connect('tpl_database.db')
            cur = db_connection.cursor()
            # result = cur.execute("SELECT * FROM sqlite_master").fetchall()
            # result = cur.execute("PRAGMA table_info('%s')" % table_name).fetchall()
            result = cur.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()
            return_list.append("content of tables: " + str(result))
            for table_tuple in result:
                table_name = table_tuple[0]
                return_list.append("   " + table_name)
                cur.execute("SELECT * FROM " + table_name + ";")
                rows = cur.fetchall()
                for row in rows:
                    return_list.append("         " + str(row))
            db_connection.close()
        return return_list
