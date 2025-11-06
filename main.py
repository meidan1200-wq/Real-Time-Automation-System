from enum import Enum
import time
from pynput import keyboard,mouse
import os
import pygetwindow as gw
from pywinauto import application
import vision as vn
from typing import Dict
import threading
import sys
import time
from functools import wraps
import psutil
import ctypes
from playwright.sync_api import sync_playwright
from botConfig import BotConfig

class World(Enum):
    Earth = 2 / 2
    Yardart = 4 / 2
    TimeChameber = 6 / 2
    Hell = 8 / 2
    BeerusPlanet = 10 / 2
    GravityChamber = 12 / 2


class SharedKey:
    def __init__(self):
        self.key = None
        self.lock = threading.Lock()


# Instantiate the keyboard controller
keyboard_controller = keyboard.Controller()
mouse_controller = mouse.Controller()


'''Training events'''
training_event_Attack = threading.Event()
training_event_Defense = threading.Event()
training_event_Ki = threading.Event()
training_event_Agility = threading.Event()
training_limit_reached = threading.Event()
'''General events'''
already_in_training_event = threading.Event()
Roblox_start_event = threading.Event()
is_ki_bar_empty_or_full = threading.Event()
is_need_to_jump = threading.Event()
is_training_removed = threading.Event()
is_time_chamber_world_enabled = threading.Event()
is_world_changed = threading.Event()


training_events = {
    "Attack": training_event_Attack,
    "Defense": training_event_Defense,
    "Ki": training_event_Ki,
    "Agility": training_event_Agility
}




def click_at_position(x, y, button=mouse.Button.left, clicks=1, interval=2):
    """Move the mouse to a specific position and click."""
    # Move the mouse to the specified position
    mouse_controller.position = (x, y)
    # Wait a bit to ensure the mouse has moved
    time.sleep(interval)
    # Perform the click
    mouse_controller.click(button, clicks)


def press_key(key, interval=1, duration = 1):
    start_time = time.time()
    while time.time() - start_time <= duration:
      #print("Pressing " + key)
      keyboard_controller.press(key)
      time.sleep(0.01)
      #print("Releasing 'Arrow'")
      keyboard_controller.release(key)
      time.sleep(interval)



def click_by_photo(training_coordinates: Dict[str, int],photo_cheaking,x,y, delay = 30):
    '''Click on spesifc button in the screen, based on image recognition, if image wasn't found doing so by spcified delay'''
    # Extract training_coordinates from the dictionary
    top = training_coordinates["top"]
    left = training_coordinates["left"]
    width = training_coordinates["width"]
    height = training_coordinates["height"]

    image_path_1 = vn.capture_screen_with_display(top,left,width,height) #cupture the screenshot

    if image_path_1 is not None:
     identifier = vn.MatchImage(image_path_1,photo_cheaking)#Try to find the button

     if identifier: #cheak ifeeee there is a match
      print("found the specified button. Clicking...")
      click_at_position(x,y)#click at position
     else:
      print(f"found the specified button. Clicking... by spesifid delay : {delay} ")
      time.sleep(delay)#Pause the software for specified time
      click_at_position(x,y)#click at position


def Smart_press_key(key, interval=0.25):
    KiBarValue = 10  # sets ki bar value

    while True:


        try:
            status = vn.GetStatus(status_player_coordinates["Energy bar"]) #Ki bar status
            if status is None:
                continue

            if not isinstance(status, tuple) and len(status) >= 2: #cheak if status is a tuple with two vaules to set
                continue

            KiBarValue = status[0]
            KiBarValueMax = status[1]
        except Exception as e:
            print(f"something went worng by seting the vaules: {e}")

        if key == 'c':

            if KiBarValue  ==  KiBarValueMax or (not training_event_Defense.is_set() and not training_event_Ki.is_set()) :
                break  # Exit the loop if the condition is not met
        elif key == 'q' or 'r':

            if KiBarValue <= KiBarValueMax/4 or (not training_event_Defense.is_set() and not training_event_Ki.is_set()) :
                break  # Exit the loop if the condition is not met

        # Press and release the key
        keyboard_controller.press(key)
        time.sleep(0.01)
        keyboard_controller.release(key)
        time.sleep(interval)


def smart_hold_ki(shared_key,key, interval=1):

    with shared_key.lock:
        shared_key.key = key

    # Press and release the key
    time.sleep(interval)
    if(not is_ki_bar_empty_or_full.is_set()): #checking if event is already set before pressing
     keyboard_controller.press(key)
     is_ki_bar_empty_or_full.wait()#wait until ki bar is full
     keyboard_controller.release(key)#Release the button
    is_ki_bar_empty_or_full.clear()#Clear ki bar event
    with shared_key.lock:
      shared_key.key = None #reset key definition




def press_alt_f4():#(x,y,button = mouse_controller, clicks=1, interval=0.1):
    #  Press and hold the Alt key
    keyboard_controller.press(keyboard.Key.alt)

    #  Press and release the F4 key
    keyboard_controller.press(keyboard.Key.f4)
    keyboard_controller.release(keyboard.Key.f4)

    # # Release the Alt key
    keyboard_controller.release(keyboard.Key.alt)


def kill_process_by_name(process_name = "RobloxPlayerBeta.exe", retries=3, delay=2):
    """
    Kills all processes with the given name, with safety checks and retries.

    :param process_name: Name of the process to kill
    :param retries: Number of retries if the process is not killed initially
    :param delay: Delay in seconds between retries
    """
    def is_process_running(pid):
        try:
            # Check if the process is still running
            psutil.Process(pid)
            return True
        except psutil.NoSuchProcess:
            return False

    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'] == process_name:
            pid = proc.info['pid']
            attempts = 0
            while attempts <= retries:
                try:
                    os.kill(pid, 9)  # Attempt to kill the process
                    time.sleep(delay)  # Wait for a bit
                    if not is_process_running(pid):
                        print(f"Successfully killed process {process_name} with PID {pid}")
                        break
                except Exception as e:
                    print(f"Error killing process {process_name} with PID {pid}: {e}")
                attempts += 1

            if attempts > retries:
                print(f"Failed to kill process {process_name} with PID {pid} after {retries} retries")




def Training_action(events, already_in_training_event, shared_key):
    while True:
        print("threading is running")
        wait_for_events(events)

        for event_name, event in events.items():
            if not event.is_set():
                continue

            if event == training_event_Ki:
                choose_world(World.BeerusPlanet, 5)
                while event.is_set():
                    print("Training Ki in progress...")
                    smart_hold_ki(shared_key, 'c')  # Charging
                    smart_hold_ki(shared_key, 'q')  # Ki blast


            if event == training_event_Defense:
                choose_world(World.Hell, 3)
                while event.is_set():
                    print("Training Defense in progress...")
                    smart_hold_ki(shared_key, 'c')  # Charging
                    smart_hold_ki(shared_key, 'r')  # Defense blast


            if event == training_event_Attack:
                choose_world(World.GravityChamber, 6)
                print("Training Attack in progress...")
                while event.is_set():
                    press_key('e', 0.01)  # Punching


            if event == training_event_Agility:
                choose_world(World.GravityChamber,6)
                is_need_to_jump.set() #Set jump event initially
                while event.is_set():
                    print("Training Agility in progress...")

                    if is_need_to_jump.is_set() :  # Wait until the event is set
                      press_key(keyboard.Key.esc, 0.5, 0.5)  # Open menueeeeeee
                      press_key("r", 0.5, 0.5)  # Reset button
                      press_key(keyboard.Key.enter, 0.5, 0.5)  # Enter to continue
                      time.sleep(5)
                      press_key(keyboard.Key.space, 0.02, 0.02)  # Start jump
                      press_key(keyboard.Key.space, 0.02, 0.02)  # Flying jump
                      is_need_to_jump.clear()  # Clear the event until next jump is needed


                    
                    smart_hold_ki(shared_key, "c")  # Charging ki-bar until max   
                    
  
                    keyboard_controller.press(keyboard.Key.shift)
                    keyboard_controller.press(keyboard.Key.space)
                    keyboard_controller.press('w')
                    print("w was pressed")

                    time.sleep(5)  #wait a bit to ensure the ki bar is being used
                    is_ki_bar_empty_or_full.wait() #wait until ki bar is empty     

                    print("w was released")
                    keyboard_controller.release('w')
                    keyboard_controller.release(keyboard.Key.space)
                    keyboard_controller.release(keyboard.Key.shift)
                    is_ki_bar_empty_or_full.clear()  # Clear ki bar event
                    
                    

        already_in_training_event.clear()



def ChangeWorld(World : World):
    """Channging to specified a world."""
    numberofclicks = 2 #determines how should the last button to be clicked
    if(World.name == "GravityChamber"):
      numberofclicks = 1 
    press_key('m') #Opens menu
    time.sleep(1) #ensuring click
    press_key('\\',0.25,0.75) #KeyBind Control Keyborad instand mouse\\ toggle on
    press_key(keyboard.Key.up,0.25,0.25) #reset position saftey
    time.sleep(1)#ensuring click
    press_key(keyboard.Key.down,0.25,1.25) #Go to World Button
    press_key(keyboard.Key.enter, 0.25, 0.25) #Opens world tab
    press_key(keyboard.Key.right, 0.25, 0.25) # Navigate to World window
    press_key(keyboard.Key.down, 0.25, 0.25) #Exit slider
    press_key(keyboard.Key.down,0.25,World.value/4) #Navigate to spesific world
    press_key(keyboard.Key.enter, 0.25, 0.25) #click on the World
    press_key('\\',0.5,1) #KeyBind Control Keyborad instand mouse\\ toggle on
    press_key(keyboard.Key.down,0.25,1.25) #Go to World Button
    press_key(keyboard.Key.right, 0.25, 0.25) #Opens Navigate to World window
    press_key(keyboard.Key.left,0.5,numberofclicks/2) #Opens Navigate to World window
    press_key(keyboard.Key.enter, 0.25, 0.25) #click on change world button
    press_key('m') #Closing menu (optinial)
    press_key('\\',1) #KeyBind Control Keyborad instand mouse\\ toggle off
    time.sleep(5) #wait a bit before closing the function

   

def choose_world(world: World, requirement=10, interval=15):
    current_zenkai_limit = config.next_zenkai - 1  # vn.GetStatus(status_player_coordinates["Zenkai"])

    # Check that world exists AND current_zenkai_limit is a valid number
    if world is not None and isinstance(current_zenkai_limit, (int, float)) and current_zenkai_limit >= requirement:
        ChangeWorld(world)
    elif is_time_chamber_world_enabled.is_set():
        ChangeWorld(World.TimeChameber)
        is_time_chamber_world_enabled.clear()
    else:
        # Handle invalid or missing zenkai info gracefully
        if current_zenkai_limit is None:
            print("Warning: current_zenkai_limit is None — cannot compare.")
        else:
            print(f"No world matches player stats. Zenkai: {current_zenkai_limit}, requirement: {requirement}")

        ChangeWorld(World.Earth)
        print("Staying in Earth...")
        
    print("World has been changed...")
    time.sleep(interval)  # Wait for the world to change
    is_world_changed.set() #notify world has been changed     




def open_Roblox_app(playwright):

    browser = playwright.chromium.launch(headless=False)

    # Load the saved state
    context = browser.new_context() #storage_state=config.login_save_file
    page = context.new_page()

    try:
        # Open the website, now you should be logged in
        page.goto("https://www.roblox.com/games/71315343/Dragon-Ball-Rage")

        # Locate the button by its selector and click it
        page.locator('[data-testid="play-button"]').click()

        try:
            # Wait until a specific button is loaded and visible, continue process if timeout reached
            page.wait_for_selector('#decline-btn.btn-control-md', timeout=2000)  # Timeout in milliseconds

            # Continue with your operations
        except TimeoutError:
         print("Button did not appear within 2 seconds. Proceeding anyway.")
        except Exception as e:
         print(f"Error has occurred - {e}")


        # Check if the login page button appears
        if page.locator('#decline-btn.btn-control-md').is_visible():

            # Function to save login state
            def save_login_state():
                try:
                    # Click on the login page button
                    page.locator('#decline-btn.btn-control-md').click()

                    # Wait until the URL changes after login
                    page.wait_for_url(f"**/login**", timeout=10000)

                    usernames, passwords = config.username, config.password # Retrieve credentials from config

                    # Enter username and password
                    page.fill("#login-username", usernames)
                    page.fill("#login-password", passwords)

                    # Click the login button
                    page.locator("#login-button").click()


                    # Wait until the URL changes after login
                    page.wait_for_url("**/games/71315343/Dragon-Ball-Rage**", timeout=10000)

                    print(f"Exists? {os.path.exists(config.login_save_file)}")

                    # Save the browser context (cookies, local storage, etc.)
                    context.storage_state(path=config.login_save_file)
                except TimeoutError:
                    print("Navigation to the expected URL after login failed.")
                except Exception as e:
                    print(f"Login failed... Error has been occurred - {e}")
                    training_limit_reached.set() #terminate script


            # Perform login steps again
            save_login_state()

            # Locate the main button by its selector and click it again
            page.locator('[data-testid="play-button"]').click()

            #Wait a bit before closing
            time.sleep(3)

            # Reload the page after saving the new login state (optional)
            #page.reload()


        #Insure the click is on Chromium web brwoser by foucs the window
        focuse_window("Dragon Ball Rage - Roblox - Chromium","chrome.exe")

        #Wait a bit before clicking
        time.sleep(2)

        #standing on the play button protocol
        press_key(keyboard.Key.down)
        #press on the play button protocol


        press_key(keyboard.Key.enter)

        #Wait a bit before closing
        time.sleep(5)
    finally:
        browser.close()


def Reset():

   '''Restart roblox'''

   window = find_window_by_process_name("Roblox","RobloxPlayerBeta.exe")

   if(window): #cheaks if Roblox is open
      kill_process_by_name("RobloxPlayerBeta.exe") #closing roblox
      time.sleep(1) #wait a sec for closing the app

   #Reopen Roblox
   with sync_playwright() as playwright:
     open_Roblox_app(playwright)

   time.sleep(15)
   focuse_window("Roblox") #Ensuring roblox isn't Minimized
   Roblox_start_event.set()#event set. notify the the protection function to cheak application
   time.sleep(10)#wait a bit to roblox to open
   press_key(keyboard.Key.down,0.5,3)


def get_player_current_stats():
    zenkai_value = None
    player_training_limit = None
    current_training_value = None

    dragon_balls_limit = False

    

    print("Open menu to get current zenkai and training limit values...")
    press_key('m')  # Opens menu
    time.sleep(1)
    press_key('\\', 0.5, 1.5)  # KeyBind Control Keyboard instant mouse toggle on
    time.sleep(1)
    press_key(keyboard.Key.up ,0.25,0.25)  # Safety check position reset
    press_key(keyboard.Key.down, 0.25, 1)  # Go to player stats
    press_key(keyboard.Key.enter,0.25,0.25)  # Opens Zenkai tab

    # --- Get current values ---
    zenkai_value = vn.GetStatus(status_player_coordinates["Next Zenkai"])
    player_training_limit = vn.GetStatus(status_player_coordinates["Training limit"])
    dragon_balls_limit = vn.GetStatus(status_player_coordinates["Zenkai Button Text"],"text") == "USE DRAGON BALLS"  # Check if dragon balls limit is set

    # --- Handle tuple result for training limit ---
    if isinstance(player_training_limit, tuple):
        # Take the highest numeric value (ignores non-numeric values safely)

        
        numeric_values = [v for v in player_training_limit if isinstance(v, (int, float))]
        if numeric_values:
            current_training_value = player_training_limit[0] # Assuming the first element is the min
            player_training_limit = player_training_limit[1]  # Assuming the second element is the max
        else:
            raise ValueError(f"Invalid tuple contents: {player_training_limit}")


    # --- Navigate back ---
    time.sleep(1)
    press_key(keyboard.Key.up, 0.25, 1)  # Opens Zenkai reset tab
    press_key(keyboard.Key.enter)  # Choose reset tab
    press_key('\\', 0.5,0.5)  # KeyBind Control Keyboard instant mouse toggle on
    press_key('m')  # Closes menu

    # --- Validation ---
    if (zenkai_value is None or isinstance(zenkai_value, (str, tuple)) or
        player_training_limit is None or isinstance(player_training_limit, (str, tuple)) or
        current_training_value is None or isinstance(current_training_value, (str, tuple))):
        raise ValueError(f"One or more were Invalid return values: zenkai={zenkai_value}, training_limit={player_training_limit} , current_training_value={current_training_value}")

    '''''''''''''''''''Limit training condition cheak'''''''''''''''''''''''''

    if dragon_balls_limit and current_training_value >= player_training_limit: #stops the script if the limit is reached
        print("Dragon balls training limit reached — notifying exit thread.")
        training_limit_reached.set() #set the event to notify the exit thread

    ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

    # Return both values as a tuple
    return zenkai_value, player_training_limit




def update_zenkai_boost(test_bool = False):

    '''when limit is reached increase Zenkai boost number'''

    print("Attempting to update the player Zenkai boost stat...")
    press_key('m')  # Opens menu
    time.sleep(1)
    press_key('\\', 0.5, 1.5)  # KeyBind Control Keyboard instant mouse toggle on
    time.sleep(1)
    press_key(keyboard.Key.up)  # Safety check position reset
    press_key(keyboard.Key.down, 0.25,1)  # Go to player stats
    press_key(keyboard.Key.enter,0.25,0.25)  # Opens Zenkai tab
    press_key(keyboard.Key.right,0.25,0.25)  # Navigate to Zenaki boost button
    press_key(keyboard.Key.up,0.25,0.25)  # Navigate to Zenaki boost button
    time.sleep(1) #wait to ensuring spot
    press_key(keyboard.Key.enter) #confirem zenaki//rest the level
    time.sleep(1) #wait to ensuring click



    press_key('\\')  # --- closing special controls ---
    #press_key('m',0.5,1)  # in case of a fail Closes menu

    time.sleep(3) #wait to ensuring click




def reset_zenkai_state(results_dict):
    """Clear results and reset counter."""
    results_dict.clear()
    config.next_zenkai = None



def get_process_id_from_window_handle(hwnd):
    pid = ctypes.c_ulong()
    ctypes.windll.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
    return pid.value


def find_window_by_process_name(window_title,process_name):
    # Get all windows with the specified title
    windows = gw.getWindowsWithTitle(window_title)

    for window in windows:
        try:
            hwnd = window._hWnd  # Get the window handle
            pid = get_process_id_from_window_handle(hwnd)  # Get the process ID from the window handle
            process = psutil.Process(pid)
            if process.name() == process_name:
                print(process.name())
                return window
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue

    return None



# Function to check if a window is minimized and restore it
def focuse_window(window_title, proces_name = "RobloxPlayerBeta.exe" ):
    # Get windows with the specified title
    window = find_window_by_process_name(window_title,proces_name)

    if not window:
        print(f"No window found with title: {window_title}")
    else:

        print(f"Found window '{window_title}'")

        # Check if the window is minimized
        if window.isMinimized or not window.isMaximized or not window.isActive:
            print(f"Window '{window_title}' is minimized. Restoring...")
            window.restore()

            print(f"Bringing window '{window_title}' to focus...")

            # Connect to the application and bring the window to focus
            app = application.Application().connect(handle=window._hWnd)
            top_window = app.top_window()
            top_window.set_focus()
            top_window.maximize()




def chooser(already_in_training_event,shared_key):

    
    zenkai_boost_managed_length = None # Length of training types to manage based on zenkai boost
    min_value = float('inf')  # Initialize min_value to positive infinity
    min_arg_name = ''  # Initialize to an empty string
    results_dict = {}  # Dictionary to store the results with their names

    focuse_window("Roblox") #Ensuring roblox isn't Minimized
    time.sleep(2)  # Wait a bit to ensure focus

    while True:

        if already_in_training_event.is_set():
            try:

                time.sleep(0.5) #Adding a bit delay to the fucntion 
                
                result = vn.GetStatus(training_coordinates[min_arg_name])

                if result is None or isinstance(result, str) or isinstance(result, tuple) or result >= config.current_training_limit * 1.25:
                    raise ValueError(f"Invalid return value: {result}")

                check_values(result) #layer of protection cheaks if values are changed every 30 seconds

                ki_bar_checker(shared_key) #determines whether the keyboard is empty

                if result >= config.current_training_limit: #cheak if the current value reached the limit
                    print("Training limit has been reached. Clearing events and restarting chooser...")
                    clear_events(training_events)

                    results_dict.clear()
                    is_ki_bar_empty_or_full.set()
                    config.previous_values = None #Optinal reset previous values for next cheak


                    continue

                config.software_failure_counter = 0 #Reset counter

            except Exception as e:
                print(f"Error occurred: {e}. reaching to Restart")
                training_protector(Roblox_start_event,results_dict)
        else:

            for i, name in enumerate(list(training_coordinates.keys())):
                try:

                    coordinate = training_coordinates.get(name)
                    # Skip if coordinate was removed or already processed
                    if (config.next_zenkai != None and name in results_dict) or coordinate is None:
                       print(f"One of the vaules were already set. skipping...")
                       continue

                    result = vn.GetStatus(coordinate)
                    if result is None or isinstance(result, str) or isinstance(result, tuple):
                        raise ValueError(f"Invalid return value: {result}")


                    results_dict[name] = result  # Store the result with the name

                    if(config.next_zenkai is None): #store the current zenaki boost if it's None
                       config.next_zenkai,config.current_training_limit = get_player_current_stats()
                       print(f"Next zenkai boost : {config.next_zenkai}, Current training limit : {config.current_training_limit}")

                       #Retrieve length for how many stats should be in order to update
                       zenkai_boost_managed_length = zenaki_boost_required_length()

                    config.software_failure_counter = 0 #Reset counter

                except Exception as e:
                    print(f"Iteration {i + 1}: Error occurred - {e}")
                    training_protector(Roblox_start_event,results_dict)


            '''''''''''''''''''''''''''Zenkai_update'''''''''''''''''''''''''''''''''
            try:

                # Ensure correct length before checks
                if len(results_dict) != zenkai_boost_managed_length:
                    continue  # skip until we have enough data

                
                # --- Handle failure limit reached ---
                if config.zenkai_failure_counter >= 3:
                  print("⚠️ Maximum failure attempts reached. Forcing game reset.")
                  reset_zenkai_state(results_dict)
                  config.zenkai_failure_counter = 0 # Reset failure counter
                  Reset()  # Reset Roblox
                  continue  # Restart the loop after forcing a reset


                # --- Handle successful ZENAKI threshold reached ---
                if all(value >= config.current_training_limit for value in results_dict.values()):
                 print("✅ All values meet or exceed limit. Updating ZENAKI boost...")
                 reset_zenkai_state(results_dict)
                 config.zenkai_failure_counter += 1
                 update_zenkai_boost()
                 continue # Restart the loop after ZENAKI boost update

                # --- If none of the above, reset failure counter ---
                config.zenkai_failure_counter = 0

            except TypeError as e:
                print(f"TypeError during Zenkai update check: {e}")
                continue


            ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

            #Insure the world is set in case of a match 
            if all(value >= 1.25* 1e6 for value in results_dict.values()):
                 is_time_chamber_world_enabled.set()
                 
            #Filter any values above current limit
            if(config.current_training_limit is not None):
             results_dict = {key: value for key, value in results_dict.items() if value < config.current_training_limit}

            if not results_dict : #if empty reset the loop
                print("dictionary is empty. Cheaking for restart...")
                continue


            #Finds the smallest number from the dictionary
            min_arg_name, min_value = min(results_dict.items(), key=lambda x: x[1])
            print(f"The smallest value is {min_value} for the key '{min_arg_name}'.")



            if min_arg_name in training_events:
                print(f"Training action has been chosen: {min_arg_name}")
                event_to_set = training_events[min_arg_name] #sets the chosen event for futher process
                event_to_set.set()
                already_in_training_event.set()
                clear_events(training_events, event_to_not_turn_off=event_to_set)
                is_world_changed.wait()  # Wait a bit before restarting the loop
                is_world_changed.clear() # clear the event for next use
            else:

                print("No valid value was found")
                clear_events(training_events)
                time.sleep(5)  # Wait a bit before restarting the loop

def zenaki_boost_required_length():

    '''Determines how many training types should be active based on current zenkai boost'''
    saved_length = None  # Ensure saved_length is Reset before any action or call

    if config.next_zenkai is None:
        print("Next zenkai boost is None. Cannot determine required length.")
        return None

    current_zenkai_boost = config.next_zenkai - 1 #vn.GetStatus(status_player_coordinates["Zenkai"])

    if current_zenkai_boost >= 6:
        # Removes chosen training for a certain condition
      if(not is_training_removed.is_set()):
        disable_specified_training(training_coordinates, training_events, "Agility")
      saved_length = 3
    else:
      saved_length = 4

    return saved_length


def disable_specified_training(dict1, dict2, key):
    """Removes a key-value pair from both dictionaries if the key exists."""

    message = []
    removed_from_dict1 = False
    removed_from_dict2 = False

    for i, d in enumerate((dict1, dict2), 1):
        if key in d:
            message.append(f"Key '{key}' found in dictionary {i}... Removing")
            del d[key]
            if i == 1:
                removed_from_dict1 = True
            else:
                removed_from_dict2 = True
        else:
            message.append(f"Key '{key}' not found in dictionary {i}")

    #if vaule successfully removed from both dictionaries set the event
    if removed_from_dict1 and removed_from_dict2:
        is_training_removed.set()

    print(' '.join(message)
)



def training_protector(roblox_event,results_dict_to_clean = None):

    try:

       windows = find_window_by_process_name("Roblox","RobloxPlayerBeta.exe") #reaching for the Roblox

       if not windows:#Cheaking if Roblox is open
            print(f"No window found with title: Roblox")
            clear_events(training_events)#clear all training events
            Reset() #Reset Roblox
            config.software_failure_counter += 1
       else:
         focuse_window("Roblox") #Ensuring roblox isn't Minimized
         config.software_failure_counter += 1

       #Prevents infinte recovering if the software cannot stabilize itself 
       if config.software_failure_counter >= 10:
           print("Too... Many calls for the function terminate script... ")
           training_limit_reached.set()
           time.sleep(10) #Insures the event has time to perfrom action
           return 
           
       disconnect_matcher = vn.GetStatus(detectors["Disconect"],return_type = "text") #retrieve text from image

        #cheak if there is match
       if not 'Disconnected' in disconnect_matcher:
         return

       #retrieve text from image about type of error
       if detectors.get("Error_code"):
         error_code_matcher = vn.GetStatus(detectors["Error_code"], "text", 150) or ""

       if "Error Code:" in error_code_matcher:
           print(f"{error_code_matcher} Reset...")



       clear_events(training_events)#clear all training events
       if(results_dict_to_clean):
         results_dict_to_clean.clear()#clear the the dictionary from data if needed
       print("Connection has been occurred. Reset...")
       Reset() #Reset Roblox

       roblox_event.wait()#wait until the roblox opens

       connection_lost_matcher = vn.GetStatus(detectors["Internet_lost"],return_type = "text")
       if 'Error info: HitpErrern ConnectFail' in connection_lost_matcher:
         print("Internet connection has been lost. Stopping process...")
         time.sleep(2)
         kill_process_by_name("RobloxPlayerBeta.exe") #closing roblox
         training_limit_reached.set() #terminate script
       print("internet connection still intact. Reopen Roblox...")
       roblox_event.clear()
       return
    except Exception as e:
     print(f"Extraction failed error : Error occurred - {e}")
     return


def throttle_one_minute(func):
    last_called = [0]  # Using a mutable type to hold the last called timestamp

    @wraps(func)
    def wrapper(*args, **kwargs):
        current_time = time.time()
        if current_time - last_called[0] >= 30:
            last_called[0] = current_time
            return func(*args, **kwargs)
        else:
            #print("Function call throttled. Please wait for half minute.")
            return   # or you can raise an exception or return a specific value
    return wrapper

@throttle_one_minute
def check_values(current_values):
    """
    Protect training types by checking if the values are equal.
    After 10 consecutive equal values (failures), triggers additional code.
    """

    # If this is the first check
    if config.previous_values is None:
        print(f"Previous value is None. Setting to current value: {current_values}.")
        config.previous_values = current_values
        config.values_failure_counter = 0  # reset counter
        return # Exit after preparing initial state


    # If value didn't change
    if current_values == config.previous_values:
        config.values_failure_counter += 1
        print(f"Current values match the previous values. Failure count: {config.values_failure_counter}")

        # Regular behavior
        focuse_window("Roblox") #Ensuring roblox isn't Minimized

        is_ki_bar_empty_or_full.set()
        if training_event_Agility.is_set():
            is_need_to_jump.set()

        # If 10 consecutive failures reached
        if config.values_failure_counter >= 5:
            print("⚠️ 10 consecutive failed checks reached! Executing recovery code...")
            Reset()  # Reset Roblox
            config.values_failure_counter = 0 # Reset the failure counter after handling
    else:
        # If value changed → reset counter
        print(f"Value changed from {config.previous_values} to {current_values}. Resetting failure counter.")
        config.previous_values = current_values
        config.values_failure_counter = 0 

   

        
def ki_bar_checker(shared_key):

    '''Cheaks when to relase the holding button by seting an event'''

    KiBarValue = 10  # sets ki bar value

    status = vn.GetStatus(status_player_coordinates["Energy bar"]) #Ki bar status

    if status is None: #cheak if the ki bar status is null
      is_ki_bar_empty_or_full.clear()
      return  
    
    if not isinstance(status, tuple) or len(status) < 2: #cheak if status is a tuple with two vaules to set
      is_ki_bar_empty_or_full.clear()
      return


    if(status[0] > status[1]): #cheak if the ki bar value is more than max value
        return
    
    KiBarValue = status[0]
    KiBarValueMax = status[1]

    with shared_key.lock:
        key = shared_key.key  # Retrieve the key from the shared object

    if key == 'c':

        if KiBarValue  ==  KiBarValueMax or (not training_event_Defense.is_set() and not training_event_Ki.is_set() and not training_event_Agility.is_set()) :
           is_ki_bar_empty_or_full.set() # set the event if the condition is met
    else:

        if KiBarValue <= KiBarValueMax/4 or (not training_event_Defense.is_set() and not training_event_Ki.is_set() and not training_event_Agility.is_set()) :
           is_ki_bar_empty_or_full.set() # set the event if the condition is met


def health_bar_checker():

    status = vn.GetStatus(status_player_coordinates["Energy bar"]) #Ki bar status

    if status is None: #cheak if the ki bar status is null
     is_ki_bar_empty_or_full.clear()

    if not isinstance(status, tuple) and len(status) >= 2: #cheak if status is a tuple with two vaules to set
     is_ki_bar_empty_or_full.clear()

    healthBarValue = status[0]
    healthBarValueMax = status[1]

    if healthBarValue == healthBarValueMax:
       return True
    else:
       return False



'''Events methods'''

# Function to set all events
def set_events(events):
    for event in events:
        event.set()

def clear_events(events, event_to_not_turn_off=None):
    for event_name, event in events.items():
        if event_to_not_turn_off is None or event != event_to_not_turn_off:
            event.clear()


def wait_for_events(events):
    print("Waiting for at least one event to be set...")
    while not any(event.is_set() for event_name, event in events.items()):
        time.sleep(0.1)  # Sleep briefly to avoid busy-waiting
    print("At least one event has been set!")


'''program control functions'''


def on_press_progrem(key):
    try:
        if key == keyboard.Key.delete:  # Example: stop when del key is pressed
            print("Keybind detected — stopping...")
            training_limit_reached.set()
    except AttributeError:
        pass  # ignore special keys if not needed

def on_release_progrem(key):
    pass

def release_all_keyboard_keys():

    for key in list(pressed_keys):
        keyboard_controller.release(key)
        pressed_keys.remove(key)  # Remove key from the set once released

def start_listener():
    """Thread that listens for keyboard input OR training-limit event."""
    listener = keyboard.Listener(on_press=on_press_progrem, on_release=on_release_progrem)
    listener.start()  # Non-blocking start

    print("Listening for keybind or event...")

    # Keep looping until either condition happens
    while not training_limit_reached.is_set():
        time.sleep(0.1)  # light wait to reduce CPU usage

    print("Training limit or Zenkai boost max reached — terminating script...")
    release_all_keyboard_keys()
    clear_events(training_events)#clear all training events
    config.overwrite_state_file()
    sys.exit()


if __name__ == "__main__":

    # initialize Obejcts
    shared_key = SharedKey()
    config = BotConfig()
    pressed_keys = set()

    # Load coordinates configurations
    training_coordinates = config.training_coordinates
    status_player_coordinates = config.status_player_coordinates
    detectors = config.detectors

    # Start the keyboard listener in a separate thread
    listener_thread = threading.Thread(target=start_listener)
    listener_thread.start()

    # Create thread1 and set it as daemon
    thread1 = threading.Thread(target=chooser, args=(already_in_training_event, shared_key), daemon=True)
    thread1.start()

    # Create thread2 and set it as daemon
    thread2 = threading.Thread(target=Training_action, args=(training_events, already_in_training_event, shared_key), daemon=True)
    thread2.start()

    listener_thread.join()  # Keeps main thread alive to ensure no missing processes







