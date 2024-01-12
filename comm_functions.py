#!/usr/bin/env python
import sys, os, string, sqlite3, getopt
from shutil import copyfile
import tpl_settings



def copy_file(src, dst_folder):
    """
    copy_file

    function to copy a file to certain destination
    
    """
    # dst_folder = "c:\\tmp\\python\\tpl_search\\file_storage"
    src_folder, src_file = os.path.split(src)
    dst = os.path.join(dst_folder, src_file)
    print (dst_folder, src_folder, src_file, dst)
    copyfile(src, dst)


def check_word_criteria(w):
    """
    check_word_criteria

    the keywords are investigated for sense and lentgth and will be filtered
    according certain criterias

    """
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



def read_rc_file(tpl_obj):
    """
    read_rc_file
    
    the rc file contains:
        the location of the tpl search database that was created with the tool 
        and 
        the location of the tpl path that is used to create the tpl database

    example would be:
       c:\\soft\\nastran\\V2023_1\\msc20231\\nast\\tpl
    """
    status = 0
    try:
        print (" read rc file in folder: ", os.getcwd())
        file_in = open("tpl_search.rc","r")
        line_list = file_in.readlines()
        file_in.close()
        if len(line_list) > 0:
            tpl_obj.Settings.Sql_Directory.set_path_name( line_list[0].strip() )
    except:
        print ("WARNING: no rc file ...")  
        status = 1
    
    print (" current setting for sql path location is: ", tpl_obj.Settings.Sql_Directory.get_path_name() )
    return status
        



def convert_input_to_arg_list(input_list, method):
    """
    convert_input_to_arg_list
    
    the argument list is used for definition of settings as create, search, sql directory, 
    also for input_attributes file or for raw user input, the input will be converted into 
    a virtual argument list, that will be processed then with the same argument processing method

    Arguments:
        input_list:   list of several user inputs
        method:       method definition (FILE, ARGS, RAW)
    
    Return:
        prepared list for argument processing
    """
    return_list = []
    print (" convert input to arg list:", input_list, method)

    if method == "FILE":
        input_list = [e.strip() for e in input_list]
        return_list = input_list

    if method == "ARGS":
        return_list = input_list[1:]

    if method == "RAW":
        return_list = input_list

    print (" return list is now: ", return_list)
    return return_list



def process_argument_list(tpl_obj, arg_list, method):
    """
    process_argument_list
    
    use getopt library to process argument list and assign according values to settings object
    and the sub-objects as Sql_Directory, Create and Search
    
    Arguments:
        tpl_obj:    object of tpl_library
        arg_list:   original argument list
    
    Return:
        status:     status value
    """
    status = 0
    print (" process argument list:" , arg_list, method)
    # modification of arg list, depending on method
    arg_list = convert_input_to_arg_list(arg_list, method)
    # processing arg list
    short_options = "p:cs:n:"
    long_options = ["sql_path_loc=", "create", "search=", "not="]
    try:
        options, remainder = getopt.getopt(arg_list, short_options, long_options)
        print ("options and remainder", options, remainder)
        for opt, arg in options:
            if opt in ['-p', '--sql_path_loc']:
                tpl_obj.Settings.Sql_Directory.set_path_name(arg) 
                tpl_obj.Settings.Sql_Directory.set_source(method)
            if opt in ['-f','--create']:
                tpl_obj.Settings.set_tpl_action("CREATE")
                tpl_obj.Settings.Create.set_source(method)
            if opt in ['-s','--search']:
                tpl_obj.Settings.Search.set_and_list(arg.split())
                tpl_obj.Settings.set_tpl_action("SEARCH")
                tpl_obj.Settings.Search.set_source(method)
            if opt in ['-n','--not']:
                tpl_obj.Settings.Search.set_not_list(arg.split())                        
        status = tpl_obj.Settings.approve_settings()      
    except:
        print ("no argument processing ...")
        status = -1
    print ("process arg list status is now: ", status, arg_list)
    return status


def read_input_attributes(tpl_obj, arg_list):
    """
    read_input_attributes

    read main attributes as  CREATE   or   SEARCH
    (optional the SQL PATH)
    and minor attributes as search keywords

    PROCESS STEP 1   attribute file
    PROCESS STEP 2   key words in submit command
    PROCESS STEP 3   input directly by user
    """
    status = 0
    # 1 - FILE
    method = "FILE"
    try:
        file_in = open("input_attributes.txt","r")
        line_list = file_in.readlines()
        file_in.close()
        status = process_argument_list(tpl_obj, line_list, method)
    except:
        status = -1
    # 2 - ARGS
    if status != 0:
        method = "ARGS"
        status = process_argument_list(tpl_obj, arg_list, method)
    # 3 - RAW
    if status != 0:
        method = "RAW"
        try:
            tpl_action = input('tpl_action :')
            options = input('options: ')
            status = process_argument_list(tpl_obj, [tpl_action, options], method)                            
        except:
            status = -1

    # debug settings
    for line in tpl_obj.Settings.get_debug_output():
        print (line)

    return status

