# ============================================================
# КОТОГАДАЛКА - Мини-тест "Какой ты кот сегодня?"
# ============================================================
# Это приложение с графическим интерфейсом на Tkinter
# Пользователь отвечает на вопросы и узнаёт, какой он кот
# ============================================================

# --- ИСПРАВЛЕНИЕ ДЛЯ WINDOWS + POETRY ---
# Poetry создаёт виртуальное окружение, которое не видит Tcl/Tk
# Этот код указывает правильные пути к библиотекам Tcl/Tk
import os
import sys

# Получаем путь к системному Python (где установлен Tcl/Tk)
python_dir = sys.base_prefix

# Устанавливаем переменные окружения для Tcl и Tk
os.environ['TCL_LIBRARY'] = os.path.join(python_dir, 'tcl', 'tcl8.6')
os.environ['TK_LIBRARY'] = os.path.join(python_dir, 'tcl', 'tk8.6')

# --- ИМПОРТЫ ---
# tkinter - стандартная библиотека Python для создания окон и кнопок
import tkinter as tk
from tkinter import messagebox  # для всплывающих окон с сообщениями

# PIL (Pillow) - для загрузки и отображения изображений в Tkinter
# Установка: pip install Pillow (или poetry add Pillow)
from PIL import Image, ImageTk

# ============================================================
# ДАННЫЕ ДЛЯ ТЕСТА
# ============================================================

# Список вопросов теста
# Каждый вопрос - это словарь с текстом вопроса и вариантами ответов
# Каждый вариант ответа содержит текст и количество баллов (score)
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

# Типы котов (результаты теста)
# Каждый тип содержит: название, описание, диапазон баллов (min, max), цвет
# image_folder - название папки с картинками для этого типа
CAT_TYPES = [
    {
        "name": "Сонный котик 😴",
        "description": "Сегодня тебе нужен отдых. Позволь себе расслабиться, "
                       "как кот на мягком пледе. Не требуй от себя слишком многого. "
                       "Горячий чай, тёплый плед и любимый сериал — вот твой рецепт на сегодня!",
        "min_score": 5,
        "max_score": 9,
        "color": "#9E9E9E",  # серый цвет
        "image_folder": "sleepy"  # папка images/sleepy/
    },
    {
        "name": "Задумчивый кот 🐱",
        "description": "Ты сегодня в созерцательном настроении. Хорошее время "
                       "для размышлений и планирования. Как кот, который смотрит "
                       "в окно и думает о важном. Может, стоит записать свои мысли?",
        "min_score": 10,
        "max_score": 14,
        "color": "#78909C",  # серо-голубой
        "image_folder": "thoughtful"  # папка images/thoughtful/
    },
    {
        "name": "Довольный котик 😺",
        "description": "У тебя хорошее, стабильное настроение! Как кот, который "
                       "поел и теперь доволен жизнью. Отличный день для обычных дел "
                       "и маленьких радостей. Мур-мур!",
        "min_score": 15,
        "max_score": 19,
        "color": "#81C784",  # зелёный
        "image_folder": "happy"  # папка images/happy/
    },
    {
        "name": "Игривый кот 😸",
        "description": "Ты полон энергии и готов к приключениям! Как котёнок, "
                       "который гоняется за солнечным зайчиком. Отличный день "
                       "для активностей и новых начинаний!",
        "min_score": 20,
        "max_score": 22,
        "color": "#FFB74D",  # оранжевый
        "image_folder": "playful"  # папка images/playful/
    },
    {
        "name": "Кот-ураган 🙀",
        "description": "Энергия бьёт через край! Ты как кот в 3 часа ночи — "
                       "готов свернуть горы и носиться по потолку! Используй "
                       "эту энергию с умом — сегодня тебе всё по плечу!",
        "min_score": 23,
        "max_score": 25,
        "color": "#FF7043",  # красно-оранжевый
        "image_folder": "crazy"  # папка images/crazy/
    }
]

# ============================================================
# НАСТРОЙКИ КАРТИНОК
# ============================================================

import os
import random

# Папка с картинками (рядом с main.py)
IMAGES_FOLDER = "images"

# Соответствие типов котов и папок с картинками
CAT_IMAGE_FOLDERS = {
    "sleepy": "sleepy",  # Сонный котик
    "thoughtful": "thoughtful",  # Задумчивый кот
    "happy": "happy",  # Довольный котик
    "playful": "playful",  # Игривый кот
    "crazy": "crazy"  # Кот-ураган
}


# ============================================================
# ФУНКЦИИ ДЛЯ РАБОТЫ С КАРТИНКАМИ
# ============================================================

def get_random_local_image(folder_name):
    """
    Получает путь к случайной картинке из указанной папки.

    Параметры:
        folder_name - название папки (sleepy, thoughtful, happy, playful, crazy)

    Возвращает:
        Путь к файлу картинки или None если папка пуста
    """
    # Получаем путь к папке со скриптом
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Полный путь к папке с картинками
    folder_path = os.path.join(script_dir, IMAGES_FOLDER, folder_name)

    print(f"[IMG] Ищу картинки в: {folder_path}")

    # Проверяем, существует ли папка
    if not os.path.exists(folder_path):
        print(f"[IMG] Папка не найдена: {folder_path}")
        return None

    # Получаем список файлов картинок
    image_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.jfif')
    images = [
        f for f in os.listdir(folder_path)
        if f.lower().endswith(image_extensions)
    ]

    print(f"[IMG] Найдено картинок: {len(images)}")

    if not images:
        print(f"[IMG] В папке нет картинок")
        return None

    # Выбираем случайную картинку
    random_image = random.choice(images)
    full_path = os.path.join(folder_path, random_image)

    print(f"[IMG] Выбрана: {random_image}")

    return full_path


def load_local_image(image_path, max_width=250, max_height=250):
    """
    Загружает локальное изображение и подготавливает его для Tkinter.

    Параметры:
        image_path - путь к файлу изображения
        max_width - максимальная ширина
        max_height - максимальная высота

    Возвращает:
        ImageTk.PhotoImage объект или None при ошибке
    """
    try:
        print(f"[IMG] Загружаю файл: {image_path}")

        # Открываем изображение
        image = Image.open(image_path)

        print(f"[IMG] Формат: {image.format}, Размер: {image.size}")

        # Конвертируем в RGB
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

        # Масштабируем
        width, height = image.size
        ratio = min(max_width / width, max_height / height)

        if ratio < 1:
            new_width = int(width * ratio)
            new_height = int(height * ratio)
            image = image.resize((new_width, new_height), Image.LANCZOS)
            print(f"[IMG] Изменён размер: {new_width}x{new_height}")

        photo = ImageTk.PhotoImage(image)
        print("[IMG] Картинка готова!")
        return photo

    except Exception as e:
        print(f"[IMG] Ошибка: {type(e).__name__}: {e}")

    return None


# ============================================================
# КЛАСС ПРИЛОЖЕНИЯ
# ============================================================

class CatMoodTestApp:
    """
    Главный класс приложения.
    Создаёт окно и управляет всеми экранами теста.
    """

    def __init__(self):
        """
        Конструктор - вызывается при создании объекта.
        Здесь мы настраиваем главное окно приложения.
        """
        # Создаём главное окно
        self.window = tk.Tk()
        self.window.title("🐱 Какой ты кот сегодня?")
        self.window.geometry("600x500")  # ширина x высота в пикселях
        self.window.configure(bg="#1a1a2e")  # тёмный фон

        # Запрещаем изменять размер окна (чтобы не ломался дизайн)
        self.window.resizable(False, False)

        # --- Переменные для хранения состояния теста ---
        self.current_question = 0  # номер текущего вопроса (начинаем с 0)
        self.total_score = 0  # сумма баллов за ответы
        self.answers = []  # список ответов пользователя

        # --- Создаём контейнер для содержимого ---
        # Frame - это как коробка, в которую мы кладём другие элементы
        self.main_frame = tk.Frame(self.window, bg="#1a1a2e")
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Показываем стартовый экран
        self.show_start_screen()

    def clear_screen(self):
        """
        Очищает экран - удаляет все элементы из main_frame.
        Вызываем перед показом нового экрана.
        """
        # Проходим по всем дочерним элементам и удаляем их
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def show_start_screen(self):
        """
        Показывает стартовый экран с приветствием и кнопкой начала теста.
        """
        # Сначала очищаем экран
        self.clear_screen()

        # --- Заголовок ---
        title_label = tk.Label(
            self.main_frame,
            text="🐱 Какой ты кот сегодня? 🐱",
            font=("Arial", 24, "bold"),
            fg="#e94560",  # розовый цвет текста
            bg="#1a1a2e"  # фон как у родителя
        )
        title_label.pack(pady=40)  # pady - отступ сверху и снизу

        # --- Описание ---
        description = (
            "Пройди короткий тест из 5 вопросов\n"
            "и узнай, какой ты кот сегодня!\n\n"
            "🌙 Это поможет лучше понять своё настроение"
        )
        desc_label = tk.Label(
            self.main_frame,
            text=description,
            font=("Arial", 14),
            fg="#ffffff",
            bg="#1a1a2e",
            justify="center"  # выравнивание текста по центру
        )
        desc_label.pack(pady=30)

        # --- Кнопка "Начать тест" ---
        start_button = tk.Button(
            self.main_frame,
            text="✨ Начать тест ✨",
            font=("Arial", 16, "bold"),
            fg="#ffffff",
            bg="#e94560",
            activebackground="#ff6b6b",  # цвет при нажатии
            activeforeground="#ffffff",
            width=20,
            height=2,
            border=0,
            cursor="hand2",  # курсор-рука при наведении
            command=self.start_test  # функция, которая вызовется при клике
        )
        start_button.pack(pady=40)

    def start_test(self):
        """
        Начинает тест: сбрасывает счётчики и показывает первый вопрос.
        """
        # Сбрасываем все переменные
        self.current_question = 0
        self.total_score = 0
        self.answers = []

        # Показываем первый вопрос
        self.show_question()

    def show_question(self):
        """
        Показывает текущий вопрос с вариантами ответов.
        """
        self.clear_screen()

        # Получаем данные текущего вопроса из списка
        question_data = QUESTIONS[self.current_question]

        # --- Прогресс (какой вопрос из скольки) ---
        progress_text = f"Вопрос {self.current_question + 1} из {len(QUESTIONS)}"
        progress_label = tk.Label(
            self.main_frame,
            text=progress_text,
            font=("Arial", 12),
            fg="#a0a0a0",  # серый цвет
            bg="#1a1a2e"
        )
        progress_label.pack(pady=10)

        # --- Прогресс-бар (визуальный) ---
        # Создаём рамку для прогресс-бара
        progress_frame = tk.Frame(self.main_frame, bg="#333333", height=10)
        progress_frame.pack(fill="x", pady=5)

        # Вычисляем ширину заполненной части (в процентах)
        progress_percent = (self.current_question + 1) / len(QUESTIONS)

        # Создаём заполненную часть прогресс-бара
        progress_fill = tk.Frame(
            progress_frame,
            bg="#e94560",
            height=10,
            width=int(560 * progress_percent)  # 560 = ширина окна минус отступы
        )
        progress_fill.place(x=0, y=0)

        # --- Текст вопроса ---
        question_label = tk.Label(
            self.main_frame,
            text=question_data["text"],
            font=("Arial", 18),
            fg="#ffffff",
            bg="#1a1a2e",
            wraplength=500  # перенос текста, если длинный
        )
        question_label.pack(pady=30)

        # --- Варианты ответов (кнопки) ---
        # Проходим по всем вариантам ответа
        for option in question_data["options"]:
            # Создаём кнопку для каждого варианта
            option_button = tk.Button(
                self.main_frame,
                text=option["text"],
                font=("Arial", 12),
                fg="#ffffff",
                bg="#16213e",
                activebackground="#e94560",
                activeforeground="#ffffff",
                width=40,
                height=2,
                border=0,
                cursor="hand2",
                # lambda нужна, чтобы передать score в функцию
                # без lambda все кнопки передавали бы одинаковый score
                command=lambda score=option["score"]: self.answer_question(score)
            )
            option_button.pack(pady=5)

            # Добавляем эффект при наведении мыши
            option_button.bind('<Enter>', lambda e, btn=option_button: btn.configure(bg="#e94560"))
            option_button.bind('<Leave>', lambda e, btn=option_button: btn.configure(bg="#16213e"))

    def answer_question(self, score):
        """
        Обрабатывает ответ на вопрос.
        score - количество баллов за выбранный ответ.
        """
        # Добавляем баллы к общему счёту
        self.total_score += score

        # Сохраняем ответ в список
        self.answers.append(score)

        # Переходим к следующему вопросу
        self.current_question += 1

        # Проверяем, есть ли ещё вопросы
        if self.current_question < len(QUESTIONS):
            # Показываем следующий вопрос
            self.show_question()
        else:
            # Вопросы закончились - показываем результат
            self.show_result()

    def get_cat_type(self):
        """
        Определяет тип кота по набранным баллам.
        Возвращает словарь с данными о типе кота.
        """
        # Проходим по всем типам котов
        for cat_type in CAT_TYPES:
            # Проверяем, попадают ли баллы в диапазон этого типа
            if cat_type["min_score"] <= self.total_score <= cat_type["max_score"]:
                return cat_type

        # Если ничего не подошло (не должно случиться), возвращаем первый тип
        return CAT_TYPES[0]

    def show_result(self):
        """
        Показывает результат теста с картинкой кота из API.
        """
        self.clear_screen()

        # Определяем тип кота
        cat_type = self.get_cat_type()

        # --- Заголовок "Твой результат" ---
        result_title = tk.Label(
            self.main_frame,
            text="✨ Твой результат ✨",
            font=("Arial", 16),
            fg="#a0a0a0",
            bg="#1a1a2e"
        )
        result_title.pack(pady=10)

        # --- Название типа кота ---
        cat_name_label = tk.Label(
            self.main_frame,
            text=cat_type["name"],
            font=("Arial", 24, "bold"),
            fg=cat_type["color"],  # используем цвет из данных
            bg="#1a1a2e"
        )
        cat_name_label.pack(pady=5)

        # --- Баллы ---
        score_label = tk.Label(
            self.main_frame,
            text=f"Твои баллы: {self.total_score} из {len(QUESTIONS) * 5}",
            font=("Arial", 11),
            fg="#a0a0a0",
            bg="#1a1a2e"
        )
        score_label.pack(pady=5)

        # --- Загрузка и отображение картинки кота ---
        # Создаём рамку для картинки
        image_frame = tk.Frame(self.main_frame, bg="#1a1a2e")
        image_frame.pack(pady=10)

        # Метка для картинки (сначала показываем текст загрузки)
        self.image_label = tk.Label(
            image_frame,
            text="🐱 Загружаю котика...",
            font=("Arial", 12),
            fg="#a0a0a0",
            bg="#1a1a2e"
        )
        self.image_label.pack()

        # Загружаем картинку в отдельном потоке, чтобы интерфейс не зависал
        # Но для простоты сделаем синхронно (подождём загрузку)
        self.load_cat_image(cat_type["image_folder"])

        # --- Описание типа ---
        # Создаём рамку с цветной границей для описания
        desc_frame = tk.Frame(
            self.main_frame,
            bg=cat_type["color"],
            padx=3,
            pady=3
        )
        desc_frame.pack(pady=10, padx=20, fill="x")

        # Внутренняя часть рамки
        desc_inner = tk.Frame(desc_frame, bg="#16213e")
        desc_inner.pack(fill="both", expand=True)

        desc_label = tk.Label(
            desc_inner,
            text=cat_type["description"],
            font=("Arial", 11),
            fg="#ffffff",
            bg="#16213e",
            wraplength=450,
            justify="center",
            padx=15,
            pady=10
        )
        desc_label.pack()

        # --- Кнопки ---
        buttons_frame = tk.Frame(self.main_frame, bg="#1a1a2e")
        buttons_frame.pack(pady=15)

        # Кнопка "Другой котик" - загружает новую картинку
        new_cat_button = tk.Button(
            buttons_frame,
            text="🔄 Другой котик",
            font=("Arial", 11),
            fg="#ffffff",
            bg="#16213e",
            activebackground="#e94560",
            activeforeground="#ffffff",
            width=14,
            height=2,
            border=0,
            cursor="hand2",
            command=lambda: self.load_cat_image(cat_type["image_folder"])
        )
        new_cat_button.pack(side="left", padx=5)

        retry_button = tk.Button(
            buttons_frame,
            text="🔁 Заново",
            font=("Arial", 11),
            fg="#ffffff",
            bg="#16213e",
            activebackground="#e94560",
            activeforeground="#ffffff",
            width=14,
            height=2,
            border=0,
            cursor="hand2",
            command=self.start_test
        )
        retry_button.pack(side="left", padx=5)

        home_button = tk.Button(
            buttons_frame,
            text="🏠 На главную",
            font=("Arial", 11),
            fg="#ffffff",
            bg="#16213e",
            activebackground="#e94560",
            activeforeground="#ffffff",
            width=14,
            height=2,
            border=0,
            cursor="hand2",
            command=self.show_start_screen
        )
        home_button.pack(side="left", padx=5)

    def load_cat_image(self, image_folder):
        """
        Загружает случайную картинку кота из локальной папки.

        Параметры:
            image_folder - название папки с картинками (sleepy, happy и т.д.)
        """
        self.image_label.config(text="🐱 Ищу котика...", image="")

        self.window.update()

        image_path = get_random_local_image(image_folder)

        if image_path:
            photo = load_local_image(image_path, max_width=200, max_height=200)

            if photo:
                self.current_photo = photo

                self.image_label.config(image=photo, text="")
            else:
                self.image_label.config(text="😿 Не удалось загрузить картинку")
        else:
            self.image_label.config(text="😿 Картинки не найдены\nДобавь в папку images/")

    def run(self):
        """
        Запускает приложение.
        mainloop() - это бесконечный цикл, который ждёт действий пользователя.
        """
        self.window.mainloop()

# ============================================================
# ФУНКЦИИ ПРОВЕРКИ ТАРО
# ============================================================
class Deck:

    BASEPATH = 'images/tarot/png/'

    def __init__(self):
        import json
        
        with open('markup.json', 'r') as markup_file:
            markup = json.load(markup_file)

        self.cards = []

        for i in markup:
            self.cards.append(TarotCard(i['name'], i['id'], self.BASEPATH + i['name'] + '.png'))
    
    def pull_card(self):
        import random

        card = random.choice(self.cards)
        self.cards.remove(card)
        return card

class TarotCard:

    def __init__(self, name, value, image_path):
        self.name = name
        self.value = value
        self.image_path = image_path

def get_prediction(cards):
    import requests
    import base64

    auth = "Basic " + base64.b64encode("649129:12788919b4c04b4ce2ddd4c31b36260a2aecf2d9".encode()).decode()

    r = requests.post("https://json.astrologyapi.com/v1/tarot_predictions", 
        headers = {
            'Authorization': auth,
            'Content-Type': 'application/json'
        },
        params = {
            'love': cards[0].value,
            'career': cards[1].value,
            'finance': cards[2].value
        })

    return r.json()

class Layout:

    def __init__(self, cards = {}):
        self.cards = cards

    def append_card(self, theme, card):
        self.cards[theme] = card

class TarotApp:
    from PIL import Image, ImageTk

    """
    Проверка расклада таро
    """

    def __init__(self, root):
        """
        Конструктор - вызывается при создании объекта.
        Здесь мы настраиваем главное окно приложения.
        """
        self.root = root
        self.root.title("Расклад таро")
        self.root.geometry("1000x1000")  
        self.root.configure(bg="#1a1a2e")  

        self.root.resizable(False, False)

        self.main_frame = tk.Frame(self.root, bg="#1a1a2e")
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        self.deck = Deck()
        self.show_start_screen()

    def clear_screen(self):
        """
        Очищает экран - удаляет все элементы из main_frame.
        Вызываем перед показом нового экрана.
        """
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def run(self):
        """
        Запускает приложение.
        mainloop() - это бесконечный цикл, который ждёт действий пользователя.
        """
        self.root.mainloop()

    def show_start_screen(self):
        """
        Главное окно с предложением расклада
        """
        self.clear_screen()

        title_label = tk.Label(
            self.main_frame,
            text="Сделаем расклад таро?",
            font=("Arial", 24, "bold"),
            fg="#e94560",  
            bg="#1a1a2e"  
        )
        title_label.pack(pady=40)  

        description = (
            "Попроси разложить карты таро"
            "и узнай, что тебя ждет в жизни"
        )
        desc_label = tk.Label(
            self.main_frame,
            text=description,
            font=("Arial", 14),
            fg="#ffffff",
            bg="#1a1a2e",
            justify="center"  
        )
        desc_label.pack(pady=30)

        # --- Кнопка "Начать тест" ---
        start_button = tk.Button(
            self.main_frame,
            text="✨ Начать расклад ✨",
            font=("Arial", 16, "bold"),
            fg="#ffffff",
            bg="#e94560",
            activebackground="#ff6b6b",  
            activeforeground="#ffffff",
            width=20,
            height=2,
            border=0,
            cursor="hand2",  
            command=self.start_test  
        )
        start_button.pack(pady=40)  
    
    def start_test(self):
        self.clear_screen()

        self.canvas = tk.Canvas(self.main_frame, bg="#1a1a2e", highlightthickness=0, borderwidth=0, relief='flat')
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        img = Image.open('./images/tarot/png/back.png')
        img = img.resize((200, 378), Image.Resampling.LANCZOS)
        self.deck_img = ImageTk.PhotoImage(img)
        self.deck_draw = self.canvas.create_image(150, 200, image=self.deck_img)

        self.card_images = {}  
        self.cards_for_prediction = []
        
        for i in range(1, 4):
            drawn_card = self.deck.pull_card()
            self.cards_for_prediction.append(drawn_card)

            img = Image.open(drawn_card.image_path)
            img = img.resize((200, 378), Image.Resampling.LANCZOS)
            card_img = ImageTk.PhotoImage(img)
            
            self.card_images[f"card_{i}"] = card_img  
            self.canvas.create_image(i * 200 + 50 * i, 600, image=card_img)

        
        self.prediction = get_prediction((self.cards_for_prediction))
        # Для тестирования
        # self.prediction = {'love': 'The singles and eligible may find love interest at their work place. You may be attracted to a married person who may not reveal his marital status to you. Some background search will help. You may come across someone you will seem to be a perfect match for you; who will revere you and respect you for who you are. This may prove to be a very passionate phase in your love life. Emotions shall be on a roller coaster; desires and urges shall climax.  Your love feelings shall be positively reciprocated in a big way! If you have been facing problems in your relationships, today is the day to use your communicative skills effectively and clear all differences. Your soothing words will bring the other person around to see and understand your point of view. You may look to introduce some fun elements in your relationship. You can plan an adventurous trip to an exotic place or indulge in some energetic, outdoor sports such as paragliding. You can set out to explore new unvisited places of interest. Be careful not to be so lost in your love life that you ignore other important aspect of your life.', 'career': 'Time is ripe to put your best foot forward. Your ambitious and farsighted vision will help you achieve your goals today. You shall come up with decisive suggestions which will have long term impact. Many possibilities will open up before you. You shall be able to make the right choices with a clear mind and a positive self-righteousness. You will come across as a creative and formidable force. You will come across as creative, passionate and energetic person. You may be offered a new job or increased responsibilities today. You shall get ample opportunities to prove your work capabilities. You will make outstanding progress at work and win accolades and promotions. Those who are stuck up in a stagnant job may decide to opt out and look for more challenging openings. If you have been thinking to be self-employed, then this may turn out to be just the right career choice for you. It is time to implement any new business strategy you might have and take control of your business dealings. You shall benefit from the advice given by an experienced person. Explore your options, dream big and try new things, but remember, you shall alone be responsible and accountable for your actions and decisions.', 'finance': 'This may be an exceptionally rewarding and profitable period for you. A new job may be offered to you. You may get a chance to work with an experienced person who will mentor you in the new occupation. You would be able to learn many new tricks of trade from him. You shall get enough opportunities prove your mettle in your area of expertise. You shall be able to complete your assignments successfully and this may find expression in form of a promotion or elevated status. You are all set to take risks and invest in ventures which you think will yield you abundant returns. In case you are facing a financial crunch, you may look out for an additional source or means of earning income. It might as well be trading or commission related work. Any work which gives you monetary freedom is fine to you. A newly discovered talent can be put to professional practice. A windfall gain is possible. Freshers from college may decide to venture into business. Businessmen may come up with new offers to attract customers and thereby increase their sales and revenues. You may proceed with new projects, fresh investments, etc.'}

        self.text_widget = tk.Text(
            self.canvas,
            height=20,
            width=70,
            wrap="word",
            bg="#1a1a2e",
            fg="white"
        )

        self.text_window = self.canvas.create_window(550, 190, window=self.text_widget)

        button_frame = tk.Frame(self.canvas, bg="#1a1a2e")
    
        # Создаем кнопки внутри Frame
        button1 = tk.Button(
            button_frame,
            text="Что меня ждет в личной жизни?",
            font=("Arial", 12, "bold"),
            fg="#ffffff",
            bg="#e94560",
            width=15,
            height=2,
            command=lambda: self.update_text(self.prediction['love']),
            justify="center",
            wraplength=150
        )
        
        button2 = tk.Button(
            button_frame,
            text="Что меня ждет в карьере?",
            font=("Arial", 12, "bold"),
            fg="#ffffff",
            bg="#e94560",
            width=15,
            height=2,
            command=lambda: self.update_text(self.prediction['career']),
            justify="center",
            wraplength=150
        )
        
        button3 = tk.Button(
            button_frame,
            text="Что меня ждет в финансах?",
            font=("Arial", 12, "bold"),
            fg="#ffffff",
            bg="#e94560",
            width=15,
            height=2,
            command=lambda: self.update_text(self.prediction['finance']),
            justify="center",
            wraplength=150
        )
        
        button1.pack(side="left", padx=45, pady=5)
        button2.pack(side="left", padx=45, pady=5)
        button3.pack(side="left", padx=45, pady=5)

        self.button_frame_window = self.canvas.create_window(
            500,      
            850,    
            window=button_frame
        )


    def update_text(self, new_text):
        self.text_widget.config(state="normal")
        self.text_widget.delete("1.0", "end")
        self.text_widget.insert("1.0", new_text)
        self.text_widget.config(state="disabled")
# ============================================================
# ТОЧКА ВХОДА В ПРОГРАММУ
# ============================================================

# Эта проверка нужна, чтобы код ниже выполнялся только при запуске файла напрямую
# (а не при импорте в другой файл)
if __name__ == "__main__":
    # Создаём экземпляр приложения
    # app = CatMoodTestApp()
    root = tk.Tk()
    app = TarotApp(root)

    # Запускаем приложение
    app.run()
