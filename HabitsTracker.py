import sys
import os
import time
import json
from datetime import datetime, timedelta, date
import sqlite3

try:
    # Импортируем всё что нужно по отдельности
    from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget
    from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout
    from PyQt5.QtWidgets import QLabel, QLineEdit, QPushButton
    from PyQt5.QtWidgets import QListWidget, QListWidgetItem, QTabWidget
    from PyQt5.QtWidgets import QTextEdit, QCalendarWidget, QMessageBox
    from PyQt5.QtWidgets import QGroupBox, QFormLayout, QComboBox
    from PyQt5.QtWidgets import QProgressBar, QTableWidget, QTableWidgetItem
    from PyQt5.QtWidgets import QHeaderView, QDialog, QFrame, QToolButton
    from PyQt5.QtWidgets import QStatusBar, QAction, QMenu, QSizePolicy
    from PyQt5.QtWidgets import QGraphicsDropShadowEffect, QScrollArea, QGridLayout

    from PyQt5.QtCore import Qt, QDate, QSize, QSettings
    from PyQt5.QtGui import QFont, QColor, QTextCharFormat, QBrush
    from PyQt5.QtGui import QIcon, QPixmap, QPainter, QPalette

except ImportError as e:
    print(f"Ошибка импорта PyQt5: {e}")
    print("\nУстановите PyQt5:")
    print("pip install PyQt5")
    sys.exit(1)

# Регистрируем адаптеры и конвертеры для datetime перед созданием соединения
def adapt_datetime(dt):
    """Конвертировать datetime в строку ISO формата"""
    if isinstance(dt, datetime):
        return dt.isoformat()
    elif isinstance(dt, date):
        return dt.isoformat()
    return str(dt)

def convert_datetime(timestamp):
    """Конвертировать строку из базы данных в datetime"""
    if timestamp is None:
        return None

    if isinstance(timestamp, bytes):
        timestamp = timestamp.decode('utf-8')

    # Пробуем разные форматы дат
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(timestamp, fmt)
        except ValueError:
            continue

    # Если ни один формат не подошел, возвращаем строку
    return timestamp

def convert_date(timestamp):
    """Конвертировать строку из базы данных в date"""
    dt = convert_datetime(timestamp)
    if isinstance(dt, datetime):
        return dt.date()
    return dt

# Регистрируем конвертеры глобально
sqlite3.register_adapter(datetime, adapt_datetime)
sqlite3.register_adapter(date, adapt_datetime)
sqlite3.register_converter("timestamp", convert_datetime)
sqlite3.register_converter("datetime", convert_datetime)
sqlite3.register_converter("date", convert_date)

class SettingsManager:
    """Менеджер настроек приложения"""
    def __init__(self):
        self.settings = QSettings("HabitTracker", "AppSettings")

    def get_theme(self):
        """Получить текущую тему"""
        return self.settings.value("theme", "light")

    def set_theme(self, theme):
        """Установить тему"""
        self.settings.setValue("theme", theme)

    def get_window_geometry(self):
        """Получить геометрию окна"""
        return self.settings.value("window_geometry")

    def set_window_geometry(self, geometry):
        """Сохранить геометрию окна"""
        self.settings.setValue("window_geometry", geometry)

    def get_window_state(self):
        """Получить состояние окна"""
        return self.settings.value("window_state")

    def set_window_state(self, state):
        """Сохранить состояние окна"""
        self.settings.setValue("window_state", state)

class ThemeManager:
    """Менеджер тем приложения"""

    @staticmethod
    def get_light_theme():
        """Светлая тема"""
        return {
            "name": "light",
            "primary": "#4CAF50",
            "secondary": "#2196F3",
            "accent": "#FF9800",
            "error": "#F44336",
            "success": "#4CAF50",
            "warning": "#FF9800",
            "info": "#2196F3",

            "background": "#f8f9fa",
            "surface": "#ffffff",
            "card_background": "#ffffff",
            "card_border": "#e0e0e0",

            "text_primary": "#2c3e50",
            "text_secondary": "#7f8c8d",
            "text_disabled": "#bdc3c7",

            "border": "#e0e0e0",
            "divider": "#f0f0f0",

            "hover": "#f5f5f5",
            "selected": "#e3f2fd",
            "active": "#4CAF50",

            "shadow": "rgba(0, 0, 0, 0.1)",
            "overlay": "rgba(0, 0, 0, 0.5)",

            "button_primary": "#4CAF50",
            "button_secondary": "#2196F3",
            "button_success": "#4CAF50",
            "button_error": "#F44336",
            "button_warning": "#FF9800",

            "progress_bar": "#4CAF50",
            "progress_background": "#f0f0f0",

            "calendar_background": "#ffffff",
            "calendar_text": "#2c3e50",
            "calendar_selected": "#4CAF50",
            "calendar_completed": "#d4edda",
            "calendar_missed": "#f8d7da",

            "table_background": "#ffffff",
            "table_header": "#f8f9fa",
            "table_row_even": "#ffffff",
            "table_row_odd": "#f9f9f9",

            "menu_background": "#ffffff",
            "menu_text": "#2c3e50",
            "menu_hover": "#e3f2fd",

            "status_bar": "#2c3e50",
            "status_text": "#ffffff"
        }

    @staticmethod
    def get_dark_theme():
        """Темная тема"""
        return {
            "name": "dark",
            "primary": "#66BB6A",
            "secondary": "#64B5F6",
            "accent": "#FFB74D",
            "error": "#EF5350",
            "success": "#66BB6A",
            "warning": "#FFB74D",
            "info": "#64B5F6",

            "background": "#121212",
            "surface": "#1e1e1e",
            "card_background": "#2d2d2d",
            "card_border": "#404040",

            "text_primary": "#ffffff",
            "text_secondary": "#b0b0b0",
            "text_disabled": "#666666",

            "border": "#404040",
            "divider": "#333333",

            "hover": "#3d3d3d",
            "selected": "#2d3d4d",
            "active": "#66BB6A",

            "shadow": "rgba(0, 0, 0, 0.3)",
            "overlay": "rgba(0, 0, 0, 0.7)",

            "button_primary": "#66BB6A",
            "button_secondary": "#64B5F6",
            "button_success": "#66BB6A",
            "button_error": "#EF5350",
            "button_warning": "#FFB74D",

            "progress_bar": "#66BB6A",
            "progress_background": "#404040",

            "calendar_background": "#2d2d2d",
            "calendar_text": "#ffffff",
            "calendar_selected": "#66BB6A",
            "calendar_completed": "#2d4d2d",
            "calendar_missed": "#4d2d2d",

            "table_background": "#2d2d2d",
            "table_header": "#3d3d3d",
            "table_row_even": "#2d2d2d",
            "table_row_odd": "#333333",

            "menu_background": "#2d2d2d",
            "menu_text": "#ffffff",
            "menu_hover": "#3d4d5d",

            "status_bar": "#1a1a1a",
            "status_text": "#ffffff"
        }

    @staticmethod
    def get_blue_theme():
        """Синяя тема"""
        return {
            "name": "blue",
            "primary": "#2196F3",
            "secondary": "#4CAF50",
            "accent": "#FF9800",
            "error": "#F44336",
            "success": "#4CAF50",
            "warning": "#FF9800",
            "info": "#2196F3",

            "background": "#e3f2fd",
            "surface": "#ffffff",
            "card_background": "#ffffff",
            "card_border": "#bbdefb",

            "text_primary": "#0d47a1",
            "text_secondary": "#1976d2",
            "text_disabled": "#90caf9",

            "border": "#bbdefb",
            "divider": "#e3f2fd",

            "hover": "#f3f9ff",
            "selected": "#e3f2fd",
            "active": "#2196F3",

            "shadow": "rgba(33, 150, 243, 0.2)",
            "overlay": "rgba(13, 71, 161, 0.5)",

            "button_primary": "#2196F3",
            "button_secondary": "#4CAF50",
            "button_success": "#4CAF50",
            "button_error": "#F44336",
            "button_warning": "#FF9800",

            "progress_bar": "#2196F3",
            "progress_background": "#e3f2fd",

            "calendar_background": "#ffffff",
            "calendar_text": "#0d47a1",
            "calendar_selected": "#2196F3",
            "calendar_completed": "#d4edda",
            "calendar_missed": "#f8d7da",

            "table_background": "#ffffff",
            "table_header": "#e3f2fd",
            "table_row_even": "#ffffff",
            "table_row_odd": "#f5fbff",

            "menu_background": "#ffffff",
            "menu_text": "#0d47a1",
            "menu_hover": "#e3f2fd",

            "status_bar": "#1976d2",
            "status_text": "#ffffff"
        }

    @staticmethod
    def get_themes():
        """Получить список доступных тем"""
        return {
            "light": "Светлая",
            "dark": "Темная",
            "blue": "Синяя"
        }

    @staticmethod
    def get_theme_by_name(name):
        """Получить тему по имени"""
        if name == "dark":
            return ThemeManager.get_dark_theme()
        elif name == "blue":
            return ThemeManager.get_blue_theme()
        else:
            return ThemeManager.get_light_theme()

class StyledButton(QPushButton):
    """Стилизованная кнопка с поддержкой тем"""
    def __init__(self, text="", color=None, theme=None):
        super().__init__(text)
        self.theme = theme
        self.custom_color = color
        self.setMinimumHeight(40)
        self.setCursor(Qt.PointingHandCursor)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setXOffset(0)
        shadow.setYOffset(2)
        shadow.setColor(QColor(0, 0, 0, 60))
        self.setGraphicsEffect(shadow)

        self.update_style()

    def set_theme(self, theme):
        """Установить тему"""
        self.theme = theme
        self.update_style()

    def update_style(self):
        """Обновить стиль кнопки"""
        if not self.theme:
            return

        color = self.custom_color if self.custom_color else self.theme["button_primary"]

        style = f"""
        QPushButton {{
            background-color: {color};
            color: white;
            border: none;
            border-radius: 8px;
            padding: 10px 20px;
            font-weight: bold;
            font-size: 14px;
        }}
        QPushButton:hover {{
            background-color: {self.darken_color(color, 20)};
        }}
        QPushButton:pressed {{
            background-color: {self.darken_color(color, 30)};
        }}
        QPushButton:disabled {{
            background-color: {self.theme['text_disabled']};
            color: {self.theme['text_secondary']};
        }}
        """
        self.setStyleSheet(style)

    def darken_color(self, color, percent):
        """Затемнить цвет на указанный процент"""
        c = QColor(color)
        return c.darker(100 + percent).name()

class StyledCard(QFrame):
    """Стилизованная карточка с поддержкой тем"""
    def __init__(self, parent=None, theme=None):
        super().__init__(parent)
        self.theme = theme
        self.setFrameShape(QFrame.NoFrame)
        self.setFrameShadow(QFrame.Plain)
        self.setLineWidth(0)
        self.setMidLineWidth(0)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setXOffset(0)
        shadow.setYOffset(3)
        shadow.setColor(QColor(0, 0, 0, 30))
        self.setGraphicsEffect(shadow)

        self.update_style()

    def set_theme(self, theme):
        """Установить тему"""
        self.theme = theme
        self.update_style()

    def update_style(self):
        """Обновить стиль карточки"""
        if not self.theme:
            return

        style = f"""
        QFrame {{
            background-color: {self.theme['card_background']};
            border-radius: 10px;
            border: 1px solid {self.theme['card_border']};
        }}
        """
        self.setStyleSheet(style)

class ThemeDialog(QDialog):
    """Диалог выбора темы"""
    def __init__(self, parent=None, current_theme="light"):
        super().__init__(parent)
        self.current_theme = current_theme
        self.selected_theme = current_theme
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("🎨 Выбор темы")
        self.setFixedSize(500, 400)

        main_layout = QVBoxLayout()

        title = QLabel("Выбор темы оформления")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title.setStyleSheet("color: #2c3e50; padding: 10px;")
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)

        card = QFrame()
        card.setFrameShape(QFrame.NoFrame)
        card.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border-radius: 10px;
            }
        """)
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(20)
        card_layout.setContentsMargins(20, 20, 20, 20)

        themes = ThemeManager.get_themes()
        self.theme_buttons = []

        for theme_id, theme_name in themes.items():
            theme_btn = QPushButton(theme_name)
            theme_btn.setCheckable(True)
            theme_btn.setMinimumHeight(60)
            theme_btn.setFont(QFont("Segoe UI", 12))

            # Устанавливаем стиль для каждой темы
            if theme_id == "light":
                theme_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #f8f9fa;
                        color: #2c3e50;
                        border: 2px solid #e0e0e0;
                        border-radius: 8px;
                        text-align: left;
                        padding-left: 20px;
                    }
                    QPushButton:hover {
                        background-color: #e9ecef;
                        border-color: #4CAF50;
                    }
                    QPushButton:checked {
                        background-color: #4CAF50;
                        color: white;
                        border-color: #4CAF50;
                    }
                """)
            elif theme_id == "dark":
                theme_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #2d2d2d;
                        color: #ffffff;
                        border: 2px solid #404040;
                        border-radius: 8px;
                        text-align: left;
                        padding-left: 20px;
                    }
                    QPushButton:hover {
                        background-color: #3d3d3d;
                        border-color: #66BB6A;
                    }
                    QPushButton:checked {
                        background-color: #66BB6A;
                        color: white;
                        border-color: #66BB6A;
                    }
                """)
            elif theme_id == "blue":
                theme_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #e3f2fd;
                        color: #0d47a1;
                        border: 2px solid #bbdefb;
                        border-radius: 8px;
                        text-align: left;
                        padding-left: 20px;
                    }
                    QPushButton:hover {
                        background-color: #bbdefb;
                        border-color: #2196F3;
                    }
                    QPushButton:checked {
                        background-color: #2196F3;
                        color: white;
                        border-color: #2196F3;
                    }
                """)

            theme_btn.theme_id = theme_id
            theme_btn.clicked.connect(lambda checked, btn=theme_btn: self.on_theme_selected(btn))

            if theme_id == self.current_theme:
                theme_btn.setChecked(True)

            card_layout.addWidget(theme_btn)
            self.theme_buttons.append(theme_btn)

        card_layout.addStretch()
        main_layout.addWidget(card)

        button_layout = QHBoxLayout()
        button_layout.addStretch()

        cancel_button = QPushButton("Отмена")
        cancel_button.setMinimumHeight(40)
        cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        cancel_button.clicked.connect(self.reject)

        apply_button = QPushButton("Применить")
        apply_button.setMinimumHeight(40)
        apply_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #43A047;
            }
        """)
        apply_button.clicked.connect(self.accept)

        button_layout.addWidget(cancel_button)
        button_layout.addWidget(apply_button)

        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)

        self.setStyleSheet("""
            QDialog {
                background-color: #f8f9fa;
            }
        """)

    def on_theme_selected(self, button):
        """Обработка выбора темы"""
        for btn in self.theme_buttons:
            if btn != button:
                btn.setChecked(False)
        self.selected_theme = button.theme_id

    def get_selected_theme(self):
        """Получить выбранную тему"""
        return self.selected_theme

class HabitTrackerDB:
    """Класс для работы с базой данных"""
    def __init__(self, db_name="habits.db"):
        # Используем абсолютный путь
        import os
        self.db_name = os.path.join(os.path.dirname(__file__), db_name)
        self.conn = None
        self.connect()

    def connect(self):
        """Устанавливаем соединение с базой данных"""
        if self.conn:
            try:
                self.conn.close()
            except:
                pass

        # Используем detect_types для поддержки datetime
        # И отключаем конвертеры по умолчанию с помощью isolation_level=None
        self.conn = sqlite3.connect(
            self.db_name,
            detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES,
            isolation_level=None
        )
        # Отключаем конвертеры по умолчанию
        self.conn.execute("PRAGMA legacy_alter_table = ON")
        self.create_tables()
        self.update_tables()

    def create_tables(self):
        cursor = self.conn.cursor()

        # Используем TEXT для хранения дат в ISO формате
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS habits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                frequency TEXT DEFAULT 'daily',
                target_days INTEGER DEFAULT 7,
                color TEXT DEFAULT '#4CAF50',
                icon TEXT DEFAULT 'default',
                created_date TEXT DEFAULT (datetime('now', 'localtime'))
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS habit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                habit_id INTEGER,
                date TEXT NOT NULL,
                completed BOOLEAN DEFAULT 0,
                notes TEXT,
                FOREIGN KEY (habit_id) REFERENCES habits (id) ON DELETE CASCADE
            )
        ''')

        # Создаем индекс для ускорения запросов
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_habit_logs_habit_date ON habit_logs(habit_id, date)')

        self.conn.commit()

    def update_tables(self):
        cursor = self.conn.cursor()
        cursor.execute("PRAGMA table_info(habits)")
        columns = {column[1] for column in cursor.fetchall()}

        if 'color' not in columns:
            try:
                cursor.execute("ALTER TABLE habits ADD COLUMN color TEXT DEFAULT '#4CAF50'")
                self.conn.commit()
            except:
                pass

        if 'target_days' not in columns:
            try:
                cursor.execute("ALTER TABLE habits ADD COLUMN target_days INTEGER DEFAULT 7")
                self.conn.commit()
            except:
                pass

        if 'icon' not in columns:
            try:
                cursor.execute("ALTER TABLE habits ADD COLUMN icon TEXT DEFAULT 'default'")
                self.conn.commit()
            except:
                pass

    def add_habit(self, name, description="", frequency="daily", target_days=7, color="#4CAF50", icon="default"):
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO habits (name, description, frequency, target_days, color, icon) VALUES (?, ?, ?, ?, ?, ?)",
            (name, description, frequency, target_days, color, icon)
        )
        self.conn.commit()
        return cursor.lastrowid

    def get_habits(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM habits ORDER BY created_date")
        rows = cursor.fetchall()

        habits = []
        for row in rows:
            # Преобразуем строку даты в объект datetime если нужно
            if len(row) > 7 and isinstance(row[7], str):
                try:
                    row = list(row)
                    row[7] = convert_datetime(row[7])
                    row = tuple(row)
                except:
                    pass
            habits.append(row)

        return habits

    def get_habit(self, habit_id):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM habits WHERE id = ?", (habit_id,))
        row = cursor.fetchone()

        if row and len(row) > 7 and isinstance(row[7], str):
            try:
                row = list(row)
                row[7] = convert_datetime(row[7])
                row = tuple(row)
            except:
                pass

        return row

    def update_habit(self, habit_id, name, description, frequency, target_days, color, icon):
        cursor = self.conn.cursor()
        cursor.execute(
            """UPDATE habits SET name = ?, description = ?, frequency = ?, 
               target_days = ?, color = ?, icon = ? WHERE id = ?""",
            (name, description, frequency, int(target_days), color, icon, habit_id)
        )
        self.conn.commit()

    def delete_habit(self, habit_id):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM habits WHERE id = ?", (habit_id,))
        # habit_logs удалятся автоматически благодаря каскадному удалению
        self.conn.commit()

    def mark_completed(self, habit_id, date=None, notes=""):
        if date is None:
            date = datetime.now()
        elif isinstance(date, str):
            date = datetime.strptime(date, "%Y-%m-%d")

        date_str = date.strftime("%Y-%m-%d")

        cursor = self.conn.cursor()

        cursor.execute(
            "SELECT id FROM habit_logs WHERE habit_id = ? AND date = ?",
            (habit_id, date_str)
        )

        if cursor.fetchone():
            cursor.execute(
                "UPDATE habit_logs SET completed = 1, notes = ? WHERE habit_id = ? AND date = ?",
                (notes, habit_id, date_str)
            )
        else:
            cursor.execute(
                "INSERT INTO habit_logs (habit_id, date, completed, notes) VALUES (?, ?, 1, ?)",
                (habit_id, date_str, notes)
            )

        self.conn.commit()

    def mark_missed(self, habit_id, date=None):
        if date is None:
            date = datetime.now()
        elif isinstance(date, str):
            date = datetime.strptime(date, "%Y-%m-%d")

        date_str = date.strftime("%Y-%m-%d")

        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT OR REPLACE INTO habit_logs (habit_id, date, completed, notes) VALUES (?, ?, 0, 'Пропущено')",
            (habit_id, date_str)
        )
        self.conn.commit()

    def get_habit_logs(self, habit_id, days=30):
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT date, completed, notes FROM habit_logs 
            WHERE habit_id = ? AND date BETWEEN ? AND ?
            ORDER BY date
        ''', (habit_id, start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")))

        rows = cursor.fetchall()

        logs = []
        for date_str, completed, notes in rows:
            # Преобразуем строку даты в объект date
            try:
                if isinstance(date_str, str):
                    date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
                elif isinstance(date_str, datetime):
                    date_obj = date_str.date()
                else:
                    date_obj = datetime.now().date()
            except:
                date_obj = datetime.now().date()

            logs.append((date_obj, bool(completed), notes))

        return logs

    def get_habit_stats(self, habit_id, days=30):
        habit = self.get_habit(habit_id)
        if not habit:
            return None

        logs = self.get_habit_logs(habit_id, days)

        completed_days = sum(1 for log in logs if log[1])
        total_days = len(logs)
        success_rate = (completed_days / total_days * 100) if total_days > 0 else 0

        current_streak = 0
        today = datetime.now().date()

        for i in range(days + 1):
            check_date = today - timedelta(days=i)
            check_date_str = check_date.strftime("%Y-%m-%d")

            # Ищем запись для этой даты
            found = False
            for log_date, completed, _ in logs:
                if log_date == check_date and completed:
                    found = True
                    break

            if found:
                current_streak += 1
            else:
                break

        best_streak = 0
        current = 0

        # Сортируем логи по дате
        sorted_logs = sorted(logs, key=lambda x: x[0])
        for log in sorted_logs:
            if log[1]:
                current += 1
                best_streak = max(best_streak, current)
            else:
                current = 0

        target_days = 7
        if len(habit) > 4:
            try:
                target_days = int(habit[4])
            except (ValueError, TypeError):
                target_days = 7

        return {
            'name': habit[1],
            'target_days': target_days,
            'completed_days': completed_days,
            'total_days': total_days,
            'success_rate': success_rate,
            'current_streak': current_streak,
            'best_streak': best_streak,
            'color': habit[5] if len(habit) > 5 else '#4CAF50'
        }

    def get_today_habits(self):
        today = datetime.now().strftime("%Y-%m-%d")
        cursor = self.conn.cursor()

        cursor.execute('''
            SELECT h.id, h.name, 
                   COALESCE(h.color, '#4CAF50') as color,
                   COALESCE(h.icon, 'default') as icon,
                   CASE WHEN l.completed = 1 THEN 1 ELSE 0 END as completed
            FROM habits h
            LEFT JOIN habit_logs l ON h.id = l.habit_id AND l.date = ?
            ORDER BY h.created_date
        ''', (today,))

        return cursor.fetchall()

    def get_weekly_stats(self):
        cursor = self.conn.cursor()

        end_date = datetime.now()
        start_date = end_date - timedelta(days=6)

        cursor.execute('''
            SELECT h.id, h.name, COALESCE(h.color, '#4CAF50') as color,
                   SUM(CASE WHEN l.completed = 1 THEN 1 ELSE 0 END) as completed_days,
                   COUNT(DISTINCT l.date) as total_days
            FROM habits h
            LEFT JOIN habit_logs l ON h.id = l.habit_id AND l.date BETWEEN ? AND ?
            GROUP BY h.id, h.name, h.color
        ''', (start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")))

        return cursor.fetchall()

    def close(self):
        """Закрываем соединение с базой данных"""
        if self.conn:
            try:
                self.conn.close()
                self.conn = None
            except:
                pass

    def __del__(self):
        """Деструктор для гарантированного закрытия соединения"""
        self.close()

class AddHabitDialog(QDialog):
    """Диалог добавления/редактирования привычки с поддержкой тем"""
    def __init__(self, parent=None, habit_id=None, theme=None):
        super().__init__(parent)
        self.habit_id = habit_id
        self.db = HabitTrackerDB()
        self.theme = theme or ThemeManager.get_light_theme()
        self.init_ui()
        if habit_id:
            self.load_habit_data()

    def init_ui(self):
        self.setWindowTitle("➕ Добавить привычку" if not self.habit_id else "✎ Редактировать привычку")
        self.setFixedSize(500, 600)

        main_layout = QVBoxLayout()

        title = QLabel("Добавление привычки" if not self.habit_id else "Редактирование привычки")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title.setStyleSheet(f"color: {self.theme['text_primary']}; padding: 10px;")
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)

        card = StyledCard(theme=self.theme)
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(15)
        card_layout.setContentsMargins(20, 20, 20, 20)

        name_layout = QHBoxLayout()
        name_icon = QLabel("🏷️")
        name_icon.setFont(QFont("Segoe UI", 14))
        name_layout.addWidget(name_icon)

        name_label = QLabel("Название:")
        name_label.setFont(QFont("Segoe UI", 11, QFont.Bold))
        name_label.setStyleSheet(f"color: {self.theme['text_primary']};")
        name_layout.addWidget(name_label)
        name_layout.addStretch()

        card_layout.addLayout(name_layout)
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Например: Утренняя зарядка")
        self.name_input.setMinimumHeight(40)
        self.name_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {self.theme['surface']};
                color: {self.theme['text_primary']};
                border: 1px solid {self.theme['border']};
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 14px;
            }}
            QLineEdit:focus {{
                border-color: {self.theme['primary']};
            }}
            QLineEdit::placeholder {{
                color: {self.theme['text_disabled']};
            }}
        """)
        card_layout.addWidget(self.name_input)

        desc_layout = QHBoxLayout()
        desc_icon = QLabel("📝")
        desc_icon.setFont(QFont("Segoe UI", 14))
        desc_layout.addWidget(desc_icon)

        desc_label = QLabel("Описание:")
        desc_label.setFont(QFont("Segoe UI", 11, QFont.Bold))
        desc_label.setStyleSheet(f"color: {self.theme['text_primary']};")
        desc_layout.addWidget(desc_label)
        desc_layout.addStretch()

        card_layout.addLayout(desc_layout)
        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("Необязательное описание...")
        self.description_input.setMinimumHeight(100)
        self.description_input.setMaximumHeight(120)
        self.description_input.setStyleSheet(f"""
            QTextEdit {{
                background-color: {self.theme['surface']};
                color: {self.theme['text_primary']};
                border: 1px solid {self.theme['border']};
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 14px;
            }}
            QTextEdit:focus {{
                border-color: {self.theme['primary']};
            }}
        """)
        card_layout.addWidget(self.description_input)

        freq_layout = QHBoxLayout()
        freq_icon = QLabel("⏰")
        freq_icon.setFont(QFont("Segoe UI", 14))
        freq_layout.addWidget(freq_icon)

        freq_label = QLabel("Частота:")
        freq_label.setFont(QFont("Segoe UI", 11, QFont.Bold))
        freq_label.setStyleSheet(f"color: {self.theme['text_primary']};")
        freq_layout.addWidget(freq_label)
        freq_layout.addStretch()

        card_layout.addLayout(freq_layout)
        self.frequency_combo = QComboBox()
        self.frequency_combo.addItems(["Ежедневно", "Еженедельно", "Ежемесячно"])
        self.frequency_combo.setMinimumHeight(40)
        self.frequency_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {self.theme['surface']};
                color: {self.theme['text_primary']};
                border: 1px solid {self.theme['border']};
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 14px;
            }}
            QComboBox:hover {{
                border-color: {self.theme['hover']};
            }}
            QComboBox:focus {{
                border-color: {self.theme['primary']};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 30px;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid {self.theme['text_secondary']};
                margin-right: 10px;
            }}
            QComboBox QAbstractItemView {{
                background-color: {self.theme['surface']};
                color: {self.theme['text_primary']};
                border: 1px solid {self.theme['border']};
                selection-background-color: {self.theme['selected']};
            }}
        """)
        card_layout.addWidget(self.frequency_combo)

        target_layout = QHBoxLayout()
        target_icon = QLabel("🎯")
        target_icon.setFont(QFont("Segoe UI", 14))
        target_layout.addWidget(target_icon)

        target_label = QLabel("Цель (дней в неделю):")
        target_label.setFont(QFont("Segoe UI", 11, QFont.Bold))
        target_label.setStyleSheet(f"color: {self.theme['text_primary']};")
        target_layout.addWidget(target_label)
        target_layout.addStretch()

        card_layout.addLayout(target_layout)
        self.target_input = QLineEdit("7")
        self.target_input.setMinimumHeight(40)
        self.target_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {self.theme['surface']};
                color: {self.theme['text_primary']};
                border: 1px solid {self.theme['border']};
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 14px;
            }}
            QLineEdit:focus {{
                border-color: {self.theme['primary']};
            }}
        """)
        card_layout.addWidget(self.target_input)

        color_layout = QHBoxLayout()
        color_icon = QLabel("🎨")
        color_icon.setFont(QFont("Segoe UI", 14))
        color_layout.addWidget(color_icon)

        color_label = QLabel("Цвет:")
        color_label.setFont(QFont("Segoe UI", 11, QFont.Bold))
        color_label.setStyleSheet(f"color: {self.theme['text_primary']};")
        color_layout.addWidget(color_label)
        color_layout.addStretch()

        card_layout.addLayout(color_layout)

        color_widget = QWidget()
        color_widget_layout = QHBoxLayout(color_widget)
        color_widget_layout.setContentsMargins(0, 0, 0, 0)

        self.color_buttons = []
        colors = [
            ("#4CAF50", "Зеленый"),
            ("#2196F3", "Синий"),
            ("#FF9800", "Оранжевый"),
            ("#9C27B0", "Фиолетовый"),
            ("#F44336", "Красный"),
            ("#00BCD4", "Бирюзовый"),
            ("#FFEB3B", "Желтый"),
            ("#E91E63", "Розовый")
        ]

        for color_code, color_name in colors:
            color_btn = QToolButton()
            color_btn.setFixedSize(30, 30)
            color_btn.setStyleSheet(f"""
                QToolButton {{
                    background-color: {color_code};
                    border-radius: 15px;
                    border: 2px solid {self.theme['surface']};
                }}
                QToolButton:hover {{
                    border: 2px solid {self.theme['border']};
                }}
                QToolButton:checked {{
                    border: 2px solid {self.theme['text_primary']};
                }}
            """)
            color_btn.setCheckable(True)
            color_btn.setToolTip(color_name)
            color_btn.color = color_code
            color_btn.clicked.connect(self.on_color_selected)
            color_widget_layout.addWidget(color_btn)
            self.color_buttons.append(color_btn)

        color_widget_layout.addStretch()
        card_layout.addWidget(color_widget)
        self.selected_color = "#4CAF50"
        self.color_buttons[0].setChecked(True)

        main_layout.addWidget(card)

        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.cancel_button = StyledButton("Отмена", "#c02121", self.theme)
        self.cancel_button.clicked.connect(self.reject)

        self.save_button = StyledButton("Сохранить", "#219C26", self.theme)
        self.save_button.clicked.connect(self.save_habit)

        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.save_button)

        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)

        # Устанавливаем фон диалога
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {self.theme['background']};
                border: none;
            }}
            QLabel {{
                color: {self.theme['text_primary']};
            }}
        """)

    def on_color_selected(self):
        for btn in self.color_buttons:
            if btn.isChecked():
                self.selected_color = btn.color
                break

    def load_habit_data(self):
        habit = self.db.get_habit(self.habit_id)
        if habit:
            self.name_input.setText(habit[1])
            self.description_input.setText(habit[2] if habit[2] else "")

            frequency_map = {"daily": "Ежедневно", "weekly": "Еженедельно", "monthly": "Ежемесячно"}
            freq = frequency_map.get(habit[3], "Ежедневно")
            self.frequency_combo.setCurrentText(freq)

            target_days = habit[4] if len(habit) > 4 else 7
            self.target_input.setText(str(target_days))

            color = habit[5] if len(habit) > 5 else "#4CAF50"
            self.selected_color = color
            for btn in self.color_buttons:
                if btn.color == color:
                    btn.setChecked(True)
                    break

    def save_habit(self):
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Ошибка", "Введите название привычки")
            return

        description = self.description_input.toPlainText()

        frequency_map = {"Ежедневно": "daily", "Еженедельно": "weekly", "Ежемесячно": "monthly"}
        frequency = frequency_map[self.frequency_combo.currentText()]

        try:
            target_days = int(self.target_input.text())
        except:
            target_days = 7

        if self.habit_id:
            self.db.update_habit(self.habit_id, name, description, frequency, target_days, self.selected_color, "default")
        else:
            self.db.add_habit(name, description, frequency, target_days, self.selected_color, "default")

        self.accept()

    def closeEvent(self, event):
        self.db.close()
        event.accept()

class TodayTab(QWidget):
    """Вкладка "Сегодня" с поддержкой тем"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = HabitTrackerDB()
        self.theme = None
        self.init_ui()
        self.load_today_habits()

    def init_ui(self):
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(20)

        self.setLayout(self.layout)

    def set_theme(self, theme):
        """Установить тему"""
        self.theme = theme
        self.update_theme()

    def update_theme(self):
        """Обновить тему"""
        if not self.theme:
            return

        # Очищаем layout
        while self.layout.count():
            child = self.layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # Устанавливаем фон
        self.setStyleSheet(f"background-color: {self.theme['background']}; border: none;")

        # Заголовок
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)

        title = QLabel("Сегодня")
        title.setFont(QFont("Segoe UI", 24, QFont.Bold))
        title.setStyleSheet(f"color: {self.theme['text_primary']};")

        date_label = QLabel(datetime.now().strftime('%d %B %Y'))
        date_label.setFont(QFont("Segoe UI", 14))
        date_label.setStyleSheet(f"color: {self.theme['text_secondary']};")

        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(date_label)

        self.layout.addWidget(header_widget)

        # Карточка статистики
        stats_card = StyledCard(theme=self.theme)
        stats_layout = QHBoxLayout(stats_card)
        stats_layout.setContentsMargins(20, 20, 20, 20)

        weekly_stats = self.db.get_weekly_stats()

        if weekly_stats:
            for habit in weekly_stats:
                habit_id, name, color, completed, total = habit
                if total > 0:
                    progress = (completed / total) * 100

                    stat_widget = QWidget()
                    stat_layout = QVBoxLayout(stat_widget)

                    name_label = QLabel(name)
                    name_label.setFont(QFont("Segoe UI", 10, QFont.Bold))
                    name_label.setStyleSheet(f"color: {color};")
                    name_label.setWordWrap(True)

                    progress_text = QLabel(f"{completed}/{total} дней")
                    progress_text.setFont(QFont("Segoe UI", 9))
                    progress_text.setStyleSheet(f"color: {self.theme['text_secondary']};")

                    stat_layout.addWidget(name_label)
                    stat_layout.addWidget(progress_text)

                    stats_layout.addWidget(stat_widget)

        if not weekly_stats:
            no_stats_label = QLabel("Нет данных за неделю")
            no_stats_label.setFont(QFont("Segoe UI", 11))
            no_stats_label.setStyleSheet(f"color: {self.theme['text_disabled']};")
            no_stats_label.setAlignment(Qt.AlignCenter)
            stats_layout.addWidget(no_stats_label)

        self.layout.addWidget(stats_card)

        # Заголовок списка привычек
        habits_label = QLabel("Привычки на сегодня")
        habits_label.setFont(QFont("Segoe UI", 16, QFont.Bold))
        habits_label.setStyleSheet(f"color: {self.theme['text_primary']}; margin: 10px 0;")
        self.layout.addWidget(habits_label)

        # Список привычек
        self.habits_scroll = QScrollArea()
        self.habits_scroll.setWidgetResizable(True)
        self.habits_scroll.setFrameShape(QFrame.NoFrame)
        self.habits_scroll.setStyleSheet(f"""
            QScrollArea {{
                border: none;
                background-color: transparent;
            }}
            QScrollBar:vertical {{
                border: none;
                background-color: {self.theme['divider']};
                width: 10px;
                margin: 0px;
                border-radius: 5px;
            }}
            QScrollBar::handle:vertical {{
                background-color: {self.theme['text_secondary']};
                min-height: 20px;
                border-radius: 5px;
            }}
            QScrollBar::handle:vertical:hover {{
                background-color: {self.theme['text_primary']};
            }}
        """)

        self.habits_widget = QWidget()
        self.habits_layout = QVBoxLayout(self.habits_widget)
        self.habits_layout.setSpacing(15)
        self.habits_layout.setContentsMargins(5, 5, 5, 5)

        self.habits_scroll.setWidget(self.habits_widget)
        self.layout.addWidget(self.habits_scroll)

        # Кнопка обновления
        refresh_button = StyledButton("🔄 Обновить", self.theme["button_secondary"], self.theme)
        refresh_button.clicked.connect(self.load_today_habits)
        self.layout.addWidget(refresh_button)

        # Загружаем привычки
        self.load_today_habits()

    def load_today_habits(self):
        if not hasattr(self, 'habits_layout'):
            return

        while self.habits_layout.count():
            child = self.habits_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        try:
            habits = self.db.get_today_habits()
        except Exception as e:
            error_card = StyledCard(theme=self.theme)
            error_layout = QVBoxLayout(error_card)
            error_layout.setContentsMargins(30, 30, 30, 30)

            error_label = QLabel(f"Ошибка загрузки данных:\n{str(e)}")
            error_label.setStyleSheet(f"color: {self.theme['error']};")
            error_label.setAlignment(Qt.AlignCenter)

            error_layout.addWidget(error_label)
            self.habits_layout.addWidget(error_card)
            return

        if not habits:
            empty_card = StyledCard(theme=self.theme)
            empty_layout = QVBoxLayout(empty_card)
            empty_layout.setContentsMargins(30, 30, 30, 30)

            empty_icon = QLabel("🎉")
            empty_icon.setFont(QFont("Segoe UI", 48))
            empty_icon.setAlignment(Qt.AlignCenter)
            empty_icon.setStyleSheet(f"color: {self.theme['text_secondary']};")

            empty_text = QLabel("На сегодня привычек нет!\nДобавьте новые привычки во вкладке 'Все привычки'.")
            empty_text.setFont(QFont("Segoe UI", 12))
            empty_text.setStyleSheet(f"color: {self.theme['text_secondary']};")
            empty_text.setAlignment(Qt.AlignCenter)

            empty_layout.addWidget(empty_icon)
            empty_layout.addWidget(empty_text)

            self.habits_layout.addWidget(empty_card)
            return

        for habit in habits:
            habit_id, name, color, icon, completed = habit

            card = StyledCard(theme=self.theme)
            card.setMinimumHeight(80)

            card_layout = QHBoxLayout(card)
            card_layout.setContentsMargins(20, 15, 20, 15)

            left_widget = QWidget()
            left_layout = QVBoxLayout(left_widget)
            left_layout.setContentsMargins(0, 0, 0, 0)
            left_layout.setSpacing(5)

            status_icon = QLabel("✓" if completed else "○")
            status_icon.setFont(QFont("Segoe UI", 24))
            status_icon.setStyleSheet(f"color: {color};")
            status_icon.setAlignment(Qt.AlignCenter)

            status_text = QLabel("Выполнено" if completed else "Не выполнено")
            status_text.setFont(QFont("Segoe UI", 9))
            if not completed:
                status_text.setStyleSheet(f"color: {self.theme['text_secondary']};")
            else:
                status_text.setStyleSheet(f"color: {color}; font-weight: bold;")
            status_text.setAlignment(Qt.AlignCenter)

            left_layout.addWidget(status_icon)
            left_layout.addWidget(status_text)

            card_layout.addWidget(left_widget)

            middle_widget = QWidget()
            middle_layout = QVBoxLayout(middle_widget)
            middle_layout.setContentsMargins(15, 0, 15, 0)
            middle_layout.setSpacing(5)

            name_label = QLabel(name)
            name_label.setFont(QFont("Segoe UI", 14, QFont.Bold))
            if completed:
                name_label.setStyleSheet(f"text-decoration: line-through; color: {self.theme['text_disabled']};")
            else:
                name_label.setStyleSheet(f"color: {self.theme['text_primary']};")

            time_label = QLabel("Сегодня")
            time_label.setFont(QFont("Segoe UI", 11))
            time_label.setStyleSheet(f"color: {self.theme['text_secondary']};")

            middle_layout.addWidget(name_label)
            middle_layout.addWidget(time_label)

            card_layout.addWidget(middle_widget)

            card_layout.addStretch()

            if not completed:
                complete_button = StyledButton("Выполнить", color, self.theme)
                complete_button.setFixedWidth(100)
                complete_button.clicked.connect(lambda _, h_id=habit_id: self.mark_completed(h_id))
                card_layout.addWidget(complete_button)
            else:
                completed_label = QLabel("✓ Готово")
                completed_label.setFont(QFont("Segoe UI", 11, QFont.Bold))
                completed_label.setStyleSheet(f"color: {color};")
                card_layout.addWidget(completed_label)

            self.habits_layout.addWidget(card)

        self.habits_layout.addStretch()

    def mark_completed(self, habit_id):
        try:
            self.db.mark_completed(habit_id)
            self.load_today_habits()
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось отметить привычку: {str(e)}")

    def closeEvent(self, event):
        self.db.close()
        event.accept()

class HabitsTab(QWidget):
    """Вкладка "Все привычки" с поддержкой тем"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = HabitTrackerDB()
        self.theme = None
        self.selected_habit_id = None
        self.init_ui()
        self.load_habits()

    def init_ui(self):
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(20)

        self.setLayout(self.layout)

    def set_theme(self, theme):
        """Установить тему"""
        self.theme = theme
        self.update_theme()

    def update_theme(self):
        """Обновить тему"""
        if not self.theme:
            return

        # Очищаем layout
        while self.layout.count():
            child = self.layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # Устанавливаем фон
        self.setStyleSheet(f"background-color: {self.theme['background']}; border: none;")

        # Заголовок
        title = QLabel("Все привычки")
        title.setFont(QFont("Segoe UI", 24, QFont.Bold))
        title.setStyleSheet(f"color: {self.theme['text_primary']};")
        self.layout.addWidget(title)

        # Панель инструментов
        toolbar = QWidget()
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(0, 0, 0, 0)

        self.add_button = StyledButton("➕ Добавить привычку", self.theme["button_primary"], self.theme)
        self.add_button.clicked.connect(self.add_habit)

        self.edit_button = StyledButton("✎ Редактировать", self.theme["button_secondary"], self.theme)
        self.edit_button.clicked.connect(self.edit_habit)
        self.edit_button.setEnabled(False)

        self.delete_button = StyledButton("🗑️ Удалить", self.theme["button_error"], self.theme)
        self.delete_button.clicked.connect(self.delete_habit)
        self.delete_button.setEnabled(False)

        toolbar_layout.addWidget(self.add_button)
        toolbar_layout.addWidget(self.edit_button)
        toolbar_layout.addWidget(self.delete_button)
        toolbar_layout.addStretch()

        self.layout.addWidget(toolbar)

        # Контейнер для карточек привычек
        self.habits_widget = QWidget()
        self.habits_layout = QVBoxLayout(self.habits_widget)
        self.habits_layout.setSpacing(15)
        self.habits_layout.setContentsMargins(5, 5, 5, 5)

        # Прокручиваемая область
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet(f"""
            QScrollArea {{
                border: none;
                background-color: transparent;
            }}
            QScrollBar:vertical {{
                border: none;
                background-color: {self.theme['divider']};
                width: 10px;
                margin: 0px;
                border-radius: 5px;
            }}
            QScrollBar::handle:vertical {{
                background-color: {self.theme['text_secondary']};
                min-height: 20px;
                border-radius: 5px;
            }}
            QScrollBar::handle:vertical:hover {{
                background-color: {self.theme['text_primary']};
            }}
        """)
        scroll.setWidget(self.habits_widget)

        self.layout.addWidget(scroll)

        # Загружаем привычки
        self.load_habits()

    def create_habit_card(self, habit):
        """Создать карточку привычки"""
        card = StyledCard(theme=self.theme)
        card.setMinimumHeight(120)
        card.habit_id = habit[0]
        card.setCursor(Qt.PointingHandCursor)

        def on_card_clicked(event):
            self.select_habit(habit[0], card)
            event.accept()

        card.mousePressEvent = on_card_clicked

        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(10)

        top_layout = QHBoxLayout()

        color_indicator = QLabel("●")
        color_indicator.setFont(QFont("Segoe UI", 20))
        color_indicator.setStyleSheet(f"color: {habit[5] if len(habit) > 5 else '#4CAF50'};")

        name_label = QLabel(habit[1])
        name_label.setFont(QFont("Segoe UI", 14, QFont.Bold))
        name_label.setStyleSheet(f"color: {self.theme['text_primary']};")
        name_label.setWordWrap(True)

        top_layout.addWidget(color_indicator)
        top_layout.addWidget(name_label)
        top_layout.addStretch()

        layout.addLayout(top_layout)

        if habit[2]:
            desc_label = QLabel(habit[2])
            desc_label.setFont(QFont("Segoe UI", 11))
            desc_label.setStyleSheet(f"color: {self.theme['text_secondary']};")
            desc_label.setWordWrap(True)
            layout.addWidget(desc_label)

        bottom_layout = QHBoxLayout()

        freq_map = {"daily": "Ежедневно", "weekly": "Еженедельно", "monthly": "Ежемесячно"}
        frequency = freq_map.get(habit[3], habit[3])

        freq_label = QLabel(f"⏰ {frequency}")
        freq_label.setFont(QFont("Segoe UI", 10))
        freq_label.setStyleSheet(f"color: {self.theme['text_primary']};")

        target_label = QLabel(f"🎯 {habit[4]} дней/неделю")
        target_label.setFont(QFont("Segoe UI", 10))
        target_label.setStyleSheet(f"color: {self.theme['text_primary']};")

        bottom_layout.addWidget(freq_label)
        bottom_layout.addWidget(target_label)
        bottom_layout.addStretch()

        layout.addLayout(bottom_layout)

        return card

    def select_habit(self, habit_id, selected_card):
        """Выбрать привычку"""
        self.selected_habit_id = habit_id

        # Снимаем выделение со всех карточек
        for i in range(self.habits_layout.count()):
            widget = self.habits_layout.itemAt(i).widget()
            if isinstance(widget, StyledCard):
                if hasattr(widget, 'habit_id'):
                    widget.setStyleSheet(f"""
                        QFrame {{
                            background-color: {self.theme['card_background']};
                            border-radius: 10px;
                            border: 1px solid {self.theme['card_border']};
                        }}
                    """)

        # Выделяем выбранную карточку
        selected_card.setStyleSheet(f"""
            QFrame {{
                background-color: {self.theme['selected']};
                border-radius: 10px;
                border: 2px solid {self.theme['primary']};
            }}
        """)

        self.edit_button.setEnabled(True)
        self.delete_button.setEnabled(True)

    def load_habits(self):
        if not hasattr(self, 'habits_layout'):
            return

        while self.habits_layout.count():
            child = self.habits_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        try:
            habits = self.db.get_habits()
        except Exception as e:
            error_widget = QWidget()
            error_layout = QVBoxLayout(error_widget)
            error_layout.setAlignment(Qt.AlignCenter)

            error_label = QLabel(f"Ошибка загрузки привычек:\n{str(e)}")
            error_label.setStyleSheet(f"color: {self.theme['error']}; text-align: center;")
            error_label.setAlignment(Qt.AlignCenter)

            error_layout.addWidget(error_label)
            self.habits_layout.addWidget(error_widget)
            return

        if not habits:
            empty_widget = QWidget()
            empty_layout = QVBoxLayout(empty_widget)
            empty_layout.setAlignment(Qt.AlignCenter)

            empty_icon = QLabel("📋")
            empty_icon.setFont(QFont("Segoe UI", 64))
            empty_icon.setAlignment(Qt.AlignCenter)
            empty_icon.setStyleSheet(f"color: {self.theme['text_secondary']};")

            empty_text = QLabel("У вас еще нет привычек\nНажмите 'Добавить привычку', чтобы создать первую!")
            empty_text.setFont(QFont("Segoe UI", 14))
            empty_text.setStyleSheet(f"color: {self.theme['text_secondary']}; text-align: center;")
            empty_text.setAlignment(Qt.AlignCenter)

            empty_layout.addWidget(empty_icon)
            empty_layout.addWidget(empty_text)

            self.habits_layout.addWidget(empty_widget)
            return

        for habit in habits:
            card = self.create_habit_card(habit)
            self.habits_layout.addWidget(card)

        self.habits_layout.addStretch()

    def add_habit(self):
        dialog = AddHabitDialog(self, theme=self.theme)
        if dialog.exec_() == QDialog.Accepted:
            try:
                self.load_habits()
                self.edit_button.setEnabled(False)
                self.delete_button.setEnabled(False)
                self.selected_habit_id = None
            except Exception as e:
                QMessageBox.warning(self, "Ошибка", f"Не удалось загрузить привычки: {str(e)}")

    def edit_habit(self):
        if not self.selected_habit_id:
            QMessageBox.warning(self, "Ошибка", "Выберите привычку для редактирования")
            return

        dialog = AddHabitDialog(self, habit_id=self.selected_habit_id, theme=self.theme)
        if dialog.exec_() == QDialog.Accepted:
            try:
                self.load_habits()
                self.edit_button.setEnabled(False)
                self.delete_button.setEnabled(False)
                self.selected_habit_id = None
            except Exception as e:
                QMessageBox.warning(self, "Ошибка", f"Не удалось обновить привычки: {str(e)}")

    def delete_habit(self):
        if not self.selected_habit_id:
            QMessageBox.warning(self, "Ошибка", "Выберите привычку для удаления")
            return

        reply = QMessageBox.question(
            self, "Удаление привычки",
            "Вы уверены, что хотите удалить выбранную привычку?\n"
            "Это действие нельзя отменить!",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                self.db.delete_habit(self.selected_habit_id)
                self.load_habits()
                self.edit_button.setEnabled(False)
                self.delete_button.setEnabled(False)
                self.selected_habit_id = None

                QMessageBox.information(self, "Успешно", "Привычка успешно удалена!")
            except Exception as e:
                QMessageBox.warning(self, "Ошибка", f"Не удалось удалить привычку: {str(e)}")

    def closeEvent(self, event):
        self.db.close()
        event.accept()

class StatsTab(QWidget):
    """Вкладка "Статистика" с поддержкой тем"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = HabitTrackerDB()
        self.theme = None
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(20)

        self.setLayout(self.layout)

    def set_theme(self, theme):
        """Установить тему"""
        self.theme = theme
        self.update_theme()

    def update_theme(self):
        """Обновить тему"""
        if not self.theme:
            return

        # Очищаем layout
        while self.layout.count():
            child = self.layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # Устанавливаем фон
        self.setStyleSheet(f"background-color: {self.theme['background']}; border: none;")

        # Заголовок
        title = QLabel("Статистика")
        title.setFont(QFont("Segoe UI", 24, QFont.Bold))
        title.setStyleSheet(f"color: {self.theme['text_primary']};")
        self.layout.addWidget(title)

        # Выбор привычки
        selector_card = StyledCard(theme=self.theme)
        selector_layout = QHBoxLayout(selector_card)
        selector_layout.setContentsMargins(20, 15, 20, 15)

        selector_label = QLabel("📊 Выберите привычку:")
        selector_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        selector_label.setStyleSheet(f"color: {self.theme['text_primary']};")

        self.habit_combo = QComboBox()
        self.habit_combo.setMinimumHeight(40)
        self.habit_combo.currentIndexChanged.connect(self.show_stats)
        self.habit_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {self.theme['surface']};
                color: {self.theme['text_primary']};
                border: 1px solid {self.theme['border']};
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 14px;
            }}
            QComboBox:hover {{
                border-color: {self.theme['hover']};
            }}
            QComboBox:focus {{
                border-color: {self.theme['primary']};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 30px;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid {self.theme['text_secondary']};
                margin-right: 10px;
            }}
            QComboBox QAbstractItemView {{
                background-color: {self.theme['surface']};
                color: {self.theme['text_primary']};
                border: 1px solid {self.theme['border']};
                selection-background-color: {self.theme['selected']};
            }}
        """)

        selector_layout.addWidget(selector_label)
        selector_layout.addWidget(self.habit_combo)
        selector_layout.addStretch()

        self.layout.addWidget(selector_card)

        # Карточка статистики
        self.stats_card = StyledCard(theme=self.theme)
        self.stats_layout = QVBoxLayout(self.stats_card)
        self.stats_layout.setContentsMargins(30, 25, 30, 25)
        self.stats_layout.setSpacing(20)

        self.empty_stats_label = QLabel("Выберите привычку для отображения статистики")
        self.empty_stats_label.setFont(QFont("Segoe UI", 14))
        self.empty_stats_label.setStyleSheet(f"color: {self.theme['text_disabled']};")
        self.empty_stats_label.setAlignment(Qt.AlignCenter)
        self.stats_layout.addWidget(self.empty_stats_label)

        self.layout.addWidget(self.stats_card)

        # Заголовок таблицы
        logs_label = QLabel("История выполнения")
        logs_label.setFont(QFont("Segoe UI", 16, QFont.Bold))
        logs_label.setStyleSheet(f"color: {self.theme['text_primary']}; margin: 10px 0;")
        self.layout.addWidget(logs_label)

        # Таблица логов
        self.logs_table = QTableWidget()
        self.logs_table.setColumnCount(3)
        self.logs_table.setHorizontalHeaderLabels(["📅 Дата", "✅ Статус", "📝 Заметки"])
        self.logs_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.logs_table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {self.theme['table_background']};
                color: {self.theme['text_primary']};
                border: none;
                border-radius: 8px;
                gridline-color: {self.theme['divider']};
            }}
            QHeaderView::section {{
                background-color: {self.theme['table_header']};
                color: {self.theme['text_primary']};
                padding: 12px;
                border: none;
                font-weight: bold;
            }}
            QTableWidget::item {{
                padding: 10px;
            }}
            QTableWidget::item:selected {{
                background-color: {self.theme['selected']};
            }}
        """)
        self.logs_table.setAlternatingRowColors(True)
        self.layout.addWidget(self.logs_table)

        # Загружаем привычки
        self.load_habits()

    def load_habits(self):
        try:
            habits = self.db.get_habits()
            self.habit_combo.clear()

            for habit in habits:
                self.habit_combo.addItem(habit[1], habit[0])
        except Exception as e:
            if hasattr(self, 'empty_stats_label'):
                self.empty_stats_label.setText(f"Ошибка загрузки привычек:\n{str(e)}")

    def show_stats(self):
        if self.habit_combo.currentIndex() == -1:
            return

        habit_id = self.habit_combo.currentData()
        try:
            stats = self.db.get_habit_stats(habit_id, days=30)

            if not stats:
                self.empty_stats_label.setText("Статистика недоступна")
                self.logs_table.setRowCount(0)
                return

            while self.stats_layout.count():
                child = self.stats_layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()

            stats_widget = QWidget()
            stats_grid = QGridLayout(stats_widget)
            stats_grid.setSpacing(20)

            metrics = [
                ("🎯 Текущая серия", f"{stats['current_streak']} дней", stats['color']),
                ("🏆 Лучшая серия", f"{stats['best_streak']} дней", self.theme['accent']),
                ("✅ Выполнено дней", f"{stats['completed_days']} из {stats['total_days']}", self.theme['success']),
                ("📈 Успешность", f"{stats['success_rate']:.1f}%", self.theme['info']),
                ("🎯 Цель недели", f"{stats['target_days']} дней", self.theme['secondary'])
            ]

            row, col = 0, 0
            for title, value, color in metrics:
                metric_card = StyledCard(theme=self.theme)
                metric_card.setFixedHeight(120)

                metric_layout = QVBoxLayout(metric_card)
                metric_layout.setContentsMargins(15, 15, 15, 15)
                metric_layout.setSpacing(10)

                title_label = QLabel(title)
                title_label.setFont(QFont("Segoe UI", 11))
                title_label.setStyleSheet(f"color: {color}; font-weight: bold;")

                value_label = QLabel(value)
                value_label.setFont(QFont("Segoe UI", 24, QFont.Bold))
                value_label.setStyleSheet(f"color: {self.theme['text_primary']};")
                value_label.setAlignment(Qt.AlignCenter)

                metric_layout.addWidget(title_label)
                metric_layout.addWidget(value_label)

                stats_grid.addWidget(metric_card, row, col)

                col += 1
                if col > 2:
                    col = 0
                    row += 1

            self.stats_layout.addWidget(stats_widget)

            try:
                target_days = int(stats['target_days'])
            except (ValueError, TypeError):
                target_days = 7

            if target_days > 0:
                progress_layout = QHBoxLayout()
                progress_label = QLabel("Прогресс недели:")
                progress_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
                progress_label.setStyleSheet(f"color: {self.theme['text_primary']};")

                progress = min(int((stats['current_streak'] / target_days) * 100), 100)

                progress_bar = QProgressBar()
                progress_bar.setValue(progress)
                progress_bar.setTextVisible(True)
                progress_bar.setFormat(f"{progress}%")
                progress_bar.setStyleSheet(f"""
                    QProgressBar {{
                        background-color: {self.theme['progress_background']};
                        color: {self.theme['text_primary']};
                        border: 1px solid {self.theme['border']};
                        border-radius: 6px;
                        text-align: center;
                        font-weight: bold;
                        height: 30px;
                    }}
                    QProgressBar::chunk {{
                        background-color: {stats['color']};
                        border-radius: 4px;
                    }}
                """)

                progress_layout.addWidget(progress_label)
                progress_layout.addWidget(progress_bar)

                self.stats_layout.addLayout(progress_layout)

            self.load_habit_logs(habit_id)

        except Exception as e:
            self.empty_stats_label.setText(f"Ошибка загрузки статистики:\n{str(e)}")
            self.logs_table.setRowCount(0)

    def load_habit_logs(self, habit_id):
        try:
            logs = self.db.get_habit_logs(habit_id, days=14)
            self.logs_table.setRowCount(len(logs))

            for row, log in enumerate(logs):
                date_obj, completed, notes = log

                if isinstance(date_obj, datetime):
                    date_str = date_obj.strftime("%d.%m.%Y")
                else:
                    date_str = str(date_obj)

                status = "✅ Выполнено" if completed else "❌ Пропущено"
                notes = notes if notes else ""

                date_item = QTableWidgetItem(date_str)
                status_item = QTableWidgetItem(status)
                notes_item = QTableWidgetItem(notes)

                if completed:
                    status_item.setForeground(QColor(self.theme['success']))
                else:
                    status_item.setForeground(QColor(self.theme['error']))

                self.logs_table.setItem(row, 0, date_item)
                self.logs_table.setItem(row, 1, status_item)
                self.logs_table.setItem(row, 2, notes_item)
        except Exception as e:
            self.logs_table.setRowCount(0)

    def closeEvent(self, event):
        self.db.close()
        event.accept()

class CalendarTab(QWidget):
    """Вкладка "Календарь" с поддержкой тем"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = HabitTrackerDB()
        self.current_habit_id = None
        self.theme = None
        self.current_month = datetime.now().month
        self.current_year = datetime.now().year
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(20)

        self.setLayout(self.layout)

    def set_theme(self, theme):
        """Установить тему"""
        self.theme = theme
        self.update_theme()

    def update_theme(self):
        """Обновить тему"""
        if not self.theme:
            return

        # Очищаем layout
        while self.layout.count():
            child = self.layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # Устанавливаем фон
        self.setStyleSheet(f"background-color: {self.theme['background']}; border: none;")

        # Заголовок
        title = QLabel("Календарь привычек")
        title.setFont(QFont("Segoe UI", 24, QFont.Bold))
        title.setStyleSheet(f"color: {self.theme['text_primary']};")
        self.layout.addWidget(title)

        # Выбор привычки
        selector_card = StyledCard(theme=self.theme)
        selector_layout = QHBoxLayout(selector_card)
        selector_layout.setContentsMargins(20, 15, 20, 15)

        selector_label = QLabel("📅 Выберите привычку:")
        selector_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        selector_label.setStyleSheet(f"color: {self.theme['text_primary']};")

        self.habit_combo = QComboBox()
        self.habit_combo.setMinimumHeight(40)
        self.habit_combo.currentIndexChanged.connect(self.load_calendar)
        self.habit_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {self.theme['surface']};
                color: {self.theme['text_primary']};
                border: 1px solid {self.theme['border']};
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 14px;
                min-width: 200px;
            }}
            QComboBox:hover {{
                border-color: {self.theme['hover']};
            }}
            QComboBox:focus {{
                border-color: {self.theme['primary']};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 30px;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid {self.theme['text_secondary']};
                margin-right: 10px;
            }}
            QComboBox QAbstractItemView {{
                background-color: {self.theme['surface']};
                color: {self.theme['text_primary']};
                border: 1px solid {self.theme['border']};
                selection-background-color: {self.theme['selected']};
                min-width: 200px;
            }}
        """)

        selector_layout.addWidget(selector_label)
        selector_layout.addWidget(self.habit_combo)
        selector_layout.addStretch()

        self.layout.addWidget(selector_card)

        # Создаем кастомную навигационную панель
        nav_card = StyledCard(theme=self.theme)
        nav_layout = QHBoxLayout(nav_card)
        nav_layout.setContentsMargins(20, 15, 20, 15)

        # Кнопка назад (предыдущий месяц)
        prev_button = QPushButton("◀")
        prev_button.setFont(QFont("Segoe UI", 16))
        prev_button.setFixedSize(40, 40)
        prev_button.setCursor(Qt.PointingHandCursor)
        prev_button.clicked.connect(self.prev_month)
        prev_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.theme['surface']};
                color: {self.theme['text_primary']};
                border: 1px solid {self.theme['border']};
                border-radius: 6px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {self.theme['hover']};
                border-color: {self.theme['primary']};
            }}
        """)

        # Текущий месяц и год
        self.month_label = QLabel()
        self.update_month_label()
        self.month_label.setFont(QFont("Segoe UI", 16, QFont.Bold))
        self.month_label.setStyleSheet(f"color: {self.theme['text_primary']};")
        self.month_label.setAlignment(Qt.AlignCenter)

        # Кнопка вперед (следующий месяц)
        next_button = QPushButton("▶")
        next_button.setFont(QFont("Segoe UI", 16))
        next_button.setFixedSize(40, 40)
        next_button.setCursor(Qt.PointingHandCursor)
        next_button.clicked.connect(self.next_month)
        next_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.theme['surface']};
                color: {self.theme['text_primary']};
                border: 1px solid {self.theme['border']};
                border-radius: 6px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {self.theme['hover']};
                border-color: {self.theme['primary']};
            }}
        """)

        # Выбор года
        self.year_combo = QComboBox()
        current_year = datetime.now().year
        for year in range(current_year - 5, current_year + 6):
            self.year_combo.addItem(str(year))
        self.year_combo.setCurrentText(str(self.current_year))
        self.year_combo.currentTextChanged.connect(self.year_changed)
        self.year_combo.setMinimumHeight(35)
        self.year_combo.setMaximumWidth(100)
        self.year_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {self.theme['surface']};
                color: {self.theme['text_primary']};
                border: 1px solid {self.theme['border']};
                border-radius: 6px;
                padding: 5px 10px;
                font-size: 14px;
            }}
            QComboBox:hover {{
                border-color: {self.theme['hover']};
            }}
            QComboBox:focus {{
                border-color: {self.theme['primary']};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 20px;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid {self.theme['text_secondary']};
                margin-right: 5px;
            }}
        """)

        nav_layout.addWidget(prev_button)
        nav_layout.addWidget(self.month_label)
        nav_layout.addWidget(self.year_combo)
        nav_layout.addWidget(next_button)
        nav_layout.addStretch()

        self.layout.addWidget(nav_card)

        # Календарь без навигационной панели
        calendar_card = StyledCard(theme=self.theme)
        calendar_card_layout = QVBoxLayout(calendar_card)
        calendar_card_layout.setContentsMargins(20, 20, 20, 20)
        calendar_card_layout.setSpacing(0)

        # Создаем кастомный календарь с полным отключением колесика
        class NoWheelCalendar(QCalendarWidget):
            def wheelEvent(self, event):
                # Полностью блокируем колесико мыши
                event.ignore()
                return

            def event(self, event):
                # Перехватываем ВСЕ события колесика
                if event.type() == event.Wheel:
                    # Не позволяем событию дойти до стандартной обработки
                    return True
                return super().event(event)

        self.calendar = NoWheelCalendar()
        self.calendar.setGridVisible(True)
        self.calendar.clicked.connect(self.on_date_clicked)

        # Скрываем навигационную панель стандартного календаря
        self.calendar.setNavigationBarVisible(False)

        # Устанавливаем текущий месяц и год
        qdate = QDate(self.current_year, self.current_month, 1)
        self.calendar.setCurrentPage(self.current_year, self.current_month)
        self.calendar.setSelectedDate(qdate)

        # Устанавливаем минимальные размеры
        self.calendar.setMinimumSize(600, 400)

        # Полностью отключаем фокус для колесика
        self.calendar.setFocusPolicy(Qt.NoFocus)

        self.calendar.setStyleSheet(f"""
            QCalendarWidget {{
                background-color: {self.theme['calendar_background']};
                color: {self.theme['calendar_text']};
                border: none;
                border-radius: 8px;
                font-size: 12px;
            }}
            QCalendarWidget QAbstractItemView:enabled {{
                color: {self.theme['calendar_text']};
                background-color: {self.theme['calendar_background']};
                selection-background-color: {self.theme['calendar_selected']};
                selection-color: {self.theme['text_primary']};
                font-size: 12px;
                outline: none;
            }}
            QCalendarWidget QAbstractItemView:disabled {{
                color: {self.theme['text_disabled']};
            }}
            QCalendarWidget QTableView {{
                alternate-background-color: {self.theme['table_row_odd']};
                gridline-color: {self.theme['divider']};
            }}
            QCalendarWidget QTableView::item {{
                padding: 8px;
                border: none;
                font-size: 12px;
            }}
            QCalendarWidget QTableView::item:selected {{
                background-color: {self.theme['calendar_selected']};
                border-radius: 4px;
            }}
            QCalendarWidget QHeaderView::section {{
                background-color: {self.theme['table_header']};
                color: {self.theme['text_primary']};
                padding: 10px;
                border: none;
                font-size: 12px;
                font-weight: bold;
            }}
        """)

        calendar_card_layout.addWidget(self.calendar)
        self.layout.addWidget(calendar_card)

        # Информация о дате
        self.info_card = StyledCard(theme=self.theme)
        info_layout = QVBoxLayout(self.info_card)
        info_layout.setContentsMargins(20, 15, 20, 15)

        self.date_info = QLabel("Выберите дату в календаре")
        self.date_info.setFont(QFont("Segoe UI", 12))
        self.date_info.setStyleSheet(f"color: {self.theme['text_secondary']};")
        self.date_info.setWordWrap(True)

        info_layout.addWidget(self.date_info)
        self.layout.addWidget(self.info_card)

        # Кнопки управления
        button_card = StyledCard(theme=self.theme)
        button_layout = QHBoxLayout(button_card)
        button_layout.setContentsMargins(20, 15, 20, 15)

        self.mark_completed_button = StyledButton("✅ Отметить как выполненную", self.theme["button_success"], self.theme)
        self.mark_completed_button.clicked.connect(self.mark_completed)

        self.mark_missed_button = StyledButton("❌ Отметить как пропущенную", self.theme["button_error"], self.theme)
        self.mark_missed_button.clicked.connect(self.mark_missed)

        button_layout.addWidget(self.mark_completed_button)
        button_layout.addWidget(self.mark_missed_button)

        self.layout.addWidget(button_card)
        self.layout.addStretch()

        # Загружаем привычки
        self.load_habits()

    def update_month_label(self):
        """Обновить метку с названием месяца"""
        month_names = {
            1: "Январь", 2: "Февраль", 3: "Март", 4: "Апрель",
            5: "Май", 6: "Июнь", 7: "Июль", 8: "Август",
            9: "Сентябрь", 10: "Октябрь", 11: "Ноябрь", 12: "Декабрь"
        }
        month_name = month_names.get(self.current_month, "Неизвестный месяц")
        self.month_label.setText(f"{month_name} {self.current_year}")

    def prev_month(self):
        """Перейти к предыдущему месяцу"""
        self.current_month -= 1
        if self.current_month < 1:
            self.current_month = 12
            self.current_year -= 1
        self.update_month_label()
        self.year_combo.setCurrentText(str(self.current_year))
        self.calendar.setCurrentPage(self.current_year, self.current_month)
        self.load_calendar()

    def next_month(self):
        """Перейти к следующему месяцу"""
        self.current_month += 1
        if self.current_month > 12:
            self.current_month = 1
            self.current_year += 1
        self.update_month_label()
        self.year_combo.setCurrentText(str(self.current_year))
        self.calendar.setCurrentPage(self.current_year, self.current_month)
        self.load_calendar()

    def year_changed(self, year_text):
        """Обработка изменения года"""
        try:
            new_year = int(year_text)
            if new_year != self.current_year:
                self.current_year = new_year
                self.update_month_label()
                self.calendar.setCurrentPage(self.current_year, self.current_month)
                self.load_calendar()
        except ValueError:
            pass

    def load_habits(self):
        try:
            habits = self.db.get_habits()
            self.habit_combo.clear()

            for habit in habits:
                self.habit_combo.addItem(habit[1], habit[0])

            if habits:
                self.current_habit_id = habits[0][0]
                self.load_calendar()
        except Exception as e:
            if hasattr(self, 'date_info'):
                self.date_info.setText(f"Ошибка загрузки привычек: {str(e)}")

    def load_calendar(self):
        if self.habit_combo.currentIndex() == -1:
            return

        self.current_habit_id = self.habit_combo.currentData()

        try:
            # Получаем логи для текущего месяца
            logs = self.db.get_habit_logs(self.current_habit_id, days=365)  # Получаем все логи

            self.calendar.setDateTextFormat(QDate(), QTextCharFormat())

            completed_format = QTextCharFormat()
            completed_format.setBackground(QBrush(QColor(self.theme['calendar_completed'])))
            completed_format.setFontWeight(QFont.Bold)

            missed_format = QTextCharFormat()
            missed_format.setBackground(QBrush(QColor(self.theme['calendar_missed'])))

            for date_obj, completed, _ in logs:
                if isinstance(date_obj, datetime):
                    date_str = date_obj.strftime("%Y-%m-%d")
                else:
                    date_str = str(date_obj)

                try:
                    qdate = QDate.fromString(date_str, "yyyy-MM-dd")
                    if qdate.isValid():
                        # Проверяем, что дата в текущем месяце
                        if qdate.year() == self.current_year and qdate.month() == self.current_month:
                            if completed:
                                self.calendar.setDateTextFormat(qdate, completed_format)
                            else:
                                self.calendar.setDateTextFormat(qdate, missed_format)
                except:
                    continue
        except Exception as e:
            if hasattr(self, 'date_info'):
                self.date_info.setText(f"Ошибка загрузки календаря: {str(e)}")

    def on_date_clicked(self, date):
        if not self.current_habit_id:
            return

        date_str = date.toString("yyyy-MM-dd")

        try:
            logs = self.db.get_habit_logs(self.current_habit_id, days=365)

            for log_date, completed, notes in logs:
                if isinstance(log_date, datetime):
                    log_date_str = log_date.strftime("%Y-%m-%d")
                else:
                    log_date_str = str(log_date)

                if log_date_str == date_str:
                    status = "✅ Выполнено" if completed else "❌ Пропущено"
                    notes_text = f"\n📝 Заметки: {notes}" if notes else ""
                    self.date_info.setText(f"📅 <b>{date.toString('dd.MM.yyyy')}</b>\n{status}{notes_text}")
                    return

            self.date_info.setText(f"📅 <b>{date.toString('dd.MM.yyyy')}</b>\nℹ️ Нет данных")
        except Exception as e:
            self.date_info.setText(f"Ошибка загрузки данных: {str(e)}")

    def mark_completed(self):
        if not self.current_habit_id:
            QMessageBox.warning(self, "Ошибка", "Выберите привычку")
            return

        date = self.calendar.selectedDate()
        date_str = date.toString("yyyy-MM-dd")

        try:
            self.db.mark_completed(self.current_habit_id, date_str)
            self.load_calendar()
            self.on_date_clicked(date)

            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setWindowTitle("Успешно")
            msg.setText("Привычка отмечена как выполненная!")
            msg.setStyleSheet(f"""
                QMessageBox {{
                    background-color: {self.theme['surface']};
                    color: {self.theme['text_primary']};
                }}
                QMessageBox QLabel {{
                    font-size: 14px;
                }}
            """)
            msg.exec_()
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось отметить привычку: {str(e)}")

    def mark_missed(self):
        if not self.current_habit_id:
            QMessageBox.warning(self, "Ошибка", "Выберите привычку")
            return

        date = self.calendar.selectedDate()
        date_str = date.toString("yyyy-MM-dd")

        try:
            self.db.mark_missed(self.current_habit_id, date_str)
            self.load_calendar()
            self.on_date_clicked(date)

            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setWindowTitle("Успешно")
            msg.setText("Привычка отмечена как пропущенная!")
            msg.setStyleSheet(f"""
                QMessageBox {{
                    background-color: {self.theme['surface']};
                    color: {self.theme['text_primary']};
                }}
                QMessageBox QLabel {{
                    font-size: 14px;
                }}
            """)
            msg.exec_()
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось отметить привычку: {str(e)}")

    def closeEvent(self, event):
        self.db.close()
        event.accept()

class MainWindow(QMainWindow):
    """Главное окно приложения с поддержкой тем"""
    def __init__(self):
        super().__init__()
        self.settings_manager = SettingsManager()
        self.db = HabitTrackerDB()

        # Загружаем сохраненную тему
        saved_theme = self.settings_manager.get_theme()
        self.current_theme = ThemeManager.get_theme_by_name(saved_theme)

        self.init_ui()
        self.apply_theme()

    def init_ui(self):
        self.setWindowTitle("🚀 Трекер привычек")
        self.setGeometry(100, 100, 1200, 800)

        # Восстанавливаем размер и положение окна
        geometry = self.settings_manager.get_window_geometry()
        if geometry:
            self.restoreGeometry(geometry)

        state = self.settings_manager.get_window_state()
        if state:
            self.restoreState(state)

        self.tab_widget = QTabWidget()
        self.tab_widget.setDocumentMode(True)

        # Убираем рамку у tab widget
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: none;
                background-color: transparent;
            }
            QTabBar::tab {
                min-width: 120px;
                padding: 10px 20px;
            }
        """)

        self.today_tab = TodayTab()
        self.habits_tab = HabitsTab()
        self.stats_tab = StatsTab()
        self.calendar_tab = CalendarTab()

        self.tab_widget.addTab(self.today_tab, "📅 Сегодня")
        self.tab_widget.addTab(self.habits_tab, "📋 Все привычки")
        self.tab_widget.addTab(self.stats_tab, "📊 Статистика")
        self.tab_widget.addTab(self.calendar_tab, "🗓️ Календарь")

        self.tab_widget.currentChanged.connect(self.on_tab_changed)

        self.setCentralWidget(self.tab_widget)

        self.create_menu()

        self.statusBar().showMessage(f"Готово | Тема: {self.current_theme['name']} | {datetime.now().strftime('%d.%m.%Y %H:%M')}")

    def apply_theme(self):
        """Применить текущую тему ко всему приложению"""
        # Применяем тему к главному окну
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {self.current_theme['background']};
            }}
            QTabWidget::pane {{
                border: none;
                background-color: transparent;
            }}
            QTabBar::tab {{
                background-color: {self.current_theme['surface']};
                color: {self.current_theme['text_secondary']};
                padding: 15px 25px;
                margin-right: 2px;
                font-size: 14px;
                font-weight: bold;
                border: none;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                min-width: 120px;
            }}
            QTabBar::tab:selected {{
                background-color: {self.current_theme['surface']};
                color: {self.current_theme['text_primary']};
                border-bottom: 3px solid {self.current_theme['primary']};
            }}
            QTabBar::tab:hover {{
                background-color: {self.current_theme['hover']};
                color: {self.current_theme['text_primary']};
            }}
            QStatusBar {{
                background-color: {self.current_theme['status_bar']};
                color: {self.current_theme['status_text']};
                font-size: 12px;
            }}
        """)

        # Применяем тему ко всем вкладкам
        self.today_tab.set_theme(self.current_theme)
        self.habits_tab.set_theme(self.current_theme)
        self.stats_tab.set_theme(self.current_theme)
        self.calendar_tab.set_theme(self.current_theme)

        # Обновляем меню
        self.update_menu_style()

    def update_menu_style(self):
        """Обновить стиль меню"""
        menubar = self.menuBar()
        menubar.setStyleSheet(f"""
            QMenuBar {{
                background-color: {self.current_theme['status_bar']};
                color: {self.current_theme['status_text']};
                font-size: 13px;
                font-weight: bold;
            }}
            QMenuBar::item {{
                background-color: transparent;
                padding: 8px 15px;
            }}
            QMenuBar::item:selected {{
                background-color: {self.current_theme['selected']};
            }}
            QMenu {{
                background-color: {self.current_theme['menu_background']};
                color: {self.current_theme['menu_text']};
                border: 1px solid {self.current_theme['border']};
                border-radius: 4px;
                padding: 5px;
            }}
            QMenu::item {{
                padding: 8px 25px 8px 20px;
                font-size: 13px;
                color: {self.current_theme['menu_text']};
            }}
            QMenu::item:selected {{
                background-color: {self.current_theme['menu_hover']};
                color: {self.current_theme['primary']};
            }}
            QMenu::separator {{
                height: 1px;
                background-color: {self.current_theme['divider']};
                margin: 5px 10px;
            }}
        """)

    def create_menu(self):
        menubar = self.menuBar()

        # Меню Файл
        file_menu = menubar.addMenu("📁 Файл")

        new_action = QAction("➕ Новая привычка", self)
        new_action.triggered.connect(self.new_habit)
        file_menu.addAction(new_action)

        export_action = QAction("📤 Экспорт данных", self)
        export_action.triggered.connect(self.export_data)
        file_menu.addAction(export_action)

        import_action = QAction("📥 Импорт данных", self)
        import_action.triggered.connect(self.import_data)
        file_menu.addAction(import_action)

        file_menu.addSeparator()

        reset_action = QAction("🔄 Сбросить данные", self)
        reset_action.triggered.connect(self.reset_database)
        file_menu.addAction(reset_action)

        file_menu.addSeparator()

        exit_action = QAction("🚪 Выход", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Меню Вид (только темы оформления)
        view_menu = menubar.addMenu("🎨 Вид")

        # Меню тем
        theme_menu = view_menu.addMenu("Тема оформления")

        light_theme_action = QAction("🌞 Светлая тема", self)
        light_theme_action.triggered.connect(lambda: self.change_theme("light"))
        theme_menu.addAction(light_theme_action)

        dark_theme_action = QAction("🌙 Темная тема", self)
        dark_theme_action.triggered.connect(lambda: self.change_theme("dark"))
        theme_menu.addAction(dark_theme_action)

        blue_theme_action = QAction("🔵 Синяя тема", self)
        blue_theme_action.triggered.connect(lambda: self.change_theme("blue"))
        theme_menu.addAction(blue_theme_action)

        theme_menu.addSeparator()

        choose_theme_action = QAction("Выбрать тему...", self)
        choose_theme_action.triggered.connect(self.choose_theme)
        theme_menu.addAction(choose_theme_action)

        # Меню Помощь
        help_menu = menubar.addMenu("❓ Помощь")

        about_action = QAction("ℹ️ О программе", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

        tips_action = QAction("💡 Советы", self)
        tips_action.triggered.connect(self.show_tips)
        help_menu.addAction(tips_action)

        # Обновляем стиль меню
        self.update_menu_style()

    def change_theme(self, theme_name):
        """Сменить тему"""
        self.current_theme = ThemeManager.get_theme_by_name(theme_name)
        self.settings_manager.set_theme(theme_name)
        self.apply_theme()

        # Обновляем статус бар
        theme_names = {"light": "Светлая", "dark": "Темная", "blue": "Синяя"}
        self.statusBar().showMessage(f"Тема изменена на: {theme_names.get(theme_name, theme_name)} | {datetime.now().strftime('%d.%m.%Y %H:%M')}")

    def choose_theme(self):
        """Открыть диалог выбора темы"""
        dialog = ThemeDialog(self, self.current_theme['name'])
        if dialog.exec_() == QDialog.Accepted:
            theme_name = dialog.get_selected_theme()
            self.change_theme(theme_name)

    def new_habit(self):
        dialog = AddHabitDialog(self, theme=self.current_theme)
        if dialog.exec_() == QDialog.Accepted:
            try:
                self.habits_tab.load_habits()
                self.today_tab.load_today_habits()
            except Exception as e:
                self.show_message("Ошибка", f"Не удалось обновить данные: {str(e)}", "error")

    def on_tab_changed(self, index):
        try:
            if index == 0:
                self.today_tab.load_today_habits()
            elif index == 1:
                self.habits_tab.load_habits()
            elif index == 2:
                self.stats_tab.load_habits()
                if self.stats_tab.habit_combo.count() > 0:
                    self.stats_tab.show_stats()
            elif index == 3:
                self.calendar_tab.load_habits()
        except Exception as e:
            self.statusBar().showMessage(f"Ошибка: {str(e)}")

        theme_names = {"light": "Светлая", "dark": "Темная", "blue": "Синяя"}
        theme_name = theme_names.get(self.current_theme['name'], self.current_theme['name'])
        self.statusBar().showMessage(f"Готово | Тема: {theme_name} | {datetime.now().strftime('%d.%m.%Y %H:%M')}")

    def export_data(self):
        try:
            habits = self.db.get_habits()
            with open('habits_export.txt', 'w', encoding='utf-8') as f:
                f.write("=" * 60 + "\n")
                f.write("ЭКСПОРТ ПРИВЫЧЕК\n")
                f.write("=" * 60 + "\n\n")
                for habit in habits:
                    f.write(f"🏷️  Привычка: {habit[1]}\n")
                    f.write(f"📝  Описание: {habit[2] if habit[2] else 'Нет описания'}\n")
                    f.write(f"⏰  Частота: {habit[3]}\n")
                    f.write(f"🎯  Цель: {habit[4]} дней/неделю\n")
                    if len(habit) > 6:
                        f.write(f"📅  Создана: {habit[7]}\n")
                    f.write("-" * 40 + "\n\n")

            self.show_message("Экспорт завершен", "Данные успешно экспортированы в файл habits_export.txt", "info")
        except Exception as e:
            self.show_message("Ошибка экспорта", f"Ошибка при экспорте: {str(e)}", "error")

    def import_data(self):
        self.show_message("Импорт данных", "Функция импорта будет доступна в следующей версии.", "info")

    def reset_database(self):
        reply = QMessageBox.question(
            self, "Сброс базы данных",
            "<b>⚠️ ВНИМАНИЕ!</b><br><br>"
            "Вы уверены, что хотите сбросить все данные?<br>"
            "Это действие <b>нельзя</b> отменить!<br><br>"
            "Все ваши привычки и история будут удалены.",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                self.db.close()

                self.today_tab.db.close()
                self.habits_tab.db.close()
                self.stats_tab.db.close()
                self.calendar_tab.db.close()

                time.sleep(0.1)

                db_path = "habits.db"

                if os.path.exists(db_path):
                    max_attempts = 3
                    for attempt in range(max_attempts):
                        try:
                            os.remove(db_path)
                            break
                        except PermissionError:
                            if attempt < max_attempts - 1:
                                time.sleep(0.2)
                            else:
                                raise

                self.db = HabitTrackerDB()

                self.today_tab.db = self.db
                self.habits_tab.db = self.db
                self.stats_tab.db = self.db
                self.calendar_tab.db = self.db

                self.today_tab.load_today_habits()
                self.habits_tab.load_habits()
                self.stats_tab.load_habits()
                self.calendar_tab.load_habits()

                self.tab_widget.setCurrentIndex(0)

                self.show_message("База данных сброшена",
                                  "Все данные были успешно сброшены.\nСоздайте новые привычки.",
                                  "success")

            except Exception as e:
                self.show_message("Ошибка",
                                  f"Ошибка при сбросе базы данных: {str(e)}\n\n"
                                  "Попробуйте:\n"
                                  "1. Перезапустить приложение\n"
                                  "2. Проверить, не открыт ли файл habits.db в другой программе\n"
                                  "3. Удалить файл habits.db вручную",
                                  "error")

    def show_tips(self):
        tips = """
        <h2>💡 Советы по использованию трекера привычек:</h2>
        
        <b>1. Начинайте с малого</b><br>
        Добавляйте 1-2 привычки за раз, не перегружайте себя.
        
        <b>2. Будьте реалистичны</b><br>
        Устанавливайте достижимые цели (например, 4-5 дней в неделю).
        
        <b>3. Используйте напоминания</b><br>
        Отмечайте привычки в одно и то же время каждый день.
        
        <b>4. Анализируйте статистику</b><br>
        Регулярно просматривайте статистику, чтобы видеть прогресс.
        
        <b>5. Не ругайте себя за пропуски</b><br>
        Важно не идеальное выполнение, а постоянное движение к цели.
        
        <b>6. Отмечайте успехи</b><br>
        Каждая выполненная привычка - это маленькая победа!
        
        <b>7. Меняйте тему оформления</b><br>
        Выберите удобную для вас тему в меню "Вид" → "Тема оформления".
        """

        msg = QMessageBox()
        msg.setWindowTitle("💡 Советы")
        msg.setTextFormat(Qt.RichText)
        msg.setText(tips)
        msg.setIconPixmap(QPixmap(64, 64))
        msg.exec_()

    def show_about(self):
        theme_names = {"light": "Светлая", "dark": "Темная", "blue": "Синяя"}
        current_theme_name = theme_names.get(self.current_theme['name'], self.current_theme['name'])

        about_text = f"""
        <div style='text-align: center;'>
            <h1 style='color: {self.current_theme["primary"]};'>🚀 Трекер привычек</h1>
            <h3 style='color: {self.current_theme["text_primary"]};'>Версия 3.0</h3>
            
            <p style='color: {self.current_theme["text_secondary"]}; font-size: 14px;'>
                Мощный инструмент для формирования и отслеживания привычек.<br>
                Помогает развивать полезные привычки и избавляться от вредных.
            </p>
            
            <hr style='border: 1px solid {self.current_theme["divider"]};'>
            
            <div style='text-align: left;'>
                <p><b>✨ Основные возможности:</b></p>
                <ul>
                    <li>📅 Ежедневное отслеживание привычек</li>
                    <li>📋 Управление списком привычек</li>
                    <li>📊 Детальная статистика и аналитика</li>
                    <li>🗓️ Визуализация в календаре</li>
                    <li>🎨 <b style='color: {self.current_theme["primary"]};'>3 темы оформления</b> (светлая, темная, синяя)</li>
                    <li>💾 Автосохранение настроек</li>
                </ul>
                
                <p><b>🎨 Текущая тема:</b> {current_theme_name}</p>
                
                <p><b>🛠 Технологии:</b></p>
                <ul>
                    <li>Python 3</li>
                    <li>PyQt5 для графического интерфейса</li>
                    <li>SQLite для хранения данных</li>
                </ul>
            </div>
            
            <hr style='border: 1px solid {self.current_theme["divider"]};'>
            
            <p style='color: {self.current_theme["text_disabled"]}; font-size: 12px;'>
                © 2024 Трекер привычек. Все права защищены.<br>
                Сделано с ❤️ для развития полезных привычек.
            </p>
        </div>
        """

        msg = QMessageBox()
        msg.setWindowTitle("ℹ️ О программе")
        msg.setTextFormat(Qt.RichText)
        msg.setText(about_text)
        msg.setIconPixmap(QPixmap(64, 64))
        msg.exec_()

    def show_message(self, title, message, type="info"):
        msg = QMessageBox()

        if type == "info":
            msg.setIcon(QMessageBox.Information)
            msg.setWindowTitle(f"ℹ️ {title}")
        elif type == "success":
            msg.setIcon(QMessageBox.Information)
            msg.setWindowTitle(f"✅ {title}")
        elif type == "error":
            msg.setIcon(QMessageBox.Critical)
            msg.setWindowTitle(f"❌ {title}")
        elif type == "warning":
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle(f"⚠️ {title}")

        msg.setText(message)
        msg.setStyleSheet(f"""
            QMessageBox {{
                background-color: {self.current_theme['surface']};
                color: {self.current_theme['text_primary']};
            }}
            QMessageBox QLabel {{
                font-size: 14px;
            }}
        """)
        msg.exec_()

    def closeEvent(self, event):
        # Сохраняем настройки
        self.settings_manager.set_window_geometry(self.saveGeometry())
        self.settings_manager.set_window_state(self.saveState())

        try:
            self.db.close()
        except:
            pass
        event.accept()

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    app.setApplicationName("Трекер привычек")
    app.setApplicationDisplayName("🚀 Трекер привычек")

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()