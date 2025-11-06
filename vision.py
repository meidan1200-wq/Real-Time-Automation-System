import time 
import cv2 as cv
import pytesseract
import re
import numpy as np
import mss
import os
import sys
from typing import Dict

def MatchImage(frame_image, Image_ToCompare= "middle.png"):
    # Load numbers image
    numbers_img = cv.imread(Image_ToCompare, cv.IMREAD_UNCHANGED)

    
    # Convert frame_image to NumPy array if it's not already
    if not isinstance(frame_image, np.ndarray):
        frame_image = np.array(frame_image)
    
    # Check if the images are loaded correctly
    if numbers_img is None:
        raise FileNotFoundError(f"Could not load '{Image_ToCompare}'. Please check the file path.")

    if frame_image is None:
        raise ValueError("Frame image is invalid.")
    
    # cv.imshow("sddfs",numbers_img)
    # cv.waitKey(0)
    # cv.imshow("dfdsf",frame_image)
    # cv.waitKey(0)

    
    # Ensure the template is smaller than the source image
    if numbers_img.shape[0] > frame_image.shape[0] or numbers_img.shape[1] > frame_image.shape[1]:
        raise ValueError("Template image (numbers_img) is larger than the source image (frame_image).")

    # Perform template matching
    result = cv.matchTemplate(frame_image, numbers_img, cv.TM_CCOEFF_NORMED)
    
    threshold = 0.3

    # Check if any match was found
    if np.max(result) >= threshold:
        return True
    else:
        return False


    
def extract_text_from_image(image,threshold_min):
    # Ensure pytesseract can find the tesseract executable.
    # If the user has already configured pytesseract.pytesseract.tesseract_cmd elsewhere, don't overwrite it.
    if not getattr(pytesseract.pytesseract, 'tesseract_cmd', None):
        # Try common Windows install paths first, then rely on PATH.
        common_paths = [
            r'C:\Program Files\Tesseract-OCR\tesseract.exe',
            r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe'
        ]
        for p in common_paths:
            if os.path.exists(p):
                pytesseract.pytesseract.tesseract_cmd = p
                break
        else:
            # If not found in common locations, try calling tesseract through PATH.
            try:
                pytesseract.get_tesseract_version()
            except EnvironmentError:

                print("Tesseract executable not found. Please install Tesseract OCR for Windows and add it to your PATH,\n"
                    "or set pytesseract.pytesseract.tesseract_cmd to the full path to the tesseract.exe.\n"
                    "Installer: https://github.com/tesseract-ocr/tesseract#windows\n"
                    "Example PowerShell (run as Admin): winget install --id=UB-Mannheim.Tesseract -e --source winget"   
                    )
                sys.exit()
                
                
    
    # Convert the image to grayscale
    gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)

    # Apply thresholding to preprocess the image
    _, thresh = cv.threshold(gray, threshold_min, 255, cv.THRESH_BINARY_INV)

    # cv.imshow("ww",thresh)
    # cv.waitKey(0)
   
    # Use pytesseract to extract text from the image
    custom_config = r'--oem 3 --psm 6'  # General text extraction
    #Extract the text fromt he image with no spaces before and after 
    text = trim_text(pytesseract.image_to_string(thresh, config=custom_config))
    
    return text


def trim_text(text):
    if not text:
        return ""
    
    start = 0
    end = len(text) - 1
    
    while start <= end and text[start].isspace():
        start += 1
    
    while end >= start and text[end].isspace():
        end -= 1
    
    return text[start:end + 1]


def extract_numbers(text):
    # Use a single regular expression pattern to capture both integers and floats, possibly followed by 'k' or 'M'
    pattern = r'\b\d+[,.]?\d*[kM]?\b'

    text_update = text.replace(',', '.')  # Replace comma with dot
    match = text_update.replace('..', '.')  # Remove double dots

    # Find all matches in the text
    matches = re.findall(pattern, match)

    # If matches are found, process each match
    if matches:
        def convert(match):
            if match[-1] in 'kM':
                number = float(match[:-1])
                if match[-1] == 'k':
                    return number * 1e3
                elif match[-1] == 'M':
                    return number * 1e6
            else:
                try:
                    return float(match) if '.' in match else int(match)
                except ValueError:
                    return None  # Return None if conversion fails
        
        converted_matches = [convert(m) for m in matches]
        # Filter out None values from the list of converted matches
        converted_matches = [m for m in converted_matches if m is not None]
        
        if len(converted_matches) == 1:
            return converted_matches[0]
        elif len(converted_matches) > 1:
            return tuple(converted_matches)
        else:
            return None
    else:
        return None  # Return None if no matches are found
    

def capture_screen_with_display(top, left, width, height, fx=1, fy=1):  

    with mss.mss() as sct:
        monitor = {"top": top, "left": left, "width": width, "height": height}
        
        img = sct.grab(monitor)
        img = np.array(img)  # Convert to NumPy array
        #img = cv.cvtColor(img, cv.COLOR_RGB2BGR)  # Convert RGB to BGR color
        # cv.imshow("vision",img)
        # cv.waitKey(0)
            
        image = cv.resize(img, (0, 0), fx=fx, fy=fy)
        # cv.imshow("Computer Vision", image)
        return image

        

def GetStatus(coordinates: Dict[str, int],return_type = "digits",threshold_min = 220):
    
    scale_factor = 0.5  # Define the scale factor (0.5 for half size, 2 for double size)

    start_time = time.time()
    frame_count = 0

    # Extract coordinates from the dictionary
    top = coordinates["top"]
    left = coordinates["left"]
    width = coordinates["width"]
    height = coordinates["height"]

    try:
        #while True:
           
            
            image_path_1 = capture_screen_with_display(top,left,width,height)
            
                        
            if image_path_1 is not None:
                # Extract and print text from the images
                line = extract_text_from_image(image_path_1,threshold_min)
                ##print("Extracted text from cropped image:")
                if(return_type == "digits"):
                 #print(line)#print the extrcted text 
                 result = extract_numbers(line) #extract the digits from the text  
                 #print(result)   
                elif return_type == "text":
                 result = line
                 #print(result)# print text result
                 
                return result
                

            #cv.imshow('Screenshot', screenshot_cv)
            
            
            # if cv.waitKey(1) & 0xFF == ord('z'):  # Exit loop on 'q' key press
            #     break

            # Print frames per second (FPS) every second
            frame_count += 1
            if time.time() - start_time >= 1:
                #print(f"FPS: {frame_count}")
                start_time = time.time()
                frame_count = 0
                

    finally:
        cv.destroyAllWindows()


