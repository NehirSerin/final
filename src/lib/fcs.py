from pipython import GCSDevice, pitools
from pypylon import pylon
import cv2
import numpy as np
from cmr import capture_single_image
import lib.cnf as cnf

config = cnf.load_config("../../config.json")

def move_to_focus(pidevice, camera, dz=0.005):
    """
    Function to find the sharpest image by moving the camera along the z-axis 
    and calculating the sharpness based on edge detection (Canny).

    Parameters:
    - pidevice: The device object to control the stage.
    - camera: The camera object to capture images.
    - dz: The step size for movement along the z-axis (default is 0.005).

    Returns:
    - best_focus: The z-axis position where the sharpest image was found.
    """
    sharpness_scores = []
    step_nums = np.arange(-10, 11)  # Step range from -10 to 10, inclusive

    # Get current z position
    current_z = pidevice.qPOS(AXES["z"])
    
    for step_num in step_nums:
        # Move the stage along the z-axis
        target_z = current_z + dz * step_num
        pidevice.MOV(AXES["z"], target_z)
        
        # Capture the image at the current z position
        img = capture_single_image(camera)
        
        # Ensure the image is grayscale (needed for Canny)
        if len(img.shape) == 3:  # If it's not grayscale, convert it
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Apply Canny edge detection to find sharpness
        edges = cv2.Canny(img, threshold1=100, threshold2=200)
        sharpness = np.sum(edges)  # Sum of edge pixel intensities
        sharpness_scores.append(sharpness)

    # Find the index of the maximum sharpness score
    best_index = np.argmax(sharpness_scores)
    best_focus = current_z + dz * step_nums[best_index]
    
    pidevice.MOV(AXES["z"], best_focus)  # Move to the best focus position    
