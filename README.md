# Gradys Ground Station
Web application, from Project GrADyS, to monitor, control and display mobile devices networks in field tests

# Introduction
This is a repository for the Ground Station framework, developed for the GrADyS project and future IoT projects. It's an extensible and reusable framework, to help visualizing the location and activity status of interconnected network nodes, monitor and store the flow of data and send commands to a set of devices with different protocols. The framework is developed to be extensible, introducing ways to insert new buttons, commands, protocols and funcionalities, according to the project's needs.

![Main showcase](/readme_images/mainShowcase.gif)

# Installation
## Prerequisites
In order to use the components in this repository, you need to have Python 3.0 or higher installed. Also pip, a Python package manager, is recomended to manage and automatically install the required packages of this project. 
To install Python on Windows, [follow these instructions](https://docs.python.org/3/using/windows.html).
After installing Python, pip should be installed by default. You can check if it's already installed and it's version:
```console
C:\> python -m pip --version
```
If not installed or need to updgrade, you can get more information [here](https://pip.pypa.io/en/stable/getting-started/).

## Cloning the repository
With Python3 installed, you should be able to clone this repository. [More information on how to clone](https://docs.github.com/en/repositories/creating-and-managing-repositories/cloning-a-repository).

## Creating a virtual environment
In order to keep this framework in a separate environment, with it's own packages and versions, it's recommended to create a virtual environment. On Windows:
```console
Windows
C:\> python -m venv C:\path-to-this-cloned-repository/venv
```
On Linux, you can check if virtualenv is already installed, install it, if not already installed, and create the venv:
```console
Linux
gradys-gs$ virtualenv --version
  virtualenv xx.x.x
gradys-gs$ sudo pip3 install virtualenv
gradys-gs$ virtualenv venv
```

This will create a folder called *venv*, inside the project's folder. Now you have to activate the environment to install/use packages only from this venv.
```console
Windows
C:\> C:\path-to-this-cloned-repository\venv\Scripts\activate
```
```console
Linux
gradys-gs$ source venv/bin/activate
```

If you need more information about virtual environments with python, it [can be found here](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/#creating-a-virtual-environment).

## Installing necessary packages
The list of necessary packages are inside requeriments.txt file. It'll be installed automatically, using the Python package manager, pip. You can install, running on Windows console:
```console
C:\path-to-this-cloned-repository\> pip install -r requeriments.txt
```


# Usage
## Secret variables:
This project uses Google Maps services, with paid features. To use these functionalities you need to have or create a Google Maps API Key. [Google's guide on how to create an API Key](https://developers.google.com/maps/gmp-get-started).
This project also use Django Framework that has a secret key variable, for security purposes.
You can [generate your Django secret key here](https://djecrety.ir/).
The framework will load automatically these as environment variables. With both private keys created, 
<!--ts-->
  * Inside */config/.env*, insert the secret keys:
    * SECRET_KEY='xxxx'
    *Changing 'xxxx' with your Django secret key*
    * GOOGLE_MAPS_API_KEY='xxxx'
    *Changing 'xxxx' with your Google Maps key*
<!--te-->

## Running the server:
Django provides lightweight development Web server, that you can use via manage.py file. By default, the server runs on port 8000 on the IP address 127.0.0.1 and should not be used on production.
You can run with:
```console
C:\path-to-this-cloned-repository\> python manage.py runserver
```
Or, with diferent IP/PORT, in this example Port 8000 on IP address 1.2.3.4:
```console
C:\path-to-this-cloned-repository\> python manage.py runserver 1.2.3.4:8000
```

## Connecting to home page:
You should be able to connect to the home page now, acessing, on your browser, the IP/PORT the server is up, on default: localhost:8000.


# Project Struct
Gradys Ground Station is structured following the classic concept of web development, with Front-end module, responsible for the interface and visualization, and Back-end module, responsible for server-side information processing. Front-end is built with Javascript language, HTML, or [Template language](https://docs.djangoproject.com/en/3.2/ref/templates/language/) from Django, and Cascading Style Sheets (CSS) language. Back-end is mainly built with Python language, using [Django Framework](https://www.djangoproject.com/).
Both modules comunicate with each other via WebSocket channels. A socket connection is a dedicated full-duplex channel based in the Transmission Control Protocol (TCP). This project uses [Django Channels](https://channels.readthedocs.io/en/stable/) library to handle WebSockets communication.


## Django

### URL/View

To understand the server-side struct of this project, first it's required a basic understanding of how Django is structured and how it operates.
Building a URL scheme with Django is a simple task, thanks to the URL/View mapping that the python web framework provides.
When a user requests a page from the URL schema, Django does a mapping to the corresponding Python function, that's called *View*.
So, for example, the URL scheme below has a mapping between the **home page** path and **index** view, also between ***/command/*** path (note that 'command' is a simple integer) and **receive_command_test** view.
```python
urlpatterns = [
    path('', index),
    path('<int:command>/', receive_command_test),
]
```
 Inside the main app's folder, *connections*, there is *urls.py* and *views.py* files. The *urls.py* file is responsible for making the association between a URL address and a view. Note that there is another *urls.py* file, inside the *config* folder, that is responsible for the whole project's pathing. So, for example, if there was another app in our project, we could create a prefix path to that specific app. Our main app has the default path, so there's no prefix attached. 
 If you want to add a new URL path, it should be added a new path() item inside the urlpatterns list, in */connections/urls.py*. For example:
```python
urlpatterns = [
    path('', index),
    path('<int:command>/', receive_command_test),
    path('new-path/', new_view)
]
```
Now we want a view to handle the new url path request. A view is a Python function that takes a Web request and returns a Web response. This response can be the HTML contents of a Web page, or a JSON or a redirect, or a 404 error, anything, really. The view itself contains whatever arbitrary logic is necessary to return that response.
```python
def index(request):
  context = {
    'google_maps_key': settings.GOOGLE_MAPS_API_KEY
  }
  return render(request, 'index.html', context=context)
```
The example above is the **index view**, accessed when home page is loaded. It receives a request, creates a context variable, with the google maps key from *.env*, and load the *index.html* template, attached with the context.
We store our views inside */connections/views.py*. If you want to create the new view, it should receive a **request** and **return** something (could be anything). To send additional parameters, you can send via the url, for example, the url localhost:8000/new-path/10/, needs to be declared inside the *connections/urls.py* as integer as:
```python
path('new-path/<int:id>/', new_view)
```
And our view can receive an **id** parameter, as follows:
```python
def new_view(request, id):
  # Function Logic
  return 
```
Now, accessing the default server 127.0.0.1:8000/new-path/5/ is going to call our new_view method, sending the parameter 5.

### Routing/Consumers
Our main app form of communication with templates, or HTMLs, is using **websocket connections**. [Django Channels](https://channels.readthedocs.io/en/stable/) package mediates these connections.
The logic to stablish a websocket connection is similar with the URL/View logic presented on the topic above. The ***connections/routing.py*** file contains the websocket url patterns, or schema:
```python
ws_urlpatterns = [
  path('ws/connection/', ConnectionConsumer.as_asgi()),
  path('ws/receive/', ReceiveCommandConsumer.as_asgi()),
]
```
As said, Django Channels makes a mapping, associating an url with a ***Consumer***. A Consumer is a Python Class that handles a websocket connection.
So, when our Javascript is loaded, it tries to connect with a specific Consumer, accessing a specific URL, inside our ws_urlpatters.
```javascript
// Javascript stablishing new connection
var socket = new WebSocket('ws://localhost:8000/ws/connection/');
```
When this command is read, the ConnectionConsumer is called and a connection is initated.
Our Consumers are inside ***connections/consumers_wrappers/*** and a new one can be created, inheriting WebsocketConsumer or AsyncWebsocketConsumer, depending on it's functionality. You can substitute three main methods:
<!--ts-->
* **connect**: called when the specific url is accessed and start a dedicated connection with self.accept. This is the only method you NEED to override.
* **receive**: called when a message is sent via socket connection.
* **disconnect**: called when the connection is closed.
<!--te-->

Creating a new Consumer, is simple as creating a new file inside **connections/consumers_wrapper/** with a Class like:
```python
class NewConsumer(AsyncWebsocketConsumer):
  async def connect(self):
    await self.accept()

  async def receive(self, message):
    # Handle the message

  async def disconnect(self, close_code):
    # Handle disconnection

  async def additional_method(self, *args):
    # Additional method's logic
```
To send a message to the other side of connection (Django -> Javascript) it can be done using the ***send*** method, inherted from WebSocket class:
```python
await self.send(data)
```
Creating the new path can be done adding a new path to ws_urlpatters list:
```python
ws_urlpatterns = [
  path('ws/connection/', ConnectionConsumer.as_asgi()),
  path('ws/receive/', ReceiveCommandConsumer.as_asgi()),
  path('ws/new-socket/', NewConsumer.as_asgi()),
]
```
Finnaly, accessing ws://localhost:8000/ws/new-socket/, a dedicated full-duplex connection should be stablished and our two ends can communicate with each other.

## Front-end
Our front-end consists in templates files, CSS styling files and Javascript files.
The home page template file is rendered when the default ip+port is accessed, as showed above. New templates files can be added inside the **/templates/** folder. They work very similarly to HTML files, with some add-ons. 
```html
{% load static %}
<link rel="stylesheet"  href="{% static 'connections/css/connection.css' %}">
```
The code above introduces the '{% %}' tag (that's not HTML native), in this case, to load a css file to the page.
For more information about [templates, you can access here](https://docs.djangoproject.com/en/3.2/topics/templates/).
To load a Javascript file in a template, the logic is the same, as long this Javascript file is inside the folder that ***STATIC_URL variable*** is pointing to. This variable is inside **config/settings.py**. In our case STATIC_URL variable is pointing to /static/ folder.
```python
STATIC_URL = '/static/'
```
Our ***index.html*** home page template loads ***gmap.js***, responsible for Google Map's virtual map and ***main.js***, responsible for starting websockets connections with the back-end and the main button's logic.
To start a websocket connection, you have to create a new object, sending an available URL in the routing schema (see Routing/Consumers topic).
```javascript
var socket = new WebSocket('ws://localhost:8000/ws/connection/');
```
This object has methods to interact with the socket connection. Here are the main:
<!--ts-->
* **send**: Transmits data to the server via the WebSocket connection.
```javascript
socket.send(jsonToSend);
```
* **readyState**: The current state of the connection, this is one of the [Ready state constants](https://developer.mozilla.org/pt-BR/docs/Web/API/WebSocket#ready_state_constants). Read-only.
```javascript
if (socket.readyState == WebSocket.OPEN) {
    // Handle connection OPEN
}
```
* **onclose**: An event listener to be called when the readyState of the WebSocket connection changes to CLOSED.
```javascript
socket.onclose = function(e) {
  // Handle connection closed
};
```
* **onmessage**: An event listener to be called when a message is received from the server. Receives a message parameter.
```javascript
socket.onmessage = function(msg) {
  // Handle message received
}
```
<!--te-->

### Command Buttons
Another important functionality in this framework is the possibility to send commands, through the interface, to available devices.
We can register a new button inside the template, create a onClick callback function and send the command via websocket to Django (back-end).
<!--ts-->
* Create new button in ***/templates/index.html***
```html
<input class="button" id="new-button" type="button" value="New Command">
```
* Register an onclick function, in ***/static/connections/main.js***
```javascript
var newCommandNumber = 40

document.querySelector('#new-button').onclick = function(e) {
  sendCommand(newCommandNumber);
};
```
* Send to the back-end, when button is clicked
```javascript
function sendCommand(type) {
  jsonToSend = {id: 1, type: type}
  // ...
  if (socket.readyState == WebSocket.OPEN) {
    socket.send(jsonToSend);
  }
}
```
<!--te-->
Notice that the socket object must be instatiated already, and the connection 'OPEN'.
The corresponding Consumer will receive the message and handle, acording to it's command type.

## Communicating with external devices
The main purpose of this framework is to exchange information with other devices. Currently there is implemented two ways for external connections.

### Serial Connection
The first way is plugin a ESP32 microcontroller to the framework's machine. This microcontroller should be able to detect other devices, receive and send information to them.
Our framework can stablish an UART connection with a plugged ESP32 microcontroller, receive everything is sent via serial and send commands via serial, making the microcontroller responsible for retransmiting the command.
In order to accept a connection with a ESP32 microcontroller, you need to insert the correct UART Port and baudrate, inside ***config.ini*** (see below for **Changing the code** topic and **Serial connection** subtopic).
The ***SerialConnection*** class, from */connections/serial_connector.py*, is instantiated when javascript starts a websocket connection of this type. The instantiated object keeps trying connection with the UART Port. Once a microcontroller is plugged, the interface indicates this change, and you are able to exchange information through the ESP32 microcontroller.

### POST Requests
Another way to communicate with our framework is with **POST requests**. A device, let's say an UAV (drone), wants to send it's location to our ground station. This can be achieved with a POST request to a specific URL, registered in ***config.ini*** file (see below for **Changing the code** topic and ***HTTP Requests*** subtopic). Note that the device should attach, on the message, it's own IP and PORT, so our framework can send commands back to it.
The specific URL, to receive POSTs, is mapped to a view. So, when the device send it's location on body's request, the ***post_to_socket*** view receive the request and extracts the information from it's body. We want to send this information to our interface and also to save it in the log file. Who is responsible for both actions is the ***PostConsumer***, inside */connections/consumers_wrapper/post_consumer.py*.
This way, the post_to_socket view needs to send the message to PostConsumer, getting an instance of this class and calling this Class function **receive_post(message)**.


## Changing the code
Some of the framework's informations are initialized by the *config.ini* file. Below are listed the parameters that can be changed.
### Serial connection
One way this framework can comunicate with a network is with a dedicated ESP32, using UART Protocol. The ESP device connected via serial has a specific PORT and Baudrate, that can be changed inside *config.ini* with the [serial] tag:
```python
[serial]
# The serial PORT the ESP32 is connected
port = COM4

# Rate of information transferred in the serial port
# Needs to be the same in ESP32 connection
baudrate = 115200

# If this Protocol is used
serial_available = false
```

### HTTP Requests
Another way to comunicate with nodes of the network is receiving/sending information via POST/GET Requests. Django provides a routing system that acessibles URLs trigger methods, or *Views*.
A device can send a POST request to http://127.0.0.1:8000/update-info/ (or IP/PORT running the application). Notice that a device should send inside the message it's own IP/PORT, so the application can send commands via HTTP requests.
This structure is described with more details below, on the Project Struct topic.

Inside the *config.ini* file, below the [post] tag, you can change some of the protocol's variables:
```python
[post]
# Default ip/port, if device don't provide on message sent
ip = http://127.0.0.1:8000/

# Endpoint that'll receive POST requests with device's information
path_receive_info = update-info/
```

### List of devices updater
The application saves the latest messages of unique devices in a list, inside the *update_periodically_consumer.py*, for each execution. From time to time, it's sent to the front-end, via web-socket, with the activity status of each device. A device can be active, on hold and inactive, depending on the interval of it's last message.
These variables can be adjusted in the *config.ini* file, below the [list-updater] tag:
```python
[post]
# The amount of seconds to a device be considered 'inactive'
seconds_to_device_be_inactive = 50

# The amount of seconds to a device be considered 'on hold'
seconds_to_device_be_on_hold = 25

# The amount of seconds to update the list of devices in Front-End
update_delay = 20
```


## Folders structure
    .
    ├── config              # Contains Django's configurations files
    ├── connections         # Main app folder
    ├── static              # Static js, css, images files
    ├── templates           # Files with template language (html)
    ├── config.ini          # Contains project's adjustable parameters
    ├── manage.py           # Django’s command-line utility for administrative tasks
    ├── requeriments.txt    # Contains all packages and versions required
    └── README.md

We will open the folders that require more attention:

**Connections**
This is the main app's folder, with the necessary tools to allow connections and information exchange with other devices

    .
    ├── ...             
    ├── connections
    |   ├── consumers_wrapper   # Folder with all websocket consumers
    |   ├── LOGS                # Stores all .log files generated
    |   ├── utils               # Auxiliary tools
    |   ├── ...
    |   ├── routing.py          # Paths for websocket connections
    |   ├── serial_connector.py # Auxiliary class to stablish/handle connection with esp32 device
    |   ├── urls.py             # Paths for views
    |   ├── views.py            # Methods called when specific url is accessed
    └── ...

**Templates**
This folder contains the files written with template language. These files can be associated with traditional HTML files, but with tags, interpreted by Django.

    .
    ├── ...             
    ├── templates
    |   ├── index.html   # Home page, runs main.js
    └── ...

**Static**
Contains static files, like Images, CSS and Javascript. Django provides django.contrib.staticfiles to help you manage them. These files can be configured inside *config/settings.py*:
```python
STATIC_URL = '/static/'
```
In the **templates files**, can be used the static template tag to build the URL for the given relative path using the configured *STATICFILES_STORAGE*:
```python
{% load static %}
<img src="{% static 'my_app/example.jpg' %}" alt="My image">
```

    .
    ├── ...             
    ├── static
    |   ├── connections   # Folder to separate the main app's static files
    |   |    ├── css      # All css used inside connections
    |   |    ├── images   # All images used in the project
    |   |    ├── js       # All javascript files
        └──
    └── ...
