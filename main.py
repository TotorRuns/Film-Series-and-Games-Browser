import sys
import os
from PyQt6.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget, QLineEdit, QPushButton, QHBoxLayout, QLabel, QHeaderView
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtCore import Qt, QSize
import requests
from dotenv import load_dotenv

class MovieApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Movie Information")
        self.setGeometry(100, 100, 800, 600)
        
        self.layout = QVBoxLayout()
        self.search_layout = QHBoxLayout()
        
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Enter movie title, TV Series title, or Video Game")
        self.search_bar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.search_button = QPushButton("Search")
        self.search_button.clicked.connect(self.load_movies)
        
        self.search_layout.addWidget(self.search_bar)
        self.search_layout.addWidget(self.search_button)
        
        self.table_widget = QTableWidget()
        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_widget.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.table_widget.setAlternatingRowColors(True)
        
        self.layout.addLayout(self.search_layout)
        self.layout.addWidget(self.table_widget)
        
        container = QWidget()
        container.setLayout(self.layout)
        self.setCentralWidget(container)
        
        # Placeholder for the icon
        self.setWindowIcon(QIcon("favicon.ico"))

    def resizeEvent(self, event):
        self.table_widget.setColumnWidth(0, self.width() // 5)
        self.table_widget.setColumnWidth(1, self.width() // 5)
        self.table_widget.setColumnWidth(2, self.width() // 5)
        self.table_widget.setColumnWidth(3, self.width() // 5)
        self.table_widget.setColumnWidth(4, self.width() // 5)
        super().resizeEvent(event)

    def load_movies(self):
        load_dotenv()
        omdb_api_key = os.getenv('OMDB_API_KEY')
        tmdb_api_key = os.getenv('TMDB_API_KEY')
        rawg_api_key = os.getenv('RAWG_API_KEY')
        query = self.search_bar.text()
        
        omdb_url = f"http://www.omdbapi.com/?apikey={omdb_api_key}&s={query}"
        omdb_response = requests.get(omdb_url)
        omdb_data = omdb_response.json()
        
        if omdb_data['Response'] == 'True':
            movies = omdb_data['Search']
            self.table_widget.setRowCount(len(movies))
            self.table_widget.setColumnCount(5)
            self.table_widget.setHorizontalHeaderLabels(['Title', 'Year', 'Type', 'Poster', 'IMDB ID'])
            
            for row, movie in enumerate(movies):
                title_item = QTableWidgetItem(movie['Title'])
                title_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table_widget.setItem(row, 0, title_item)
                
                year_item = QTableWidgetItem(movie['Year'])
                year_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table_widget.setItem(row, 1, year_item)
                
                type_item = QTableWidgetItem(movie['Type'])
                type_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table_widget.setItem(row, 2, type_item)
                
                if movie['Type'] == 'game':
                    rawg_url = f"https://api.rawg.io/api/games?key={rawg_api_key}&search={movie['Title']}"
                    rawg_response = requests.get(rawg_url)
                    rawg_data = rawg_response.json()
                    
                    if rawg_data['results']:
                        poster_url = rawg_data['results'][0].get('background_image')  # Verwenden Sie das Hintergrundbild für das Cover
                        if poster_url:
                            poster_response = requests.get(poster_url)
                            pixmap = QPixmap()
                            pixmap.loadFromData(poster_response.content)
                            pixmap = pixmap.scaled(100, 150, aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio)  # Bildgröße anpassen und Seitenverhältnis beibehalten
                            poster_label = QLabel()
                            poster_label.setPixmap(pixmap)
                            self.table_widget.setCellWidget(row, 3, poster_label)
                            self.table_widget.setRowHeight(row, pixmap.height())  # Zeilenhöhe anpassen
                        else:
                            self.table_widget.setItem(row, 3, QTableWidgetItem("N/A"))
                    else:
                        self.table_widget.setItem(row, 3, QTableWidgetItem("N/A"))
                else:
                    tmdb_url = f"https://api.themoviedb.org/3/find/{movie['imdbID']}?api_key={tmdb_api_key}&external_source=imdb_id"
                    tmdb_response = requests.get(tmdb_url)
                    tmdb_data = tmdb_response.json()
                    
                    if movie['Type'] == 'series' and tmdb_data['tv_results']:
                        poster_path = tmdb_data['tv_results'][0]['poster_path']
                    elif movie['Type'] != 'series' and tmdb_data['movie_results']:
                        poster_path = tmdb_data['movie_results'][0]['poster_path']
                    else:
                        poster_path = None
                    
                    poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else "N/A"
                    if poster_url != "N/A":
                        poster_response = requests.get(poster_url)
                        pixmap = QPixmap()
                        pixmap.loadFromData(poster_response.content)
                        pixmap = pixmap.scaled(100, 150, aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio)  # Bildgröße anpassen und Seitenverhältnis beibehalten
                        poster_label = QLabel()
                        poster_label.setPixmap(pixmap)
                        self.table_widget.setCellWidget(row, 3, poster_label)
                        self.table_widget.setRowHeight(row, pixmap.height())  # Zeilenhöhe anpassen
                    else:
                        self.table_widget.setItem(row, 3, QTableWidgetItem("N/A"))
                
                imdb_id_item = QTableWidgetItem(movie['imdbID'])
                imdb_id_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table_widget.setItem(row, 4, imdb_id_item)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MovieApp()
    window.show()
    sys.exit(app.exec())
