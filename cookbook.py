#!/bin/env python

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker,relationship

#--------------------------------------------------------
# Models
#--------------------------------------------------------
Base = declarative_base()

a_table_tags = Table('a_recipe_tags', Base.metadata,
    Column('recipes_id', Integer, ForeignKey('recipes.id')),
    Column('tags_id', Integer, ForeignKey('tags.id'))
)

class Recipe(Base):
    __tablename__ = "recipes"
    id = Column(Integer,primary_key=True)
    name = Column(String,default="Neues Rezept",unique=True)
    baking_time = Column(String,default="")
    baking_temp = Column(String,default="")
    description = Column(String,default="")
    picture = Column(LargeBinary)
    category_id = Column(Integer, ForeignKey('categories.id'))
    category = relationship("Category")
    tags = relationship("Tags",secondary=a_table_tags)


class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer,primary_key=True)
    name = Column(String,unique=True)

class Tags(Base):
    __tablename__ = "tags"
    id = Column(Integer,primary_key=True)
    name = Column(String,default="")

class Ingredients(Base):
    __tablename__ = "ingredients"
    id = Column(Integer,primary_key=True)
    name = Column(String)
    amount = Column(String, default="")

class RecipeRow(Gtk.ListBoxRow):
    def __init__(self,recipe):
        super(Gtk.ListBoxRow, self).__init__()
        self.recipe = recipe
        self.add(Gtk.Label(recipe.name))

class Handler:
    def add_recipe(self,button):
        try:
            recipe = Recipe()
            session.add(recipe)
            session.commit()
        except:
            session.rollback()
        self.update()

    def update(self):
        liste = builder.get_object("ls_recipes")
        liste.clear()
        recipes = session.query(Recipe).all()
        for r in recipes:
            liste.append([r.name])

        ls_cat = builder.get_object("ls_cat")
        cats = session.query(Category).all()
        ls_cat.clear()
        for c in cats:
            ls_cat.append([c.name])



    def load_recipe(self,selection):
        model,item = selection.get_selected()
        if not item:
            return
        recipe_name = model.get_value(item,0)
        if not recipe_name:
            return
        global current_recipe
        current_recipe = session.query(Recipe).filter(Recipe.name == recipe_name).one()
        name = builder.get_object("txt_name")
        name.set_text(current_recipe.name)
        time = builder.get_object("txt_time")
        time.set_text(current_recipe.baking_time)
        temp = builder.get_object("txt_temp")
        temp.set_text(current_recipe.baking_temp)
        cat = builder.get_object("txt_cat")
        if current_recipe.category:
            cat.set_text(current_recipe.category.name)
        else:
            cat.set_text("")

        tags = builder.get_object("txt_tags")
        if current_recipe.tags:
            tags.set_text(",".join(map(lambda t:t.name,current_recipe.tags)))
        else:
            tags.set_text("")

        desc = builder.get_object("txt_description")
        desc.get_buffer().set_text(current_recipe.description)

    def save_recipe(self,button):
        name = builder.get_object("txt_name")
        time = builder.get_object("txt_time")
        temp = builder.get_object("txt_temp")
        desc = builder.get_object("txt_description")
        dbuf = desc.get_buffer()
        current_recipe.description = dbuf.get_text(dbuf.get_start_iter(),dbuf.get_end_iter(),False)

        tags = builder.get_object("txt_tags")
        tags = tags.get_text()
        tags = tags.split(",")
        current_recipe.tags.clear()
        for tag in tags:
            db_tag = session.query(Tags).filter(Tags.name==tag).first()
            if db_tag:
                current_recipe.tags.append(db_tag)
            else:
                new_tag = Tags(name=tag)
                session.add(new_tag)
                current_recipe.tags.append(new_tag)

        cat = builder.get_object("txt_cat")
        cat_txt = cat.get_text()
        if cat_txt:
            db_cat = session.query(Category).filter(Category.name==cat_txt).first()
            if db_cat:
                current_recipe.category = db_cat
            else:
                new_cat = Category(name = cat_txt)
                session.add(new_cat)
                current_recipe.category = new_cat

        current_recipe.name = name.get_text()
        current_recipe.baking_temp = temp.get_text()
        current_recipe.baking_time = time.get_text()
        session.commit()
        self.update()

    def show_main(self,widget):
        cbt_cat = builder.get_object("cbt_cat")
        ls_cat = builder.get_object("ls_cat")
        cbt_cat.set_model(ls_cat)

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