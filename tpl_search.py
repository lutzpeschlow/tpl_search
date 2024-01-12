#!/usr/bin/env python
import sys, os, string, sqlite3, getopt
from tkinter import *
from shutil import copyfile
import tpl_lib_content
import tpl_settings
import comm_functions

# ------------------------ main ---------------------------------------------------------

def main():
    """
    main()

    the main function covers two main options:
    create - creates a key word database
    search - search in the key word database
    

    CREATE
    
    if create is selected, a tpl_database.db file as sqlite database is 
    created and stored in the tpl folder itself, for example:
        c:\soft\nastran\V2022_4\msc20224\nast\tpl\tpl_database.db
    this database is then also used, if a search command is called
    
    if search is selected there is a bundle of anding and not words:
    SEARCH
    MDBULK MDMPLN
    not_word
    
    the three lines of an input_attributes.txt will contain:
    search command
    anding word list
    not word list
    
    the tpl_database.db is searched according required words

    the process order of searching the database would be:
    - read input_attributes.txt
    - read arguments in submit command
    - requires user to input during runtime

    """
    search_result_list = []

    # os.chdir("c:\\tmp\\python\\tpl_search")
    print (os.getcwd(), sys.argv) 

    # instance of library content object
    tpl = tpl_lib_content.Lib_Content()

    # read rc file and get sql path location, if there is no rc file the next option 
    # to set the sql path would be in input attributes
    comm_functions.read_rc_file(tpl)

    # read input attributes create / search / set_sql_path
    comm_functions.read_input_attributes(tpl, sys.argv)
    
    # (1) CREATE
    if tpl.Settings.get_tpl_action() == "CREATE":
        # os.chdir("c:\\tmp\\python\\tpl_search\\example_folders")
        # os.chdir("c:\\soft\\nastran\\V2021_1\\msc20211\\nast\\doc\\tpl")
        # os.chdir("c:\\soft\\nastran\\V2021_3\\msc20213\\nast\\tpl")
        # os.chdir("c:\\soft\\nastran\\V2022_4\\msc20224\\nast\\tpl")
        # C:\soft\nastran\V2023_1\msc20231\nast\tpl
        # os.chdir("c:\\soft\\nastran\\V2023_1\\msc20231\\nast\\tpl")
        os.chdir(tpl.Settings.Sql_Directory.get_path_name())
        
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
    
    if tpl.Settings.get_tpl_action()  == "SEARCH":
        os.chdir(tpl.Settings.Sql_Directory.get_path_name())
        status, search_result_list = tpl.search_in_database(tpl.Settings.Search.get_and_list(),tpl.Settings.Search.get_not_list())

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
                dst_folder = "c:\\tmp\\python\\tpl_search\\file_storage"
                print (data)
                comm_functions.copy_file(data, dst_folder)
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



