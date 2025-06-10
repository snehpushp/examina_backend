# Importing all the models from the respective files
from app.core.db.session import engine

# DO NOT CHANGE THE ORDER OF IMPORT UNLESS NECESSARY
from .base import Base
from .exams import *
from .questions import *

# Creating tables in database
Base.metadata.create_all(bind=engine)
