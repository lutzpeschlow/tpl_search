# tpl_search
tool for searching Nastran Test Problem Library by using sqlite database


two main options:
    create - creates a key word database
    search - search in the key word database
    

CREATE
    
    if create is selected, a tpl_database.db file as sqlite database is 
    created and stored in the tpl folder itself, for example:
        c:\soft\nastran\V2022_4\msc20224\nast\tpl\tpl_database.db
    this database is then also used, if a search command is called
    
SEACH

    if search is selected there is a bundle of anding and not words:
    --search
    MDBULK MDMPLN
    --not
    not_word
    
    the three lines of an input_attributes.txt will contain:
    <search command>
    anding word list
    <not command>
    not word list
    
    the tpl_database.db is searched according required words

    the process order of searching the database would be:
    - read input_attributes.txt
    - read arguments in submit command
    - requires user to input during runtime

    if using commandline an example would be:
        C:/soft/python/V3_7_3/python.exe tpl_search.py --search "SOL 400 CQUAD4"
        or
        C:/soft/python/V3_7_3/python.exe tpl_search.py --search "SOL 400 CQUAD4" --not NLTANS

    if using raw user input an example would be:
        --search
        SOL 400 CQUAD4


