#!/bin/env python

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

class Recipe:
    def __init__(self):
        self.name = "Neues Rezept"


class RecipeRow(Gtk.ListBoxRow):
    def __init__(self,index):
        super(Gtk.ListBoxRow, self).__init__()
        self.index = index
        r = rezepte[index]
        self.add(Gtk.Label(r.name))

class Handler:
    def add_recipe(self,button):
        recipe = Recipe()
        rezepte.append(recipe)
        self.update()

    def update(self):
        liste = builder.get_object("rezeptliste")
        list(map(liste.remove,liste.get_children()))
        for i,r in enumerate(rezepte):
            liste.add(RecipeRow(i))
        liste.show_all()

    def load_recipe(self,box,row):
        r = rezepte[row.index]
        name = builder.get_object("txt_name")
        name.set_text(r.name)

    def save_recipe(self,button):
        liste = builder.get_object("rezeptliste")
        name = builder.get_object("txt_name")
        row = liste.get_selected_rows()
        index = row[0].index
        rezepte[index].name=name.get_text()
        self.update()




        

rezepte = []



builder = Gtk.Builder()
builder.add_from_file("cookbook.glade")
builder.connect_signals(Handler())
win = builder.get_object("main")
win.connect("delete-event", Gtk.main_quit)
win.show_all()
Gtk.main()
