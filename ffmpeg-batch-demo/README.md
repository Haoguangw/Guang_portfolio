# FFmpeg Batch Processing Demo

A Python wrapper for batch-processing video files with FFmpeg. Three practical tasks:

1. **Compress / transcode** — batch compress videos to H.264 MP4 with CRF quality control
2. **Extract frames** — batch extract frames (thumbnails / stills) at a given rate
3. **Extract audio** — batch rip audio from videos to MP3

## Requirements

- Python 3.9+
- FFmpeg (auto-detected in PATH; or pass `--ffmpeg`)

## Usage

```bash
# 1. Batch compress (CRF 28 = good quality / small size balance)
python batch_ffmpeg.py compress ./input ./output --crf 28

# 2. Extract 1 frame per second
python batch_ffmpeg.py frames ./input ./output --fps 1

# 3. Extract audio to MP3
python batch_ffmpeg.py audio ./input ./output

# If ffmpeg is not in PATH:
python batch_ffmpeg.py compress ./in ./out --ffmpeg C:/path/to/ffmpeg.exe
```

Supported input: mp4 / mov / avi / mkv / webm

## Demo run (self-test)

```bash
# 生成两个测试视频（2 秒、1280x720、带音轨）
ffmpeg -y -f lavfi -i testsrc=duration=2:size=1280x720:rate=30 -f lavfi -i sine=frequency=440:duration=2 -c:v libx264 -c:a aac demo_a.mp4
ffmpeg -y -f lavfi -i testsrc2=duration=2:size=1280x720:rate=30 -f lavfi -i sine=frequency=660:duration=2 -c:v libx264 -c:a aac demo_b.mp4

python batch_ffmpeg.py compress ./sample ./output/compress
python batch_ffmpeg.py frames   ./sample ./output/frames --fps 1
python batch_ffmpeg.py audio    ./sample ./output/audio
```
