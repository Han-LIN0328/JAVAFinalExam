"""
overlay_image.py
─────────────────────────────────────────────────────────────────────────────
將任意圖片以透視變換貼到空地上（純 Pillow + NumPy，不依賴 OpenCV）
 
用法：
    python overlay_image.py                            # 使用預設 NewBalance.png
    python overlay_image.py --overlay 你的圖片.png     # 使用自訂圖片
    python overlay_image.py --preview                  # 在四角畫圈確認位置
 
輸出：overlayimageresult.png
─────────────────────────────────────────────────────────────────────────────
"""
 
import argparse
import numpy as np
from pathlib import Path
from PIL import Image, ImageDraw
 
# ── 空地的四個角落座標（在 background.png 上） ────────────────────────────
# 順序：左上 → 右上 → 右下 → 左下
DST_CORNERS = [
   (495, 493),   # 左上
    (769, 473),   # 右上
   (887, 678),   # 右下
    (556, 707),   # 左下
]
# ─────────────────────────────────────────────────────────────────────────────
 
 
def find_perspective_coeffs(src_pts, dst_pts):
    """
    計算透視變換係數（從 dst → src 的逆映射，供 PIL Image.transform 使用）。
    src_pts / dst_pts：4 個 (x, y) 點，順序一致。
    回傳 8 個係數 (a,b,c,d,e,f,g,h)，使得：
        x_src = (a*xd + b*yd + c) / (g*xd + h*yd + 1)
        y_src = (d*xd + e*yd + f) / (g*xd + h*yd + 1)
    """
    matrix = []
    for (xs, ys), (xd, yd) in zip(src_pts, dst_pts):
        matrix.append([xd, yd, 1, 0,  0,  0, -xs*xd, -xs*yd])
        matrix.append([0,  0,  0, xd, yd, 1, -ys*xd, -ys*yd])
    A = np.array(matrix, dtype=np.float64)
    b = []
    for (xs, ys), _ in zip(src_pts, dst_pts):
        b += [xs, ys]
    b = np.array(b, dtype=np.float64)
 
    coeffs, _, _, _ = np.linalg.lstsq(A, b, rcond=None)
    return tuple(coeffs)
 
 
def overlay_perspective(background_path: str,
                        overlay_path: str,
                        output_path: str = "result.png",
                        preview: bool = False):
 
    bg = Image.open(background_path).convert("RGB")
    overlay = Image.open(overlay_path).convert("RGB")
 
    bg_w, bg_h = bg.size
    ov_w, ov_h = overlay.size
 
    # 覆蓋圖的原始四角（矩形）
    src_corners = [
        (0,    0),
        (ov_w, 0),
        (ov_w, ov_h),
        (0,    ov_h),
    ]
 
    # 計算 dst → src 的逆透視係數
    coeffs = find_perspective_coeffs(src_corners, DST_CORNERS)
 
    # 把覆蓋圖透視扭曲到背景圖大小的畫布上
    warped = overlay.transform(
        (bg_w, bg_h),
        Image.PERSPECTIVE,
        coeffs,
        resample=Image.BICUBIC,
    )
 
    # 建立遮罩（只貼四邊形內部）
    mask = Image.new("L", (bg_w, bg_h), 0)
    draw = ImageDraw.Draw(mask)
    draw.polygon(DST_CORNERS, fill=255)
 
    # 合成
    result = bg.copy()
    result.paste(warped, mask=mask)
 
    # 預覽：在四角畫圓
    if preview:
        d = ImageDraw.Draw(result)
        for (x, y) in DST_CORNERS:
            d.ellipse([x-8, y-8, x+8, y+8], fill=(0, 255, 0))
        print("預覽模式：綠點標示四個角落，請依需求調整 DST_CORNERS")
 
    result.save(output_path)
    print(f"✅ 已儲存：{output_path}")
    print(f"   背景圖尺寸：{bg_w} × {bg_h}")
    print(f"   覆蓋圖：{Path(overlay_path).name}  ({ov_w} × {ov_h})")
    print(f"   四角座標：{DST_CORNERS}")
 
 
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="透視貼圖到空地（純 Pillow）")
    
    # 使用絕對路徑，確保無論從哪執行都能找到檔案
    script_dir = Path(__file__).parent
    default_bg = str(script_dir / "background.png")
    default_overlay = str(script_dir / "NewBalance.png")
    default_output = str(script_dir / "overlayimageresult.png")
    
    parser.add_argument("--background", default=default_bg)
    parser.add_argument("--overlay",    default=default_overlay)
    parser.add_argument("--output",     default=default_output)
    parser.add_argument("--preview",    action="store_true")
    args = parser.parse_args()
    
    print(f"背景圖：{args.background}")
    print(f"覆蓋圖：{args.overlay}")
    
    overlay_perspective(args.background, args.overlay, args.output, args.preview)
