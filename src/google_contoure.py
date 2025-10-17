import cv2

# 1. Read and Preprocess the Image
image = cv2.imread(r'.\dora_24pieces\0_photos\20251012_1.jpg')
gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
_, thresh_image = cv2.threshold(gray_image, 127, 255, cv2.THRESH_BINARY) # Adjust threshold values as needed

# 2. Find Contours
contours, hierarchy = cv2.findContours(thresh_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# 3. Draw Contours
output_image = image.copy() # Create a copy to draw on
cv2.drawContours(output_image, contours, -1, (0, 255, 0), 2) # Draw all contours in green with thickness 2

# 4. Save the output image
output_filename = 'outlined_objects.jpg'
cv2.imwrite(output_filename, output_image)
print(f"Image with contours saved as '{output_filename}'")
