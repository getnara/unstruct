import os
import uuid
import ssl
import certifi

# Configure SSL context to use certifi's certificates
ssl_context = ssl.create_default_context(cafile=certifi.where())
ssl._create_default_https_context = lambda: ssl_context

import numpy as np
from langchain_community.vectorstores import LanceDB

from langchain_experimental.open_clip import OpenCLIPEmbeddings
from PIL import Image as _PILImage

import base64
import io
from io import BytesIO

import numpy as np
from PIL import Image

from moviepy.editor import VideoFileClip
from functools import lru_cache
from pdf2image import convert_from_path
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader


def resize_base64_image(base64_string, size=(128, 128)):
    """
    Resize an image encoded as a Base64 string.

    Args:
    base64_string (str): Base64 string of the original image.
    size (tuple): Desired size of the image as (width, height).

    Returns:
    str: Base64 string of the resized image.
    """
    # Decode the Base64 string
    img_data = base64.b64decode(base64_string)
    img = Image.open(io.BytesIO(img_data))

    # Resize the image
    resized_img = img.resize(size, Image.LANCZOS)

    # Save the resized image to a bytes buffer
    buffered = io.BytesIO()
    resized_img.save(buffered, format=img.format)

    # Encode the resized image to Base64
    return base64.b64encode(buffered.getvalue()).decode("utf-8")


def is_base64(s):
    """Check if a string is Base64 encoded"""
    try:
        return base64.b64encode(base64.b64decode(s)) == s.encode()
    except Exception:
        return False


def split_image_text_types(docs):
    if docs is None:
        return {{"images": [], "texts": ""}}
    """Split numpy array images and texts"""
    images = []
    text = []
    for doc in docs:
        doc = doc.page_content  # Extract Document contents
        if is_base64(doc):
            # Resize image to avoid OAI server error
            images.append(
                doc#resize_base64_image(doc, size=(250, 250))
            )  # base64 encoded str
        else:
            text.append(doc)
    return {"images": images, "texts": text}

clip_embd = OpenCLIPEmbeddings(model_name="ViT-B-32", checkpoint="openai")


import cv2
import os

def get_images_from_video(video_path, output_dir='/tmp'):
    """
    Extracts frames from a video, saves them as JPEG files in the specified directory,
    and returns a list of the saved file paths.

    :param video_path: Path to the input video file.
    :param output_dir: Directory where frames will be saved. Defaults to '/tmp'.
    :return: List of file paths to the saved frames.
    """
    # Create the output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Initialize video capture
    video = cv2.VideoCapture(video_path)
    
    if not video.isOpened():
        raise IOError(f"Cannot open video file {video_path}")
    
    frame_paths = []
    frame_count = 0
    name = os.path.basename(video_path)
   
    while True:
        success, frame = video.read()
        if not success:
            break  # Exit loop if no frame is returned
        
        # Construct the filename with zero-padded frame number
        frame_filename = os.path.join(output_dir, f"{name}_frame_{frame_count:05d}.jpg")
        
        # Save the frame as a JPEG file
        cv2.imwrite(frame_filename, frame)
        
        # Append the file path to the list
        frame_paths.append(frame_filename)
        
        frame_count += 1
    
    # Release the video capture object
    video.release()
    
    print(f"{frame_count} frames saved to {output_dir}.")
    return frame_paths

@lru_cache(maxsize=None)
def get_audio_from_video(video_path,  output_dir='/tmp'):
    name = os.path.basename(video_path)
    mp3_file = os.path.join(output_dir, f"{name}.mp3")

    # Load the video clip
    video_clip = VideoFileClip(video_path)

    # Extract the audio from the video clip
    audio_clip = video_clip.audio

    # Write the audio to a separate file
    try:
        audio_clip.write_audiofile(mp3_file)

        # Close the video and audio clips
        audio_clip.close()
    except:
        pass
    video_clip.close()

    print("Audio extraction successful!")
    return mp3_file
# Create chroma

def get_images_from_document(doc_path,  output_dir='/tmp'):
    images = convert_from_path(doc_path)
    if not images or len(images) == 0:
        return []
    

    name = os.path.basename(doc_path)

    frame_paths = []
    for i, image in enumerate(images):
        image_filename =  os.path.join(output_dir, f"{name}_frame_{i:05d}.jpg")
        print(image_filename)
    
        image.save(image_filename)
    
    # Append the file path to the list
        frame_paths.append(image_filename)
    
    return frame_paths


import os

from deepgram import (
    DeepgramClient,
    PrerecordedOptions,
)


DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")
# URL to the audio file
# main.py (python example)

import os

from deepgram import (
    DeepgramClient,
    PrerecordedOptions,
    FileSource,
)



@lru_cache(maxsize=None)
def transcribe(audio_file):
    try:
        # STEP 1 Create a Deepgram client using the API key
        deepgram = DeepgramClient(DEEPGRAM_API_KEY)

        with open(audio_file, "rb") as file:
            buffer_data = file.read()

        payload: FileSource = {
            "buffer": buffer_data,
        }

        #STEP 2: Configure Deepgram options for audio analysis
        options = PrerecordedOptions(
            model="nova-2",
            smart_format=True,
        )

        # STEP 3: Call the transcribe_file method with the text payload and options
        response = deepgram.listen.prerecorded.v("1").transcribe_file(payload, options)

        # STEP 4: Print the response
        transcript = response.results.channels[0].alternatives[0].transcript
        return transcript
        

    except Exception as e:
        print(f"Exception: {e}")
    return ""




class VectorStore:
    def __init__(self, name, video_path=None, image_only=False) -> None:
        self.indexed_image = False
        self.indexed_text = False
        self.transcript = ""
    
        self.image_vectorstore = LanceDB(
            table_name=name, embedding=clip_embd,
            uri="/tmp/vdb_images"
        )

        self.text_vectorstore =  LanceDB(
            table_name=name, embedding=clip_embd,
            uri="/tmp/vdb_texts"
        )
        if self.image_vectorstore.get_table(name):
            self.indexed_image = True
        if self.text_vectorstore.get_table(name):
            self.indexed_text = True
        if image_only and self.image_vectorstore.get_table(name):
            self.indexed_image = True
        

    def index_video(self, video_path):
        if self.indexed_image and self.indexed_text:
            print("already indexed", video_path)
            return
        images = get_images_from_video(video_path=video_path)
        audio_file = get_audio_from_video(video_path)
        self.transcript  = transcribe(audio_file)
        
        if not self.indexed_image:
            try:
                self.image_vectorstore.delete(delete_all=True)
            except:
                pass
            self.image_vectorstore.add_images(images)
            self.indexed_image = True
        
        if not self.indexed_text:
            self.text_vectorstore.add_texts([self.transcript])
            self.indexed_text = True

    def index_audio(self, audio_path):
        if self.indexed_text:
            print("already indexed", audio_path)
            return
        
        self.transcript  = transcribe(audio_path)
        if not self.indexed_text:
            self.text_vectorstore.add_texts([self.transcript])
            self.indexed_text = True

    def index_images(self, images):
        if not self.indexed_image:
            try:
                self.image_vectorstore.delete(delete_all=True)
            except:
                pass
            self.image_vectorstore.add_images(images)
            self.indexed_image = True

    def index_document(self, doc_path):
        error = None
        if self.indexed_image and self.indexed_text:
            print("already indexed", doc_path)
            return
        try:
            images = get_images_from_document(doc_path=doc_path)
            if not self.indexed_image:
                try:
                    self.image_vectorstore.delete(delete_all=True)
                except:
                    pass
                self.image_vectorstore.add_images(images)
                self.indexed_image = True
        except:
            error = True

        try:
            loader = PyPDFLoader(doc_path)

            docs = loader.load()
            print(len(docs))

            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
            splits = text_splitter.split_documents(docs)
            if not self.indexed_text:
                self.text_vectorstore.add_documents(
                    documents=splits
                )
                self.indexed_text = True
        except:
            error = True
        if not error:
            self.indexed_image = True
            self.indexed_text = True

    def invoke(self, query, k=10):
        data = {
            'images': [],
            'texts': []
        }
        try:
            results =  self.image_vectorstore.as_retriever().invoke(query, k=k)
            data = split_image_text_types(results)
        except:
            pass
        try:
            text_data = self.text_vectorstore.as_retriever().invoke(query, k=k)
            texts = [t.page_content for t in text_data]

            data['texts'] = texts
        except:
            pass
        return data