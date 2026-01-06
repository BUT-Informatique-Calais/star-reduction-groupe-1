import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QGroupBox, QLabel, QHBoxLayout, QListWidget, QPushButton, QSlider, QLineEdit, QFormLayout
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt

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
        
        # ========= ZONE HAUTE =========
        # ===== Image gauche =====
        box_left = QGroupBox("Image originale")
        layout_left = QVBoxLayout()
        box_left.setLayout(layout_left)

        img_left = QLabel()
        img_left.setAlignment(Qt.AlignmentFlag.AlignCenter)
        img_left.setPixmap(
            QPixmap("image_originale.png").scaled(
                300, 300,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
        )

        layout_left.addWidget(img_left)

        # ===== Image droite =====
        box_right = QGroupBox("Image traitée")
        layout_right = QVBoxLayout()
        box_right.setLayout(layout_right)

        img_right = QLabel()
        img_right.setAlignment(Qt.AlignmentFlag.AlignCenter)
        img_right.setPixmap(
            QPixmap("image_traitee.png").scaled(
                300, 300,
                Qt.AspectRatioMode.KeepAspectRatio
            )
        )

        layout_right.addWidget(img_right)

        # ===== Layout horizontal =====
        top_layout = QHBoxLayout()
        top_layout.addWidget(box_left)
        top_layout.addWidget(box_right)

        # ===== ZONE BASSE =====
        bottom_layout = QHBoxLayout()

        # Gauche
        left_list = QListWidget()
        left_list.addItems(["Item 1", "Item 2"])

        # Centre
        center_box = QGroupBox("Actions")
        center_layout = QVBoxLayout()
        center_box.setLayout(center_layout)

        center_layout.addWidget(QPushButton("Lancer"))
        center_layout.addWidget(QSlider(Qt.Orientation.Horizontal))

        # Droite
        right_box = QGroupBox("Paramètres")
        right_layout = QFormLayout()
        right_box.setLayout(right_layout)

        p1 = QLineEdit("Valeur A")
        p1.setReadOnly(True)
        right_layout.addRow("Param A :", p1)

        bottom_layout.addWidget(left_list)
        bottom_layout.addWidget(center_box)
        bottom_layout.addWidget(right_box)

        # Assemblage
        main_layout.addLayout(top_layout)
        main_layout.addLayout(bottom_layout)

        
        inserer_image
        # insérer les images
        image_label = QLabel()
        image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    
        pixmap = QPixmap("results/original.png")
        # adapter la taille
        pixmap = pixmap.scaled(
            500, 800,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        # insertion dans le QLabel
        image_label.setPixmap(pixmap)
        # adapter le qlabel au layout de la box
        layout_left.addWidget(image_label)
    


def main():
    app = QApplication(sys.argv)
    window = StarReducApp()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()