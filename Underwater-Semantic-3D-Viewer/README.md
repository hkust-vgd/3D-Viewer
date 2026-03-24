# Underwater-Semantic-3D-Viewer

## Description
A 3D viewer designed for underwater scenario. 3D reconstruction based on VGGT and 2D segmentation based on CoralSRT / SAMv3

## Installation

Firstly, create a conda environment: (note sam3 requires python=3.12)
```bash
conda create -n semantic-slam python=3.12
conda deactivate
conda activate semantic-slam
```
Install SAM3 dependencies
```bash
pip install torch==2.7.0 torchvision torchaudio --index-url https://download.pytorch.org/whl/cu126
pip install -e .
```
Install VGGT dependencies
```bash
cd vggt
pip install -r requirements.txt
pip install -r requirements_demo.txt
```

## Usage
To run the viewer, you just need to run a simple command:
```bash
cd vggt
python demo_viser_semantic.py --image_folder /path/to/your/images
```
`--image_folder` should be a folder containing frames from your video. As an example, a single 4090 GPU can support up to 80 frames.

`generate_demo.py` under the root directory is a tool to help you automate frame extraction. To use it, 
1. Put all the videos you need under a folder
2. If you want to clip your videos, you can create a config.csv file with the format `{filename, start, end}`. `start` and `end` should be float and the unit is seconds.
3. Execute `python generate_demo.py /path/to/your/videos --config /path/to/your/config.csv --fps 4`

This will create a `data/demo/` folder, and within there will be demo1, demo2 ... etc.
