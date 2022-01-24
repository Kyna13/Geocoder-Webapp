from flask import Flask, request, render_template, send_file
from werkzeug.utils import secure_filename
import pandas
import geopy
from geopy.geocoders import ArcGIS
import datetime

app = Flask(__name__)

@app.route('/')
def home():
    return render_template("index.html", btn = "", content = {}, error = "")

@app.route('/success', methods=["GET", "POST"])
def success():
    global file
    global filename
    error = ""
    file_text = ""
    content = {}
    if request.method == "POST":
        try:
            file = request.files["file_input"]
            file.save(secure_filename(file.filename))
            df=pandas.read_csv(file.filename, sep = ",")
            if "Address" in df.columns:
                # This is where the lat and long column will be added.
                nom = ArcGIS()
                df["Latitude"] = df["Address"].apply(nom.geocode).apply(lambda x: x.latitude if x != None else None)
                df["Longitude"] = df["Address"].apply(nom.geocode).apply(lambda x: x.longitude if x != None else None)

                df_t = df.T
                columns = list()
                df_t.columns = df_t.iloc[0]

                content["Index"] = list(df_t.index)

                for column in df_t.columns:
                    content[column] = list(df_t[column])

                df_t.drop("ID", axis=0, inplace=True)
                filename = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S-%f") +".csv"
                df_t.to_csv(filename, index=True)
                return render_template("index.html", btn = "Download", content = content, error = error)
            else:
                error = "Seems like you don't have an Address column. Please try adding the column and try again."
                return render_template("index.html", btn = "", content = {}, error = error)
        except:
            return render_template("index.html", btn = "", content = {}, error = "There was an error. Please make sure you are uploading a valid .csv file.")

@app.route('/download', methods=["GET", "POST"])
def download():
    return send_file(filename, attachment_filename = filename, as_attachment=True)

if __name__ == "__main__":
    app.debug = True
    app.run(threaded = True, port = 8000)
