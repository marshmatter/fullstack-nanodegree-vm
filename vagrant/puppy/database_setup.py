import sys 
from sqlalchemy import Column, ForeignKey, Integer, String, Date, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
import enum

Base = declarative_base()

class Gender(enum.Enum)
	male = "male"
	female = "female"
	unknown = "unknown"

class Province(enum.Enum)
	on = "Ontario"
	bc = "British Columbia"
	ns = "Nova Scotia"
	nl = "Newfoundland & Labrador"
	nu = "Nunavut"
	nt = "Northwest Territories"
	yk = "Yukon"
	qb = "Quebec"
	mn = "Manitoba"
	pe = "Prince Edward Island"
	nb = "New Brunswick"
	ab = "Alberta"
	sk = "Saskatchewan"


class Shelter(Base):
	__tablename__ = 'shelter'
	name = Column(String(250), nullable = False)
	address = Column(String(250))
	city = Column(String(250))
	province = Column(Enum(Province))
	postalCode = Column(String(7))
	id = Column(Integer, primary_key = True)

class Puppy(Base):
	__tablename__ = 'puppy'
	name = Column(String(80), nullable = False)
	date_of_birth = Column(Date())
	gender = Column(Enum(Gender))
	weight = Column(Float())
	shelter_id = Column( Integer, ForeignKey('shelter.id'))
	shelter = relationship(Shelter)

### insert at end ###
engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.creae_all(engine)