import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# ТВОИ НАСТРОЙКИ
ACCESS_TOKEN = 'vk1.a.hDQ9RxY-XzV7J2UFi92DRJE_wn3LySuLZosisMwWEQgIpuro0mn6d-kw0G-C1rdQkLBpeu_9pIzZrNASZKzMJ5wS-fq9b4VLkuiE5CCsmZNqyHNsI2BlfSPZVe0teNL3ma7ERxQLVNKUcP70o_pn7AcSgBIgjzx84m5H2oCwzMT89zUqZso6Z-bv4vB3bnhF3z17JtB_DF2dqjyKaUKS_A'
GROUP_ID = '233749253'

@app.route('/api/post', methods=['POST'])
def handler():
    message = request.form.get('message', '')
    photo = request.files.get('photo')
    try:
        attachments = ""
        if photo:
            # 1. Получаем сервер
            res = requests.get("https://api.vk.com/method/photos.getWallUploadServer", params={
                "group_id": GROUP_ID, "access_token": ACCESS_TOKEN, "v": "5.131"
            }).json()
            upload_url = res['response']['upload_url']

            # 2. Грузим фото
            files = {'photo': (photo.filename, photo.read())}
            up_res = requests.post(upload_url, files=files).json()

            # 3. Сохраняем
            sv_res = requests.get("https://api.vk.com/method/photos.saveWallPhoto", params={
                "group_id": GROUP_ID, "photo": up_res['photo'], "server": up_res['server'],
                "hash": up_res['hash'], "access_token": ACCESS_TOKEN, "v": "5.131"
            }).json()
            p = sv_res['response'][0]
            attachments = f"photo{p['owner_id']}_{p['id']}"

        # 4. Пост
        requests.get("https://api.vk.com/method/wall.post", params={
            "owner_id": f"-{GROUP_ID}", "from_group": 1, "message": message,
            "attachments": attachments, "access_token": ACCESS_TOKEN, "v": "5.131"
        })
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

# Эта строчка нужна для Vercel
app.debug = False