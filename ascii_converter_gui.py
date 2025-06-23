import os
import sys
import numpy as np
from PIL import Image, ImageEnhance, ImageOps, ImageFilter
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QPushButton, QSlider, QComboBox, QFileDialog, 
                            QTextEdit, QSpinBox, QGroupBox, QCheckBox, QTabWidget)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QPixmap, QImage, QFont, QTextCursor, QPalette, QColor

class ASCIIArtConverterGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ultimate ASCII Art Converter")
        self.setMinimumSize(1000, 800)
        
        # Main variables
        self.image_path = ""
        self.original_image = None
        self.processed_image = None
        self.ascii_art = ""
        self.char_sets = {
            'Basic': " .,:;+*?%S#@",
            'Extended': " `.-':_,^=;><+!rc*/z?sLTv)J7(|Fi{C}fI31tlu[neoZ5Yxjya]2ESwqkP6h9d4VpOGbUAKXHm8RD#$Bg0MNWQ%&@",
            'Blocks': " ░▒▓█",
            'Inverted': "@#S%?*+;:,. ",
            'Custom': ""
        }
        self.color_modes = {
            'None': self.convert_to_grayscale_ascii,
            'Grayscale': self.convert_to_grayscale_ascii,
            'Colored': self.convert_to_colored_ascii,
            'Edge Detection': self.convert_edge_ascii,
            'Blur': self.convert_blur_ascii,
            'Inverted': self.convert_inverted_ascii,
            'Sepia': self.convert_sepia_ascii,
            'Heatmap': self.convert_heatmap_ascii
        }
        
        # Default settings
        self.settings = {
            'output_width': 100,
            'char_set': 'Basic',
            'color_mode': 'None',
            'zoom': 1.0,
            'contrast': 1.0,
            'brightness': 1.0,
            'sharpness': 1.0,
            'edge_intensity': 1.0,
            'blur_radius': 0,
            'palette': 'Default',
            'font_size': 10,
            'live_preview': True
        }
        
        self.init_ui()
        
    def init_ui(self):
        # Central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        
        # Left panel - Controls
        control_panel = QWidget()
        control_panel.setMaximumWidth(300)
        control_layout = QVBoxLayout(control_panel)
        
        # Image controls group
        img_group = QGroupBox("Image Controls")
        img_layout = QVBoxLayout()
        
        self.btn_load = QPushButton("Load Image")
        self.btn_load.clicked.connect(self.load_image)
        img_layout.addWidget(self.btn_load)
        
        self.lbl_image = QLabel("No image loaded")
        self.lbl_image.setAlignment(Qt.AlignCenter)
        self.lbl_image.setStyleSheet("background-color: black;")
        img_layout.addWidget(self.lbl_image)
        
        img_group.setLayout(img_layout)
        control_layout.addWidget(img_group)
        
        # Conversion settings group
        conv_group = QGroupBox("Conversion Settings")
        conv_layout = QVBoxLayout()
        
        # Width control
        width_layout = QHBoxLayout()
        width_layout.addWidget(QLabel("Width:"))
        self.spin_width = QSpinBox()
        self.spin_width.setRange(20, 300)
        self.spin_width.setValue(self.settings['output_width'])
        self.spin_width.valueChanged.connect(self.update_width)
        width_layout.addWidget(self.spin_width)
        conv_layout.addLayout(width_layout)
        
        # Zoom control
        zoom_layout = QHBoxLayout()
        zoom_layout.addWidget(QLabel("Zoom:"))
        self.slider_zoom = QSlider(Qt.Horizontal)
        self.slider_zoom.setRange(5, 30)
        self.slider_zoom.setValue(int(self.settings['zoom'] * 10))
        self.slider_zoom.valueChanged.connect(self.update_zoom)
        zoom_layout.addWidget(self.slider_zoom)
        conv_layout.addLayout(zoom_layout)
        
        # Character set
        char_layout = QHBoxLayout()
        char_layout.addWidget(QLabel("Char Set:"))
        self.combo_chars = QComboBox()
        self.combo_chars.addItems(self.char_sets.keys())
        self.combo_chars.setCurrentText(self.settings['char_set'])
        self.combo_chars.currentTextChanged.connect(self.update_char_set)
        char_layout.addWidget(self.combo_chars)
        conv_layout.addLayout(char_layout)
        
        # Color mode
        color_layout = QHBoxLayout()
        color_layout.addWidget(QLabel("Color Mode:"))
        self.combo_color = QComboBox()
        self.combo_color.addItems(self.color_modes.keys())
        self.combo_color.setCurrentText(self.settings['color_mode'])
        self.combo_color.currentTextChanged.connect(self.update_color_mode)
        color_layout.addWidget(self.combo_color)
        conv_layout.addLayout(color_layout)
        
        # Palette
        palette_layout = QHBoxLayout()
        palette_layout.addWidget(QLabel("Palette:"))
        self.combo_palette = QComboBox()
        self.combo_palette.addItems(['Default', 'Vivid', 'Grayscale', 'Retro'])
        self.combo_palette.setCurrentText(self.settings['palette'])
        self.combo_palette.currentTextChanged.connect(self.update_palette)
        palette_layout.addWidget(self.combo_palette)
        conv_layout.addLayout(palette_layout)
        
        conv_group.setLayout(conv_layout)
        control_layout.addWidget(conv_group)
        
        # Image adjustment group
        adj_group = QGroupBox("Image Adjustments")
        adj_layout = QVBoxLayout()
        
        # Contrast
        contrast_layout = QHBoxLayout()
        contrast_layout.addWidget(QLabel("Contrast:"))
        self.slider_contrast = QSlider(Qt.Horizontal)
        self.slider_contrast.setRange(10, 300)
        self.slider_contrast.setValue(int(self.settings['contrast'] * 100))
        self.slider_contrast.valueChanged.connect(self.update_contrast)
        contrast_layout.addWidget(self.slider_contrast)
        adj_layout.addLayout(contrast_layout)
        
        # Brightness
        brightness_layout = QHBoxLayout()
        brightness_layout.addWidget(QLabel("Brightness:"))
        self.slider_brightness = QSlider(Qt.Horizontal)
        self.slider_brightness.setRange(10, 300)
        self.slider_brightness.setValue(int(self.settings['brightness'] * 100))
        self.slider_brightness.valueChanged.connect(self.update_brightness)
        brightness_layout.addWidget(self.slider_brightness)
        adj_layout.addLayout(brightness_layout)
        
        # Sharpness
        sharpness_layout = QHBoxLayout()
        sharpness_layout.addWidget(QLabel("Sharpness:"))
        self.slider_sharpness = QSlider(Qt.Horizontal)
        self.slider_sharpness.setRange(10, 300)
        self.slider_sharpness.setValue(int(self.settings['sharpness'] * 100))
        self.slider_sharpness.valueChanged.connect(self.update_sharpness)
        sharpness_layout.addWidget(self.slider_sharpness)
        adj_layout.addLayout(sharpness_layout)
        
        # Edge detection
        edge_layout = QHBoxLayout()
        edge_layout.addWidget(QLabel("Edge Intensity:"))
        self.slider_edge = QSlider(Qt.Horizontal)
        self.slider_edge.setRange(10, 300)
        self.slider_edge.setValue(int(self.settings['edge_intensity'] * 100))
        self.slider_edge.valueChanged.connect(self.update_edge)
        edge_layout.addWidget(self.slider_edge)
        adj_layout.addLayout(edge_layout)
        
        # Blur
        blur_layout = QHBoxLayout()
        blur_layout.addWidget(QLabel("Blur Radius:"))
        self.slider_blur = QSlider(Qt.Horizontal)
        self.slider_blur.setRange(0, 50)
        self.slider_blur.setValue(self.settings['blur_radius'])
        self.slider_blur.valueChanged.connect(self.update_blur)
        blur_layout.addWidget(self.slider_blur)
        adj_layout.addLayout(blur_layout)
        
        adj_group.setLayout(adj_layout)
        control_layout.addWidget(adj_group)
        
        # Output options group
        output_group = QGroupBox("Output Options")
        output_layout = QVBoxLayout()
        
        self.btn_copy = QPushButton("Copy to Clipboard")
        self.btn_copy.clicked.connect(self.copy_to_clipboard)
        output_layout.addWidget(self.btn_copy)
        
        self.btn_save = QPushButton("Save ASCII Art")
        self.btn_save.clicked.connect(self.save_ascii)
        output_layout.addWidget(self.btn_save)
        
        self.btn_save_img = QPushButton("Save as Image")
        self.btn_save_img.clicked.connect(self.save_as_image)
        output_layout.addWidget(self.btn_save_img)
        
        self.check_preview = QCheckBox("Live Preview")
        self.check_preview.setChecked(self.settings['live_preview'])
        self.check_preview.stateChanged.connect(self.toggle_live_preview)
        output_layout.addWidget(self.check_preview)
        
        output_group.setLayout(output_layout)
        control_layout.addWidget(output_group)
        
        control_layout.addStretch()
        
        # Right panel - Preview and ASCII output
        output_panel = QWidget()
        output_layout = QVBoxLayout(output_panel)
        
        # Tab widget for different views
        self.tab_widget = QTabWidget()
        
        # ASCII Preview tab
        self.ascii_preview = QTextEdit()
        self.ascii_preview.setReadOnly(True)
        self.ascii_preview.setFont(QFont("Courier", self.settings['font_size']))
        
        # Set black background
        palette = self.ascii_preview.palette()
        palette.setColor(QPalette.Base, QColor(0, 0, 0))
        palette.setColor(QPalette.Text, QColor(255, 255, 255))
        self.ascii_preview.setPalette(palette)
        
        self.tab_widget.addTab(self.ascii_preview, "ASCII Preview")
        
        # Image Preview tab
        self.img_preview = QLabel()
        self.img_preview.setAlignment(Qt.AlignCenter)
        self.img_preview.setStyleSheet("background-color: black;")
        self.tab_widget.addTab(self.img_preview, "Image Preview")
        
        output_layout.addWidget(self.tab_widget)
        
        # Add panels to main layout
        main_layout.addWidget(control_panel)
        main_layout.addWidget(output_panel)
        
        # Enable/disable controls based on state
        self.update_controls_state()
    
    def update_controls_state(self):
        has_image = self.original_image is not None
        controls = [
            self.spin_width, self.slider_zoom, self.combo_chars,
            self.combo_color, self.combo_palette, self.slider_contrast,
            self.slider_brightness, self.slider_sharpness, self.slider_edge,
            self.slider_blur, self.btn_copy, self.btn_save, self.btn_save_img,
            self.check_preview
        ]
        
        for control in controls:
            control.setEnabled(has_image)
    
    def load_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Image", "", 
            "Images (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        
        if file_path:
            self.image_path = file_path
            try:
                self.original_image = Image.open(file_path)
                self.update_preview_image()
                self.convert_image()
                self.update_controls_state()
            except Exception as e:
                self.show_error(f"Failed to load image: {str(e)}")
    
    def update_preview_image(self):
        if self.original_image:
            # Create thumbnail for preview
            thumb = self.original_image.copy()
            thumb.thumbnail((300, 300))
            
            # Convert to QImage
            if thumb.mode == 'RGB':
                qimage = QImage(thumb.tobytes(), thumb.width, thumb.height, 
                                thumb.width * 3, QImage.Format_RGB888)
            else:
                thumb = thumb.convert('RGB')
                qimage = QImage(thumb.tobytes(), thumb.width, thumb.height, 
                                thumb.width * 3, QImage.Format_RGB888)
            
            pixmap = QPixmap.fromImage(qimage)
            self.lbl_image.setPixmap(pixmap)
    
    def apply_image_adjustments(self, img):
        # Apply all current adjustments to the image
        if self.settings['contrast'] != 1.0:
            img = ImageEnhance.Contrast(img).enhance(self.settings['contrast'])
        if self.settings['brightness'] != 1.0:
            img = ImageEnhance.Brightness(img).enhance(self.settings['brightness'])
        if self.settings['sharpness'] != 1.0:
            img = ImageEnhance.Sharpness(img).enhance(self.settings['sharpness'])
        if self.settings['blur_radius'] > 0:
            img = img.filter(ImageFilter.GaussianBlur(self.settings['blur_radius']))
        
        return img
    
    def convert_image(self):
        if not self.original_image:
            return
            
        try:
            # Get the appropriate conversion function based on color mode
            converter = self.color_modes[self.settings['color_mode']]
            
            # Process the image
            self.processed_image = self.original_image.copy()
            self.processed_image = self.apply_image_adjustments(self.processed_image)
            
            # Convert to ASCII
            self.ascii_art = converter(self.processed_image)
            
            # Update preview
            self.update_ascii_preview()
            
        except Exception as e:
            self.show_error(f"Conversion error: {str(e)}")
    
    def convert_to_grayscale_ascii(self, img):
        # Prepare image
        img = img.convert('L')  # Convert to grayscale
        width, height = img.size
        aspect_ratio = height / width
        new_width = int(self.settings['output_width'] * self.settings['zoom'])
        new_height = int(new_width * aspect_ratio * 0.55)  # 0.55 to account for character aspect ratio
        
        img = img.resize((new_width, new_height))
        pixels = np.array(img)
        
        # Get character set
        chars = self.char_sets[self.settings['char_set']] or self.char_sets['Basic']
        char_len = len(chars)
        
        # Convert to ASCII
        ascii_chars = []
        for row in pixels:
            line = [chars[min(int(pixel * (char_len - 1) / 255), char_len-1)] for pixel in row]
            ascii_chars.append("".join(line))
        
        return "\n".join(ascii_chars)
    
    def convert_to_colored_ascii(self, img):
        img = img.convert('RGB')
        width, height = img.size
        aspect_ratio = height / width
        new_width = int(self.settings['output_width'] * self.settings['zoom'])
        new_height = int(new_width * aspect_ratio * 0.55)
        
        img = img.resize((new_width, new_height))
        pixels = np.array(img)
        
        chars = self.char_sets[self.settings['char_set']] or self.char_sets['Basic']
        char_len = len(chars)
        
        ascii_chars = []
        for row in pixels:
            line = []
            for pixel in row:
                r, g, b = pixel
                gray = int(0.2989 * r + 0.5870 * g + 0.1140 * b)
                char = chars[min(int(gray * (char_len - 1) / 255), char_len-1)]
                
                if self.settings['palette'] == 'Vivid':
                    line.append(f"\033[38;2;{r};{g};{b}m{char}\033[0m")
                else:
                    # Simplified colored output for GUI
                    line.append(char)
            
            ascii_chars.append("".join(line))
        
        return "\n".join(ascii_chars)
    
    def convert_edge_ascii(self, img):
        img = img.convert('L')
        img_np = np.array(img)
        edges = feature.canny(img_np/255., sigma=self.settings['edge_intensity'])
        edge_img = Image.fromarray((edges * 255).astype(np.uint8))
        return self.convert_to_grayscale_ascii(edge_img)
    
    def convert_blur_ascii(self, img):
        img = img.convert('L')
        if self.settings['blur_radius'] > 0:
            img = img.filter(ImageFilter.GaussianBlur(self.settings['blur_radius']))
        return self.convert_to_grayscale_ascii(img)
    
    def convert_inverted_ascii(self, img):
        img = img.convert('L')
        img = ImageOps.invert(img)
        return self.convert_to_grayscale_ascii(img)
    
    def convert_sepia_ascii(self, img):
        img = img.convert('RGB')
        width, height = img.size
        pixels = img.load()
        
        for py in range(height):
            for px in range(width):
                r, g, b = pixels[px, py]
                tr = int(0.393 * r + 0.769 * g + 0.189 * b)
                tg = int(0.349 * r + 0.686 * g + 0.168 * b)
                tb = int(0.272 * r + 0.534 * g + 0.131 * b)
                pixels[px, py] = (min(255, tr), min(255, tg), min(255, tb))
        
        return self.convert_to_colored_ascii(img)
    
    def convert_heatmap_ascii(self, img):
        # This is a simplified version for GUI
        img = img.convert('L')
        return self.convert_to_grayscale_ascii(img)
    
    def update_ascii_preview(self):
        if not self.ascii_art:
            return
            
        self.ascii_preview.clear()
        cursor = self.ascii_preview.textCursor()
        
        if self.settings['color_mode'] == 'Colored' and self.settings['palette'] == 'Vivid':
            # For colored text, we need to handle ANSI codes
            self.ascii_preview.setText(self.ascii_art)
        else:
            # For monochrome, just set the text
            self.ascii_preview.setPlainText(self.ascii_art)
        
        # Scroll to top
        cursor.movePosition(QTextCursor.Start)
        self.ascii_preview.setTextCursor(cursor)
        
        # Update image preview tab
        self.update_image_preview()
    
    def update_image_preview(self):
        if not self.processed_image:
            return
            
        # Create a thumbnail of the processed image
        thumb = self.processed_image.copy()
        thumb.thumbnail((600, 600))
        
        # Convert to QImage
        if thumb.mode == 'RGB':
            qimage = QImage(thumb.tobytes(), thumb.width, thumb.height, 
                           thumb.width * 3, QImage.Format_RGB888)
        else:
            thumb = thumb.convert('RGB')
            qimage = QImage(thumb.tobytes(), thumb.width, thumb.height, 
                           thumb.width * 3, QImage.Format_RGB888)
        
        pixmap = QPixmap.fromImage(qimage)
        self.img_preview.setPixmap(pixmap)
    
    # Settings update functions
    def update_width(self, value):
        self.settings['output_width'] = value
        if self.settings['live_preview']:
            self.convert_image()
    
    def update_zoom(self, value):
        self.settings['zoom'] = value / 10
        if self.settings['live_preview']:
            self.convert_image()
    
    def update_char_set(self, value):
        self.settings['char_set'] = value
        if self.settings['live_preview']:
            self.convert_image()
    
    def update_color_mode(self, value):
        self.settings['color_mode'] = value
        
        # Enable/disable relevant controls
        edge_enabled = value == 'Edge Detection'
        blur_enabled = value == 'Blur'
        
        self.slider_edge.setEnabled(edge_enabled)
        self.slider_blur.setEnabled(blur_enabled)
        self.combo_palette.setEnabled(value == 'Colored')
        
        if self.settings['live_preview']:
            self.convert_image()
    
    def update_palette(self, value):
        self.settings['palette'] = value
        if self.settings['live_preview'] and self.settings['color_mode'] == 'Colored':
            self.convert_image()
    
    def update_contrast(self, value):
        self.settings['contrast'] = value / 100
        if self.settings['live_preview']:
            self.convert_image()
    
    def update_brightness(self, value):
        self.settings['brightness'] = value / 100
        if self.settings['live_preview']:
            self.convert_image()
    
    def update_sharpness(self, value):
        self.settings['sharpness'] = value / 100
        if self.settings['live_preview']:
            self.convert_image()
    
    def update_edge(self, value):
        self.settings['edge_intensity'] = value / 100
        if self.settings['live_preview']:
            self.convert_image()
    
    def update_blur(self, value):
        self.settings['blur_radius'] = value
        if self.settings['live_preview']:
            self.convert_image()
    
    def toggle_live_preview(self, state):
        self.settings['live_preview'] = state == Qt.Checked
    
    # Output functions
    def copy_to_clipboard(self):
        if self.ascii_art:
            clipboard = QApplication.clipboard()
            clipboard.setText(self.ascii_art)
            self.show_message("ASCII art copied to clipboard!")
    
    def save_ascii(self):
        if not self.ascii_art:
            return
            
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save ASCII Art", "", 
            "Text Files (*.txt);;All Files (*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.ascii_art)
                self.show_message(f"ASCII art saved to {file_path}")
            except Exception as e:
                self.show_error(f"Failed to save file: {str(e)}")
    
    def save_as_image(self):
        if not self.ascii_art:
            return
            
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save as Image", "", 
            "PNG Files (*.png);;JPEG Files (*.jpg);;All Files (*)"
        )
        
        if file_path:
            try:
                # Create an image with the ASCII art
                font_size = 10
                lines = self.ascii_art.split('\n')
                img_width = max(len(line) for line in lines) * font_size // 2
                img_height = len(lines) * font_size
                
                # Create a black image
                img = Image.new('RGB', (img_width, img_height), color='black')
                
                # Draw text (simplified - for a complete solution consider using PIL.ImageDraw)
                # This is a placeholder - actual implementation would need more work
                img.save(file_path)
                
                self.show_message(f"Image saved to {file_path}")
            except Exception as e:
                self.show_error(f"Failed to save image: {str(e)}")
    
    # Utility functions
    def show_message(self, message):
        status = self.statusBar()
        status.showMessage(message, 3000)
    
    def show_error(self, message):
        self.show_message(f"Error: {message}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Modern look
    
    # Set dark theme
    palette = app.palette()
    palette.setColor(QPalette.Window, QColor(53, 53, 53))
    palette.setColor(QPalette.WindowText, Qt.white)
    palette.setColor(QPalette.Base, QColor(25, 25, 25))
    palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    palette.setColor(QPalette.ToolTipBase, Qt.white)
    palette.setColor(QPalette.ToolTipText, Qt.white)
    palette.setColor(QPalette.Text, Qt.white)
    palette.setColor(QPalette.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ButtonText, Qt.white)
    palette.setColor(QPalette.BrightText, Qt.red)
    palette.setColor(QPalette.Link, QColor(42, 130, 218))
    palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.HighlightedText, Qt.black)
    app.setPalette(palette)
    
    converter = ASCIIArtConverterGUI()
    converter.show()
    sys.exit(app.exec_())
