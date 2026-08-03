#!/usr/bin/env python3
"""
FFmpeg Batch Processing Demo
============================
批量处理视频文件的实用脚本，演示三种常见任务：
  1. 批量压缩/转码（mp4, H.264, 控制码率/分辨率）
  2. 批量抽帧（按时间间隔提取图片）
  3. 批量提取音频（mp4 -> mp3）

用法：
  python batch_ffmpeg.py compress  input_dir output_dir [--crf 28]
  python batch_ffmpeg.py frames    input_dir output_dir [--fps 1]
  python batch_ffmpeg.py audio     input_dir output_dir

需要 ffmpeg 在 PATH 中，或用 --ffmpeg 指定路径。
"""
import argparse
import os
import subprocess
import sys
from pathlib import Path

SUPPORTED_EXT = {".mp4", ".mov", ".avi", ".mkv", ".webm"}


def find_ffmpeg(explicit: str | None) -> str:
    if explicit and Path(explicit).exists():
        return explicit
    # 尝试 PATH
    import shutil
    found = shutil.which("ffmpeg")
    if found:
        return found
    # 常见默认位置（Windows）
    candidates = [
        r"D:\deepface\fastcut\ffmpeg.exe",
        r"C:\ffmpeg\bin\ffmpeg.exe",
    ]
    for c in candidates:
        if Path(c).exists():
            return c
    sys.exit("未找到 ffmpeg，请用 --ffmpeg 指定路径")


def collect_videos(input_dir: Path) -> list[Path]:
    videos = []
    for ext in SUPPORTED_EXT:
        videos.extend(input_dir.glob(f"*{ext}"))
    return sorted(videos)


def run(cmd: list[str]) -> bool:
    print("  $ " + " ".join(cmd))
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print("    FAIL:", r.stderr[-300:])
        return False
    return True


def cmd_compress(args) -> None:
    src = Path(args.input_dir)
    dst = Path(args.output_dir)
    dst.mkdir(parents=True, exist_ok=True)
    videos = collect_videos(src)
    print(f"发现 {len(videos)} 个视频文件")
    ok = 0
    for v in videos:
        out = dst / (v.stem + "_compressed.mp4")
        print(f"[{v.name}] 压缩中 ...")
        # H.264 + CRF 质量控制 + 音频 AAC，兼容性最好
        if run([args.ffmpeg, "-y", "-i", str(v), "-c:v", "libx264",
                "-crf", str(args.crf), "-preset", "medium",
                "-c:a", "aac", "-b:a", "128k", str(out)]):
            ok += 1
    print(f"完成: {ok}/{len(videos)} 个文件已压缩到 {dst}")


def cmd_frames(args) -> None:
    src = Path(args.input_dir)
    dst = Path(args.output_dir)
    dst.mkdir(parents=True, exist_ok=True)
    videos = collect_videos(src)
    print(f"发现 {len(videos)} 个视频文件")
    ok = 0
    for v in videos:
        out_dir = dst / v.stem
        out_dir.mkdir(parents=True, exist_ok=True)
        print(f"[{v.name}] 抽帧中 (每{args.fps}秒/帧) ...")
        # fps=1 -> 每秒1帧；输出 frame_00001.jpg 序列
        if run([args.ffmpeg, "-y", "-i", str(v), "-vf",
                f"fps={args.fps}", str(out_dir / "frame_%05d.jpg")]):
            n = len(list(out_dir.glob("*.jpg")))
            print(f"    抽到 {n} 帧")
            ok += 1
    print(f"完成: {ok}/{len(videos)} 个视频已抽帧到 {dst}")


def cmd_audio(args) -> None:
    src = Path(args.input_dir)
    dst = Path(args.output_dir)
    dst.mkdir(parents=True, exist_ok=True)
    videos = collect_videos(src)
    print(f"发现 {len(videos)} 个视频文件")
    ok = 0
    for v in videos:
        out = dst / (v.stem + ".mp3")
        print(f"[{v.name}] 提取音频 ...")
        if run([args.ffmpeg, "-y", "-i", str(v), "-vn", "-c:a", "libmp3lame",
                "-b:a", "192k", str(out)]):
            ok += 1
    print(f"完成: {ok}/{len(videos)} 个音频已提取到 {dst}")


def main():
    parser = argparse.ArgumentParser(description="FFmpeg 批处理工具")
    sub = parser.add_subparsers(dest="task", required=True)

    for task, fn, help_txt in [
        ("compress", cmd_compress, "批量压缩/转码"),
        ("frames", cmd_frames, "批量抽帧"),
        ("audio", cmd_audio, "批量提取音频"),
    ]:
        p = sub.add_parser(task, help=help_txt)
        p.add_argument("input_dir")
        p.add_argument("output_dir")
        p.add_argument("--ffmpeg", default=None, help="ffmpeg 可执行文件路径")
        if task == "compress":
            p.add_argument("--crf", type=int, default=28, help="CRF 质量 (18=高质, 28=默认, 35=小体积)")
        if task == "frames":
            p.add_argument("--fps", type=float, default=1.0, help="抽帧频率 (帧/秒)")

    args = parser.parse_args()
    args.ffmpeg = find_ffmpeg(getattr(args, "ffmpeg", None))
    print("ffmpeg:", args.ffmpeg)
    {"compress": cmd_compress, "frames": cmd_frames, "audio": cmd_audio}[args.task](args)


if __name__ == "__main__":
    main()
