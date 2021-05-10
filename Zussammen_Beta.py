import kivy
import os
import sys
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout #A Layout Structure
from kivy.uix.textinput import TextInput #Allows Text Input
from kivy.uix.button import Button #Allows for the usage of Buttons
from kivy.uix.screenmanager import ScreenManager, Screen #Allows for changes in Pages/Screens
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

		self.back = Button(text="Back")
		self.back.bind(on_press=self.back_button)
		self.add_widget(Label())
		self.add_widget(self.back)

	def back_button(self,instance):
		chat_app.screen_manager.current = "Connect"



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
	'''Clock.schedule_once(sys.exit, 10)'''

#The Chat Page (An App in itself)
class ChatPage(GridLayout):
	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.cols = 1
		self.add_widget(Label(text = "The real shit will be here soon....", font_size = 32))

#Running the App
if __name__ == '__main__':
	chat_app = ChatApp()
	chat_app.run()