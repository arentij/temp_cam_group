import os
from flask import Flask, render_template, request, send_from_directory
from datetime import datetime, timedelta

app = Flask(__name__)

# Define the root directory for your external images
EXTERNAL_IMAGE_DIR = "/Users/arturperevalov/CMFX_RAW/video"  # Set this to your external image folder


@app.route("/", methods=["GET", "POST"])
def index():
    folder_number = "01212"  # Default folder number
    time_input = 0  # Default time in milliseconds since zero time

    if request.method == "POST":
        folder_number = request.form.get("folder_number", "01212")
        folder_number = folder_number.zfill(5)
        time_input = int(request.form.get("time_input", 0))  # Time input in milliseconds

    # Calculate time offset for each frame based on user input
    image_data = find_images_by_time(folder_number, time_input)

    return render_template("index.html", image_data=image_data, folder_number=folder_number, time_input=time_input)


def find_images_by_time_0(folder_number, time_input):
    base_folder = os.path.join(EXTERNAL_IMAGE_DIR, f"CMFX_{folder_number}")
    image_paths = []
    max_frames = 0
    first_frame_time = None

    # Store times for each folder and identify folder with the most frames
    folder_times = {}

    if os.path.exists(base_folder):
        # print(f"subfolders {os.listdir(base_folder)}")
        for subfolder in os.listdir(base_folder):

            subfolder_path = os.path.join(base_folder, subfolder)
            if not os.path.isdir(subfolder_path):
                continue
            # print(f'Subfolder path {subfolder_path}')

            txt_file = os.path.join(base_folder, f"{subfolder}.txt")

            # print(f"Txt file {txt_file}")
            # print(f"Txt exists {os.path.exists(txt_file)}")

            if os.path.isdir(subfolder_path) and subfolder.startswith("video") and os.path.exists(txt_file):
                # Check if the folder contains images
                # print(f"Files in folder {os.listdir(subfolder_path)}")
                images_exist = any(
                    fname.startswith("frame") and fname.endswith(".jpg") for fname in os.listdir(subfolder_path))

                if not images_exist:
                    print(f"No images in {subfolder_path}")
                    continue

                with open(txt_file, 'r') as f:
                    times = [datetime.strptime(line.strip(), "%Y-%m-%d %H:%M:%S.%f") for line in f.readlines()]
                    folder_times[subfolder] = times
                    # Check for the folder with the most frames
                    if len(times) > max_frames:
                        max_frames = len(times)
                        first_frame_time = times[0]

    # No valid frames
    if first_frame_time is None:
        return image_paths

    # Convert user input from milliseconds to a timedelta
    input_time_delta = timedelta(milliseconds=time_input)
    # print(f"input time delta {input_time_delta}")
    # Find and return frames close to the specified time
    for subfolder, times in folder_times.items():
        subfolder_path = os.path.join(base_folder, subfolder)
        for i, frame_time in enumerate(times):
            relative_time = frame_time - first_frame_time
            if relative_time >= input_time_delta:
                frame_filename = f"frame{i}.jpg"
                frame_path = os.path.join(subfolder_path, frame_filename)
                if os.path.exists(frame_path):
                    image_paths.append(f"/images/{folder_number}/{subfolder}/{frame_filename}")
                break  # Only add the first frame matching or exceeding the time

    return image_paths


def find_images_by_time(folder_number, time_input):
    base_folder = os.path.join(EXTERNAL_IMAGE_DIR, f"CMFX_{folder_number}")
    image_data = []
    max_frames = 0
    first_frame_time = None

    # Store times for each folder and identify folder with the most frames
    folder_times = {}

    if os.path.exists(base_folder):
        for subfolder in os.listdir(base_folder):
            subfolder_path = os.path.join(base_folder, subfolder)
            if not os.path.isdir(subfolder_path):
                continue
            # txt_file = os.path.join(subfolder_path, f"{base_folder}.txt")
            txt_file = os.path.join(base_folder, f"{subfolder}.txt")
            print(f"Txt file {txt_file}")
            print(f"exist= {os.path.exists(txt_file)}")
            if os.path.isdir(subfolder_path) and subfolder.startswith("video") and os.path.exists(txt_file):
                # Check if the folder contains images
                images_exist = any(
                    fname.startswith("frame") and fname.endswith(".jpg") for fname in os.listdir(subfolder_path))
                if not images_exist:
                    continue

                with open(txt_file, 'r') as f:
                    times = [datetime.strptime(line.strip(), "%Y-%m-%d %H:%M:%S.%f") for line in f.readlines()]
                    folder_times[subfolder] = times
                    # Check for the folder with the most frames
                    if len(times) > max_frames:
                        max_frames = len(times)
                        first_frame_time = times[0]

    # No valid frames
    if first_frame_time is None:
        return image_data
    print(True)
    # Convert user input from milliseconds to a timedelta
    input_time_delta = timedelta(milliseconds=time_input)

    # Find and return frames close to the specified time along with their relative time in ms
    for subfolder, times in folder_times.items():
        subfolder_path = os.path.join(base_folder, subfolder)
        for i, frame_time in enumerate(times):
            relative_time = frame_time - first_frame_time
            # print(f"Relative time {relative_time}, i={i}")
            print(f"Current time {frame_time-first_frame_time}")
            # if i > 0:
            #     print(f"Current time {(frame_time-first_frame_time).total_seconds()*1000}")
            #     print(f"Current time {(times[i]-first_frame_time).total_seconds()*1000}")
            #     # print(f"Current time {times[i]-first_frame_time}")

            if relative_time >= input_time_delta:
                adjusted_i = max(0, i-1)
                frame_filename = f"frame{adjusted_i}.jpg"
                frame_path = os.path.join(subfolder_path, frame_filename)
                if os.path.exists(frame_path):
                    relative_time = times[adjusted_i]-first_frame_time
                    relative_time_ms = int(relative_time.total_seconds() * 1000)  # Convert to milliseconds
                    image_data.append({
                        "image_path": f"/images/{folder_number}/{subfolder}/{frame_filename}",
                        "time_in_ms": relative_time_ms
                    })
                break  # Only add the first frame matching or exceeding the time
    print(f"imge data {image_data}")
    return image_data


@app.route("/images/<folder_number>/<subfolder>/<filename>")
def serve_image(folder_number, subfolder, filename):
    image_directory = os.path.join(EXTERNAL_IMAGE_DIR, f"CMFX_{folder_number}", subfolder)
    print(f"Image directory {image_directory}, filename {filename}")
    return send_from_directory(image_directory, filename)

# def serve_image(folder_number, subfolder, filename):
#     image_directory = os.path.join(EXTERNAL_IMAGE_DIR, f"CMFX_{folder_number}", subfolder)
#     return send_from_directory(image_directory, filename)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)
