import os
import sys
import time
from PIL import Image, ImageEnhance, ImageOps, ImageFilter
import numpy as np
import keyboard
from termcolor import colored
import pyperclip
import cv2
from skimage import feature
from colorama import init, Back, Fore
import matplotlib.pyplot as plt
from concurrent.futures import ThreadPoolExecutor
import argparse
import json

init()  # Colorama'yı başlat

class UltimateASCIIArtConverter:
    def __init__(self):
        self.image_path = ""
        self.ascii_art = ""
        self.output_width = 100
        self.char_sets = {
            'basic': " .,:;+*?%S#@",
            'extended': " `.-':_,^=;><+!rc*/z?sLTv)J7(|Fi{C}fI31tlu[neoZ5Yxjya]2ESwqkP6h9d4VpOGbUAKXHm8RD#$Bg0MNWQ%&@",
            'blocks': " ░▒▓█",
            'inverted': "@#S%?*+;:,. ",
            'custom': ""
        }
        self.current_char_set = 'basic'
        self.color_modes = {
            'none': "No color",
            'grayscale': "Grayscale",
            'colored': "Colored",
            'edge': "Edge detection",
            'blur': "Blur effect",
            'invert': "Inverted",
            'sepia': "Sepia tone",
            'heatmap': "Heatmap"
        }
        self.current_color_mode = 'none'
        self.preview_mode = True
        self.zoom_level = 1.0
        self.contrast = 1.0
        self.brightness = 1.0
        self.sharpness = 1.0
        self.edge_intensity = 1.0
        self.blur_radius = 0
        self.animation_frames = []
        self.animation_speed = 0.1
        self.is_animated = False
        self.palette = "default"
        self.save_config = {
            'format': 'txt',
            'html_wrap': False,
            'font_size': 12,
            'bg_color': 'black'
        }
        self.history = []
        self.max_history = 5
        self.config_file = "ascii_config.json"
        self.load_config()

    # -------------------- Core Functions --------------------
    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def display_header(self):
        print(colored("╔════════════════════════════════════════════════════════════════╗", 'cyan'))
        print(colored("║", 'cyan') + colored("        🎨 ULTIMATE ASCII ART CONVERTER PRO 🎨        ", 'magenta', attrs=['bold']) + colored("║", 'cyan'))
        print(colored("╚════════════════════════════════════════════════════════════════╝", 'cyan'))
    
    def display_status(self):
        print(colored("\n⚙️ CURRENT SETTINGS:", 'yellow', attrs=['bold']))
        print(colored(f"📁 Image: {self.image_path if self.image_path else 'Not selected'}", 'yellow'))
        print(colored(f"🖥️  Width: {self.output_width} | 🔍 Zoom: {self.zoom_level:.1f}x", 'yellow'))
        print(colored(f"🎨 Color Mode: {self.color_modes[self.current_color_mode]}", 'yellow'))
        print(colored(f"🔤 Char Set: {self.current_char_set} ({self.char_sets[self.current_char_set][:10]}...)", 'yellow'))
        print(colored(f"🌈 Palette: {self.palette}", 'yellow'))
        print(colored(f"⚡ Adjustments: Contrast={self.contrast:.1f} Brightness={self.brightness:.1f}", 'yellow'))
        print(colored(f"✨ Effects: Sharpness={self.sharpness:.1f} Edge={self.edge_intensity:.1f} Blur={self.blur_radius}", 'yellow'))
    
    def display_controls(self):
        print(colored("\n🎮 CONTROLS:", 'green', attrs=['bold']))
        print(colored("┌──────────────┬──────────────┬──────────────┬──────────────┐", 'green'))
        print(colored("│ [O]pen Image │ [W]idth     │ [C]olor Mode │ [K]eyboard   │", 'green'))
        print(colored("├──────────────┼──────────────┼──────────────┼──────────────┤", 'green'))
        print(colored("│ [Z]oom       │ [B]rightness│ [T]Contrast  │ [S]harpness  │", 'green'))
        print(colored("├──────────────┼──────────────┼──────────────┼──────────────┤", 'green'))
        print(colored("│ [E]dge Detect│ [L]Blur     │ [P]alette    │ [A]nimation  │", 'green'))
        print(colored("├──────────────┼──────────────┼──────────────┼──────────────┤", 'green'))
        print(colored("│ [S]ave       │ [V]iew Full │ [H]istory    │ [D]uplicate  │", 'green'))
        print(colored("├──────────────┼──────────────┼──────────────┼──────────────┤", 'green'))
        print(colored("│ [U]ndo       │ [R]efresh   │ [I]nfo       │ [Q]uit       │", 'green'))
        print(colored("└──────────────┴──────────────┴──────────────┴──────────────┘", 'green'))
    
    def display_preview(self):
        if not self.ascii_art:
            return
            
        print(colored("\n🖼️ ASCII PREVIEW (Press SPACE for fullscreen):", 'magenta', attrs=['bold']))
        lines = self.ascii_art.split('\n')
        preview_lines = min(15, len(lines))
        
        for line in lines[:preview_lines]:
            if self.current_color_mode == 'colored':
                print(colored(line, 'green'))
            elif self.current_color_mode == 'heatmap':
                self.print_heatmap_line(line)
            elif self.current_color_mode == 'edge':
                print(colored(line, 'blue'))
            else:
                print(line)
        
        if len(lines) > preview_lines:
            print(colored(f"\n... and {len(lines)-preview_lines} more lines", 'blue'))
    
    def print_heatmap_line(self, line):
        length = len(line)
        for i, char in enumerate(line):
            ratio = i / length
            if ratio < 0.3:
                print(colored(char, 'red'), end='')
            elif ratio < 0.6:
                print(colored(char, 'yellow'), end='')
            else:
                print(colored(char, 'green'), end='')
        print()
    
    def display_menu(self):
        self.clear_screen()
        self.display_header()
        self.display_status()
        self.display_controls()
        
        if self.ascii_art and self.preview_mode:
            self.display_preview()
    
    # -------------------- Image Processing --------------------
    def apply_effects(self, img):
        # Temel ayarlar
        if self.contrast != 1.0:
            img = ImageEnhance.Contrast(img).enhance(self.contrast)
        if self.brightness != 1.0:
            img = ImageEnhance.Brightness(img).enhance(self.brightness)
        if self.sharpness != 1.0:
            img = ImageEnhance.Sharpness(img).enhance(self.sharpness)
        
        # Özel efektler
        if self.current_color_mode == 'invert':
            img = ImageOps.invert(img)
        elif self.current_color_mode == 'sepia':
            img = self.apply_sepia(img)
        elif self.current_color_mode == 'edge':
            img = self.detect_edges(img)
        elif self.current_color_mode == 'blur' and self.blur_radius > 0:
            img = img.filter(ImageFilter.GaussianBlur(self.blur_radius))
        
        return img
    
    def apply_sepia(self, img):
        width, height = img.size
        pixels = img.load()
        
        for py in range(height):
            for px in range(width):
                r, g, b = pixels[px, py]
                tr = int(0.393 * r + 0.769 * g + 0.189 * b)
                tg = int(0.349 * r + 0.686 * g + 0.168 * b)
                tb = int(0.272 * r + 0.534 * g + 0.131 * b)
                pixels[px, py] = (min(255, tr), min(255, tg), min(255, tb))
        
        return img
    
    def detect_edges(self, img):
        img_np = np.array(img)
        edges = feature.canny(img_np/255., sigma=self.edge_intensity)
        return Image.fromarray((edges * 255).astype(np.uint8))
    
    def process_gif(self, path):
        self.animation_frames = []
        self.is_animated = True
        
        try:
            gif = Image.open(path)
            for frame in range(0, gif.n_frames):
                gif.seek(frame)
                frame_img = gif.convert('RGB')
                self.animation_frames.append(frame_img)
            
            print(colored(f"Loaded GIF with {len(self.animation_frames)} frames", 'green'))
            return True
        except Exception as e:
            print(colored(f"Error processing GIF: {str(e)}", 'red'))
            return False
    
    # -------------------- Conversion --------------------
    def convert_image(self, img=None):
        if not self.image_path and img is None:
            return
            
        try:
            if img is None:
                if self.image_path.lower().endswith('.gif'):
                    if not self.process_gif(self.image_path):
                        return
                    img = self.animation_frames[0]
                else:
                    img = Image.open(self.image_path)
            
            # Renk moduna göre dönüşüm
            if self.current_color_mode in ['none', 'grayscale', 'edge', 'blur', 'invert']:
                img = img.convert('L')
            elif self.current_color_mode == 'sepia':
                img = img.convert('RGB')
            
            # Efekt uygula
            img = self.apply_effects(img)
            
            # Boyutlandırma
            width, height = img.size
            aspect_ratio = height / width
            new_width = int(self.output_width * self.zoom_level)
            new_height = int(new_width * aspect_ratio * 0.55)
            
            img = img.resize((new_width, new_height))
            
            # ASCII dönüşümü
            if self.current_color_mode == 'colored':
                self.ascii_art = self.convert_to_colored_ascii(img)
            else:
                self.ascii_art = self.convert_to_grayscale_ascii(img)
            
            # Geçmişe ekle
            self.add_to_history()
            
        except Exception as e:
            self.ascii_art = f"Error: {str(e)}"
    
    def convert_to_grayscale_ascii(self, img):
        pixels = np.array(img)
        chars = self.char_sets[self.current_char_set] or self.char_sets['basic']
        char_len = len(chars)
        
        ascii_chars = []
        for row in pixels:
            line = [chars[min(int(pixel * (char_len - 1) / 255), char_len-1)] for pixel in row]
            ascii_chars.append("".join(line))
        
        return "\n".join(ascii_chars)
    
    def convert_to_colored_ascii(self, img):
        img_rgb = img.convert('RGB')
        pixels = np.array(img_rgb)
        chars = self.char_sets[self.current_char_set] or self.char_sets['basic']
        char_len = len(chars)
        
        ascii_chars = []
        for row in pixels:
            line = []
            for pixel in row:
                r, g, b = pixel
                gray = int(0.2989 * r + 0.5870 * g + 0.1140 * b)
                char = chars[min(int(gray * (char_len - 1) / 255), char_len-1)]
                
                if self.palette == "vivid":
                    color = self.rgb_to_ansi(r, g, b)
                    line.append(f"\033[38;2;{r};{g};{b}m{char}\033[0m")
                else:
                    line.append(colored(char, self.get_ansi_color(r, g, b)))
            
            ascii_chars.append("".join(line))
        
        return "\n".join(ascii_chars)
    
    def rgb_to_ansi(self, r, g, b):
        return f"\033[38;2;{r};{g};{b}m"
    
    def get_ansi_color(self, r, g, b):
        gray = (r + g + b) // 3
        if gray < 60:
            return 'grey'
        elif gray < 120:
            return 'blue'
        elif gray < 180:
            return 'green'
        else:
            return 'white'
    
    # -------------------- Interactive Functions --------------------
    def load_image_interactive(self):
        self.clear_screen()
        print(colored("Enter image path or drag & drop file here:", 'cyan'))
        print(colored("(Supports JPG, PNG, GIF, BMP)", 'blue'))
        path = input("> ").strip('"\' ')
        
        if os.path.isfile(path):
            self.image_path = path
            self.convert_image()
            print(colored("Image loaded successfully!", 'green'))
        else:
            print(colored("File not found!", 'red'))
        
        time.sleep(1)
    
    def adjust_setting(self, setting_name, min_val, max_val, step, current_val):
        self.clear_screen()
        print(colored(f"Adjust {setting_name} (Current: {current_val:.1f})", 'cyan'))
        print(colored(f"Use ← → arrows to adjust, ENTER to confirm", 'blue'))
        
        val = current_val
        while True:
            print(colored(f"\n{setting_name}: {val:.1f}", 'yellow'))
            
            key = keyboard.read_key()
            if key == 'right' and val < max_val:
                val += step
            elif key == 'left' and val > min_val:
                val -= step
            elif key == 'enter':
                return val
            elif key == 'esc':
                return current_val
    
    def select_from_menu(self, title, options):
        self.clear_screen()
        print(colored(title, 'cyan'))
        
        for i, (key, value) in enumerate(options.items()):
            print(colored(f"{i+1}. {key}: {value}", 'yellow')))
        
        print(colored("\nSelect an option (number) or ESC to cancel:", 'blue'))
        
        while True:
            try:
                key = keyboard.read_key()
                if key == 'esc':
                    return None
                
                if key.isdigit():
                    idx = int(key) - 1
                    if 0 <= idx < len(options):
                        return list(options.keys())[idx]
            except:
                pass
    
    # -------------------- Advanced Features --------------------
    def play_animation(self):
        if not self.animation_frames:
            return
            
        self.clear_screen()
        print(colored("Playing animation... Press ESC to stop", 'magenta'))
        
        frame_idx = 0
        while not keyboard.is_pressed('esc'):
            self.convert_image(self.animation_frames[frame_idx])
            self.clear_screen()
            print(self.ascii_art)
            time.sleep(self.animation_speed)
            frame_idx = (frame_idx + 1) % len(self.animation_frames)
    
    def add_to_history(self):
        if len(self.history) >= self.max_history:
            self.history.pop(0)
        
        self.history.append({
            'ascii': self.ascii_art,
            'settings': {
                'width': self.output_width,
                'chars': self.current_char_set,
                'color': self.current_color_mode,
                'zoom': self.zoom_level,
                'contrast': self.contrast,
                'brightness': self.brightness
            }
        })
    
    def undo_last(self):
        if len(self.history) > 1:
            self.history.pop()  # Current state
            prev_state = self.history[-1]
            self.ascii_art = prev_state['ascii']
            self.apply_settings(prev_state['settings'])
            print(colored("Undo successful!", 'green'))
        else:
            print(colored("Nothing to undo!", 'yellow'))
        
        time.sleep(0.5)
    
    def apply_settings(self, settings):
        for key, value in settings.items():
            setattr(self, key, value)
    
    def save_to_file(self):
        if not self.ascii_art:
            return
            
        self.clear_screen()
        print(colored("Select save format:", 'cyan'))
        print("1. Text file (.txt)")
        print("2. HTML file (.html)")
        print("3. Image file (.png)")
        print("4. JSON file (.json)")
        print(colored("\nEnter choice (1-4) or ESC to cancel:", 'blue'))
        
        choice = keyboard.read_key()
        if choice == 'esc':
            return
        
        filename = input(colored("\nEnter filename (without extension): ", 'cyan')).strip()
        if not filename:
            print(colored("Save cancelled", 'yellow'))
            return
        
        try:
            if choice == '1':
                with open(f"{filename}.txt", "w", encoding="utf-8") as f:
                    f.write(self.ascii_art)
                print(colored(f"Saved to {filename}.txt", 'green'))
            
            elif choice == '2':
                with open(f"{filename}.html", "w", encoding="utf-8") as f:
                    f.write(f"<html><body style='background:{self.save_config['bg_color']};'>")
                    f.write(f"<pre style='color:white;font-size:{self.save_config['font_size']}px;'>")
                    f.write(self.ascii_art)
                    f.write("</pre></body></html>")
                print(colored(f"Saved to {filename}.html", 'green'))
            
            elif choice == '3':
                self.save_as_image(filename)
            
            elif choice == '4':
                data = {
                    'ascii': self.ascii_art,
                    'settings': {
                        'width': self.output_width,
                        'chars': self.current_char_set,
                        'color': self.current_color_mode,
                        'zoom': self.zoom_level
                    }
                }
                with open(f"{filename}.json", "w") as f:
                    json.dump(data, f)
                print(colored(f"Saved to {filename}.json", 'green'))
            
            time.sleep(1)
        except Exception as e:
            print(colored(f"Error saving file: {str(e)}", 'red'))
            time.sleep(1)
    
    def save_as_image(self, filename):
        try:
            # ASCII sanatını görsele dönüştür
            font_size = 10
            lines = self.ascii_art.split('\n')
            img_height = len(lines) * font_size
            img_width = max(len(line) for line in lines) * font_size // 2
            
            plt.figure(figsize=(img_width/100, img_height/100), dpi=100)
            plt.text(0.5, 0.5, self.ascii_art, 
                    fontfamily='monospace', 
                    fontsize=font_size, 
                    ha='left', 
                    va='top',
                    color='white')
            plt.axis('off')
            plt.gcf().set_facecolor('black')
            plt.savefig(f"{filename}.png", 
                      bbox_inches='tight', 
                      pad_inches=0.1, 
                      facecolor='black',
                      dpi=300)
            plt.close()
            
            print(colored(f"Saved to {filename}.png", 'green'))
        except Exception as e:
            print(colored(f"Error creating image: {str(e)}", 'red'))
    
    def copy_to_clipboard(self):
        try:
            pyperclip.copy(self.ascii_art)
            print(colored("ASCII art copied to clipboard!", 'green'))
            time.sleep(0.5)
        except Exception as e:
            print(colored(f"Error copying to clipboard: {str(e)}", 'red'))
            time.sleep(1)
    
    def show_fullscreen(self):
        self.clear_screen()
        print(colored("FULLSCREEN VIEW - Press ESC to return", 'magenta'))
        print(self.ascii_art)
        
        while not keyboard.is_pressed('esc'):
            time.sleep(0.1)
    
    def show_info(self):
        self.clear_screen()
        print(colored("ULTIMATE ASCII ART CONVERTER PRO", 'magenta', attrs=['bold']))
        print(colored("Version 3.0", 'cyan'))
        print(colored("Created with Python 3.9+", 'blue'))
        print("\nFeatures:")
        print("- Supports multiple image formats (JPG, PNG, GIF, BMP)")
        print("- 8 different color modes")
        print("- 5 character sets + custom")
        print("- Real-time adjustments (contrast, brightness, sharpness)")
        print("- Special effects (blur, edge detection, sepia)")
        print("- Animation support for GIFs")
        print("- Multiple save formats (TXT, HTML, PNG, JSON)")
        print("- Full undo/redo history")
        print("\nPress any key to return...")
        keyboard.read_key()
    
    # -------------------- Config Management --------------------
    def load_config(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    self.char_sets['custom'] = config.get('custom_chars', "")
                    self.output_width = config.get('width', 100)
                    self.current_color_mode = config.get('color_mode', 'none')
                    print(colored("Configuration loaded", 'green'))
            except:
                print(colored("Error loading config, using defaults", 'red'))
    
    def save_config(self):
        config = {
            'width': self.output_width,
            'color_mode': self.current_color_mode,
            'custom_chars': self.char_sets['custom']
        }
        
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f)
            print(colored("Configuration saved", 'green'))
        except:
            print(colored("Error saving config", 'red'))
    
    # -------------------- Main Loop --------------------
    def run(self):
        self.clear_screen()
        print(colored("Starting Ultimate ASCII Art Converter Pro...", 'green'))
        time.sleep(1)
        
        while True:
            self.display_menu()
            
            try:
                if keyboard.is_pressed('o'):  # Open image
                    self.load_image_interactive()
                elif keyboard.is_pressed('w'):  # Width
                    self.output_width = int(self.adjust_setting("Width", 20, 300, 10, self.output_width))
                    self.convert_image()
                elif keyboard.is_pressed('c'):  # Color mode
                    mode = self.select_from_menu("Select Color Mode", self.color_modes)
                    if mode:
                        self.current_color_mode = mode
                        self.convert_image()
                elif keyboard.is_pressed('k'):  # Character set
                    set_name = self.select_from_menu("Select Character Set", self.char_sets)
                    if set_name:
                        self.current_char_set = set_name
                        self.convert_image()
                elif keyboard.is_pressed('z'):  # Zoom
                    self.zoom_level = self.adjust_setting("Zoom", 0.5, 3.0, 0.1, self.zoom_level)
                    self.convert_image()
                elif keyboard.is_pressed('b'):  # Brightness
                    self.brightness = self.adjust_setting("Brightness", 0.1, 3.0, 0.1, self.brightness)
                    self.convert_image()
                elif keyboard.is_pressed('t'):  # Contrast
                    self.contrast = self.adjust_setting("Contrast", 0.1, 3.0, 0.1, self.contrast)
                    self.convert_image()
                elif keyboard.is_pressed('s'):  # Save
                    self.save_to_file()
                elif keyboard.is_pressed('v'):  # View fullscreen
                    self.show_fullscreen()
                elif keyboard.is_pressed('p'):  # Palette
                    self.palette = self.select_from_menu("Select Palette", {
                        'default': "Basic colors",
                        'vivid': "True RGB colors",
                        'grayscale': "Grayscale",
                        'retro': "Retro terminal"
                    }) or self.palette
                    self.convert_image()
                elif keyboard.is_pressed('a') and self.is_animated:  # Animation
                    self.play_animation()
                elif keyboard.is_pressed('e'):  # Edge detection
                    self.edge_intensity = self.adjust_setting("Edge Intensity", 0.1, 3.0, 0.1, self.edge_intensity)
                    self.convert_image()
                elif keyboard.is_pressed('l'):  # Blur
                    self.blur_radius = self.adjust_setting("Blur Radius", 0, 5, 1, self.blur_radius)
                    self.convert_image()
                elif keyboard.is_pressed('h'):  # History
                    self.browse_history()
                elif keyboard.is_pressed('u'):  # Undo
                    self.undo_last()
                elif keyboard.is_pressed('d'):  # Duplicate
                    self.duplicate_settings()
                elif keyboard.is_pressed('i'):  # Info
                    self.show_info()
                elif keyboard.is_pressed('r'):  # Refresh
                    self.convert_image()
                elif keyboard.is_pressed('space') and self.ascii_art:  # Toggle preview
                    self.preview_mode = not self.preview_mode
                elif keyboard.is_pressed('q'):  # Quit
                    self.save_config()
                    self.clear_screen()
                    print(colored("Thank you for using Ultimate ASCII Art Converter Pro!", 'magenta'))
                    print(colored("Goodbye! 👋", 'cyan'))
                    sys.exit(0)
                
            except Exception as e:
                print(colored(f"Error: {str(e)}", 'red'))
                time.sleep(1)

if __name__ == "__main__":
    converter = UltimateASCIIArtConverter()
    
    # Komut satırı argümanları
    parser = argparse.ArgumentParser(description='Ultimate ASCII Art Converter Pro')
    parser.add_argument('-i', '--image', help='Path to image file')
    parser.add_argument('-w', '--width', type=int, help='Output width')
    args = parser.parse_args()
    
    if args.image:
        converter.image_path = args.image
        if args.width:
            converter.output_width = args.width
        converter.convert_image()
    
    converter.run()
