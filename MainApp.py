import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QGroupBox, QLabel, QHBoxLayout, QListWidget, QPushButton, QSlider, QLineEdit, QFormLayout, QCheckBox, QFileDialog, QRadioButton, QButtonGroup, QSizePolicy, QMessageBox
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt, QTimer
import qdarkstyle # Dark mode
import os
import main_p2_origin as p2
import main_p3_starnet as p3
import shutil

FOLDER_EXAMPLES = "./examples"
FOLDER_STARNET = "./star_reduction"

class StarReducApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Star reduction App")
        self.resize(1200, 800)   # width, height
        
        # variables for process
        self.current_fits = None
        self.current_fits_starless = None
        self.current_fits_staronly = None
        self.nb_stars = 0
        
        # timer anti-spam (debounce) in order to avoid too many calculations
        self.update_timer = QTimer(self)
        self.update_timer.setSingleShot(True)
        self.update_timer.timeout.connect(self.update_process_image_choice)
        
        # main layout for window
        main_widget = QWidget(self)
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)
        
        # =================================================================
        # ======================== TOP PART ===============================
        # =================================================================
        
        # ========================= Left Image ============================
        self.box_left = QGroupBox()
        self.box_left.setTitle("Original Image")
        self.box_left.setMaximumHeight(650)
        layout_left = QVBoxLayout()
        self.box_left.setLayout(layout_left)

        self.img_left = QLabel()
        self.img_left.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout_left.addWidget(self.img_left)
        
        # ========================= Center Image =======================
        # hidden if daefault option and showed if starNet
        self.box_starNet = QGroupBox()
        self.box_starNet.setTitle("Starless")
        self.box_starNet.setMaximumHeight(650)
        layout_center = QVBoxLayout()
        self.box_starNet.setLayout(layout_center)

        self.img_center = QLabel()
        self.img_center.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout_center.addWidget(self.img_center)
        self.box_starNet.setVisible(False)

        # ========================= Right Image ===========================
        box_right = QGroupBox("Processed Image")
        box_right.setMaximumHeight(650)
        layout_right = QVBoxLayout()
        box_right.setLayout(layout_right)

        self.img_right = QLabel()
        self.img_right.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout_right.addWidget(self.img_right)

        # ==================== Add Image Box in Top =======================
        self.box_left.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.box_starNet.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        box_right.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.img_left.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
        self.img_center.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
        self.img_right.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
        
        top_layout = QHBoxLayout()
        top_layout.addWidget(self.box_left)
        top_layout.addWidget(self.box_starNet)
        top_layout.addWidget(box_right)


        # =================================================================
        # ======================== BOTTOM PART ============================
        # =================================================================

        # ============================= Left ===============================
        self.left_list = QListWidget()
        self.left_list.setFixedHeight(450)
        
        # infill list with files from folder example
        for nameFiles in os.listdir(FOLDER_EXAMPLES):
            self.left_list.addItem(nameFiles)
        
        self.left_list.itemClicked.connect(self.on_item_clicked_choice)    

        # ============================ Center ==============================
        self.central_widget = QWidget()
        self.central_container = QVBoxLayout(self.central_widget)
        
        self.model_box = QGroupBox("Models")
        self.model_layout = QVBoxLayout()
        self.model_box.setLayout(self.model_layout)
        self.model_box.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        self.model_box.setMaximumHeight(140) 
        self.central_container.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # Settings for phase 2
        self.center_box = QGroupBox("Settings")
        self.center_layout = QVBoxLayout()
        self.center_box.setLayout(self.center_layout)
        
        # Settings for phase 3 Netstar
        self.center_box_netstar = QGroupBox("Settings")
        self.center_layout_netstar = QVBoxLayout()
        self.center_box_netstar.setLayout(self.center_layout_netstar)

        # Radio buttons
        choice_row = QHBoxLayout()

        # first column
        col_1 = QVBoxLayout()
        self.case_p2 = QRadioButton()
        label_case_p2 = QLabel("Standard")
        label_case_p2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        col_1.addWidget(self.case_p2, alignment=Qt.AlignmentFlag.AlignCenter)
        col_1.addWidget(label_case_p2)

        # second column
        col_2 = QVBoxLayout()
        self.case_starNet = QRadioButton()
        label_case_starNet = QLabel("StarNet")
        label_case_starNet.setAlignment(Qt.AlignmentFlag.AlignCenter)
        col_2.addWidget(self.case_starNet, alignment=Qt.AlignmentFlag.AlignCenter)
        col_2.addWidget(label_case_starNet)

        # Assemblage
        choice_row.addLayout(col_1)
        choice_row.addLayout(col_2)
        self.model_layout.addLayout(choice_row)

        # exclusive group
        self.model_group = QButtonGroup(self)
        self.model_group.setExclusive(True)
        self.model_group.addButton(self.case_p2)
        self.model_group.addButton(self.case_starNet)

        self.case_p2.setChecked(True)  # default option

        self.model_group.buttonToggled.connect(self.on_model_changed)
        
        # Sliders for phase 2
        # First Slider fwhm
        self.slider_fwhm_label = QLabel("Fwhm")
        self.slider_fwhm_label.setToolTip("Full Width at Half Maximum => size of star in pixel")
        self.slider_fwhm_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.slider_fwhm = QSlider(Qt.Orientation.Horizontal)
        self.slider_fwhm.setMinimum(1)
        self.slider_fwhm.setMaximum(100)
        self.slider_fwhm.setValue(40)
        self.slider_fwhm.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.slider_fwhm.setTickInterval(1)
        self.slider_fwhm.setSingleStep(1)
        # value bottom 
        self.value_label_slider_fwhm = QLabel("4")
        self.value_label_slider_fwhm.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.slider_fwhm.valueChanged.connect(
            lambda v: (self.value_label_slider_fwhm.setText(str(v)),
                       self.schedule_update()
            )
        )
        
        self.center_layout.addWidget(self.slider_fwhm_label)
        self.center_layout.addWidget(self.slider_fwhm)
        self.center_layout.addWidget(self.value_label_slider_fwhm)
        
        # Second Slider threshold
        self.slider_threshold_label = QLabel("Threshold")
        self.slider_threshold_label.setToolTip("The detection threshold")
        self.slider_threshold_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.slider_threshold = QSlider(Qt.Orientation.Horizontal)
        self.slider_threshold.setMinimum(1)
        self.slider_threshold.setMaximum(20)
        self.slider_threshold.setValue(5)
        self.slider_threshold.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.slider_threshold.setTickInterval(1)
        self.slider_threshold.setSingleStep(1)
        
        self.value_label_slider_threshold = QLabel("5")
        self.value_label_slider_threshold.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.slider_threshold.valueChanged.connect(
            lambda v: (self.value_label_slider_threshold.setText(str(v)),
                       self.schedule_update()
            )
        )
        
        self.center_layout.addWidget(self.slider_threshold_label)
        self.center_layout.addWidget(self.slider_threshold)
        self.center_layout.addWidget(self.value_label_slider_threshold)

        # Third Slider erode_kernel
        self.slider_erode_kernel_label = QLabel("Erode kernel")
        self.slider_erode_kernel_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.slider_erode_kernel = QSlider(Qt.Orientation.Horizontal)
        self.slider_erode_kernel.setMinimum(1)
        self.slider_erode_kernel.setMaximum(100)
        self.slider_erode_kernel.setValue(2)
        self.slider_erode_kernel.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.slider_erode_kernel.setTickInterval(1)
        self.slider_erode_kernel.setSingleStep(1)
        
        self.value_label_slider_erode_kernel = QLabel("2")
        self.value_label_slider_erode_kernel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.slider_erode_kernel.valueChanged.connect(
            lambda v: (self.value_label_slider_erode_kernel.setText(str(v)),
                       self.schedule_update()
                       )
        )
        
        self.center_layout.addWidget(self.slider_erode_kernel_label)
        self.center_layout.addWidget(self.slider_erode_kernel)
        self.center_layout.addWidget(self.value_label_slider_erode_kernel)
        
        # Fourth Slider nb Iteration erode
        self.slider_nb_iteration_label = QLabel("Number of erosion iterations")
        self.slider_nb_iteration_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.slider_nb_iteration = QSlider(Qt.Orientation.Horizontal)
        self.slider_nb_iteration.setMinimum(1)
        self.slider_nb_iteration.setMaximum(20)
        self.slider_nb_iteration.setValue(2)
        self.slider_nb_iteration.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.slider_nb_iteration.setTickInterval(1)
        self.slider_nb_iteration.setSingleStep(1)
        
        self.value_label_slider_nb_iteration = QLabel("2")
        self.value_label_slider_nb_iteration.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.slider_nb_iteration.valueChanged.connect(
            lambda v: (self.value_label_slider_nb_iteration.setText(str(v)),
                       self.schedule_update()
            )
        )
        
        self.center_layout.addWidget(self.slider_nb_iteration_label)
        self.center_layout.addWidget(self.slider_nb_iteration)
        self.center_layout.addWidget(self.value_label_slider_nb_iteration)
        
        # Sliders pour phase 3 NetsStar
        # First Slider threshold
        self.slider_netstar_threshold_label = QLabel("Threshold")
        self.slider_netstar_threshold_label.setToolTip("The detection threshold")
        self.slider_netstar_threshold_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.slider_netstar_threshold = QSlider(Qt.Orientation.Horizontal)
        self.slider_netstar_threshold.setMinimum(1)
        self.slider_netstar_threshold.setMaximum(100)
        self.slider_netstar_threshold.setValue(5)
        self.slider_netstar_threshold.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.slider_netstar_threshold.setTickInterval(1)
        self.slider_netstar_threshold.setSingleStep(5)
        
        self.value_label_slider_netstar_threshold = QLabel("5")
        self.value_label_slider_netstar_threshold.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.slider_netstar_threshold.valueChanged.connect(
            lambda v: (self.value_label_slider_netstar_threshold.setText(str(v)),
                       self.schedule_update()
            )
        )
        
        self.center_layout_netstar.addWidget(self.slider_netstar_threshold_label)
        self.center_layout_netstar.addWidget(self.slider_netstar_threshold)
        self.center_layout_netstar.addWidget(self.value_label_slider_netstar_threshold)

        # Second Slider alpha
        self.slider_netstar_alpha_label = QLabel("Alpha : reduction coefficient")
        self.slider_netstar_alpha_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.slider_netstar_alpha = QSlider(Qt.Orientation.Horizontal)
        self.slider_netstar_alpha.setMinimum(0)
        self.slider_netstar_alpha.setMaximum(10)
        self.slider_netstar_alpha.setValue(2)
        self.slider_netstar_alpha.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.slider_netstar_alpha.setTickInterval(1)
        self.slider_netstar_alpha.setSingleStep(1)
        
        self.value_label_slider_netstar_alpha = QLabel("2")
        self.value_label_slider_netstar_alpha.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.slider_netstar_alpha.valueChanged.connect(
            lambda v: (self.value_label_slider_netstar_alpha.setText(str(v)),
                       self.schedule_update()
                       )
        )
        
        self.center_layout_netstar.addWidget(self.slider_netstar_alpha_label)
        self.center_layout_netstar.addWidget(self.slider_netstar_alpha)
        self.center_layout_netstar.addWidget(self.value_label_slider_netstar_alpha)
        
        
        self.central_container.addWidget(self.model_box)
        self.central_container.addWidget(self.center_box)
        self.central_container.addWidget(self.center_box_netstar) 
        self.center_box_netstar.setVisible(False)
        
        # ============================= Right ==============================
        right_box = QGroupBox("Parameters")
        right_box.setFixedHeight(450) 
        
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
        btn_save = QPushButton("Save Image")
        right_main_layout.addWidget(btn_save)
        
        btn_save.clicked.connect(self.save_image_as)
        
        # ==================== Add elements in Bottom =======================
        bottom_layout = QHBoxLayout()
        bottom_layout.addWidget(self.left_list)
        bottom_layout.addWidget(self.central_widget)
        bottom_layout.addWidget(right_box)

        
        # =================================================================
        # ======================== ASSOCIATION ============================
        # =================================================================
        main_layout.addLayout(top_layout)
        main_layout.addLayout(bottom_layout)
        
        # initialize UI
        self.apply_models()

    
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
    
    
    def on_item_clicked_starnet(self, item):
        '''
        load the original image matching with the selected fits
        
        :param item: the fits'name selected
        '''
        filename = item.text() # test_M31_linear.fits

        # recover name for create image_starless & image_stramask
        name, ext = os.path.splitext(filename)
        image_name_starless = f"starless_{name}.fit" # starless_starless_test_M31_linear.fit
        image_name_staronly = f"starmask_{name}.fit"
        image_png_name_starless = f"starless_{name}.png"# starless_starless_test_M31_linear.png
        image_png_name_staronly = f"starmask_{name}.png"
        
        self.current_fits_starless = os.path.join(FOLDER_STARNET, image_name_starless)
        self.current_fits_staronly = os.path.join(FOLDER_STARNET, image_name_staronly)

        # Load starless and apply handler_color_image for normalization
        data_starless, header_starless = p3.load_fits(FOLDER_STARNET + "/" + image_name_starless)
        starless = p3.handler_color_image(data_starless)

        # Load staronly and apply handler_color_image for normalization
        data_staronly, header_staronly = p3.load_fits(FOLDER_STARNET + "/" + image_name_staronly)
        staronly = p3.handler_color_image(data_staronly)

        p3.save_image(FOLDER_STARNET + "/" + image_png_name_starless, starless)
        p3.save_image(FOLDER_STARNET + "/" + image_png_name_staronly, staronly)
       
        # Update original Image
        self.img_left.setPixmap(
            QPixmap(FOLDER_STARNET + "/" +  image_png_name_staronly).scaled(
                500, 500,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
        )
        
        self.img_center.setPixmap(
            QPixmap(FOLDER_STARNET + "/" +  image_png_name_starless).scaled(
                500, 500,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
        )
        
        
    def on_item_clicked_choice(self, item):
        # Handler clic on item
        if (self.is_starnet_model()):
            self.on_item_clicked_starnet(item)
        else:
            self.on_item_clicked(item)
        
        self.schedule_update() 
        
    
    
    def schedule_update(self):
        '''
        reload the timer : if the slider is moved again, it pushes back the calculations
        
        :param self: Description
        '''
        # Standard
        if not self.is_starnet_model():
            if not self.current_fits:
                return
        # StarNet
        else:
            if not self.current_fits_starless or not self.current_fits_staronly:
                return

        self.update_timer.start(200)  # 200 ms
    
    
    def update_process_image(self):
        '''
        Calculate all processus for create the final image
        
        Read sliders'values for use in parameters of the differents function
        and display the final image in appropriate box
        '''
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
    
    def update_process_starnet(self):
        
        if not self.current_fits_starless or not self.current_fits_staronly :
            return
        
        # read sliders'values
        alpha = self.slider_netstar_alpha.value() / 10.0
        thresh = self.slider_netstar_threshold.value() / 100.0
        
        # Load starless and apply handler_color_image for normalization
        data_starless, header_starless = p3.load_fits(self.current_fits_starless)
        starless = p3.handler_color_image(data_starless)

        # Load staronly and apply handler_color_image for normalization
        data_staronly, header_staronly = p3.load_fits(self.current_fits_staronly)
        staronly = p3.handler_color_image(data_staronly)

        # Convert in grey
        staronly_gray = p3.convert_in_grey(staronly)
        starless_file_gray = p3.convert_in_grey(starless)

        # Create mask from staronly image
        mask = p3.mask_from_stars_starnet(staronly_gray, thresh)

        # Apply Gaussian Blur
        maskFlouGaussien = p3.mask_effects(mask, (3, 3), (3, 3), iterations=1)

        # Reduce staronly image with the mask and alpha factor
        star_reduced = p3.reduce_stars(staronly_gray, maskFlouGaussien, alpha)

        before, after, diff_abs = p3.save_diff_img(
            starless_file_gray, staronly_gray, star_reduced
        )

        # blink = p3.blink_image(before, after, delay=0.5, n=10)

        # Combine starless image and reduced staronly image
        final = p3.combinate_mask_image(starless_file_gray, star_reduced)

        # load the final image
        self.img_right.setPixmap(
            QPixmap("results/final_image/final_combined_phase3.png").scaled(
                500, 500,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
        )
    
    def update_process_image_choice(self):
        # Handler clic on item
        if (self.is_starnet_model()):
            self.update_process_starnet()
        else:
            self.update_process_image()
        
    
    def on_model_changed(self, button, checked):
        if not checked:
            return  # ignore auto unchecked from the other button
        self.apply_models()
        self.schedule_update()
        
        
    def save_image_as(self):
        '''
        Save the final image in a personal folder
        
        '''
        # the final image's path
        src_path = "results/final_image/image_finale.png"

        # avoid file exists
        if not os.path.exists(src_path):
            return

        # open DialogBox
        dest_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save image",
            "",
            "Images PNG (*.png);;Images JPG (*.jpg)"
        )

        if not dest_path:
            return  # annulation user

        # copy image
        shutil.copyfile(src_path, dest_path)


    def apply_models(self):
        starNet = self.case_starNet.isChecked()
    
        self.box_starNet.setVisible(starNet)
        self.center_box.setVisible(not starNet)
        self.center_box_netstar.setVisible(starNet)
        self.box_left.setTitle("Staronly" if starNet else "Original Image")
    
    
    def is_starnet_model(self):
        return self.case_starNet.isChecked()

            

if __name__ == "__main__":
    
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet()) # Apply dark style
    
    window = StarReducApp()
    window.showMaximized()
  
    sys.exit(app.exec())
