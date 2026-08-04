# 分析抽帧差异：用亮度/帧差挑差异最大的4帧
import os
import cv2
import numpy as np

frame_dir = r"D:\code\portfolio\ffmpeg-batch-demo\sample_raw\frames"
files = sorted(os.listdir(frame_dir))
frames = []
for f in files:
    img = cv2.imread(os.path.join(frame_dir, f), cv2.IMREAD_GRAYSCALE)
    if img is not None:
        frames.append((f, img))

# 帧差
diffs = []
for i in range(1, len(frames)):
    d = cv2.absdiff(frames[i][1], frames[i-1][1]).mean()
    diffs.append((frames[i][0], d))

diffs.sort(key=lambda x: -x[1])
print("帧差最大的10对:")
for f, d in diffs[:10]:
    print(f"  {f}: {d:.1f}")

# 选差异最大的4帧（间隔尽量拉开）
chosen = []
for f, d in diffs:
    if len(chosen) >= 4:
        break
    # 避免帧号太近
    if all(abs(int(f.split('_')[1].split('.')[0]) - int(c.split('_')[1].split('.')[0])) > 8 for c in chosen):
        chosen.append(f)
print("\n选中的帧:", chosen)
