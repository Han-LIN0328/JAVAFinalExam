# 影像處理期末專案：Tkinter 互動介面與 NumPy 幾何投影變換
**(Image Processing Core Technologies: Tkinter GUI & NumPy Perspective Transform)**

本專案探討並實作了兩種基於 Python 的核心影像處理技術。透過物件導向設計 (OOP) 與單應性矩陣 (Homography Matrix) 的線性代數運算，展示了如何在不依賴龐大外部電腦視覺引擎（如 OpenCV）的情況下，達成具備商業等級水準的影像渲染與增強實境 (AR) 貼圖效果。

## 🌟 核心模組與特色 (Features)

### 1. 圖像旋轉縮放工具 (`ImageDecoratorApp.py`)
基於 Tkinter 與 PIL (Pillow) 開發的動態影像裝飾框架（以富士山圖片為例）。
* **狀態機驅動**：利用 `current_angle` 與 `current_scale` 變數建立輕量級狀態機，即時響應滑桿操作並觸發畫布重繪。
* **高品質重採樣**：縮放時採用 `LANCZOS` 演算法，旋轉時採用 `BICUBIC` 演算法，大幅減少邊緣鋸齒並保留圖像細節。
* **絕對置中與邊界演算**：精準計算影像旋轉後 Bounding Box 改變帶來的位置偏移，並轉為 RGBA 模式確保擴充邊界保持透明。

### 2. 圖層疊加與透視投影工具 (`overlay_image.py`)
運用 NumPy 與線性代數實現的精確空間投影工具，將 2D 商標完美貼合於傾斜的建築空地。
* **單應性矩陣 (Homography Matrix)**：拋棄簡易的仿射變換，採用真正的 3D 至 2D 平面投影技術。
* **逆向映射 (Inverse Mapping)**：藉由目標座標反推來源座標，避免離散座標取整導致的空洞與點位缺失。
* **SVD 最小平方求解**：將非線性透視方程轉為線性方程組 $A\mathbf{h} = \mathbf{b}$，並呼叫 `np.linalg.lstsq` 高效計算出 8 個未知的透視變換係數。
* **精確遮罩融合**：利用 8-bit 灰階遮罩 (L 模式) 與多邊形填色 (`ImageDraw.polygon`)，解決透視貼圖常見的不規則黑邊痛點。

## 🛠️ 技術架構 (Tech Stack)

* **程式語言**: Python 3.x
* **圖形介面**: Tkinter (內建)
* **影像處理**: Pillow (PIL)
* **科學計算**: NumPy

## 📂 專案結構 (Project Structure)

```text
├── ImageDecoratorApp.py    # 模組一：Tkinter 動態圖像旋轉縮放工具
├── overlay_image.py        # 模組二：NumPy 矩陣透視投影與遮罩合成工具
├── futusi.jpg              # 模組一測試素材 (富士山)
├── background.jpg          # 模組二測試素材 (目標背景建築空地)
└── NewBalance.png          # 模組二測試素材 (欲覆蓋之商標 LOGO)
