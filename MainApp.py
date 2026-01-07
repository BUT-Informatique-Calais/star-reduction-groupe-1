import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QGroupBox, QLabel, QHBoxLayout, QListWidget, QPushButton, QSlider, QLineEdit, QFormLayout
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt, QTimer
import qdarkstyle # Dark mode
import os
import phase2forApp as p2

FOLDER_EXAMPLES = "./examples"

class StarReducApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Star reduction App")
        self.resize(1200, 800)   # width, height
        
        # variables for process
        self.current_fits = None
        self.nb_stars = 0
        
        # timer anti-spam (debounce) in order to avoid too many calculations
        self.update_timer = QTimer(self)
        self.update_timer.setSingleShot(True)
        self.update_timer.timeout.connect(self.update_process_image)
        
        # main layout for window
        main_widget = QWidget(self)
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)
        
        # =================================================================
        # ======================== TOP PART ===============================
        # =================================================================
        
        # ========================= Left Image ============================
        box_left = QGroupBox("Original Image")
        box_left.setFixedSize(550, 550)
        layout_left = QVBoxLayout()
        box_left.setLayout(layout_left)

        self.img_left = QLabel()
        self.img_left.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # self.img_left.setPixmap(
        #     QPixmap("results/original/original.png").scaled(
        #         500, 800,
        #         Qt.AspectRatioMode.KeepAspectRatio,
        #         Qt.TransformationMode.SmoothTransformation
        #     )
        # )
        
        layout_left.addWidget(self.img_left)

        # ========================= Right Image ===========================
        box_right = QGroupBox("Processed Image")
        box_right.setFixedSize(550, 550)
        layout_right = QVBoxLayout()
        box_right.setLayout(layout_right)

        self.img_right = QLabel()
        self.img_right.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # self.img_right.setPixmap(
        #     QPixmap("results/final_image/image_finale.png").scaled(
        #         500, 800,
        #         Qt.AspectRatioMode.KeepAspectRatio,
        #         Qt.TransformationMode.SmoothTransformation
        #     )
        # )

        layout_right.addWidget(self.img_right)

        # ==================== Add Image Box in Top =======================
        top_layout = QHBoxLayout()
        top_layout.addWidget(box_left)
        top_layout.addWidget(box_right)


        # =================================================================
        # ======================== BOTTOM PART ============================
        # =================================================================

        # ============================= Left ===============================
        self.left_list = QListWidget()
        
        # infill list with files from folder example
        for nameFiles in os.listdir(FOLDER_EXAMPLES):
            self.left_list.addItem(nameFiles)
        
        # Handler clic on item
        self.left_list.itemClicked.connect(self.on_item_clicked)

        # ============================ Center ==============================
        center_box = QGroupBox("Actions")
        center_layout = QVBoxLayout()
        center_box.setLayout(center_layout)

        # Button
        center_layout.addWidget(QPushButton("TODO OR NOT TODO"))
        
        center_layout.addStretch(1)
        
        # First Slider fwhm
        slider_fwhm_label = QLabel("Fwhm")
        slider_fwhm_label.setToolTip("Full Width at Half Maximum => size of star in pixel")
        slider_fwhm_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.slider_fwhm = QSlider(Qt.Orientation.Horizontal)
        self.slider_fwhm.setMinimum(1)
        self.slider_fwhm.setMaximum(100)
        self.slider_fwhm.setValue(40)
        self.slider_fwhm.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.slider_fwhm.setTickInterval(1)
        self.slider_fwhm.setSingleStep(1)
        # value bottom 
        value_label_slider_fwhm = QLabel("4")
        value_label_slider_fwhm.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.slider_fwhm.valueChanged.connect(
            lambda v: (value_label_slider_fwhm.setText(str(v)),
                       self.schedule_update()
            )
        )
        
        center_layout.addWidget(slider_fwhm_label)
        center_layout.addWidget(self.slider_fwhm)
        center_layout.addWidget(value_label_slider_fwhm)
        
        center_layout.addStretch(1)
        
        # Second Slider threshold
        slider_threshold_label = QLabel("Threshold")
        slider_threshold_label.setToolTip("The detection threshold")
        slider_threshold_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.slider_threshold = QSlider(Qt.Orientation.Horizontal)
        self.slider_threshold.setMinimum(1)
        self.slider_threshold.setMaximum(20)
        self.slider_threshold.setValue(5)
        self.slider_threshold.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.slider_threshold.setTickInterval(1)
        self.slider_threshold.setSingleStep(1)
        
        value_label_slider_threshold = QLabel("5")
        value_label_slider_threshold.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.slider_threshold.valueChanged.connect(
            lambda v: (value_label_slider_threshold.setText(str(v)),
                       self.schedule_update()
            )
        )
        
        center_layout.addWidget(slider_threshold_label)
        center_layout.addWidget(self.slider_threshold)
        center_layout.addWidget(value_label_slider_threshold)

        # Third Slider erode_kernel
        slider_erode_kernel_label = QLabel("Erode kernel")
        slider_erode_kernel_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.slider_erode_kernel = QSlider(Qt.Orientation.Horizontal)
        self.slider_erode_kernel.setMinimum(1)
        self.slider_erode_kernel.setMaximum(100)
        self.slider_erode_kernel.setValue(2)
        self.slider_erode_kernel.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.slider_erode_kernel.setTickInterval(1)
        self.slider_erode_kernel.setSingleStep(1)
        
        value_label_slider_erode_kernel = QLabel("2")
        value_label_slider_erode_kernel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.slider_erode_kernel.valueChanged.connect(
            lambda v: (value_label_slider_erode_kernel.setText(str(v)),
                       self.schedule_update()
                       )
        )
        
        center_layout.addWidget(slider_erode_kernel_label)
        center_layout.addWidget(self.slider_erode_kernel)
        center_layout.addWidget(value_label_slider_erode_kernel)
        
        # Fourth Slider nb Iteration erode
        slider_nb_iteration_label = QLabel("Number of erosion iterations")
        slider_nb_iteration_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.slider_nb_iteration = QSlider(Qt.Orientation.Horizontal)
        self.slider_nb_iteration.setMinimum(1)
        self.slider_nb_iteration.setMaximum(20)
        self.slider_nb_iteration.setValue(2)
        self.slider_nb_iteration.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.slider_nb_iteration.setTickInterval(1)
        self.slider_nb_iteration.setSingleStep(1)
        
        value_label_slider_nb_iteration = QLabel("2")
        value_label_slider_nb_iteration.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.slider_nb_iteration.valueChanged.connect(
            lambda v: (value_label_slider_nb_iteration.setText(str(v)),
                       self.schedule_update()
            )
        )
        
        center_layout.addWidget(slider_nb_iteration_label)
        center_layout.addWidget(self.slider_nb_iteration)
        center_layout.addWidget(value_label_slider_nb_iteration)
        
        # ============================= Right ==============================
        right_box = QGroupBox("Parameters")
        
        # main layout
        right_main_layout = QVBoxLayout()
        right_box.setLayout(right_main_layout)
        
        # parameters zone
        right_form_layout = QFormLayout()
        right_main_layout.addLayout(right_form_layout)

        self.param_nb_stars = QLineEdit()
        self.param_nb_stars.setReadOnly(True)
        right_form_layout.addRow("Number stars :", self.param_nb_stars)

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
        bottom_layout.addWidget(self.left_list)
        bottom_layout.addWidget(center_box)
        bottom_layout.addWidget(right_box)

        
        # =================================================================
        # ======================== ASSOCIATION ============================
        # =================================================================
        main_layout.addLayout(top_layout)
        main_layout.addLayout(bottom_layout)

    
    def on_item_clicked(self, item):
        '''
        load the original image matching with the selected fits
        
        :param item: the fits'name selected
        '''
        filename = item.text()
        fits_path = os.path.join(FOLDER_EXAMPLES, filename)
        
        self.current_fits = fits_path

        # Load fits
        data, header = p2.load_fits(fits_path)

        # Create original.png
        p2.handler_color_image(data)

        # Update original Image
        self.img_left.setPixmap(
            QPixmap("results/original/original.png").scaled(
                500, 500,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
        )
    
    
    def schedule_update(self):
        '''
        reload the timer : if the slider is moved again, it pushes back the calculations
        
        :param self: Description
        '''
        if not self.current_fits:
            return
    
        self.update_timer.start(500)  # 500 ms
    
    
    def update_process_image(self):
        if not self.current_fits:
            return
        
        # read sliders'values
        fwhm = self.slider_fwhm.value() / 10.0
        threshold = self.slider_threshold.value()
        erode_kernel = self.slider_erode_kernel.value()
        nb_iter = self.slider_nb_iteration.value()
        
        # do processus starless
        data, header = p2.load_fits(self.current_fits)
        image = p2.handler_color_image(data)
        image_gray = p2.convert_in_grey(image)
        
        sources = p2.detect_stars(image_gray, fwhm, threshold)
        # avoid errors if source is None
        if sources is None:
            self.nb_stars = 0
            return        
                                                                  
        self.nb_stars = 0 if sources is None else len(sources)
        self.param_nb_stars.setText(str(self.nb_stars))
        mask = p2.star_mask(image_gray, sources)
        mask_blur = p2.mask_effects(mask, (3,3), (3,3))
        
        Ierode = p2.erode_image(image_gray, (erode_kernel, erode_kernel), nb_iter)
        
        final_image = p2.combinate_mask_image(mask_blur, Ierode, image_gray)
        
        # load the final image
        self.img_right.setPixmap(
            QPixmap("results/final_image/image_finale.png").scaled(
                500, 500,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
        )
        


if __name__ == "__main__":
    
    
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet()) # Apply dark style
    
    window = StarReducApp()
    window.show()
    sys.exit(app.exec())
    