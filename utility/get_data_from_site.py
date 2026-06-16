import requests

# URL официального API/эндпоинта расписания (адрес взят для примера)
for page_id in range(1,42):
    url = "https://api.quizplease.ru/api/games/finished/4?per_page=10&order=-date&meta%5B%5D=places_ids&page={page_id}" 

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        games_data = response.json()
        inner_data = games_data.get("data", {})
        games_list = inner_data.get("data", [])
        # Извлекаем UUID из ответа сервера
        for game in games_list:
            game_id = game.get("id")
            if game_id:
                # Не забываем добавить "/game/" в путь ссылки
                print(f"https://quizplease.ru/game/{game_id}")
                "https://api.quizplease.ru/api/games/{game_id}/results"