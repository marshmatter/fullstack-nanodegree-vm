# import http classes
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import cgi

# for parsing
from urlparse import urlparse

# import database orm
from sqlalchemy import create_engine
from sqlalchemy import func
from sqlalchemy.orm import sessionmaker

#import restaurant classes (don't necessarily need MenuItem yet)
from database_setup import Base, Restaurant, MenuItem

engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

class webserverHandler(BaseHTTPRequestHandler):

	def do_GET(self):
		try:
			parsed = urlparse(self.path)

			if parsed.path =="/index":
				set_headers(self)
				output = ""
				output += "<html><body>"
				output += print_index()
				output += "</body></html>"
				self.wfile.write(output)
				print output
				return
			if parsed.path == "/restaurants":
				print_restaurant_list(self)
				return
			if parsed.path =="/restaurants/new":
				print_new_restaurant_form(self)
				return
			if parsed.path == "/restaurants/edit":
				print_rename_restaurant_form(self,parsed.params)
			if parsed.path == "/restaurants/delete":
				print_delete_confirmation(self,parsed.params)

		except IOError:
			self.send_error(404, "File Not Found %s" % self.path)


	def do_POST(self):
		try:
			parsed = urlparse(self.path)
			if parsed.path == "/restaurants/new":
				add_new_restaurant(self)
				return
			if parsed.path == "/restaurants/edit":
				rest = session.query(Restaurant).filter(Restaurant.id == parsed.params).one()
				edit_restaurant(self, rest)
			if parsed.path == "/restaurants/delete":
				rest = session.query(Restaurant).filter(Restaurant.id == parsed.params).one()
				delete_restaurant(self, rest)

		except:
			pass

# helper methods
def set_headers(self):
	self.send_response(200)
	self.send_header('Content-type', 'text/html')
	self.end_headers()

def print_index():
	output = ""
	output += "<ul>"
	output += "<li><h2><a href='/restaurants/new'>Add New Restaurant</a></h2></li>"
	output += "<li><a href='/restaurants'>Restaurant List</a></li>"
	output += "</ul>"
	return output

def return_to_index_link():
	output = ""
	output += "<a href='/index'>Return to Index</a>"
	return output

def edit_restaurant_link(restaurant):
	output = ""
	output = "<a href='/restaurants/edit;%s'>Edit</a>" % restaurant.id
	return output

def delete_restaurant_link(restaurant):
	output = ""
	output = "<a href='/restaurants/delete;%s'>Delete</a>" % restaurant.id
	return output

def add_new_restaurant_button():
	output = ""
	output += "<a href='/restaurants/new'>Add New Restaurant</a>"
	return output

def print_restaurant_list(self, do_headers=True):
	query = session.query(Restaurant)
	if do_headers == True:
		set_headers(self)
	output = ""
	output += "<html><body>"
	output += "%s <br> " % add_new_restaurant_button()
	output += "<ul>"
	for item in query:
		output += "<li><h2>%s</h2>" % item.name
		output += "{0} | {1} ".format(edit_restaurant_link(item), delete_restaurant_link(item))
		output += "</li>"
		output += "</li>"
	output += "</ul>"
	output += return_to_index_link()
	output += "</body></html>"
	self.wfile.write(output)
	print output

def print_new_restaurant_form(self, do_headers=True, failed_attempt=False):
	if (do_headers):
		set_headers(self)
	output = ""
	output += "<html><body>"
	output += "<h1>Make a New Restaurant</h1>"
	output += '''<form method='POST' enctype='multipart/form-data' action='/restaurants/new'><input name="restaurant_new_name" type="text" ><input type="submit" value="Create"> </form>''' 
	if (failed_attempt):
		output += "<h2>Error: Name Cannot Be Blank</h2>"
	output += return_to_index_link()
	output += "</body></html>"
	self.wfile.write(output)
	print output

def print_rename_restaurant_form(self, active_restaurant_id, do_headers=True, failed_attempt=False):
	active_restaurant = session.query(Restaurant).filter(Restaurant.id == active_restaurant_id).one()
	print active_restaurant.name
	if (do_headers):
		set_headers(self)
	output = ""
	output += "<html><body>"
	output += "<h1>Rename Restaurant: %s </h1>" % active_restaurant.name
	output += '''<form method='POST' enctype='multipart/form-data' action='/restaurants/edit;{1}'><input name="restaurant_updated_name" type="text" value ="{0}"><input type="submit" value="Rename"> </form>'''.format(active_restaurant.name, active_restaurant.id)
	if (failed_attempt):
		output += "<h2>Error: Name Cannot Be Blank</h2>"
	output += return_to_index_link()
	output += "</body></html>"
	self.wfile.write(output)
	print output

def print_delete_confirmation(self, active_restaurant_id, do_headers=True, failed_attempt=False):
	active_restaurant = session.query(Restaurant).filter(Restaurant.id == active_restaurant_id).one()
	print active_restaurant.name
	if (do_headers):
		set_headers(self)
	output = ""
	output += "<html><body>"
	output += "<h1>Are You Sure You Want to Delete %s </h1>" % active_restaurant.name
	output += '''<form method='POST' enctype='multipart/form-data' action='/restaurants/delete;{1}'><input type="submit" value="Delete {0}"> </form>'''.format(active_restaurant.name, active_restaurant.id)
	if (failed_attempt):
		output += "<h3>Error! Cannot delete </h3>"
	output += return_to_index_link()
	output += "</body></html>"
	self.wfile.write(output)
	print output

def add_new_restaurant(self):
	ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
	if ctype == 'multipart/form-data':
		fields = cgi.parse_multipart(self.rfile, pdict)
		formcontent = fields.get('restaurant_new_name')

	# we should do a check to make sure it's not blank
	if (formcontent[0] == ""):
		print "Restaurant Name was left blank"
		print_new_restaurant_form(self, False, True)
		return

	# name was not blank, continue
	new_restaurant = Restaurant(name=formcontent[0])
	session.add(new_restaurant)
	session.commit()

	self.send_response(301)
	self.send_header('Location','/restaurants')
	self.end_headers()

def edit_restaurant(self, active_restaurant):
	ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
	if ctype == 'multipart/form-data':
		fields = cgi.parse_multipart(self.rfile, pdict)
		formcontent = fields.get('restaurant_updated_name')

	# we should do a check to make sure it's not blank
	if (formcontent[0] == ""):
		print "Restaurant Name was left blank"
		print_rename_restaurant_form(self, active_restaurant.id, True, True)
		return

	# name was not blank, continue
	active_restaurant.name = formcontent[0]
	session.add(active_restaurant)
	session.commit()

	self.send_response(301)
	self.send_header('Location','/restaurants')
	self.end_headers()

def delete_restaurant(self, active_restaurant):
	# name was not blank, continue
	session.delete(active_restaurant)
	session.commit()

	self.send_response(301)
	self.send_header('Location','/restaurants')
	self.end_headers()

def main():
	try:
		port = 8080
		server = HTTPServer(('',port), webserverHandler)
		print "Web server running on port %s" % port
		server.serve_forever()

	except KeyboardInterrupt:
		print "^C entered, stopping web server..."
		server.socket.clost()

if __name__ == '__main__':
	main()