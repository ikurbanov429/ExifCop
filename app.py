@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        try:
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
                with Image.open(source_file) as src_img:
                    try:
                        exif_data = piexif.load(src_img.info.get("exif", b""))
                    except Exception as e:
                        print(f"Ошибка загрузки EXIF: {e}")
                        exif_data = {}

                    with Image.open(target_file) as tgt_img:
                        result_filename = source_file.filename
                        result_path = os.path.join(SAVE_FOLDER, result_filename)

                        tgt_img.save(result_path, exif=piexif.dump(exif_data), quality=95)
                        processed_files.append(result_path)

            return jsonify({
                "message": "Успешно",
                "path": SAVE_FOLDER,
                "processed_files": [os.path.basename(f) for f in processed_files],
            })
        except Exception as e:
            print(f"Ошибка обработки: {e}")
            return jsonify({"error": "Ошибка на сервере"}), 500

    return render_template("index.html")
