from flask import Flask, request, render_template, jsonify
from PIL import Image, ExifTags
import piexif
import os

# Создаём экземпляр Flask
app = Flask(__name__)

# Папка для сохранения обработанных фотографий
SAVE_FOLDER = os.path.join(os.getcwd(), "ExifCopy")
if not os.path.exists(SAVE_FOLDER):
    os.makedirs(SAVE_FOLDER)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        return jsonify({"message": "Файлы загружены успешно!"})
    return render_template("index.html")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
