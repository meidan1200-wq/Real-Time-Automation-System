import json
import os
import sys
import pyautogui
from pathlib import Path
from jsonschema import validate, ValidationError




class BotConfig:

    BASE_PATH = os.path.join(os.path.dirname(__file__), "Data_config")

    def __init__(self):
       
       # Get resolution-based file and ensure it exists
       coord_path = self.get_resolution_based_file()
       coord_path = self._full_path(coord_path)
       if not os.path.exists(coord_path):
            raise FileNotFoundError(f"File not found: {coord_path}")
       
       print(coord_path)
       
       # Define and set the initial value of the training limit
       self.data_coord = coord_path
       self.auth_file = self._full_path("Authentication.json")
       self.login_save_file = self._full_path("state.json")
       self.schema_file = self._full_path("schema_config.json")
       
       # State variables
       self.previous_values = None
       self.next_zenkai = None
       self.current_training_limit = None
       self.zenkai_failure_counter = 0
       self.values_failure_counter = 0
       self.software_failure_counter = 0

       # Configuration data
       self.training_coordinates = {}
       self.status_player_coordinates = {}
       self.detectors = {}

       # Authentication data
       self.username = None
       self.password = None

       # Load configuration from JSON file
       self.load_config()
       self.read_usernames_passwords()
       self.overwrite_state_file()
       self.check_chromium_installed()


    def _full_path(self, file_name): 
        '''Construct the full path for a given file name within the data_config folder.'''
        return os.path.join(self.BASE_PATH, file_name)


    
    # ----------------------------
    #  Schema & Config Validation
    # ----------------------------
    def _load_schema(self, path="schema_config.json"):
        """Load the schema definition from a JSON file."""
        with open(path, "r") as f:
            return json.load(f)

    def _validate_config(self, config_data):
        """Validate configuration JSON structure and content."""
        schema = self._load_schema(self.schema_file)
        try:
            validate(instance=config_data, schema=schema)
            print("✅ Config is valid.")
        except ValidationError as e:
            raise ValueError(f"❌ Invalid configuration: {e.message}")  


    # ----------------------------
    #  Config File Loading
    # ----------------------------
    def load_config(self):
        """Load and validate coordinate configuration."""
        with open(self.data_coord, "r") as f:
            config_data = json.load(f)

        # Validate JSON structure
        self._validate_config(config_data)

        # Assign data to object attributes
        self.training_coordinates = config_data.get("training_coordinates", {})
        self.status_player_coordinates = config_data.get("status_player_coordinates", {})
        self.detectors = config_data.get("detectors", {})

    
    def read_usernames_passwords(self):
        """Read usernames and passwords from the Authentication.json file."""
        if not os.path.exists(self.auth_file):
            raise FileNotFoundError(f"Missing configuration file: {self.auth_file}")

        with open(self.auth_file, "r", encoding="utf-8") as file:
            data = json.load(file)

        self.username = data.get("username")
        self.password = data.get("password")

        if not self.username or not self.password:
            raise ValueError("Missing username or password in the JSON file.")

        return self.username, self.password


    def overwrite_state_file(self):

        if not os.path.exists(self.login_save_file):
            raise FileNotFoundError(f"Missing configuration file: {self.login_save_file}")

        '''Reset the login_save file for reuse automation on web browser '''
        empty_state = {}
        with open(self.login_save_file, "w") as file:
            json.dump(empty_state, file)
            print(f"{self.login_save_file} has been reset.")

    def get_resolution_based_file(self):
        """Return a file path depending on whether the user uses 4K, 2K, or 1080p resolution.
        If resolution detection fails, stop the process completely."""

                
        try:
            width, height = pyautogui.size()
            print(f"Primary monitor resolution: {width}x{height}")
        except Exception:
                # Both methods failed — stop the program
                print("❌ Failed to detect screen resolution. Terminating process.")
                sys.exit(1)    
            

        if width is None or height is None:
            print("❌ Resolution data unavailable. Terminating process.")
            sys.exit(1)

        print(f"Detected resolution: {width}x{height}")

        # Use a tolerance of ±50 pixels
        tolerance = 50

        if abs(width - 3840) <= tolerance and abs(height - 2160) <= tolerance:
            file_path = "Data_Coordinates4k.json"
        elif abs(width - 1920) <= tolerance and abs(height - 1080) <= tolerance:
            file_path = "Data_Coordinates1080p.json"
        else:
            file_path = "Data_Coordinates_custom"
            
        # Print which file was selected
        print(f"✅ Selected file: {file_path}")
        return file_path
    
    def check_chromium_installed(self):
        """
        Check if Playwright Chromium is installed (any version).
        Raises:
            FileNotFoundError: If Chromium is not installed.
        """
        # Determine OS-specific Playwright cache path
        if sys.platform.startswith("win"):
            base_dir = Path(os.getenv("LOCALAPPDATA")) / "ms-playwright"
        elif sys.platform.startswith("darwin"):
            base_dir = Path.home() / "Library/Caches/ms-playwright"
        else:  # Linux
            base_dir = Path.home() / ".cache/ms-playwright"

        # Check for any folder starting with 'chromium-'
        chromium_folders = list(base_dir.glob("chromium-*"))
        if not chromium_folders or not any(f.exists() and any(f.iterdir()) for f in chromium_folders):
            raise FileNotFoundError(
                "Playwright Chromium is not installed. "
                "Please run: playwright install chromium"
            )
        
        







    