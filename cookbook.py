#!/bin/env python

import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

# --------------------------------------------------------
# Models
# --------------------------------------------------------
Base = declarative_base()

a_table_tags = Table('a_recipe_tags', Base.metadata,
                     Column('recipes_id', Integer, ForeignKey('recipes.id')),
                     Column('tags_id', Integer, ForeignKey('tags.id'))
                     )
a_table_ingredients = Table('a_recipe_ingredients', Base.metadata,
                     Column('recipes_id', Integer, ForeignKey('recipes.id')),
                     Column('ingredients_id', Integer, ForeignKey('ingredients.id'))
                     )


class Recipe(Base):
    __tablename__ = "recipes"
    id = Column(Integer, primary_key=True)
    name = Column(String, default="Neues Rezept", unique=True)
    baking_time = Column(String, default="")
    baking_temp = Column(String, default="")
    description = Column(String, default="")
    picture = Column(LargeBinary)
    category_id = Column(Integer, ForeignKey('categories.id'))
    category = relationship("Category",backref="recipes")
    tags = relationship("Tags", secondary=a_table_tags)
    ingredients = relationship("Ingredients", secondary=a_table_ingredients)


class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)


class Tags(Base):
    __tablename__ = "tags"
    id = Column(Integer, primary_key=True)
    name = Column(String, default="")


class Ingredients(Base):
    __tablename__ = "ingredients"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    amount = Column(String, default="")


class RecipeRow(Gtk.ListBoxRow):
    def __init__(self, recipe):
        super(Gtk.ListBoxRow, self).__init__()
        self.recipe = recipe
        self.add(Gtk.Label(recipe.name))


class Handler:
    def add_recipe(self, button):
        try:
            recipe = Recipe()
            session.add(recipe)
            session.commit()
        except:
            session.rollback()
        self.update()

    def update(self):
        global current_recipe
        liste = builder.get_object("ls_recipes")
        recipes = session.query(Recipe).all()
        for name in liste:
            found = False
            for r in recipes:
                if r.name == name[0]:
                    found == True
            if not found:
                liste.remove(name.iter)
        for r in recipes:
            found = False
            for name in liste:
                if name[0] == r.name:
                    found=True
            if not found:
                liste.append([r.name])
        for row in liste:
            if row[0] == current_recipe.name:
                print(row[0])
                selection = builder.get_object("lsel_recipes")
                selection.select_iter(row.iter)

        ls_cat = builder.get_object("ls_cat")
        cats = session.query(Category).all()
        ls_cat.clear()
        for c in cats:
            ls_cat.append([c.name])

    def load_recipe(self,tv,tp,ti):
        print("load")
        selection = tv.get_selection()
        model, item = selection.get_selected()
        if not item:
            return
        recipe_name = model.get_value(item, 0)
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
            tags.set_text(",".join(map(lambda t: t.name, current_recipe.tags)))
        else:
            tags.set_text("")

        desc = builder.get_object("txt_description")
        desc.get_buffer().set_text(current_recipe.description)

    def save_recipe(self, button):
        global current_recipe
        name = builder.get_object("txt_name")
        time = builder.get_object("txt_time")
        temp = builder.get_object("txt_temp")
        desc = builder.get_object("txt_description")
        dbuf = desc.get_buffer()
        current_recipe.description = dbuf.get_text(dbuf.get_start_iter(), dbuf.get_end_iter(), False)

        tags = builder.get_object("txt_tags")
        tags = tags.get_text()
        tags = tags.split(",")
        del current_recipe.tags[:]
        for tag in tags:
            db_tag = session.query(Tags).filter(Tags.name == tag).first()
            if db_tag:
                current_recipe.tags.append(db_tag)
            else:
                new_tag = Tags(name=tag)
                session.add(new_tag)
                current_recipe.tags.append(new_tag)

        cat = builder.get_object("txt_cat")
        cat_txt = cat.get_text()
        if cat_txt:
            db_cat = session.query(Category).filter(Category.name == cat_txt).first()
            if db_cat:
                current_recipe.category = db_cat
            else:
                new_cat = Category(name=cat_txt)
                session.add(new_cat)
                current_recipe.category = new_cat

        
        ingredients = builder.get_object("ls_ingredients")

        current_recipe.name = name.get_text()
        current_recipe.baking_temp = temp.get_text()
        current_recipe.baking_time = time.get_text()
        session.commit()
        self.update()

    def show_main(self, widget):
        cbt_cat = builder.get_object("cbt_cat")
        ls_cat = builder.get_object("ls_cat")
        cbt_cat.set_model(ls_cat)

        self.update()

    def delete_recipe(self, button):
        session.delete(current_recipe)
        session.commit()
        self.update()

    def add_ingredient(self,button):
        ingredients = builder.get_object("ls_ingredients")
        ingredients.append(["-","-"])
            
    def remove_ingredient(self,button):
        lv = builder.get_object("lv_ingredients")
        selection = lv.get_selection()
        if not selection:
            return
        model,path = selection.get_selected_rows()
        if not path:
            return
        for p in path:
            it = model.get_iter(path)
            model.remove(it)

    def edited_amount(*params):
        print(params)

    def pdf(self,button):
        with open("Template/Kochbuch.tex") as f:
            text = f.read()

        cats = session.query(Category).all()
        chapters = ""
        for cat in cats:
            chapter = """
            \section{{{name}}}
            """.format(name = cat.name)
            for recipe in cat.recipes:
                chapter += "\input{{{name}.tex}}\n".format(name = recipe.name)
            chapters += chapter

        text = text.replace("+Chapters",chapters)
        with open("build/Kochbuch.tex","w") as f:
            f.write(text)

        with open("Template/Rezept.tex") as f:
            text = f.read()
            
        for cat in cats:
            for recipe in cat.recipes:

                r_text = text.replace("+Name",recipe.name)
                r_text = r_text.replace("+Backzeit",recipe.baking_time)
                r_text = r_text.replace("+Temperatur",recipe.baking_temp)
                steps = ""
                for step in recipe.description.split("\n"):
                    steps += "\step "+step
                r_text = r_text.replace("+Beschreibung",steps)
                tags = ",".join(map(lambda x: x.name,recipe.tags))
                with open("build/{0}.tex".format(recipe.name),"w") as f:
                    f.write(r_text)



        
        


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
