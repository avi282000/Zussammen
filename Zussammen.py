import kivy
import os
import sys
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout #A Layout Structure
from kivy.uix.textinput import TextInput #Allows Text Input
from kivy.uix.button import Button #Allows for the usage of Buttons
from kivy.uix.screenmanager import ScreenManager, Screen #Allows for changes in Pages/Screens
from kivy.core.window import Window #For altering the GUI window's parameters
from kivy.uix.scrollview import ScrollView #For the Scroll Bar
import dungeon_client
from kivy.clock import Clock #For Scheduling tasks

#The Initial Page (Connect Page)
class ConnectPage(GridLayout):
	def __init__(self,**kwargs):
		super().__init__(**kwargs) #Runs the __init__ for both, "ConnectGrid" and "GridLayout"
		self.cols = 2

		if os.path.isfile("prev_details.txt"):
			with open("prev_details.txt","r") as f:
				d = f.read().split(",")
				
				prev_ip = d[0]
				prev_port = d[1]
				prev_username = d[2]

		else:
			prev_ip = ""
			prev_port = ""
			prev_username = ""

		#Widgets to be added according to the order

		#Widget 1
		self.add_widget(Label(text="IP:"))
		self.ip = TextInput(text=prev_ip, multiline=False)
		self.add_widget(self.ip)

		#Widget 2
		self.add_widget(Label(text="Port:"))
		self.port = TextInput(text=prev_port, multiline=False)
		self.add_widget(self.port)

		#Widget 3
		self.add_widget(Label(text="UserName:"))
		self.username = TextInput(text=prev_username, multiline=False)
		self.add_widget(self.username)

		#For the Button
		self.join = Button(text="Join")
		self.join.bind(on_press=self.join_button)
		self.add_widget(Label()) #Just takes the spot. The Label is described in the Button() itself
		self.add_widget(self.join)

	def join_button(self, instance):
		port = self.port.text
		ip = self.ip.text
		username = self.username.text

		with open("prev_details.txt","w") as f:
			f.write(f"{ip},{port},{username}")
		#print (f"Joining {ip}:{port} as {username}.....")
		info = f"Joining {ip}:{port} as {username}....."
		chat_app.info_page.update_info(info)
		chat_app.screen_manager.current = "Info"
		Clock.schedule_once(self.connect, 3)

	def connect(self,_):
		#Get Information from the client
		port = int(self.port.text)
		ip = self.ip.text
		username = self.username.text

		if not dungeon_client.connect(ip,port,username,show_error):
			return

		#Creating the chat page
		chat_app.create_chat_page()
		chat_app.screen_manager.current = "Chat"



#The Info Page
class InfoPage(GridLayout):
	def __init__(self,**kwargs):
		super().__init__(**kwargs)

		#Just 1 Column
		self.cols = 1

		self.message = Label(halign="center", valign="middle", font_size=32)
		self.message.bind(width=self.update_text_width)
		self.add_widget(self.message)

		'''self.back = Button(text="Back")
								self.back.bind(on_press=self.back_button)
								self.add_widget(Label())
								self.add_widget(self.back)
						
							def back_button(self,instance):
								chat_app.screen_manager.current = "Connect"'''



	def update_info(self, message):
		self.message.text = message

	def update_text_width(self, *_):
		self.message.text_size = (self.message.width*0.9, None)


#Building the App
class ChatApp(App):
	def build(self):
		self.screen_manager = ScreenManager() #Defining a Screen Manager, which will allow switching between multiple screens

		#Screen 1
		self.connect_page = ConnectPage() #Creating Page
		screen = Screen(name="Connect") #Creating Screen
		screen.add_widget(self.connect_page) #Adding Page to the Screen
		self.screen_manager.add_widget(screen)	#Adding Screen to the Screen Manager

		#Screen 2
		self.info_page = InfoPage()
		screen = Screen(name="Info")
		screen.add_widget(self.info_page)
		self.screen_manager.add_widget(screen)

		return self.screen_manager

	def create_chat_page(self):
		self.chat_page = ChatPage()
		screen = Screen(name="Chat")
		screen.add_widget(self.chat_page)
		self.screen_manager.add_widget(screen)

def show_error(message):
	chat_app.info_page.update_info(message)
	chat_app.screen_manager.current = "Info"
	Clock.schedule_once(sys.exit, 5)

#The Chat Page (An App in itself)
class ChatPage(GridLayout):

	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.cols = 1 #Defining the Columns and Rows for the Grid. The basic chatroom design is what I'm going with here
		self.rows = 2

		#For Row 1
		self.history = ScrollableLabel(height = Window.size[1]*0.9, size_hint_y = None) #Creating a Widget for all the message history. It'll take up 90% of the screen's size
		self.add_widget(self.history)
		

		#For Row 2
		self.new_message = TextInput(width = Window.size[0]*0.8, size_hint_x = None, multiline = False) #Creating a Widget for typing in a new message. Will take up 80% of the width of the row. Clearly, Multilining won't be allowed
		self.send = Button(text = "Send") #Creating the "Send" Button
		self.send.bind(on_press = self.send_message)
		

		#Crating a 2 column layout for inputting the message
		bottom_line = GridLayout(cols = 2) 
		bottom_line.add_widget(self.new_message) #Adding the input text field 
		bottom_line.add_widget(self.send) #Adding the "Send" Button
		self.add_widget(bottom_line) #Adding the columns

		Window.bind(on_key_down=self.on_key_down)


		Clock.schedule_once(self.focus_text_input, 1)

		dungeon_client.start_listening(self.incoming_message, show_error)

		self.bind(size = self.adjust_fields)

	def adjust_fields(self, *_):
		if Window.size[1]*0.1 < 50:
			new_height = Window.size[1] - 50

		else:
			new_height = Window.size[1]*0.9

		self.history.height = new_height

		if Window.size[1]*0.2 < 160:
			new_width = Window.size[1] - 160

		else:
			new_width = Window.size[1]*0.8

		self.new_message.width = new_width

		Clock.schedule_once(self.history.update_chat_history_layout, 0.01)





	#For sending the message by the press of the "Enter" the key
	def on_key_down(self, instance, keyboard, keycode, text, modifiers):
		if keycode == 40:
			self.send_message(None)

	#Re-focusing
	def focus_text_input(self, _):
		self.new_message.focus = True

	def incoming_message(self, username, message):
		if message == "/%&? has entered the dungeon./%&?":
			message=message.strip("/%&?")
			self.history.update_chat_history(f"[color=c0d104] {username} {message} [/color]")
		elif message =="/%&? has left the dungeon./%&?":
			message=message.strip("/%&?")
			self.history.update_chat_history(f"[color=730000] {username} {message} [/color]")	
		else:
			self.history.update_chat_history(f"[color=007194] {username} [/color] > {message}") #Chose Dark Cyan (#007194) for the color of the username

	def send_message(self, _):
		message = self.new_message.text #Getting the message text 
		self.new_message.text = "" #Clearing the Text Field

		if message:			
			self.history.update_chat_history(f"[color=007011] {chat_app.connect_page.username.text} [/color] > {message}")
			dungeon_client.send(message)

		#Re-focusing to the input field
		Clock.schedule_once(self.focus_text_input, 0.1)




class ScrollableLabel(ScrollView):
	def __init__(self, **kwargs):
		super().__init__(**kwargs)

		#Since ScrollView doesn't allow for multiple widgets, we might as well add a Layout, with the required number of widgets, to it
		self.layout = GridLayout(cols = 1, size_hint_y = None) #"size_hint_y = None" so that it doesn't default to any height
		self.add_widget(self.layout)

		#Here, 2 widgets are required. 1 for the chat history and the other for scrolling to new messages
		self.chat_history = Label(size_hint_y = None, markup = True)
		self.scroll_to_point = Label()
		self.layout.add_widget(self.chat_history)
		self.layout.add_widget(self.scroll_to_point)


	def update_chat_history(self, message):
		self.chat_history.text += '\n' + message

		#Defining the updated layout height (Leaving some space at the end)
		self.layout.height = self.chat_history.texture_size[1] + 20
		self.chat_history.height = self.chat_history.texture_size[1]
		self.chat_history.text_size = (self.chat_history.width*0.98, None)

		#Since the size of everything in the chat history is constantly increasing by every update, the scroll bar will come into play
		#but the window won't be scrolled all the way down
		#So to counter that problem, the empty "scroll_to_point" widget is added

		self.scroll_to(self.scroll_to_point)  


	def update_chat_history_layout(self, _=None):

		self.layout.height = self.chat_history.texture_size[1] + 20
		self.chat_history.height = self.chat_history.texture_size[1]
		self.chat_history.text_size = (self.chat_history.width*0.98, None)




#Running the App
if __name__ == '__main__':
	chat_app = ChatApp()
	chat_app.run()