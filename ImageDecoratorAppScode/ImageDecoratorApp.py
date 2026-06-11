import tkinter as tk
from PIL import Image, ImageTk
from pathlib import Path

class ImageDecoratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("富士山裝飾產生器")
        
        # 1. 讀取背景圖 (轉換為 RGBA 以支援透明度)
        try:
            # 使用絕對路徑，確保無論從哪執行都能找到圖片
            script_dir = Path(__file__).parent
            img_path = script_dir / "futusi.jpg"
            self.bg_original = Image.open(str(img_path)).convert("RGBA")
            print(f"✓ 已載入圖片：{img_path}")
        except FileNotFoundError as e:
            print(f"❌ 找不到圖片！路徑：{img_path}")
            print(f"錯誤：{e}")
            return

        # 1.5 縮放背景圖片以適應螢幕大小
        scale_factor = 0.3  # 縮放到原始尺寸的 30%，適配 24 吋螢幕
        new_w = int(self.bg_original.width * scale_factor)
        new_h = int(self.bg_original.height * scale_factor)
        self.bg_original = self.bg_original.resize((new_w, new_h), Image.Resampling.LANCZOS)

        # 2. 狀態變數記錄
        self.current_angle = 0
        self.current_scale = 1.0

        # 3. 建立 UI 介面
        bg_w, bg_h = self.bg_original.size
        self.canvas = tk.Canvas(root, width=bg_w, height=bg_h)
        self.canvas.pack()

        # 按鈕框架
        control_frame = tk.Frame(root, pady=10)
        control_frame.pack(fill=tk.X)

        # 旋轉按鈕
        tk.Label(control_frame, text="旋轉:").pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="0°", command=lambda: self.set_rotation(0)).pack(side=tk.LEFT, padx=2)
        tk.Button(control_frame, text="30°", command=lambda: self.set_rotation(30)).pack(side=tk.LEFT, padx=2)
        tk.Button(control_frame, text="60°", command=lambda: self.set_rotation(60)).pack(side=tk.LEFT, padx=2)
        tk.Button(control_frame, text="90°", command=lambda: self.set_rotation(90)).pack(side=tk.LEFT, padx=2)

        # 縮放按鈕
        tk.Label(control_frame, text="| 縮放:").pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="0.5x", command=lambda: self.set_scale(0.5)).pack(side=tk.LEFT, padx=2)
        tk.Button(control_frame, text="1x", command=lambda: self.set_scale(1.0)).pack(side=tk.LEFT, padx=2)
        tk.Button(control_frame, text="2x", command=lambda: self.set_scale(2.0)).pack(side=tk.LEFT, padx=2)

        # 匯出按鈕
        tk.Button(control_frame, text="| 匯出圖片", command=self.export_image, bg="lightgreen").pack(side=tk.LEFT, padx=10)

        # 狀態顯示框架
        status_frame = tk.Frame(root, bg="lightgray", pady=5)
        status_frame.pack(fill=tk.X)
        
        self.status_label = tk.Label(status_frame, text="", bg="lightgray", font=("Arial", 10))
        self.status_label.pack(side=tk.LEFT, padx=10)

        # 強制更新 UI 以初始化 Canvas 的實際寬高
        root.update()
        
        # 初始化顯示
        self.update_status()
        self.render_image()

    def set_rotation(self, angle):
        """設定旋轉角度並重新渲染"""
        self.current_angle = angle
        self.update_status()
        self.render_image()

    def set_scale(self, scale):
        """設定縮放倍率"""
        self.current_scale = scale
        self.update_status()
        self.render_image()

    def update_status(self):
        """更新狀態顯示"""
        status_text = f"旋轉: {self.current_angle}° | 縮放: {self.current_scale}x"
        self.status_label.config(text=status_text)

    def render_image(self):
        """核心影像處理邏輯：對背景圖進行縮放和旋轉"""
        
        # 1. 對背景圖進行整體縮放（以中心為基準）
        new_w = int(self.bg_original.width * self.current_scale)
        new_h = int(self.bg_original.height * self.current_scale)
        new_w = max(1, new_w)
        new_h = max(1, new_h)
        bg_scaled = self.bg_original.resize((new_w, new_h), Image.Resampling.BILINEAR)
        
        # 2. 對縮放後的背景圖進行旋轉（以中心為基準）
        bg_rotated = bg_scaled.rotate(-self.current_angle, expand=True, resample=Image.Resampling.BICUBIC)
        
        # 3. 將旋轉後的圖片置中於 Canvas 大小
        canvas_w = self.canvas.winfo_width()
        canvas_h = self.canvas.winfo_height()
        
        # 如果 Canvas 還沒有初始化，使用 Canvas 的配置寬高
        if canvas_w <= 1:
            canvas_w = int(self.canvas.cget("width"))
        if canvas_h <= 1:
            canvas_h = int(self.canvas.cget("height"))
        
        # 建立與 Canvas 同樣大小的白色背景
        result_image = Image.new("RGB", (canvas_w, canvas_h), (255, 255, 255))
        
        # 計算居中位置
        paste_x = (canvas_w - bg_rotated.width) // 2
        paste_y = (canvas_h - bg_rotated.height) // 2
        
        # 將旋轉後的圖片貼到中心
        if bg_rotated.mode == 'RGBA':
            result_image.paste(bg_rotated, (paste_x, paste_y), mask=bg_rotated)
        else:
            result_image.paste(bg_rotated, (paste_x, paste_y))
        
        # 4. 更新 Tkinter Canvas
        self.tk_image = ImageTk.PhotoImage(result_image)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image)

    def export_image(self):
        """匯出目前的背景圖片"""
        # 重新生成結果圖片（與 render_image 相同的邏輯）
        new_w = int(self.bg_original.width * self.current_scale)
        new_h = int(self.bg_original.height * self.current_scale)
        new_w = max(1, new_w)
        new_h = max(1, new_h)
        bg_scaled = self.bg_original.resize((new_w, new_h), Image.Resampling.BILINEAR)
        
        bg_rotated = bg_scaled.rotate(-self.current_angle, expand=True, resample=Image.Resampling.BICUBIC)
        
        # 匯出為檔案（使用絕對路徑）
        script_dir = Path(__file__).parent
        output_path = script_dir / "output_image.png"
        bg_rotated.save(str(output_path))
        print(f"✓ 圖片已匯出：{output_path}")


if __name__ == "__main__":
    root = tk.Tk()
    app = ImageDecoratorApp(root)
    root.mainloop()