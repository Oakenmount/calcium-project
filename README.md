# Wüstner Lab calcium peak analysis tool

![Screenshot](https://i.imgur.com/4scIbgo.png)

## Installation
The tool requires a few basic Python packages that can be installed with pip or conda.  
From this directory, you can install all the required packages specified in requirements.txt using the command below.  
``pip install -r requirements.txt``

Then you can launch the GUI with ``python gui.pyw``

## Meta-data files
It is advised to create a meta-data file for your videos. This is required if you want to split the video
at specific frames. 
By default, the program will look for ``myvideo.json`` when processing a video file called ``myvido.nd2``
Here's is an example of a config file, where the splits occur at frame 150 and 250.
```json
{
  "Name": "Astrocyte CTRL TG GPN",
  "Specimen": "AstCtrl137",
  "Date": "01-05-2024",
  "Description": "Astrocyte control cell exposed to TG and GPN",
  "Splits": [
    150,
    250
  ]
}
```

## Suggested file structure
You may use whatever structure you like, but the processing script expects the 3 files shown below to be in the same
directory and following these naming patterns.
```
📁experiment_1
├── 📁condition_a
│   ├── 🎞️vid_001.nd2
│   ├── 📄vid_001.json
│   ├── 🖊️vid_001_cp_masks.png
│   ├── 🎞️vid_002.nd2
│   ├── 📄vid_002.json
│   └── 🖊️vid_002_cp_masks.png
└── 📁condition_b
    ├── 🎞️vid_001.nd2
    ├── 📄vid_001.json
    └── 🖊️vid_001_cp_masks.png
```

## Todo:
- Make use of meta-data files
