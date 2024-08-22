from flask import Flask, render_template, request, redirect, url_for
import os
import glob

app = Flask(__name__, static_url_path='/static')


def process_data(filename):
    # This function should contain the logic to process the CSV file
    # and create the necessary folder and images
    print(f"Processing data from {filename}...")
    # Example: Create the folder and add dummy images
    base_folder = filename.replace('_spectrometer.csv', '')
    os.makedirs(base_folder, exist_ok=True)
    # For demonstration, create dummy images
    for i in range(5):
        with open(os.path.join(base_folder, f'frame{i}.jpg'), 'w') as f:
            f.write('')  # Replace with actual image generation logic


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        folder_number = request.form['folder_number']
        return redirect(url_for('view_images', folder_number=folder_number, image_index=0))
    return '''
        <form method="post">
            Enter folder number: <input type="text" name="folder_number">
            <input type="submit" value="Submit">
        </form>
    '''


@app.route('/view/<folder_number>/<int:image_index>')
def view_images(folder_number, image_index):
    base_folder = f'spectrometer/CMFX_{folder_number.zfill(5)}'

    # If folder does not exist, process the corresponding CSV file
    if not os.path.exists(base_folder):
        csv_filename = f'CMFX_{folder_number.zfill(5)}_spectrometer.csv'
        csv_filepath = os.path.join('/spectrometer', csv_filename)

        if os.path.exists(csv_filepath):
            process_data(csv_filepath)
        else:
            return f"CSV file {csv_filepath} not found. Cannot process data."

    # Get list of image files sorted alphabetically
    image_files = sorted(glob.glob(os.path.join(base_folder, '*.jpg')))

    if not image_files:
        return f"No images found in {base_folder}."

    # Ensure the image_index is within range
    image_index = max(0, min(image_index, len(image_files) - 1))
    image_file = image_files[image_index]

    return render_template('view.html', image_file=image_file, folder_number=folder_number, image_index=image_index,
                           total_images=len(image_files))


if __name__ == '__main__':
    # app.run(debug=False)
    app.run(host='0.0.0.0', port=80)
