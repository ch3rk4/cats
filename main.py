# КОТОГАДАЛКА - Приложение для гаданий


import os
import sys

python_dir = sys.base_prefix
os.environ['TCL_LIBRARY'] = os.path.join(python_dir, 'tcl', 'tcl8.6')
os.environ['TK_LIBRARY'] = os.path.join(python_dir, 'tcl', 'tk8.6')

# --- ИМПОРТЫ ---
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import random
import json
import sqlite3
from datetime import datetime, timedelta


# ============================================================
# БАЗА ДАННЫХ (SQLite)
# ============================================================

class Database:
    """
    Класс для работы с базой данных SQLite.
    Хранит результаты тестов и раскладов таро.
    """
    
    def __init__(self, db_name="cat_oracle.db"):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.db_path = os.path.join(script_dir, db_name)
        self.connection = sqlite3.connect(self.db_path)
        self.cursor = self.connection.cursor()
        self.create_tables()
        print(f"[DB] База данных: {self.db_path}")
    
    def create_tables(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS mood_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                cat_type TEXT NOT NULL,
                score INTEGER NOT NULL,
                answers TEXT
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS tarot_readings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                card1_name TEXT,
                card2_name TEXT,
                card3_name TEXT,
                prediction_love TEXT,
                prediction_career TEXT,
                prediction_finance TEXT
            )
        ''')
        
        self.connection.commit()
        print("[DB] Таблицы созданы")
    
    def save_mood_result(self, cat_type, score, answers):
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        answers_str = ",".join(map(str, answers))
        
        self.cursor.execute('''
            INSERT INTO mood_results (date, cat_type, score, answers)
            VALUES (?, ?, ?, ?)
        ''', (date, cat_type, score, answers_str))
        
        self.connection.commit()
        print(f"[DB] Сохранён результат теста: {cat_type}")
    
    def save_tarot_reading(self, cards, prediction):
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        card_names = [card.name if card else "" for card in cards]
        while len(card_names) < 3:
            card_names.append("")
        
        self.cursor.execute('''
            INSERT INTO tarot_readings 
            (date, card1_name, card2_name, card3_name, 
             prediction_love, prediction_career, prediction_finance)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            date, 
            card_names[0], card_names[1], card_names[2],
            prediction.get('love', ''),
            prediction.get('career', ''),
            prediction.get('finance', '')
        ))
        
        self.connection.commit()
        print(f"[DB] Сохранён расклад таро")
    
    def get_mood_history(self, limit=20):
        self.cursor.execute('''
            SELECT date, cat_type, score FROM mood_results
            ORDER BY date DESC LIMIT ?
        ''', (limit,))
        return self.cursor.fetchall()
    
    def get_tarot_history(self, limit=20):
        self.cursor.execute('''
            SELECT date, card1_name, card2_name, card3_name, prediction_love, prediction_career, prediction_finance FROM tarot_readings
            ORDER BY date DESC LIMIT ?
        ''', (limit,))
        return self.cursor.fetchall()
    
    def get_mood_statistics(self):
        self.cursor.execute('''
            SELECT cat_type, COUNT(*) as count FROM mood_results
            GROUP BY cat_type ORDER BY count DESC
        ''')
        return self.cursor.fetchall()
    
    def get_mood_trend(self, days=14):
        """
        Получает тренд настроения за последние N дней.
        Возвращает список кортежей (дата, средний_балл, количество_тестов)
        """
        start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        
        self.cursor.execute('''
            SELECT 
                DATE(date) as day,
                AVG(score) as avg_score,
                COUNT(*) as count
            FROM mood_results
            WHERE DATE(date) >= ?
            GROUP BY DATE(date)
            ORDER BY day ASC
        ''', (start_date,))
        
        return self.cursor.fetchall()
    
    def get_mood_by_weekday(self):
        """
        Получает среднее настроение по дням недели.
        0 = Воскресенье, 1 = Понедельник, ... 6 = Суббота (SQLite strftime %w)
        """
        self.cursor.execute('''
            SELECT 
                CAST(strftime('%w', date) AS INTEGER) as weekday,
                AVG(score) as avg_score,
                COUNT(*) as count
            FROM mood_results
            GROUP BY weekday
            ORDER BY weekday
        ''')
        return self.cursor.fetchall()
    
    def close(self):
        self.connection.close()
        print("[DB] Соединение закрыто")


# ============================================================
# ДАННЫЕ ДЛЯ ТЕСТА НАСТРОЕНИЯ
# ============================================================

QUESTIONS = [
    {
        "text": "Как ты себя чувствуешь прямо сейчас?",
        "options": [
            {"text": "Хочу спать и ничего не делать", "score": 1},
            {"text": "Немного устал(а)", "score": 2},
            {"text": "Нормально, обычный день", "score": 3},
            {"text": "Довольно бодро!", "score": 4},
            {"text": "Полон(на) энергии! 🔥", "score": 5}
        ]
    },
    {
        "text": "Что бы ты хотел(а) сделать прямо сейчас?",
        "options": [
            {"text": "Свернуться клубочком и уснуть", "score": 1},
            {"text": "Посидеть в тишине", "score": 2},
            {"text": "Посмотреть что-нибудь", "score": 3},
            {"text": "Пообщаться с друзьями", "score": 4},
            {"text": "Активно провести время!", "score": 5}
        ]
    },
    {
        "text": "Как ты относишься к сегодняшнему дню?",
        "options": [
            {"text": "Хочу, чтобы он скорее закончился", "score": 1},
            {"text": "Как-то не очень...", "score": 2},
            {"text": "Обычный день", "score": 3},
            {"text": "Хороший день!", "score": 4},
            {"text": "Отличный день! Всё супер!", "score": 5}
        ]
    },
    {
        "text": "Выбери погоду, которая тебе ближе сейчас:",
        "options": [
            {"text": "🌧️ Дождь за окном", "score": 1},
            {"text": "☁️ Пасмурно", "score": 2},
            {"text": "⛅ Переменная облачность", "score": 3},
            {"text": "🌤️ Солнце выглядывает", "score": 4},
            {"text": "☀️ Яркое солнце!", "score": 5}
        ]
    },
    {
        "text": "Если бы ты был(а) котом, что бы делал(а)?",
        "options": [
            {"text": "Спал(а) весь день", "score": 1},
            {"text": "Лежал(а) и смотрел(а) в окно", "score": 2},
            {"text": "Гулял(а) по дому", "score": 3},
            {"text": "Играл(а) с игрушками", "score": 4},
            {"text": "Носился(ась) как сумасшедший!", "score": 5}
        ]
    }
]

CAT_TYPES = [
    {
        "name": "Сонный котик 😴",
        "description": "Сегодня тебе нужен отдых. Позволь себе расслабиться, "
                       "как кот на мягком пледе. Не требуй от себя слишком многого.",
        "min_score": 5, "max_score": 9,
        "color": "#9E9E9E", "image_folder": "sleepy"
    },
    {
        "name": "Задумчивый кот 🐱",
        "description": "Ты сегодня в созерцательном настроении. Хорошее время "
                       "для размышлений и планирования.",
        "min_score": 10, "max_score": 14,
        "color": "#78909C", "image_folder": "thoughtful"
    },
    {
        "name": "Довольный котик 😺",
        "description": "У тебя хорошее, стабильное настроение! Как кот, который "
                       "поел и теперь доволен жизнью. Мур-мур!",
        "min_score": 15, "max_score": 19,
        "color": "#81C784", "image_folder": "happy"
    },
    {
        "name": "Игривый кот 😸",
        "description": "Ты полон энергии и готов к приключениям! Отличный день "
                       "для активностей и новых начинаний!",
        "min_score": 20, "max_score": 22,
        "color": "#FFB74D", "image_folder": "playful"
    },
    {
        "name": "Кот-ураган 🙀",
        "description": "Энергия бьёт через край! Ты как кот в 3 часа ночи — "
                       "готов свернуть горы и носиться по потолку!",
        "min_score": 23, "max_score": 25,
        "color": "#FF7043", "image_folder": "crazy"
    }
]

IMAGES_FOLDER = "images"

# Названия дней недели (индекс 0 = Воскресенье в SQLite)
WEEKDAYS = ["Вс", "Пн", "Вт", "Ср", "Чт", "Пт", "Сб"]


# ============================================================
# ФУНКЦИИ ДЛЯ РАБОТЫ С КАРТИНКАМИ
# ============================================================

def get_random_local_image(folder_name):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    folder_path = os.path.join(script_dir, IMAGES_FOLDER, folder_name)
    
    if not os.path.exists(folder_path):
        return None
    
    image_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.jfif')
    images = [f for f in os.listdir(folder_path) if f.lower().endswith(image_extensions)]
    
    if not images:
        return None
    
    return os.path.join(folder_path, random.choice(images))


def load_local_image(image_path, max_width=250, max_height=250):
    try:
        image = Image.open(image_path)
        
        if image.mode in ('RGBA', 'P', 'LA'):
            background = Image.new('RGB', image.size, (255, 255, 255))
            if image.mode == 'P':
                image = image.convert('RGBA')
            if 'A' in image.mode:
                background.paste(image, mask=image.split()[-1])
            else:
                background.paste(image)
            image = background
        elif image.mode != 'RGB':
            image = image.convert('RGB')
        
        width, height = image.size
        ratio = min(max_width / width, max_height / height)
        
        if ratio < 1:
            new_width = int(width * ratio)
            new_height = int(height * ratio)
            image = image.resize((new_width, new_height), Image.LANCZOS)
        
        return ImageTk.PhotoImage(image)
    except Exception as e:
        print(f"[IMG] Ошибка: {e}")
        return None


# ============================================================
# КЛАССЫ ДЛЯ ТАРО
# ============================================================

class TarotCard:
    def __init__(self, name, value, image_path):
        self.name = name
        self.value = value
        self.image_path = image_path


class Deck:
    BASEPATH = 'images/tarot/png/'
    
    def __init__(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        markup_path = os.path.join(script_dir, 'markup.json')
        
        with open(markup_path, 'r') as markup_file:
            markup = json.load(markup_file)
        
        self.cards = []
        for i in markup:
            card_path = os.path.join(script_dir, self.BASEPATH + i['name'] + '.png')
            self.cards.append(TarotCard(i['name'], i['id'], card_path))
    
    def pull_card(self):
        card = random.choice(self.cards)
        self.cards.remove(card)
        return card
    
    def reset(self):
        self.__init__()


def translate_prediction(text):
    import requests
    from dotenv import load_dotenv

    print(text)
    
    load_dotenv()
    API_KEY = os.getenv("API_KEY")
    folderId = os.getenv("folderId")

    r = requests.post("https://translate.api.cloud.yandex.net/translate/v2/translate",
        headers={
            "Authorization": f"Api-Key {API_KEY}",
            "Content-Type": "application/json"    
        },
        json={
            "folderId": folderId,
            "texts": [text],
            "targetLanguageCode": "ru"
        },
        timeout=15,
        verify=False
    )
    
    return r.json()['translations'][0]['text']


def get_prediction(cards):
    import requests
    import base64
    
    print(cards[0].value)

    try:
        auth = "Basic " + base64.b64encode(
            "649129:12788919b4c04b4ce2ddd4c31b36260a2aecf2d9".encode()
        ).decode()
        
        r = requests.post(
            "https://json.astrologyapi.com/v1/tarot_predictions",
            headers={
                'Authorization': auth,
                'Content-Type': 'application/json'
            },
            params={
                'love': cards[0].value,
                'career': cards[1].value,
                'finance': cards[2].value
            },
            timeout=15,
            verify=False
        )
        return r.json()
    except Exception as e:
        print(f"[API] Ошибка: {e}")
        return {
            'love': 'Не удалось получить предсказание. Попробуйте позже.',
            'career': 'Не удалось получить предсказание. Попробуйте позже.',
            'finance': 'Не удалось получить предсказание. Попробуйте позже.'
        }


# ============================================================
# ГЛАВНОЕ ПРИЛОЖЕНИЕ
# ============================================================

class MainApp:
    BG_COLOR = "#1a1a2e"
    ACCENT_COLOR = "#e94560"
    BUTTON_COLOR = "#16213e"
    TEXT_COLOR = "#ffffff"
    GRAY_COLOR = "#a0a0a0"
    
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("🐱 Котогадалка")
        self.window.geometry("800x600")
        self.window.configure(bg=self.BG_COLOR)
        self.window.resizable(False, False)
        
        self.db = Database()
        
        self.main_frame = tk.Frame(self.window, bg=self.BG_COLOR)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        self.current_question = 0
        self.total_score = 0
        self.answers = []
        
        self.deck = None
        self.cards_for_prediction = []
        self.prediction = {}
        
        self.show_main_menu()
    
    def clear_screen(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()
    
    # ==================== ГЛАВНОЕ МЕНЮ ====================
    
    def show_main_menu(self):
        self.clear_screen()
        
        tk.Label(
            self.main_frame, text="🐱 Котогадалка 🐱",
            font=("Arial", 32, "bold"), fg=self.ACCENT_COLOR, bg=self.BG_COLOR
        ).pack(pady=20)
        
        tk.Label(
            self.main_frame, text="Выбери, что хочешь сделать:",
            font=("Arial", 14), fg=self.TEXT_COLOR, bg=self.BG_COLOR
        ).pack(pady=5)
        
        buttons_frame = tk.Frame(self.main_frame, bg=self.BG_COLOR)
        buttons_frame.pack(pady=20)
        
        buttons = [
            ("😺 Какой ты кот сегодня?", self.ACCENT_COLOR, self.start_mood_test),
            ("🃏 Расклад Таро", self.ACCENT_COLOR, self.start_tarot),
            ("📈 Тренды настроения", self.BUTTON_COLOR, self.show_trends),
            ("📔 Мой дневник", self.BUTTON_COLOR, self.show_diary),
            ("📊 Статистика", self.BUTTON_COLOR, self.show_statistics),
        ]
        
        for text, color, command in buttons:
            tk.Button(
                buttons_frame, text=text, font=("Arial", 13, "bold"),
                fg=self.TEXT_COLOR, bg=color, activebackground="#ff6b6b",
                width=25, height=2, border=0, cursor="hand2", command=command
            ).pack(pady=7)
    
    # ==================== ТЕСТ НАСТРОЕНИЯ ====================
    
    def start_mood_test(self):
        self.current_question = 0
        self.total_score = 0
        self.answers = []
        self.show_mood_question()
    
    def show_mood_question(self):
        self.clear_screen()
        question_data = QUESTIONS[self.current_question]
        
        progress_text = f"Вопрос {self.current_question + 1} из {len(QUESTIONS)}"
        tk.Label(self.main_frame, text=progress_text, font=("Arial", 12),
                 fg=self.GRAY_COLOR, bg=self.BG_COLOR).pack(pady=10)
        
        progress_frame = tk.Frame(self.main_frame, bg="#333333", height=10)
        progress_frame.pack(fill="x", pady=5)
        
        progress_percent = (self.current_question + 1) / len(QUESTIONS)
        progress_fill = tk.Frame(progress_frame, bg=self.ACCENT_COLOR, height=10,
                                  width=int(760 * progress_percent))
        progress_fill.place(x=0, y=0)
        
        tk.Label(self.main_frame, text=question_data["text"], font=("Arial", 18),
                 fg=self.TEXT_COLOR, bg=self.BG_COLOR, wraplength=600).pack(pady=30)
        
        for option in question_data["options"]:
            btn = tk.Button(
                self.main_frame, text=option["text"], font=("Arial", 12),
                fg=self.TEXT_COLOR, bg=self.BUTTON_COLOR,
                activebackground=self.ACCENT_COLOR, width=45, height=2,
                border=0, cursor="hand2",
                command=lambda s=option["score"]: self.answer_mood_question(s)
            )
            btn.pack(pady=5)
            btn.bind('<Enter>', lambda e, b=btn: b.configure(bg=self.ACCENT_COLOR))
            btn.bind('<Leave>', lambda e, b=btn: b.configure(bg=self.BUTTON_COLOR))
    
    def answer_mood_question(self, score):
        self.total_score += score
        self.answers.append(score)
        self.current_question += 1
        
        if self.current_question < len(QUESTIONS):
            self.show_mood_question()
        else:
            self.show_mood_result()
    
    def get_cat_type(self):
        for cat_type in CAT_TYPES:
            if cat_type["min_score"] <= self.total_score <= cat_type["max_score"]:
                return cat_type
        return CAT_TYPES[0]
    
    def show_mood_result(self):
        self.clear_screen()
        cat_type = self.get_cat_type()
        
        self.db.save_mood_result(cat_type["name"], self.total_score, self.answers)
        
        tk.Label(self.main_frame, text="✨ Твой результат ✨", font=("Arial", 16),
                 fg=self.GRAY_COLOR, bg=self.BG_COLOR).pack(pady=10)
        
        tk.Label(self.main_frame, text=cat_type["name"], font=("Arial", 24, "bold"),
                 fg=cat_type["color"], bg=self.BG_COLOR).pack(pady=5)
        
        tk.Label(self.main_frame, text=f"Баллы: {self.total_score} из {len(QUESTIONS) * 5}",
                 font=("Arial", 11), fg=self.GRAY_COLOR, bg=self.BG_COLOR).pack(pady=5)
        
        image_frame = tk.Frame(self.main_frame, bg=self.BG_COLOR)
        image_frame.pack(pady=10)
        self.image_label = tk.Label(image_frame, bg=self.BG_COLOR)
        self.image_label.pack()
        self.load_cat_image(cat_type["image_folder"])
        
        desc_frame = tk.Frame(self.main_frame, bg=cat_type["color"], padx=3, pady=3)
        desc_frame.pack(pady=10, padx=20, fill="x")
        desc_inner = tk.Frame(desc_frame, bg=self.BUTTON_COLOR)
        desc_inner.pack(fill="both", expand=True)
        tk.Label(desc_inner, text=cat_type["description"], font=("Arial", 11),
                 fg=self.TEXT_COLOR, bg=self.BUTTON_COLOR, wraplength=500,
                 justify="center", padx=15, pady=10).pack()
        
        buttons_frame = tk.Frame(self.main_frame, bg=self.BG_COLOR)
        buttons_frame.pack(pady=15)
        
        for text, cmd in [("🔄 Другой котик", lambda: self.load_cat_image(cat_type["image_folder"])),
                          ("🔁 Заново", self.start_mood_test), ("🏠 Меню", self.show_main_menu)]:
            tk.Button(buttons_frame, text=text, font=("Arial", 11), fg=self.TEXT_COLOR,
                      bg=self.BUTTON_COLOR, width=14, height=2, border=0,
                      cursor="hand2", command=cmd).pack(side="left", padx=5)
    
    def load_cat_image(self, folder):
        image_path = get_random_local_image(folder)
        if image_path:
            photo = load_local_image(image_path, 180, 180)
            if photo:
                self.current_photo = photo
                self.image_label.config(image=photo, text="")
            else:
                self.image_label.config(text="😿 Не удалось загрузить", image="")
        else:
            self.image_label.config(text="😿 Картинки не найдены", image="")
    
    # ==================== ТРЕНДЫ НАСТРОЕНИЯ ====================
    
    def show_trends(self):
        """Показывает график тренда настроения."""
        self.clear_screen()
        
        tk.Label(self.main_frame, text="📈 Тренды настроения", font=("Arial", 24, "bold"),
                 fg=self.ACCENT_COLOR, bg=self.BG_COLOR).pack(pady=15)
        
        # Получаем данные за последние 14 дней
        trend_data = self.db.get_mood_trend(14)
        weekday_data = self.db.get_mood_by_weekday()
        
        if not trend_data:
            tk.Label(self.main_frame, 
                     text="📊 Пока нет данных для анализа.\n\nПроходи тесты настроения каждый день,\nчтобы отслеживать тренды!",
                     font=("Arial", 14), fg=self.GRAY_COLOR, bg=self.BG_COLOR,
                     justify="center").pack(pady=50)
        else:
            # Создаём Canvas для графика
            canvas = tk.Canvas(self.main_frame, width=700, height=250, 
                               bg=self.BUTTON_COLOR, highlightthickness=0)
            canvas.pack(pady=10)
            
            # Параметры графика
            padding = 50
            graph_width = 700 - 2 * padding
            graph_height = 200 - padding
            
            # Мин/макс баллы
            min_score = 5
            max_score = 25
            
            # Рисуем оси
            canvas.create_line(padding, 200, 700 - padding, 200, fill=self.GRAY_COLOR, width=2)
            canvas.create_line(padding, 200, padding, 30, fill=self.GRAY_COLOR, width=2)
            
            # Подписи оси Y (баллы)
            for score in [5, 10, 15, 20, 25]:
                y = 200 - ((score - min_score) / (max_score - min_score)) * graph_height
                canvas.create_text(padding - 20, y, text=str(score), fill=self.GRAY_COLOR, font=("Arial", 9))
                canvas.create_line(padding - 5, y, padding, y, fill=self.GRAY_COLOR)
            
            # Рисуем точки и линии
            points = []
            num_points = len(trend_data)
            
            for i, (date, avg_score, count) in enumerate(trend_data):
                x = padding + (i / max(num_points - 1, 1)) * graph_width
                y = 200 - ((avg_score - min_score) / (max_score - min_score)) * graph_height
                points.append((x, y))
                
                # Подпись даты
                if num_points <= 7 or i % 2 == 0:
                    try:
                        dt = datetime.strptime(date, "%Y-%m-%d")
                        date_str = dt.strftime("%d.%m")
                    except:
                        date_str = date[-5:]
                    canvas.create_text(x, 215, text=date_str, fill=self.GRAY_COLOR, font=("Arial", 8))
            
            # Рисуем линию тренда
            if len(points) > 1:
                for i in range(len(points) - 1):
                    x1, y1 = points[i]
                    x2, y2 = points[i + 1]
                    canvas.create_line(x1, y1, x2, y2, fill=self.ACCENT_COLOR, width=3)
            
            # Рисуем точки
            for i, (x, y) in enumerate(points):
                avg_score = trend_data[i][1]
                if avg_score >= 20:
                    color = "#81C784"  # зелёный
                elif avg_score >= 15:
                    color = "#FFB74D"  # оранжевый
                else:
                    color = "#9E9E9E"  # серый
                
                canvas.create_oval(x-6, y-6, x+6, y+6, fill=color, outline=self.TEXT_COLOR, width=2)
                canvas.create_text(x, y-15, text=f"{avg_score:.0f}", fill=self.TEXT_COLOR, font=("Arial", 8, "bold"))
            
            # Легенда
            avg_total = sum(d[1] for d in trend_data) / len(trend_data)
            tk.Label(self.main_frame, 
                     text=f"📅 Последние {len(trend_data)} дн. | Средний балл: {avg_total:.1f}",
                     font=("Arial", 10), fg=self.GRAY_COLOR, bg=self.BG_COLOR).pack(pady=5)
            
            # График по дням недели
            if weekday_data and len(weekday_data) >= 3:
                tk.Label(self.main_frame, text="📆 Среднее настроение по дням недели:",
                         font=("Arial", 12, "bold"), fg=self.TEXT_COLOR, bg=self.BG_COLOR).pack(pady=(15, 5))
                
                weekday_frame = tk.Frame(self.main_frame, bg=self.BG_COLOR)
                weekday_frame.pack(pady=5)
                
                for weekday, avg_score, count in weekday_data:
                    day_name = WEEKDAYS[weekday]
                    
                    if avg_score >= 20:
                        bar_color = "#81C784"
                    elif avg_score >= 15:
                        bar_color = "#FFB74D"
                    else:
                        bar_color = "#9E9E9E"
                    
                    day_frame = tk.Frame(weekday_frame, bg=self.BG_COLOR)
                    day_frame.pack(side="left", padx=8)
                    
                    bar_height = int((avg_score / 25) * 60)
                    bar_canvas = tk.Canvas(day_frame, width=30, height=70, 
                                           bg=self.BG_COLOR, highlightthickness=0)
                    bar_canvas.pack()
                    bar_canvas.create_rectangle(5, 70 - bar_height, 25, 70, fill=bar_color, outline="")
                    bar_canvas.create_text(15, 70 - bar_height - 10, text=f"{avg_score:.0f}", 
                                           fill=self.TEXT_COLOR, font=("Arial", 8))
                    
                    tk.Label(day_frame, text=day_name, font=("Arial", 9),
                             fg=self.GRAY_COLOR, bg=self.BG_COLOR).pack()
        
        # Кнопка назад
        tk.Button(self.main_frame, text="🏠 Вернуться в меню", font=("Arial", 12),
                  fg=self.TEXT_COLOR, bg=self.BUTTON_COLOR, width=20, height=2,
                  border=0, cursor="hand2", command=self.show_main_menu).pack(pady=15)
    
    # ==================== ТАРО ====================
    
    def start_tarot(self):
        self.clear_screen()
        self.deck = Deck()
        
        tk.Label(self.main_frame, text="🃏 Расклад Таро 🃏", font=("Arial", 24, "bold"),
                 fg=self.ACCENT_COLOR, bg=self.BG_COLOR).pack(pady=20)
        
        tk.Label(self.main_frame, text="Нажми кнопку, чтобы вытянуть три карты\nи узнать, что тебя ждёт",
                 font=("Arial", 14), fg=self.TEXT_COLOR, bg=self.BG_COLOR, justify="center").pack(pady=20)
        
        tk.Button(self.main_frame, text="✨ Вытянуть карты ✨", font=("Arial", 16, "bold"),
                  fg=self.TEXT_COLOR, bg=self.ACCENT_COLOR, width=20, height=2,
                  border=0, cursor="hand2", command=self.draw_tarot_cards).pack(pady=30)
        
        tk.Button(self.main_frame, text="🏠 Вернуться в меню", font=("Arial", 12),
                  fg=self.TEXT_COLOR, bg=self.BUTTON_COLOR, width=20, height=2,
                  border=0, cursor="hand2", command=self.show_main_menu).pack(pady=10)
    
    def draw_tarot_cards(self):
        self.clear_screen()
        
        self.canvas = tk.Canvas(self.main_frame, bg=self.BG_COLOR, highlightthickness=0, width=760, height=520)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        self.card_images = {}
        self.cards_for_prediction = []
        
        for i in range(3):
            card = self.deck.pull_card()
            self.cards_for_prediction.append(card)
            
            try:
                img = Image.open(card.image_path)
                img = img.resize((150, 280), Image.LANCZOS)
                card_img = ImageTk.PhotoImage(img)
                
                self.card_images[f"card_{i}"] = card_img
                x_pos = 130 + i * 250
                self.canvas.create_image(x_pos, 160, image=card_img)
                self.canvas.create_text(x_pos, 320, text=card.name.replace("_", " ").title(),
                                        fill=self.TEXT_COLOR, font=("Arial", 10))
            except Exception as e:
                print(f"[IMG] Ошибка загрузки карты: {e}")
        
        self.canvas.create_text(380, 360, text="⏳ Получаю предсказание...",
                                fill=self.GRAY_COLOR, font=("Arial", 12))
        self.window.update()
        
        self.prediction = get_prediction(self.cards_for_prediction)
        
        try:
            self.prediction = {
                'love': translate_prediction(self.prediction['love']),
                'career': translate_prediction(self.prediction['career']),
                'finance': translate_prediction(self.prediction['finance'])
            }
        except:
            pass
        
        self.db.save_tarot_reading(self.cards_for_prediction, self.prediction)
        
        self.text_widget = tk.Text(self.canvas, height=6, width=80, wrap="word",
                                   bg=self.BUTTON_COLOR, fg=self.TEXT_COLOR, font=("Arial", 10))
        self.canvas.create_window(380, 400, window=self.text_widget)
        self.text_widget.insert("1.0", "Выбери тему предсказания ниже...")
        self.text_widget.config(state="disabled")
        
        button_frame = tk.Frame(self.canvas, bg=self.BG_COLOR)
        
        for text, topic in [("❤️ Любовь", 'love'), ("💼 Карьера", 'career'), ("💰 Финансы", 'finance')]:
            tk.Button(button_frame, text=text, font=("Arial", 11), fg=self.TEXT_COLOR,
                      bg=self.ACCENT_COLOR, width=12, height=2, border=0,
                      command=lambda t=topic: self.show_prediction(t)).pack(side="left", padx=10)
        
        tk.Button(button_frame, text="🏠 Меню", font=("Arial", 11), fg=self.TEXT_COLOR,
                  bg=self.BUTTON_COLOR, width=12, height=2, border=0,
                  command=self.show_main_menu).pack(side="left", padx=10)
        
        self.canvas.create_window(380, 490, window=button_frame)
    
    def show_prediction(self, topic):
        text = self.prediction.get(topic, "Предсказание недоступно")
        self.text_widget.config(state="normal")
        self.text_widget.delete("1.0", "end")
        self.text_widget.insert("1.0", text)
        self.text_widget.config(state="disabled")
    
    # ==================== ДНЕВНИК ====================
    
    def show_diary(self):
        self.clear_screen()
        
        tk.Label(self.main_frame, text="📔 Мой дневник", font=("Arial", 24, "bold"),
                 fg=self.ACCENT_COLOR, bg=self.BG_COLOR).pack(pady=15)
        
        tabs_frame = tk.Frame(self.main_frame, bg=self.BG_COLOR)
        tabs_frame.pack(pady=10)
        
        tk.Button(tabs_frame, text="😺 Тесты настроения", font=("Arial", 11),
                  fg=self.TEXT_COLOR, bg=self.ACCENT_COLOR, width=18, height=2,
                  border=0, command=self.show_mood_diary).pack(side="left", padx=5)
        
        tk.Button(tabs_frame, text="🃏 Расклады таро", font=("Arial", 11),
                  fg=self.TEXT_COLOR, bg=self.BUTTON_COLOR, width=18, height=2,
                  border=0, command=self.show_tarot_diary).pack(side="left", padx=5)
        
        self.diary_container = tk.Frame(self.main_frame, bg=self.BG_COLOR)
        self.diary_container.pack(fill="both", expand=True, pady=10)
        
        self.show_mood_diary()
        
        tk.Button(self.main_frame, text="🏠 Вернуться в меню", font=("Arial", 12),
                  fg=self.TEXT_COLOR, bg=self.BUTTON_COLOR, width=20, height=2,
                  border=0, cursor="hand2", command=self.show_main_menu).pack(pady=10)
    
    def show_mood_diary(self):
        for widget in self.diary_container.winfo_children():
            widget.destroy()
        
        history = self.db.get_mood_history(15)
        
        if not history:
            tk.Label(self.diary_container, text="Пока нет записей.\nПройди тест, чтобы появилась история!",
                     font=("Arial", 12), fg=self.GRAY_COLOR, bg=self.BG_COLOR).pack(pady=50)
            return
        
        canvas = tk.Canvas(self.diary_container, bg=self.BG_COLOR, highlightthickness=0)
        scrollbar = tk.Scrollbar(self.diary_container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.BG_COLOR)
        
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        for date, cat_type, score in history:
            entry_frame = tk.Frame(scrollable_frame, bg=self.BUTTON_COLOR, padx=10, pady=8)
            entry_frame.pack(fill="x", pady=3, padx=10)
            
            try:
                dt = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
                date_str = dt.strftime("%d.%m.%Y %H:%M")
            except:
                date_str = date
            
            tk.Label(entry_frame, text=f"📅 {date_str}", font=("Arial", 10),
                     fg=self.GRAY_COLOR, bg=self.BUTTON_COLOR).pack(anchor="w")
            tk.Label(entry_frame, text=f"{cat_type} — {score} баллов", font=("Arial", 12, "bold"),
                     fg=self.TEXT_COLOR, bg=self.BUTTON_COLOR).pack(anchor="w")
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def show_tarot_diary(self):
        for widget in self.diary_container.winfo_children():
            widget.destroy()
        
        history = self.db.get_tarot_history(15)
        
        if not history:
            tk.Label(self.diary_container, text="Пока нет раскладов.\nСделай расклад, чтобы появилась история!",
                     font=("Arial", 12), fg=self.GRAY_COLOR, bg=self.BG_COLOR).pack(pady=50)
            return
        
        canvas = tk.Canvas(self.diary_container, bg=self.BG_COLOR, highlightthickness=0)
        scrollbar = tk.Scrollbar(self.diary_container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.BG_COLOR)
        
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        for date, card1, card2, card3, prediction_love, prediction_career, prediction_finance in history:
            entry_frame = tk.Frame(scrollable_frame, bg=self.BUTTON_COLOR, padx=10, pady=8)
            entry_frame.pack(fill="x", pady=3, padx=10)
            
            entry_frame.columnconfigure(0, weight=1) 
            
            try:
                dt = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
                date_str = dt.strftime("%d.%m.%Y %H:%M")
            except:
                date_str = date
            
            tk.Label(entry_frame, text=f"📅 {date_str}", font=("Arial", 10),
                    fg=self.GRAY_COLOR, bg=self.BUTTON_COLOR).grid(row=0, column=0, sticky="w")
            cards_text = f"🃏 {card1.replace('_', ' ')}, {card2.replace('_', ' ')}, {card3.replace('_', ' ')}"
            tk.Label(entry_frame, text=cards_text, font=("Arial", 11), fg=self.TEXT_COLOR,
                    bg=self.BUTTON_COLOR, wraplength=500).grid(row=1, column=0, sticky="w", pady=(0, 5))

            tk.Button(entry_frame, text="Подробнее", font=("Arial", 10),
                    fg=self.TEXT_COLOR, bg=self.BUTTON_COLOR,
                    border=0, cursor="hand2",
                    command=lambda pl=prediction_love, pc=prediction_career, pf=prediction_finance: 
                    self.show_tarot_details(pl, pc, pf)
                    ).grid(row=0, column=1, rowspan=2, sticky="ns", padx=(10, 0))
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def show_tarot_details(self, prediction_love, prediction_career, prediction_finance):
        
        for widget in self.diary_container.winfo_children():
            widget.destroy()

        main_details_frame = tk.Frame(self.diary_container, bg=self.BG_COLOR)
        main_details_frame.pack(fill="both", expand=True, padx=20, pady=20)

        tk.Label(main_details_frame, text="Детали расклада", font=("Arial", 16, "bold"),
                fg=self.TEXT_COLOR, bg=self.BG_COLOR).pack(anchor="w", pady=(0, 20))

        areas_frame = tk.Frame(main_details_frame, bg=self.BG_COLOR)
        areas_frame.pack(fill="both", expand=True)

        areas_frame.columnconfigure(0, weight=1)
        areas_frame.columnconfigure(1, weight=1)
        areas_frame.columnconfigure(2, weight=1)

        predictions = [
            ("❤️ Любовь", prediction_love),
            ("💼 Карьера", prediction_career),
            ("💰 Финансы", prediction_finance)
        ]
        
        for i, (title, text) in enumerate(predictions):
            area = tk.Frame(areas_frame, bg=self.BUTTON_COLOR, relief="solid", 
                        borderwidth=2, padx=15, pady=15)
            area.grid(row=0, column=i, sticky="nsew", padx=(0 if i == 0 else 10, 10 if i == 2 else 5))
            
            tk.Label(area, text=title, font=("Arial", 14, "bold"),
                    fg=self.TEXT_COLOR, bg=self.BUTTON_COLOR).pack(anchor="w", pady=(0, 10))
            
            text_frame = tk.Frame(area, bg=self.BUTTON_COLOR)
            text_frame.pack(fill="both", expand=True)
            
            text_widget = tk.Text(text_frame, font=("Arial", 12), fg=self.TEXT_COLOR, 
                                bg=self.BUTTON_COLOR, wrap="word", height=9,
                                borderwidth=0, highlightthickness=0)
            text_widget.insert("1.0", text)
            text_widget.config(state="disabled")
            
            scrollbar = tk.Scrollbar(text_frame, orient="vertical", command=text_widget.yview)
            text_widget.configure(yscrollcommand=scrollbar.set)
            
            text_widget.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
        

    # ==================== СТАТИСТИКА ====================
    
    def show_statistics(self):
        self.clear_screen()
        
        tk.Label(self.main_frame, text="📊 Статистика", font=("Arial", 24, "bold"),
                 fg=self.ACCENT_COLOR, bg=self.BG_COLOR).pack(pady=20)
        
        stats = self.db.get_mood_statistics()
        
        if not stats:
            tk.Label(self.main_frame, text="Пока нет данных для статистики.\nПройди несколько тестов!",
                     font=("Arial", 14), fg=self.GRAY_COLOR, bg=self.BG_COLOR).pack(pady=50)
        else:
            tk.Label(self.main_frame, text="Твои типы котов:", font=("Arial", 14),
                     fg=self.TEXT_COLOR, bg=self.BG_COLOR).pack(pady=10)
            
            total = sum(count for _, count in stats)
            
            for cat_type, count in stats:
                percent = int(count / total * 100)
                
                stat_frame = tk.Frame(self.main_frame, bg=self.BG_COLOR)
                stat_frame.pack(fill="x", padx=50, pady=5)
                
                tk.Label(stat_frame, text=f"{cat_type}: {count} раз ({percent}%)",
                         font=("Arial", 12), fg=self.TEXT_COLOR, bg=self.BG_COLOR, anchor="w").pack(side="left")
                
                bar_frame = tk.Frame(stat_frame, bg="#333333", height=20, width=200)
                bar_frame.pack(side="right", padx=10)
                bar_frame.pack_propagate(False)
                
                fill_width = int(200 * count / max(c for _, c in stats))
                bar_fill = tk.Frame(bar_frame, bg=self.ACCENT_COLOR, height=20, width=fill_width)
                bar_fill.place(x=0, y=0)
        
        tk.Button(self.main_frame, text="🏠 Вернуться в меню", font=("Arial", 12),
                  fg=self.TEXT_COLOR, bg=self.BUTTON_COLOR, width=20, height=2,
                  border=0, cursor="hand2", command=self.show_main_menu).pack(pady=30)
    
    def run(self):
        self.window.mainloop()
        self.db.close()


# ============================================================
# ТОЧКА ВХОДА
# ============================================================

if __name__ == "__main__":
    app = MainApp()
    app.run()
