#!/usr/bin/env python
import sys, os, string, sqlite3
from tkinter import *
from shutil import copyfile
# from tqdm import tqdm


class Lib_Content():

    def __init__(self):
        # file_id_dict  key: file_id   value: file_name
        # word_id_dict  key: word      value: word_id
        # tpl_content   key: word_id   values: file_ids
        self.file_id_dict = {}
        self.word_counter = 0
        self.word_id_dict = {}
        self.tpl_content = {}

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
        return tuple(return_list)

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
        return tuple(return_list)
        
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
            if check_word_criteria(w) == 0:
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
        return tuple(return_list)



    # topic: sqlite database
    def create_database(self):
        # create database
        con = sqlite3.connect('tpl_database.db')
        # file ids
        with con:
            cur = con.cursor()
            cur.execute("DROP TABLE IF EXISTS file_ids;")
            cur.execute("CREATE TABLE file_ids(id INT, name TEXT)")
            cur.executemany("INSERT INTO file_ids VALUES(?, ?)", self.get_file_ids_tuple_list())
        # word ids
        with con:
            cur = con.cursor()
            cur.execute("DROP TABLE IF EXISTS word_ids;")
            cur.execute("CREATE TABLE word_ids(id INT, word TEXT)")
            cur.executemany("INSERT INTO word_ids VALUES(?, ?)", self.get_word_ids_tuple_list())
        # tpl content
            cur = con.cursor()
            cur.execute("DROP TABLE IF EXISTS tpl_ids;")
            cur.execute("CREATE TABLE tpl_ids(id INT, tpl INT)")
            cur.executemany("INSERT INTO tpl_ids VALUES(?, ?)", self.get_tpl_ids_tuple_list())        
        # close database
        con.close()





    def search_in_database(self, and_list, not_list):
        and_ids = [ [], [] ]
        not_ids = [ [], [] ]
        num_files = 0
        return_list = []
        # open database
        db_connection = sqlite3.connect('tpl_database.db')
        cur = db_connection.cursor() 
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
        return return_list            



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



# ------------------------ main ---------------------------------------------------------

def copy_file(src):
    dst_folder = "c:\\tmp\\python\\tpl_search\\file_storage"
    src_folder, src_file = os.path.split(src)
    dst = os.path.join(dst_folder, src_file)
    print (dst_folder, src_folder, src_file, dst)
    copyfile(src, dst)








def check_word_criteria(w):
    criteria = [0,0,0,0,0]
    return_value = 1
#   criteria 1 - no words allowed that are smaller than 2 characters
    if (len(w) < 3):
        criteria[0] = 1
#   criteria 2 - no long digits are allowed
    if ( ( (w.isdigit() == True) and (len(w) >= 5) ) or \
         ( (w.isdigit() == True) and (len(w) <= 2) ) ):
        criteria[1] = 1
#   criteria 3 - no long strings with many digits are allowed
    if (len(w) > 8):
        w_trans = w.translate(w.maketrans("1234567890","          "))
        w_trans = w_trans.replace(" ","")
        if (len(w_trans) <= 2):
            criteria[2] = 1
#   criteria 4 - leading many zeros are not allowed
    if (w[0:3] == "00"):
        criteria[3] = 1
#   criteria 5 - leading digit with following letters are not allowed
    if (len(w) > 1):
        if (w[0].isdigit()==True):
            w_trans = w.translate(w.maketrans("1234567890","          "))
            w_trans = w_trans.replace(" ","")
            if (len(w_trans) > 0):            
                if (w_trans.isalpha()==True):
                    criteria[4] = 1
#   criteria 6 - leading letter and four ending digits are not allowed
    if (len(w) >= 5):
        if (w[0].isalpha()==True):
            if (w[len(w)-4:].isdigit()==True):            
                criteria_06 = 1
#      all criteria should be valid
    if sum(criteria)==0:
        return_value = 0
#      return value
    return return_value      



def read_input_attributes():
    tpl_action = ""
    and_list = []
    not_list = []
    file_in = open("input_attributes.txt","r")
    line_list = file_in.readlines()
    file_in.close()
    if "CREATE" in line_list[0]:
        tpl_action = "CREATE"
    if "SEARCH" in line_list[0]:
        tpl_action = "SEARCH"
        and_list = [entry.upper().strip() for entry in line_list[1].strip().split()]
        try:
            not_list = not_list = [entry.upper().strip() for entry in line_list[2].strip().split()]
        except:
            not_list = []
    return tpl_action, and_list, not_list



# =======================================================================================



def main():
    """
    input_attributes.txt controls the action that should be made,
    create tpl database or search in database:
    
    CREATE
    
    if create is selected, a tpl_database.db file as sqlite database is 
    created and stored in the tpl folder itself, for example:
        c:\soft\nastran\V2022_4\msc20224\nast\tpl\tpl_database.db
    this database is then also used, if a search command is called
    
    
    
    SEARCH
    MDBULK MDMPLN
    not_word
    
    the three lines of the search option contain:
    search command
    anding word list
    not word list
    
    the tpl_database.db is searched according required words
    
    """
    
    
    
    search_result_list = []

    os.chdir("c:\\tmp\\python\\tpl_search")
    print (os.getcwd(), sys.argv) 
    tpl_action, and_list, not_list = read_input_attributes()
    print (tpl_action, and_list, not_list)
    tpl = Lib_Content()


    # (1) CREATE
    if tpl_action == "CREATE":
        # os.chdir("c:\\tmp\\python\\tpl_search\\example_folders")
        # os.chdir("c:\\soft\\nastran\\V2021_1\\msc20211\\nast\\doc\\tpl")
        # os.chdir("c:\\soft\\nastran\\V2021_3\\msc20213\\nast\\tpl")
        # os.chdir("c:\\soft\\nastran\\V2022_4\\msc20224\\nast\\tpl")
        # C:\soft\nastran\V2023_1\msc20231\nast\tpl
        os.chdir("c:\\soft\\nastran\\V2023_1\\msc20231\\nast\\tpl")
        
        print (os.getcwd())
        # set all files
        tpl.set_file_dict(".")
        # read content of files
        tpl.set_tpl_content()
        # create sqlite database
        tpl.create_database()

        # DEBUG
        debug_list = []
        for line in tpl.get_debug_printout("MEM", True):
            debug_list.append(line + "\n")
        debug_list.append(" --- \n")
        for line in tpl.get_debug_printout("FILE_ID", True):
            debug_list.append(line + "\n")
        debug_list.append(" --- \n")
        for line in tpl.get_debug_printout("DB", True):
            debug_list.append(line + "\n")
        with open('debug.txt', 'w') as f:
            for line in debug_list:
                try:
                    f.write(debug_list)
                except:
                    pass
        # file_out.close()
    

    # (2) SEARCH
    # os.chdir("c:\\tmp\\python\\tpl_search\\example_folders")
    # os.chdir("c:\\soft\\nastran\\V2021_1\\msc20211\\nast\\doc\\tpl")
    # os.chdir("c:\\soft\\nastran\\V2021_3\\msc20213\\nast\\tpl")
    # os.chdir("c:\\soft\\nastran\\V2022_4\\msc20224\\nast\\tpl")
    if tpl_action == "SEARCH":
        os.chdir("c:\\soft\\nastran\\V2023_1\\msc20231\\nast\\tpl")
        print (" V2023.1 ")
        search_result_list = tpl.search_in_database(and_list, not_list)
        
    

    # (3) TKINTER
    root = Tk()
    root.title('tpl_search')
    root.geometry('1000x1000')
    root.config(bg='#999999')

    my_listbox = Listbox(root, width=50, height=400, bg='#123456', fg='#EEEEEE')
    my_listbox.pack(pady=40, side='left')
    
    # , width=40, height=10, selectmode=SINGLE   text=lb.get(ANCHOR)
    files_as_text = ""
    for item in search_result_list:
        my_listbox.insert(0, item)
        files_as_text = files_as_text + item + "  \n"
    my_text = Text(root, height=80, width=90)
    my_text.configure(bg='#333333', fg='#EEEEEE')
    my_text.pack(side='right')
    text = "for insert into the \n textbox ..."
    my_text.insert(END,files_as_text)

    scroll_y = Scrollbar(root, orient="vertical", command=my_text.yview)
    scroll_y.pack(side="left", expand=True, fill="y")

    my_text.configure(yscrollcommand=scroll_y.set)

    # TKScrollTXT = tkscrolled.ScrolledText(10, width=width, height=height, wrap='word')

    def listbox_item_selected(event):
        line_text = ""
        selection = event.widget.curselection()
        if selection:
            index = selection[0]
            data = event.widget.get(index)
            print (data)
            copy_file(data)
            file_in = open(data,'r')
            line_list = file_in.readlines()
            file_in.close()
            for line in line_list:
                line_text = line_text + line
            my_text.delete(1.0, END)
            my_text.insert(END,line_text)
        else:
            my_text.insert(END," ")
    my_listbox.bind('<<ListboxSelect>>',listbox_item_selected)
    root.mainloop()

# =======================================================================================
   
if __name__ == "__main__":
    main()   
   
# =======================================================================================



