from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QVBoxLayout, QPushButton, QLineEdit, QLabel, QTableWidget, QWidget, QComboBox
import sys
import sqlite3

class LibraryApp(QMainWindow):
    def __init__(self):
        super(LibraryApp, self).__init__()
        self.initUI()
        self.load_books()  # загрузка книг из бд при запуске
        self.load_genres()  # аналогично, загрузка жанров

    def initUI(self):
        self.setWindowTitle("Библиотека")
        self.setGeometry(100, 100, 450, 600)

        # стили (из-за них не видно стрелочки выпадающего списка у жанров справа, добавлять картинку для этого я не буду, дабы не засорять проект)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }

            QLabel {
                font-size: 14px;
                color: #2f2f2f;
            }

            QPushButton {
                background-color: #4285F4;
                color: white;
                font: bold 12px;
                border: 2px solid #4285F4;
                border-radius: 4px;
                padding: 5px;
                min-width: 80px;
            }

            QPushButton:hover {
                background-color: #3578E5;
            }

            QPushButton:pressed {
                background-color: #2C5BB6;
                border-color: #2C5BB6;
            }

            QLineEdit, QComboBox {
                font-size: 14px;
                border: 2px solid #BDBDBD;
                border-radius: 4px;
                padding: 5px;
                min-height: 20px;
            }

            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: right center;
                width: 15px;
                border-left-width: 1px;
                border-left-color: #BDBDBD;
                border-left-style: solid;
                border-top-right-radius: 2px;
                border-bottom-right-radius: 2px;
            }

            QTableWidget {
                gridline-color: #D3D3D3;
                selection-background-color: #ADD8E6;
            }

            QTableWidget::item {
                padding: 5px;
                border-color: transparent;
            }

            QTableWidget::item:selected {
                background-color: #ADD8E6;
            }
        """)

        # главный виджет
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        # лейаут
        layout = QVBoxLayout(central_widget)

        # виджет таблицы
        self.tableWidget = QTableWidget()
        self.tableWidget.setColumnCount(3)
        self.tableWidget.setHorizontalHeaderLabels(["ID", "Название", "Автор"])
        self.tableWidget.clicked.connect(self.show_details)
        layout.addWidget(self.tableWidget)

        # название
        self.titleInput = QLineEdit(self)
        layout.addWidget(QLabel("Название:"))
        layout.addWidget(self.titleInput)

        # автор
        self.authorInput = QLineEdit(self)
        layout.addWidget(QLabel("Автор:"))
        layout.addWidget(self.authorInput)

        # описание
        self.descriptionInput = QLineEdit(self)
        layout.addWidget(QLabel("Описание:"))
        layout.addWidget(self.descriptionInput)

        # жанр (ComboBox)
        self.genreInput = QComboBox(self)
        layout.addWidget(QLabel("Жанр:"))
        layout.addWidget(self.genreInput)
        self.genreInput.setEditable(True)

        # кнопка добавить
        self.addBookButton = QPushButton("Добавить книгу", self)
        self.addBookButton.clicked.connect(self.add_book)
        layout.addWidget(self.addBookButton)

        # кнопка удалить
        self.deleteBookButton = QPushButton("Удалить книгу", self)
        self.deleteBookButton.clicked.connect(self.delete_book)
        layout.addWidget(self.deleteBookButton)

        # поиск
        self.searchInput = QLineEdit(self)
        layout.addWidget(QLabel("Поиск по (Названию/Автору):"))
        layout.addWidget(self.searchInput)

        # кнопка поиска
        self.searchButton = QPushButton("Найти", self)
        self.searchButton.clicked.connect(self.search_books)
        layout.addWidget(self.searchButton)

        # лейбл деталей
        self.detailLabel = QLabel("Детали: выберите книгу, чтобы увидеть детали", self)
        layout.addWidget(self.detailLabel)

    def load_books(self, genre_filter=None):
        self.tableWidget.setRowCount(0)
        conn = sqlite3.connect('library.db')
        c = conn.cursor()
        query = "SELECT id, title, author FROM books"
        if genre_filter:
            query += " WHERE genre=?"
            c.execute(query, (genre_filter,))
        else:
            c.execute(query)
        for row_number, row_data in enumerate(c.fetchall()):
            self.tableWidget.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                self.tableWidget.setItem(row_number, column_number, QTableWidgetItem(str(data)))
        conn.close()

    def load_genres(self):
        conn = sqlite3.connect('library.db')
        c = conn.cursor()
        c.execute("SELECT DISTINCT genre FROM books")
        self.genreInput.clear()
        genres = [item[0] for item in c.fetchall()]
        self.genreInput.addItems(genres)
        conn.close()

    def add_book(self):
        title = self.titleInput.text()
        author = self.authorInput.text()
        description = self.descriptionInput.text()
        genre = self.genreInput.currentText()
        conn = sqlite3.connect('library.db')
        c = conn.cursor()
        c.execute("INSERT INTO books (title, author, description, genre) VALUES (?, ?, ?, ?)", (title, author, description, genre))
        conn.commit()
        conn.close()
        self.load_books()
        self.load_genres()

    def delete_book(self):
        current_row = self.tableWidget.currentRow()
        current_id = self.tableWidget.item(current_row, 0).text()
        conn = sqlite3.connect('library.db')
        c = conn.cursor()
        c.execute("DELETE FROM books WHERE id=?", (current_id,))
        conn.commit()
        conn.close()
        self.tableWidget.removeRow(current_row)

    def search_books(self):
        search_term = self.searchInput.text()
        self.tableWidget.setRowCount(0)
        conn = sqlite3.connect('library.db')
        c = conn.cursor()
        query = "SELECT id, title, author FROM books WHERE title LIKE ? OR author LIKE ?"
        c.execute(query, ('%'+search_term+'%', '%'+search_term+'%'))
        for row_number, row_data in enumerate(c.fetchall()):
            self.tableWidget.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                self.tableWidget.setItem(row_number, column_number, QTableWidgetItem(str(data)))
        conn.close()

    def show_details(self, index):
        row = index.row()
        book_id = self.tableWidget.item(row, 0).text()
        conn = sqlite3.connect('library.db')
        c = conn.cursor()
        c.execute("SELECT title, author, description, genre FROM books WHERE id=?", (book_id,))
        book = c.fetchone()
        detail_text = f"Название: {book[0]}\nАвтор: {book[1]}\nОписание: {book[2]}\nЖанр: {book[3]}"
        self.detailLabel.setText(detail_text)
        conn.close()

def main():
    app = QApplication(sys.argv)
    main_window = LibraryApp()
    main_window.show()
    app.exec_()

if __name__ == "__main__":
    main()