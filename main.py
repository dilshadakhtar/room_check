import streamlit as st
import requests
import json
from PIL import Image
import time


def upload_image(image_file):
    """
    Uploads an image to Cloudinary and returns the public URL of the uploaded image.

    :param image_file: The image file to be uploaded.
    :return: The public URL of the uploaded image.
    """
    try:
        # Return the secure URL of the uploaded image
        image_file.save("uploaded.png")
        print("Image Uploaded")
        return image_file
    except Exception as e:
        print(f"An error occurred during the image upload: {e}")
        return None

# Streamlit UI
st.title("Room Customizer App")
st.write("Upload an image of your room and customize the wall color and flooring!")

# Image upload
uploaded_file = st.file_uploader("Choose an image of your room (PNG or JPG only)", type=["png", "jpg", "jpeg"])

# Input wall color and flooring type
wall_color = st.text_input("Enter the desired wall color", "white")
floor_type = st.text_input("Enter the desired flooring type", "wooden")

# Only proceed if the user has uploaded an image
if uploaded_file is not None:
    # Display the uploaded image
    image = Image.open(uploaded_file)
    st.image(image, caption='Uploaded Room Image', use_column_width=True)

    # Upload the image to get a publicly accessible URL
    image_url = upload_image(uploaded_file)
    print(image_url)
    # Generate modified image on button click
    if st.button("Modify Room") and image_url:
        api = st.text_input("Enter the API Key:")
        st.write("Processing... Please wait.")

        # Payload for API request
        payload = json.dumps({
            "key": api,
            "prompt": f"A bedroom with {wall_color} walls and {floor_type} flooring, photorealistic, detailed, high quality. Keep all other details of the room exactly the same.",
            "negative_prompt": "ugly, blurry, low quality, distorted, deformed",
            "init_image": image_url,  # Use the URL of the uploaded image
            "seed": 0,
            "guidance_scale": 8,
            "strength": 0.3,
            "num_inference_steps": 51,
            "base64": False,
            "temp": False,
            "webhook": None,
            "track_id": None
        })

        # API headers
        headers = {
            'Content-Type': 'application/json'
        }

        # Send request to the API
        response = requests.post("https://modelslab.com/api/v6/interior/make", headers=headers, data=payload)
        print(response.text)
        # Check if the response is successful
        if response.status_code == 200:
            result = response.json()
            track_id = result.get('track_id')

            # Polling for the status to be 'success'
            status_url = f"https://modelslab.com/api/v6/status/{track_id}"
            while True:
                status_response = requests.get(status_url)
                print(status_response)
                status_result = status_response.json()
                status = status_result.get('status')
                print(status)

                if status == 'success':
                    image_url = status_result['output'][0]
                    break
                elif status == 'failed':
                    st.error("Image generation failed. Please try again.")
                    break
                else:
                    time.sleep(5)  # Wait for 5 seconds before checking again

            # Display the modified image
            st.image(image_url, caption='Modified Room Image', use_column_width=True)
        else:
            st.error("There was an issue with the image modification process. Please try again.")
