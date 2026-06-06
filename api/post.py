import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# ВСТАВЬ СВОЙ ТОКЕН ТУТ
ACCESS_TOKEN = 'vk1.a.6ESnOuNRiuANsEsvU_5mwdVKnWvcC2kMpWHQvxJIjS0uqKVmLm8crcuDqcuPQooKsO2R7OzQ5LCt_jbOzuFVv11KVaaKyaVlGWuCJ_7gskzpB9TSLM6IDlCBaYRNImPpFpLBoFkHOWAEZHt_htn6Q-oPoHu7FTK2EdWROIUgYQU-MTqd3nGViHcyIABaAbAyvbGJDvEM9jcUWOcnZsO_7w'
GROUP_ID = '233749253'

@app.route('/api/post', methods=['POST'])
def post_to_vk():
    message = request.form.get('message', '')
    photo = request.files.get('photo')
    try:
        attachments = ""
        if photo:
            # 1. Получаем сервер
            res = requests.get("https://api.vk.com/method/photos.getWallUploadServer", params={
                "group_id": GROUP_ID, "access_token": ACCESS_TOKEN, "v": "5.131"
            }).json()
            
            if 'error' in res:
                return jsonify({"success": False, "error": f"Ошибка сервера загрузки: {res['error']['error_msg']}"})
            
            upload_url = res['response']['upload_url']

            # 2. Грузим фото
            files = {'photo': (photo.filename, photo.read())}
            upload_res = requests.post(upload_url, files=files).json()

            # 3. Сохраняем фото
            save_res = requests.get("https://api.vk.com/method/photos.saveWallPhoto", params={
                "group_id": GROUP_ID, "photo": upload_res['photo'], "server": upload_res['server'],
                "hash": upload_res['hash'], "access_token": ACCESS_TOKEN, "v": "5.131"
            }).json()
            
            if 'error' in save_res:
                return jsonify({"success": False, "error": f"Ошибка сохранения фото: {save_res['error']['error_msg']}"})
                
            p = save_res['response'][0]
            attachments = f"photo{p['owner_id']}_{p['id']}"

        # 4. Публикуем пост
        post_res = requests.get("https://api.vk.com/method/wall.post", params={
            "owner_id": f"-{GROUP_ID}", "from_group": 1, "message": message,
            "attachments": attachments, "access_token": ACCESS_TOKEN, "v": "5.131"
        }).json()
        
        if 'error' in post_res:
            return jsonify({"success": False, "error": f"Ошибка публикации: {post_res['error']['error_msg']}"})
            
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

def handler(request):
    return app(request)
