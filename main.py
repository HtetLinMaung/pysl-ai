# pip install fastapi uvicorn opencv-python-headless numpy dlib face-recognition pytesseract Pillow python-multipart requests
# https://scontent.frgn4-1.fna.fbcdn.net/v/t39.30808-1/297797132_3059369084354358_5333256072745780839_n.jpg?stp=dst-jpg_p200x200&_nc_cat=109&ccb=1-7&_nc_sid=7206a8&_nc_ohc=V0aQpuSu40kAX_ycdec&_nc_ht=scontent.frgn4-1.fna&oh=00_AfAHoCmE5AAc2oXMncLp8TZS8DuPsJ6wM-dkNnhnTGnB-w&oe=641F4E3C

from urllib.request import urlretrieve
import uvicorn
from fastapi import FastAPI, File, Form, UploadFile
import face_recognition
import os
import numpy as np
import cv2
import pytesseract
from PIL import Image
import requests
from io import BytesIO

app = FastAPI()


# curl - X POST - H "Content-Type: multipart/form-data" \
#     - F "file=@/home/user/Downloads/profile.jpg" \
#     - F "label=HLM" \
#     "http://localhost:8000/learn-face"
# const axios = require('axios');

# const formData = new FormData();
# formData.append('file', imageFile);
# formData.append('label', 'John');

# axios.post('http://localhost:8000/learn-face', formData, {
#   headers: {
#     'Content-Type': 'multipart/form-data'
#   }
# })
# .then((response) => {
#   console.log(response.data);
# })
# .catch((error) => {
#   console.log(error);
# });


@app.post("/learn-face")
async def learn_face(file: UploadFile = File(...), label: str = Form(...)):
    # Read the image file and convert it to a numpy array
    contents = await file.read()
    np_array = np.fromstring(contents, np.uint8)
    image = cv2.imdecode(np_array, cv2.IMREAD_COLOR)

    # Find the face in the image and learn it
    face_locations = face_recognition.face_locations(image)
    if len(face_locations) == 1:
        face_encoding = face_recognition.face_encodings(
            image, face_locations)[0]
        # Save the face encoding with label to a file
        file_path = os.path.join(os.getcwd(), "face_encodings.txt")
        with open(file_path, "a") as f:
            encoding_str = ",".join(str(val) for val in face_encoding)
            f.write(label + "," + encoding_str + "\n")
        return {
            "code": 200,
            "message": "Face learned and saved to file successfully",
        }
    else:
        return {
            "code": 500,
            "message": "Could not find a single face in the image"
        }


# curl -X POST -H "Content-Type: application/json" -d '{"url": "https://example.com/image.jpg"}' http://localhost:8000/learn-face-v2
# axios.post('http://localhost:8000/learn-face-v2', {
#   "url": "https://example.com/image.jpg"
# })
# .then(response => {
#   console.log(response.data);
# })
# .catch(error => {
#   console.error(error);
# });


@app.post("/learn-face-v2")
async def learn_face(url: str):
    # Download the image from the URL and convert it to a numpy array
    image_file, _ = urlretrieve(url)
    image = cv2.imread(image_file)

    # Find the face in the image and learn it
    face_locations = face_recognition.face_locations(image)
    if len(face_locations) == 1:
        face_encoding = face_recognition.face_encodings(
            image, face_locations)[0]
        # Save the face encoding to a file
        file_path = os.path.join(os.getcwd(), "face_encodings.txt")
        with open(file_path, "a") as f:
            encoding_str = ",".join(str(val) for val in face_encoding)
            f.write(encoding_str + "\n")
        return {"message": "Face learned and saved to file successfully"}
    else:
        return {"error": "Could not find a single face in the image"}

# curl -X POST -F "file=@/path/to/image.jpg" http://localhost:8000/match-face
# function matchFace(file) {
#   const formData = new FormData();
#   formData.append('file', file);
#   return axios.post('http://localhost:8000/match-face', formData, {
#     headers: {
#       'Content-Type': 'multipart/form-data'
#     }
#   });
# }


@app.post("/match-face")
async def match_face(file: UploadFile = File(...)):
    # Read the image file and convert it to a numpy array
    contents = await file.read()
    np_array = np.fromstring(contents, np.uint8)
    image = cv2.imdecode(np_array, cv2.IMREAD_COLOR)

    # Find the face in the image and encode it
    face_locations = face_recognition.face_locations(image)
    if len(face_locations) == 1:
        face_encoding = face_recognition.face_encodings(
            image, face_locations)[0]
    else:
        return {"error": "Could not find a single face in the image"}

    # Load saved face encodings and their labels from file
    file_path = os.path.join(os.getcwd(), "face_encodings.txt")
    with open(file_path, "r") as f:
        saved_encodings = f.read().splitlines()

    # Extract labels and face encodings from saved encodings
    labels, encodings = [], []
    for encoding_str in saved_encodings:
        label, encoding = encoding_str.split(":")
        labels.append(label)
        encoding_arr = np.fromstring(encoding, sep=",")
        encodings.append(encoding_arr)

    # Compare face encoding to saved encodings
    matches = face_recognition.compare_faces(encodings, face_encoding)

    if True in matches:
        # Get the label associated with the matched encoding
        matched_label = labels[matches.index(True)]
        return {"message": f"Face matched successfully with label {matched_label}"}
    else:
        return {"error": "Could not match the face to any saved encodings"}


@app.post("/match-face-v2")
async def match_face(url: str):
   # Download the image from the URL and convert it to a numpy array
    image_file, _ = urlretrieve(url)
    image = cv2.imread(image_file)

    # Find the face in the image and encode it
    face_locations = face_recognition.face_locations(image)
    if len(face_locations) == 1:
        face_encoding = face_recognition.face_encodings(
            image, face_locations)[0]
    else:
        return {"error": "Could not find a single face in the image"}

    # Load saved face encodings from file
    file_path = os.path.join(os.getcwd(), "face_encodings.txt")
    with open(file_path, "r") as f:
        saved_encodings = f.read().splitlines()

    # Convert saved encodings to numpy arrays
    saved_encodings = [np.fromstring(encoding, sep=",")
                       for encoding in saved_encodings]

    # Compare face encoding to saved encodings
    matches = face_recognition.compare_faces(saved_encodings, face_encoding)

    if True in matches:
        return {"message": "Face matched successfully"}
    else:
        return {"error": "Could not match the face to any saved encodings"}


def extract_text(image):
    text = pytesseract.image_to_string(image)
    return text


@app.post("/extract-text")
async def extract_text_api(image: UploadFile = File(...)):
    with Image.open(image.file) as img:
        text = extract_text(img)
    return {"text": text}


def extract_text(image):
    text = pytesseract.image_to_string(image)
    return text


@app.post("/extract-text-v2")
async def extract_text_api(image_url: str):
    response = requests.get(image_url)
    image = Image.open(BytesIO(response.content))
    text = extract_text(image)
    return {"text": text}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
