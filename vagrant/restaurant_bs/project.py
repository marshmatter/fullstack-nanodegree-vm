from flask import Flask , render_template, request, redirect, url_for, flash, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem

app = Flask(__name__)

engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

sitename = "Good Eats on the Streets"

@app.route('/')
@app.route('/restaurants/')
def showAllRestaurants():
	restaurantList = session.query(Restaurant).all()
	return render_template('restaurantList.html', sitename=sitename, pagename="Restaurant List", restaurantList=restaurantList)

@app.route('/restaurants/new/', methods=['GET','POST'])
def createNewRestaurant():
	if request.method == 'POST':
		newRestaurant = Restaurant(name = request.form['name'])
		session.add(newRestaurant)
		session.commit()
		flash("Added " + newRestaurant.name) 
		print "Added %s to database" % newRestaurant.name
		return redirect( url_for('showAllRestaurants'))
	else:
		return render_template('newRestaurant.html', sitename=sitename, pagename="Add New Restaurant")

@app.route('/restaurants/<int:restaurant_id>/')
def showRestaurantMenu(restaurant_id):
	activeRestaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
	activeMenuItems = session.query(MenuItem).filter_by(restaurant_id=activeRestaurant.id)
	hasItems = False
	if activeMenuItems.count() > 0:
		hasItems = True

	return render_template('showRestaurantMenu.html', sitename=sitename, pagename=activeRestaurant.name, restaurant=activeRestaurant, menu_items=activeMenuItems, hasItems=hasItems)

@app.route('/restaurants/<int:restaurant_id>/edit/', methods=['GET','POST'])
def editRestaurant(restaurant_id):
	return

@app.route('/restaurants/<int:restaurant_id>/delete/', methods=['GET','POST'])
def deleteRestaurant(restaurant_id):
	activeRestaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
	if request.method == 'POST':
		session.delete(activeRestaurant)
		session.commit()
		flash(activeRestaurant.name + " deleted")
		print("Restaurant Deleted: " + activeRestaurant.name)
		return redirect( url_for('showAllRestaurants'))
	else:
		return render_template('deleteRestaurant.html', sitename=sitename, pagename=activeRestaurant.name, restaurant=activeRestaurant)

@app.route('/restaurants/<int:restaurant_id>/new/', methods=['GET','POST'])
def addMenuItem(restaurant_id):
	activeRestaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
	if request.method == 'POST':
		newItem = MenuItem(name = request.form['name'], restaurant_id = restaurant_id, description=request.form['description'], price=request.form['price'], course=request.form['course'])
		session.add(newItem)
		session.commit()
		flash(request.form['name'] + " added.")
		return redirect( url_for('showRestaurantMenu', restaurant_id = restaurant_id))
	else:
		return render_template('addMenuItem.html', sitename=sitename, pagename=activeRestaurant.name, restaurant=activeRestaurant)

@app.route('/restaurants/<int:restaurant_id>/<int:menu_id>/edit/', methods=['GET','POST'])
def editMenuItem(restaurant_id, menu_id):
	itemToEdit = session.query(MenuItem).filter_by(id=menu_id).one()
	activeRestaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
	if request.method == 'POST':
		itemToEdit.name = request.form['name']
		itemToEdit.price = request.form['price']
		itemToEdit.course = request.form['course']
		itemToEdit.description = request.form['description']
		session.add(itemToEdit)
		session.commit()
		flash(itemToEdit.name + " updated.")
		return redirect( url_for('showRestaurantMenu', restaurant_id = restaurant_id ))
	else:
		return render_template('editMenuItem.html', sitename=sitename, pagename=activeRestaurant.name, restaurant=activeRestaurant, item=itemToEdit)

@app.route('/restaurants/<int:restaurant_id>/<int:menu_id>/delete/', methods=['GET','POST'])
def deleteMenuItem(restaurant_id, menu_id):
	itemToDelete = session.query(MenuItem).filter_by(id=menu_id).one()
	activeRestaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
	if request.method == 'POST':
		session.delete(itemToDelete)
		session.commit()
		flash(itemToDelete.name + " removed.")
		return redirect( url_for('showRestaurantMenu', restaurant_id = restaurant_id ))
	else:
		return render_template('deleteMenuItem.html', sitename=sitename, pagename=activeRestaurant.name, restaurant=activeRestaurant, item=itemToDelete)

# JSON API
@app.route('/restaurants/<int:restaurant_id>/JSON/')
@app.route('/restaurants/<int:restaurant_id>/json/')
def restaurantMenuJSON(restaurant_id):
	restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
	items = session.query(MenuItem).filter_by(restaurant_id=restaurant_id).all()
	return jsonify(MenuItems=[i.serialize for i in items])

@app.route('/restaurants/<int:restaurant_id>/<int:menu_id>/JSON/')
@app.route('/restaurants/<int:restaurant_id>/<int:menu_id>/json/')
def menuItemJSON(restaurant_id,menu_id):
	restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
	item = session.query(MenuItem).filter_by(restaurant_id=restaurant_id).filter_by(id=menu_id).one()
	return jsonify(MenuItem=item.serialize)

@app.route('/restaurants/JSON/')
@app.route('/restaurants/json/')
def restaurantListJSON():
	restaurant_list = session.query(Restaurant)
	return jsonify(Restaurants=[i.serialize for i in restaurant_list])

if __name__ == '__main__':
	app.secret_key = 'super_secret_key222'
	app.debug = True
	app.run(host='0.0.0.0', port=5000)