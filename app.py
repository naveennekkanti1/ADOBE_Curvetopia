import os
from flask import Flask, render_template, request, send_from_directory, redirect, url_for
import numpy as np
import matplotlib.pyplot as plt

app = Flask(__name__)

# Ensure that these folders exist and have the right permissions on your server
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['PROCESSED_FOLDER'] = 'static/processed'

# Create folders if they do not exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['PROCESSED_FOLDER'], exist_ok=True)

# Function to read CSV and return paths
def read_csv(csv_path):
    np_path_XYs = np.genfromtxt(csv_path, delimiter=',')
    path_XYs = []

    for i in np.unique(np_path_XYs[:, 0]):
        npXYs = np_path_XYs[np_path_XYs[:, 0] == i][:, 1:]
        XYs = []

        for j in np.unique(npXYs[:, 0]):
            XY = npXYs[npXYs[:, 0] == j][:, 1:]
            XYs.append(XY)

        path_XYs.append(XYs)

    return path_XYs

# Placeholder function for processing (including symmetry)
def process_curves(paths_XYs, process_type):
    if process_type == "symmetry":
        return explore_symmetry(paths_XYs)
    elif process_type == "regularize":
        return regularize_curves(paths_XYs)
    elif process_type == "complete":
        return complete_curves(paths_XYs)
    else:
        return paths_XYs

def explore_symmetry(paths_XYs):
    # Example symmetry logic (flipping over the y-axis)
    symmetrical_paths = []
    for path in paths_XYs:
        symmetrical_path = []
        for XY in path:
            symmetrical_XY = np.copy(XY)
            symmetrical_XY[:, 0] = -symmetrical_XY[:, 0]  # Flip over y-axis
            symmetrical_path.append(symmetrical_XY)
        symmetrical_paths.append(symmetrical_path)
    return symmetrical_paths

def regularize_curves(paths_XYs):
    # Placeholder for regularization logic
    return paths_XYs

def complete_curves(paths_XYs):
    # Placeholder for curve completion logic
    return paths_XYs

# Function to save processed curves to a CSV
def save_csv(paths_XYs, output_path):
    rows = []
    for i, path_XYs in enumerate(paths_XYs):
        for j, XY in enumerate(path_XYs):
            for k, point in enumerate(XY):
                rows.append([i, j, k, point[0], point[1]])

    np.savetxt(output_path, rows, delimiter=',', fmt='%d,%d,%d,%f,%f')

# Function to plot and save the curves as an image
def plot_curves(paths_XYs, filename):
    plt.figure(figsize=(10, 10))
    for path_XYs in paths_XYs:
        for XY in path_XYs:
            plt.plot(XY[:, 0], XY[:, 1], 'k-', linewidth=2)  # 'k-' is for black color
    
    img_path = os.path.join(app.config['PROCESSED_FOLDER'], f'{filename}.png')
    plt.savefig(img_path)
    plt.close()
    return img_path

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            return 'No file part'
        file = request.files['file']
        if file.filename == '':
            return 'No selected file'
        if file:
            filename = file.filename
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            # Read the uploaded file
            paths_XYs = read_csv(file_path)

            # Process curves based on user selection
            process_type = request.form['process_type']
            processed_paths = process_curves(paths_XYs, process_type)

            # Save processed file
            output_filename = f"{os.path.splitext(filename)[0]}_sol.csv"
            output_path = os.path.join(app.config['PROCESSED_FOLDER'], output_filename)
            save_csv(processed_paths, output_path)

            # Determine the image filename based on the process type
            if process_type == "symmetry":
                image_filename = f"{os.path.splitext(filename)[0]}_aftersymmetry"
            else:
                image_filename = f"{os.path.splitext(filename)[0]}_sol"
                
            # Plot and save the processed curves
            plot_image_path = plot_curves(processed_paths, image_filename)

            # Redirect to the index with query parameters to avoid resubmitting the form
            return redirect(url_for('index', processed_file=output_filename, plot_image=os.path.basename(plot_image_path)))

    return render_template('index.html', processed_file=request.args.get('processed_file'), plot_image=request.args.get('plot_image'))

@app.route('/processed/<filename>')
def processed_file(filename):
    return send_from_directory(app.config['PROCESSED_FOLDER'], filename)

@app.route('/processed_image/<filename>')
def processed_image(filename):
    return send_from_directory(app.config['PROCESSED_FOLDER'], filename)

if __name__ == '__main__':
    app.run()
