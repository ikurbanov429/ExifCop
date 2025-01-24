from flask import Flask, request, render_template, jsonify
from PIL import Image, ExifTags
import piexif
import os

app = Flask(__name__)

# Папка для сохранения обработанных фотографий
SAVE_FOLDER = "/storage/emulated/0/ExifCopy"
if not os.path.exists(SAVE_FOLDER):
    os.makedirs(SAVE_FOLDER)

def modify_exif(exif_data, new_model="Custom Phone Model"):
    """Изменить модель телефона в EXIF-данных."""
    if "0th" in exif_data:
        # Указываем новую модель и производителя
        exif_data["0th"][piexif.ImageIFD.Make] = "Custom Manufacturer".encode("utf-8")
        exif_data["0th"][piexif.ImageIFD.Model] = new_model.encode("utf-8")
    return exif_data

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Проверяем наличие файлов
        if "source" not in request.files or "target" not in request.files:
            return jsonify({"error": "Не выбраны файлы для загрузки"}), 400

        # Получаем файлы
        source_files = request.files.getlist("source")
        target_files = request.files.getlist("target")

        if len(source_files) != len(target_files):
            return jsonify({"error": "Количество исходных и целевых файлов должно совпадать"}), 400

        processed_files = []
        for source_file, target_file in zip(source_files, target_files):
            try:
                with Image.open(source_file) as src_img:
                    exif_data = piexif.load(src_img.info.get("exif", b""))

                    # Изменяем модель телефона в EXIF
                    exif_data = modify_exif(exif_data, new_model="My Custom Phone")

                    with Image.open(target_file) as tgt_img:
                        # Сохраняем нижнее фото с обновлёнными EXIF-данными
                        result_filename = source_file.filename
                        result_path = os.path.join(SAVE_FOLDER, result_filename)

                        if os.path.exists(result_path):
                            os.remove(result_path)  # Удаляем старую версию файла

                        exif_bytes = piexif.dump(exif_data)
                        tgt_img.save(result_path, exif=exif_bytes, quality=95)
                        processed_files.append(result_path)
            except Exception as e:
                print(f"Ошибка обработки файлов {source_file.filename} и {target_file.filename}: {e}")
                continue

        return jsonify({
            "message": "Успешно",
            "path": SAVE_FOLDER,
            "processed_files": [os.path.basename(f) for f in processed_files],
        })

    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)