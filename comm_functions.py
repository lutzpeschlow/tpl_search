#!/usr/bin/env python
import sys, os, string, sqlite3, getopt
from pathlib import Path
import shutil
import tpl_settings

def get_help():
    """
    get help for tpl search tool
    """
    print ("\nHelp for tpl search")
    print ("=====================")
    print ("tool for searching tpl library database file")
    print ("use create or search")
    print ("tpl_search.rc file should be defined for tpl database location\n")



def copy_file(src, dst_folder):
    """
    copy_file

    function to copy a file to certain destination
    """
    src_folder, src_file = os.path.split(src)
    path_obj = Path(dst_folder)
    path_obj.mkdir(exist_ok=True)
    dst = os.path.join(dst_folder, src_file)
    # shutil.copyfile(src, dst)
    shutil.copy2(src, dst)




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
    print ("... reading rc file in folder: ",os.getcwd())
    try:
        file_in = open("tpl_search.rc","r")
        line_list = file_in.readlines()
        file_in.close()
        if len(line_list) > 0:
            tpl_obj.Settings.Sql_Directory.set_path_name( line_list[0].strip() )
        print (" current setting for sql path location is: ", tpl_obj.Settings.Sql_Directory.get_path_name() )
    except:  
        status = -1
    # return value
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
    if method == "FILE":
        input_list = [e.strip() for e in input_list]
        return_list = input_list
    if method == "ARGS":
        return_list = input_list[1:]
    if method == "RAW":
        return_list = input_list    
    return return_list



def process_argument_list(tpl_obj, arg_list, method):
    """
    process_argument_list
    
    use getopt library to process argument list and assign according values to settings object

    method can be FILE,ARGS,RAW
    
    Arguments:
        tpl_obj:    object of tpl_library
        arg_list:   original argument list
    
    Return:
        status:     status value
    """
    status = 0
    # modification of arg list, depending on method
    arg_list = convert_input_to_arg_list(arg_list, method)
    print ("method/arg list: ", method, arg_list)
    # processing arg list
    short_options = "cs:n:"
    long_options = ["create", "search=", "not="]
    try:
        options, remainder = getopt.getopt(arg_list, short_options, long_options)
        for opt, arg in options:
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
    # debug output
    # output_list = tpl_obj.Settings.get_debug_output()
    # for line in output_list:
    #     print (line)
    # return status
    return status





def read_input_attributes(tpl_obj, arg_list):
    """
    read_input_attributes

    read main attributes as  CREATE   or   SEARCH
    and minor attributes as search keywords

    PROCESS STEP 1   attribute file                 input_attributes.txt
    PROCESS STEP 2   key words in submit command    --create or --search
    PROCESS STEP 3   input directly by user         same commands as in submission

    different options are provided to transfer arguments to the tool,
    via attribute file, keywords during submission, raw user input

    these three options are processed one after the other
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
        print ("method/arg list: ", method)
        status = -1
    # 2 - ARGS
    
    if status != 0:
        method = "ARGS"
        status = process_argument_list(tpl_obj, arg_list, method)
    # 3 - RAW
    if status != 0:
        method = "RAW"
        try:
            print("no attribute file and command line arguments, user raw input is required")
            tpl_action = input('tpl_action  (use --create or --search)    :  ')
            options    = input('options     (what keywords are searched)  :  ')
            status = process_argument_list(tpl_obj, [tpl_action, options], method)                            
        except:
            status = -1
    # debug settings
    # for line in tpl_obj.Settings.get_debug_output():
    #     print (line)
    # return status value
    return status

