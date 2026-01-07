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
        left_list = QListWidget()
        left_list.addItems(["Image 1", "Image 2", "Image 3", "Image 4", "Image 5"])

        # ============================ Center ==============================
        center_box = QGroupBox("Actions")
        center_layout = QVBoxLayout()
        center_box.setLayout(center_layout)

        center_layout.addWidget(QPushButton("TODO OR NOT TODO"))
        
        center_layout.addStretch(1)
        
        slider1_label = QLabel("Un paramtre")
        slider1_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        slider1 = QSlider(Qt.Orientation.Horizontal)
        slider1.setMinimum(1)
        slider1.setMaximum(20)
        slider1.setValue(5)
        slider1.setTickPosition(QSlider.TickPosition.TicksBelow)
        slider1.setTickInterval(1)
        slider1.setSingleStep(1)
        
        value_label_slider1 = QLabel("0")
        value_label_slider1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        slider1.valueChanged.connect(
            lambda v: value_label_slider1.setText(str(v))
        )
        
        center_layout.addWidget(slider1_label)
        center_layout.addWidget(slider1)
        center_layout.addWidget(value_label_slider1)
        
        center_layout.addStretch(1)
        
        slider2_label = QLabel("Un autre paramtre")
        slider2_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        slider2 = QSlider(Qt.Orientation.Horizontal)
        slider2.setMinimum(1)
        slider2.setMaximum(20)
        slider2.setValue(5)
        slider2.setTickPosition(QSlider.TickPosition.TicksBelow)
        slider2.setTickInterval(1)
        slider2.setSingleStep(1)
        
        value_label_slider2 = QLabel("0")
        value_label_slider2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        slider2.valueChanged.connect(
            lambda v: value_label_slider2.setText(str(v))
        )
        
        center_layout.addWidget(slider2_label)
        center_layout.addWidget(slider2)
        center_layout.addWidget(value_label_slider2)

        # ============================= Right ==============================
        right_box = QGroupBox("Paramètres")
        
        # main layout
        right_main_layout = QVBoxLayout()
        right_box.setLayout(right_main_layout)
        
        # parameters zone
        right_form_layout = QFormLayout()
        right_main_layout.addLayout(right_form_layout)

        param1 = QLineEdit("TODO")
        param1.setReadOnly(True)
        right_form_layout.addRow("Param 1 :", param1)

        param2 = QLineEdit("TODO")
        param2.setReadOnly(True)
        right_form_layout.addRow("Param 2 :", param2)
        
        param3 = QLineEdit("TODO")
        param3.setReadOnly(True)
        right_form_layout.addRow("Param 3 :", param3)
        
        param4 = QLineEdit("TODO")
        param4.setReadOnly(True)
        right_form_layout.addRow("Param 4 :", param4)
        
        param5 = QLineEdit("TODO")
        param5.setReadOnly(True)
        right_form_layout.addRow("Param 5 :", param5)
        
        # spacer for keep button register on bottom
        right_main_layout.addStretch(1)
        
        # Button registration
        btn_save = QPushButton("Enregistrer Image")
        right_main_layout.addWidget(btn_save)
        
        # ==================== Add elements in Bottom =======================
        bottom_layout = QHBoxLayout()
        bottom_layout.addWidget(left_list)
        bottom_layout.addWidget(center_box)
        bottom_layout.addWidget(right_box)

        
        # =================================================================
        # ======================== ASSOCIATION ============================
        # =================================================================
        main_layout.addLayout(top_layout)
        main_layout.addLayout(bottom_layout)

    


if __name__ == "__main__":
    
    
    app = QApplication(sys.argv)
    # app.setStyleSheet(qdarkstyle.load_stylesheet()) # Apply dark style
    
    window = StarReducApp()
    window.show()
    sys.exit(app.exec())
    