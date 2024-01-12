#!/usr/bin/env python
import sys, os, string, sqlite3, getopt

class Search():

    def __init__(self):
        self.and_list = []
        self.not_list = []
        self.source = ""

    def set_and_list(self, and_list):  self.and_list = and_list
    def set_not_list(self, not_list):  self.not_list = not_list
    def set_source(self, source):      self.source = source

    def get_and_list(self):            return self.and_list
    def get_not_list(self):            return self.not_list
    def get_source(self):              return self.source

    def get_debug_output(self):
        return_list = []
        return_list.append(" debug output for: Search")
        return_list.append("  " + str(self.get_and_list()))
        return_list.append("  " + str(self.get_not_list()))
        return_list.append("  " + str(self.get_source()))
        return return_list


class Create():
    def __init__(self):
        self.source = ""

    def set_source(self, source):    self.source = source
    def get_source(self):            return self.source

    def get_debug_output(self):
        return_list = []
        return_list.append(" debug output for: Create")
        return_list.append("  " + str(self.get_source()))
        return return_list


class Sql_Directory():
    def __init__(self):
        self.path_name = "."
        self.source = ""

    def set_path_name(self, path_name):   self.path_name = path_name
    def set_source(self, source):    self.source = source

    def get_path_name(self):         return self.path_name
    def get_source(self):            return self.source

    def get_debug_output(self):
        return_list = []
        return_list.append(" debug output for: Sql_Directory")
        return_list.append("  " + str(self.get_path_name()))
        return_list.append("  " + str(self.get_source()))
        return return_list



class Settings():
    def __init__(self):
        self.Search = Search()
        self.Create = Create()
        self.Sql_Directory = Sql_Directory()
        self.tpl_action = ""

    def set_tpl_action(self, tpl_action):    self.tpl_action = tpl_action
    def get_tpl_action(self):                return self.tpl_action

    def approve_settings(self):
        return_value = 0
        if self.tpl_action == "":
            return_value = -1
        return return_value


    def get_debug_output(self):
        return_list = []
        return_list.append("debug output for Settings:")
        return_list.extend(self.Search.get_debug_output())
        return_list.extend(self.Create.get_debug_output())
        return_list.extend(self.Sql_Directory.get_debug_output())
        return_list.append(" tpl_action: " + str(self.get_tpl_action()))
        return_list.append("---")
        return return_list
        
