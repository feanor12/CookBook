#!/bin/env python

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class Recipe(Base):
    __tablename__ = "recipes"
    id = Column(Integer,primary_key=True)
    name = Column(String,default="Neues Rezept")
    baking_time = Column(String,default="3")
    baking_temp = Column(String,default="3")
    picture = Column(LargeBinary)

class RecipeRow(Gtk.ListBoxRow):
    def __init__(self,recipe):
        super(Gtk.ListBoxRow, self).__init__()
        self.recipe = recipe
        self.add(Gtk.Label(recipe.name))

class Handler:
    def add_recipe(self,button):
        recipe = Recipe()
        session.add(recipe)
        session.commit()
        self.update()

    def update(self):
        liste = builder.get_object("rezeptliste")
        list(map(liste.remove,liste.get_children()))
        recipes = session.query(Recipe).all()
        for r in recipes:
            liste.add(RecipeRow(r))
        liste.show_all()



    def load_recipe(self,box,row):
        global current_recipe
        current_recipe = row.recipe
        name = builder.get_object("txt_name")
        name.set_text(current_recipe.name)
        time = builder.get_object("txt_time")
        time.set_text(current_recipe.baking_time)
        temp = builder.get_object("txt_temp")
        temp.set_text(current_recipe.baking_temp)


    def save_recipe(self,button):
        name = builder.get_object("txt_name")
        time = builder.get_object("txt_time")
        temp = builder.get_object("txt_temp")
        current_recipe.name = name.get_text()
        current_recipe.baking_temp = temp.get_text()
        current_recipe.baking_time = time.get_text()
        session.commit()
        self.update()

    def show_main(self,widget):
        self.update()

    def delete_recipe(self,button):
        session.delete(current_recipe)
        session.commit()
        self.update()


current_recipe = None
engine = create_engine('sqlite:///CookBook.db')
Base.metadata.create_all(engine)
DBSession = sessionmaker(bind=engine)
session = DBSession()

builder = Gtk.Builder()
builder.add_from_file("cookbook.glade")
builder.connect_signals(Handler())
win = builder.get_object("main")
win.connect("delete-event", Gtk.main_quit)
win.show_all()
Gtk.main()
session.close()