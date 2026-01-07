import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QGroupBox, QLabel, QHBoxLayout, QListWidget, QPushButton, QSlider, QLineEdit, QFormLayout
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
import qdarkstyle # Dark mode

class StarReducApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Application de réduction d'étoiles")
        self.resize(1200, 800)   # largeur, hauteur
        
        # Layout principal pour la fenetre
        main_widget = QWidget(self)
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)
        
        # =================================================================
        # ======================== TOP PART ===============================
        # =================================================================
        
        # ========================= Left Image ============================
        box_left = QGroupBox("Image originale")
        layout_left = QVBoxLayout()
        box_left.setLayout(layout_left)

        img_left = QLabel()
        img_left.setAlignment(Qt.AlignmentFlag.AlignCenter)
        img_left.setPixmap(
            QPixmap("results/original/original.png").scaled(
                500, 800,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
        )
        
        layout_left.addWidget(img_left)

        # ========================= Right Image ===========================
        box_right = QGroupBox("Image traitée")
        layout_right = QVBoxLayout()
        box_right.setLayout(layout_right)

        img_right = QLabel()
        img_right.setAlignment(Qt.AlignmentFlag.AlignCenter)
        img_right.setPixmap(
            QPixmap("results/final_image/image_finale.png").scaled(
                500, 800,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
        )

        layout_right.addWidget(img_right)

        # ==================== Add Image Box in Top =======================
        top_layout = QHBoxLayout()
        top_layout.addWidget(box_left)
        top_layout.addWidget(box_right)


        # =================================================================
        # ======================== BOTTOM PART ============================
        # =================================================================

        # ============================= Left ===============================


        # ============================ Center ==============================


        # ============================= Right ==============================


        # Assemblage
        main_layout.addLayout(top_layout)


    


if __name__ == "__main__":
    
    
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet()) # Apply dark style
    
    window = StarReducApp()
    window.show()
    sys.exit(app.exec())
    