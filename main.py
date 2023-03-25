# pip install fastapi uvicorn opencv-python-headless numpy dlib face-recognition pytesseract Pillow python-multipart requests


import urllib.request
from urllib.request import urlretrieve
import uvicorn
from fastapi import FastAPI, File, Form, Request, UploadFile
import face_recognition
import os
import numpy as np
import cv2
import pytesseract
from PIL import Image
import requests
from io import BytesIO
import fcntl

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
            fcntl.flock(f, fcntl.LOCK_EX)  # create an exclusive lock
            try:
                encoding_str = ",".join(str(val) for val in face_encoding)
                f.write(label + "," + encoding_str + "\n")
                f.flush()  # flush the buffer to ensure the write is complete
                os.fsync(f.fileno())  # sync the file to disk
            finally:
                fcntl.flock(f, fcntl.LOCK_UN)  # release the lock
        return {
            "code": 200,
            "message": "Face learned and saved to file successfully",
        }
    else:
        return {
            "code": 400,
            "message": "Could not find a single face in the image"
        }

# curl --location --request POST 'http://localhost:8000/learn-face-v2' \
# --header 'Content-Type: application/json' \
# --data-raw '{
#     "image_url": "https://scontent.frgn4-1.fna.fbcdn.net/v/t39.30808-1/297797132_3059369084354358_5333256072745780839_n.jpg?stp=dst-jpg_p200x200&_nc_cat=109&ccb=1-7&_nc_sid=7206a8&_nc_ohc=V0aQpuSu40kAX_ycdec&_nc_ht=scontent.frgn4-1.fna&oh=00_AfAHoCmE5AAc2oXMncLp8TZS8DuPsJ6wM-dkNnhnTGnB-w&oe=641F4E3C",
#     "label": "HLM"
# }'
# axios.post('http://localhost:8000/learn-face', {
#     image_url: 'https://example.com/image.jpg',
#     label: 'John Doe'
# })
# .then(response => {
#     console.log(response.data);
# })
# .catch(error => {
#     console.error(error);
# });


@app.post("/learn-face-v2")
async def learn_face_v2(request: Request):
    data = await request.json()
    image_url = data.get("image_url")
    label = data.get("label")

    # Download the image from URL and convert it to a numpy array
    response = requests.get(image_url)
    np_array = np.frombuffer(response.content, np.uint8)
    image = cv2.imdecode(np_array, cv2.IMREAD_COLOR)

    # Find the face in the image and learn it
    face_locations = face_recognition.face_locations(image)
    if len(face_locations) == 1:
        face_encoding = face_recognition.face_encodings(
            image, face_locations)[0]
        # Save the face encoding with label to a file
        file_path = os.path.join(os.getcwd(), "face_encodings.txt")
        with open(file_path, "a") as f:
            fcntl.flock(f, fcntl.LOCK_EX)  # create an exclusive lock
            try:
                encoding_str = ",".join(str(val) for val in face_encoding)
                f.write(label + "," + encoding_str + "\n")
                f.flush()  # flush the buffer to ensure the write is complete
                os.fsync(f.fileno())  # sync the file to disk
            finally:
                fcntl.flock(f, fcntl.LOCK_UN)  # release the lock
        return {
            "code": 200,
            "message": "Face learned and saved to file successfully",
        }
    else:
        return {
            "code": 400,
            "message": "Could not find a single face in the image"
        }

# curl -X POST \
#   http://localhost:8000/learn-faces-v2 \
#   -H 'Content-Type: application/json' \
#   -d '{
#     "face_data": [
#         {
#             "image_url": "https://example.com/image1.jpg",
#             "label": "John"
#         },
#         {
#             "image_url": "https://example.com/image2.jpg",
#             "label": "Jane"
#         }
#     ]
# }'

# import axios from 'axios';

# const apiUrl = 'http://localhost:8000/learn-faces-v2';

# const faceData = [
#   {
#     image_url: 'https://example.com/image1.jpg',
#     label: 'John'
#   },
#   {
#     image_url: 'https://example.com/image2.jpg',
#     label: 'Jane'
#   }
# ];

# axios.post(apiUrl, { face_data: faceData })
#   .then(response => console.log(response.data))
#   .catch(error => console.error(error));


@app.post("/learn-faces-v2")
async def learn_faces_v2(request: Request):
    data = await request.json()
    face_data = data.get("face_data")

    message = ''
    for face in face_data:
        try:
            image_url = face.get("image_url")
            label = face.get("label")

            # Download the image from URL and convert it to a numpy array
            response = requests.get(image_url)
            np_array = np.frombuffer(response.content, np.uint8)
            image = cv2.imdecode(np_array, cv2.IMREAD_COLOR)

            # Find the face in the image and learn it
            face_locations = face_recognition.face_locations(image)
            if len(face_locations) == 1:
                face_encoding = face_recognition.face_encodings(
                    image, face_locations)[0]
                # Save the face encoding with label to a file
                file_path = os.path.join(os.getcwd(), "face_encodings.txt")
                with open(file_path, "a") as f:
                    fcntl.flock(f, fcntl.LOCK_EX)  # create an exclusive lock
                    try:
                        encoding_str = ",".join(str(val)
                                                for val in face_encoding)
                        f.write(label + "," + encoding_str + "\n")
                        f.flush()  # flush the buffer to ensure the write is complete
                        os.fsync(f.fileno())  # sync the file to disk
                    finally:
                        fcntl.flock(f, fcntl.LOCK_UN)  # release the lock
            else:
                message += f"Could not find a single face in the image with URL {image_url}\n"
                print(message)  # You can print the message for debug purposes.
        except Exception as e:
            message += f"Error processing image with URL {image_url}: {str(e)}\n"
            print(message)  # You can print the message for debug purposes.

    return {
        "code": 200,
        "message": f"{message}Faces learned and saved to file successfully",
    }


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

        # Load previously saved face encodings and labels
        encodings_path = os.path.join(os.getcwd(), "face_encodings.txt")
        with open(encodings_path, "r") as f:
            face_encodings = []
            face_labels = []
            for line in f:
                parts = line.strip().split(",")
                face_labels.append(parts[0])
                face_encodings.append(np.array(parts[1:], dtype=float))

        # Find the closest match in the saved encodings and return the label
        matches = face_recognition.compare_faces(face_encodings, face_encoding)
        index = np.argwhere(matches).flatten()
        if len(index) > 0:
            label = face_labels[index[0]]
            return {"code": 200, "message": "Face matched successfully", "label": label}
        else:
            return {"code": 400, "message": "Could not match the face to any saved encoding"}
    else:
        return {"code": 400, "message": "Could not find a single face in the image"}


@app.post("/match-face-v2")
async def match_face_v2(request: Request):
    data = await request.json()
    image_url = data.get("image_url")

    # Download the image from URL and convert it to a numpy array
    response = requests.get(image_url)
    np_array = np.frombuffer(response.content, np.uint8)
    image = cv2.imdecode(np_array, cv2.IMREAD_COLOR)

    # Find the face in the image and encode it
    face_locations = face_recognition.face_locations(image)
    if len(face_locations) == 1:
        face_encoding = face_recognition.face_encodings(
            image, face_locations)[0]

        # Load previously saved face encodings and labels
        encodings_path = os.path.join(os.getcwd(), "face_encodings.txt")
        with open(encodings_path, "r") as f:
            face_encodings = []
            face_labels = []
            for line in f:
                parts = line.strip().split(",")
                face_labels.append(parts[0])
                face_encodings.append(np.array(parts[1:], dtype=float))

        # Find the closest match in the saved encodings and return the label
        matches = face_recognition.compare_faces(face_encodings, face_encoding)
        index = np.argwhere(matches).flatten()
        if len(index) > 0:
            label = face_labels[index[0]]
            return {"code": 200, "message": "Face matched successfully", "label": label}
        else:
            return {"code": 400, "message": "Could not match the face to any saved encoding"}
    else:
        return {"code": 400, "message": "Could not find a single face in the image"}


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
