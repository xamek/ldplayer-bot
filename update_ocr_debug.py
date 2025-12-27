import json
import os

notebook_path = r"d:\Xamek\Workspace\ldplayer-bot\cvtest.ipynb"

# Advanced Batch OCR Debug Cell
debug_source = [
    "import cv2\n",
    "import pytesseract\n",
    "import os\n",
    "import matplotlib.pyplot as plt\n",
    "import numpy as np\n",
    "\n",
    "def show_images(images, titles):\n",
    "    n = len(images)\n",
    "    fig, axes = plt.subplots(1, n, figsize=(20, 5))\n",
    "    if n == 1: axes = [axes]\n",
    "    for ax, img, title in zip(axes, images, titles):\n",
    "        ax.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB) if len(img.shape) == 3 else img, cmap='gray')\n",
    "        ax.set_title(title)\n",
    "        ax.axis('off')\n",
    "    plt.show()\n",
    "\n",
    "def debug_ocr_strategies(img_path, target=\"Loading\"):\n",
    "    img = cv2.imread(img_path)\n",
    "    if img is None: return\n",
    "    \n",
    "    print(f\"\\n--- Debugging: {os.path.basename(img_path)} ---\")\n",
    "    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)\n",
    "    \n",
    "    # Define strategies\n",
    "    strategies = []\n",
    "    \n",
    "    # 1. Standard (Current prod)\n",
    "    _, t127 = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)\n",
    "    strategies.append((t127, \"Fixed 127\"))\n",
    "    \n",
    "    # 2. Otsu\n",
    "    _, otsu = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)\n",
    "    strategies.append((otsu, \"Otsu\"))\n",
    "    \n",
    "    # 3. Adaptive\n",
    "    adapt = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)\n",
    "    strategies.append((adapt, \"Adaptive\"))\n",
    "    \n",
    "    # 4. Inverted Otsu\n",
    "    inv_otsu = cv2.bitwise_not(otsu)\n",
    "    strategies.append((inv_otsu, \"Inv Otsu\"))\n",
    "    \n",
    "    imgs_to_show = [gray]\n",
    "    titles_to_show = [\"Grayscale\"]\n",
    "    \n",
    "    found_any = False\n",
    "    for s_img, label in strategies:\n",
    "        text = pytesseract.image_to_string(s_img, config=\"--psm 11\").strip().replace('\\n', ' ')\n",
    "        found = target.lower() in text.lower()\n",
    "        status = \"✅\" if found else \"❌\"\n",
    "        print(f\"{status} {label:10} | Extracted: '{text[:50]}...'\")\n",
    "        imgs_to_show.append(s_img)\n",
    "        titles_to_show.append(f\"{label} ({status})\")\n",
    "        if found: found_any = True\n",
    "        \n",
    "    show_images(imgs_to_show, titles_to_show)\n",
    "\n",
    "states_dir = \"unknown_states\"\n",
    "files = [f for f in os.listdir(states_dir) if f.endswith('.png')]\n",
    "for f in files:\n",
    "    debug_ocr_strategies(os.path.join(states_dir, f))\n"
]

new_nb = {
    "cells": [
        {
            "cell_type": "code",
            "execution_count": None,
            "id": "multi_strategy_ocr_debug",
            "metadata": {},
            "outputs": [],
            "source": debug_source
        }
    ],
    "metadata": {
        "kernelspec": {
            "display_name": "Python 3 (ipykernel)",
            "language": "python",
            "name": "python3"
        }
    },
    "nbformat": 4,
    "nbformat_minor": 5
}

with open(notebook_path, 'w', encoding='utf-8') as f:
    json.dump(new_nb, f, indent=1)

print("Updated cvtest.ipynb with multi-strategy OCR debug cell.")
