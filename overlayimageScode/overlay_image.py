import argparse
import numpy as np
from pathlib import Path
from PIL import Image, ImageDraw

# ──────────────────────────────────────────────────────────────────────────
# 設定：空地的四個角落座標（在 background.png 上）
# 順序：左上 → 右上 → 右下 → 左下
DST_CORNERS = [
    (495, 493),   # 左上
    (769, 473),   # 右上
    (887, 678),   # 右下
    (556, 707),   # 左下
]
# ──────────────────────────────────────────────────────────────────────────
 
 
def find_perspective_coeffs(src_pts, dst_pts):
    """
    計算透視變換係數（從 dst → src 的逆映射）
    參數：src_pts / dst_pts 為 4 個 (x, y) 點，順序一致
    回傳：8 個變換係數 (a,b,c,d,e,f,g,h)
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
 
    # Step 1. 載入背景圖和覆蓋圖
    bg = Image.open(background_path).convert("RGB")
    overlay = Image.open(overlay_path).convert("RGB")
    bg_w, bg_h = bg.size
    ov_w, ov_h = overlay.size

    # Step 2. 定義覆蓋圖的原始四角（矩形）
    src_corners = [
        (0,    0),
        (ov_w, 0),
        (ov_w, ov_h),
        (0,    ov_h),
    ]

    # Step 3. 計算透視變換係數
    coeffs = find_perspective_coeffs(src_corners, DST_CORNERS)

    # Step 4. 對覆蓋圖進行透視扭曲
    warped = overlay.transform(
        (bg_w, bg_h),
        Image.PERSPECTIVE,
        coeffs,
        resample=Image.BICUBIC,
    )

    # Step 5. 建立遮罩（只貼四邊形內部）
    mask = Image.new("L", (bg_w, bg_h), 0)
    draw = ImageDraw.Draw(mask)
    draw.polygon(DST_CORNERS, fill=255)

    # Step 6. 合成背景圖和扭曲後的覆蓋圖
    result = bg.copy()
    result.paste(warped, mask=mask)

    # Step 7. 預覽模式（在四角畫綠圈）
    if preview:
        d = ImageDraw.Draw(result)
        for (x, y) in DST_CORNERS:
            d.ellipse([x-8, y-8, x+8, y+8], fill=(0, 255, 0))
        print("✓ 預覽模式：綠點標示四個角落，請依需求調整 DST_CORNERS")

    # Step 8. 儲存結果
    result.save(output_path)
    print(f"✅ 已儲存：{output_path}")
    print(f"   背景圖尺寸：{bg_w} × {bg_h}")
    print(f"   覆蓋圖：{Path(overlay_path).name}  ({ov_w} × {ov_h})")
    print(f"   四角座標：{DST_CORNERS}")
 
 
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="透視貼圖到空地（純 Pillow + NumPy）")

    # 使用絕對路徑確保檔案查找
    script_dir = Path(__file__).parent
    default_bg = str(script_dir / "background.png")
    default_overlay = str(script_dir / "NewBalance.png")
    default_output = str(script_dir / "overlayimageresult.png")
    
    parser.add_argument("--background", default=default_bg, help="背景圖路徑")
    parser.add_argument("--overlay",    default=default_overlay, help="覆蓋圖路徑")
    parser.add_argument("--output",     default=default_output, help="輸出圖路徑")
    parser.add_argument("--preview",    action="store_true", help="預覽模式")
    args = parser.parse_args()

    print(f"背景圖：{args.background}")
    print(f"覆蓋圖：{args.overlay}")

    overlay_perspective(args.background, args.overlay, args.output, args.preview)
