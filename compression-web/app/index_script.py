import os
import cv2
import numpy as np
import matplotlib.pyplot as plt

# JPEG compression detection functions

def detect_jpeg_blockiness(image):
    """Detect blockiness characteristic of JPEG compression (8x8 pixel blocks).

    Return eight blockiness ratios, one for each boundary in an 8x8 block:
    - blockiness_ratios[0]: boundary between pixels 0-1
    - blockiness_ratios[1]: boundary between pixels 1-2
    - ...
    - blockiness_ratios[7]: boundary between pixels 7-8 (main block boundary)
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) > 2 else image
    
    # Compute adjacent pixel differences once
    h_diff = np.abs(np.diff(gray, axis=1))  # right neighbour
    v_diff = np.abs(np.diff(gray, axis=0))  # bottom neighbour
    
    blockiness_ratios = np.zeros(8, dtype=np.float32)
    
    # For each position in an 8x8 block (0-7)
    for offset in range(8):
        # Examine boundary differences at the current offset
        h_block_diff = h_diff[:, offset::8]  # every 8 pixels horizontally, starting at offset
        v_block_diff = v_diff[offset::8, :]  # every 8 pixels vertically, starting at offset
        
        # Use masks to avoid expensive np.delete calls
        h_mask = np.ones(h_diff.shape[1], dtype=bool)
        h_mask[offset::8] = False
        v_mask = np.ones(v_diff.shape[0], dtype=bool)
        v_mask[offset::8] = False
        
        # Mean differences at block boundaries and at other positions
        block_diff_mean = (h_block_diff.mean() + v_block_diff.mean()) * 0.5
        non_block_diff_mean = (h_diff[:, h_mask].mean() + v_diff[v_mask, :].mean()) * 0.5
        
        # Blockiness ratio for the current boundary
        blockiness_ratios[offset] = block_diff_mean / non_block_diff_mean if non_block_diff_mean > 0 else 0.0
    
    return blockiness_ratios


def estimate_jpeg_quality(image):
    """Estimate JPEG quality by comparing the image with recompressed versions.

    This function attempts to estimate the original image's JPEG quality by:
    1. Recompressing the image at the candidate quality levels listed below.
    2. Comparing each result with the original using mean squared error (MSE).
    3. Selecting the quality level that produces the most similar image.

    This method may be unreliable because it:
    - Does not account for the original JPEG compression parameters.
    - Does not distinguish uncompressed images from high-quality JPEG images.
    - May produce incorrect results for images compressed twice.
    """
    # Convert colour images to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) > 2 else image
    gray_float = gray.astype(np.float32)  # Convert once for reuse
    
    qualities = [10, 20, 30, 40, 50, 60, 70, 75, 78, 80, 82, 84, 86, 88, 89, 90, 91, 92, 93, 94, 95]
    best_quality = 100
    best_mse = float('inf')
    best_psnr = 0.0
    
    for quality in qualities:
        # Encode the image into a buffer at the specified JPEG quality
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), quality]
        _, encoded_img = cv2.imencode('.jpg', gray, encode_param)
        
        # Decode the compressed image
        decoded_img = cv2.imdecode(encoded_img, cv2.IMREAD_GRAYSCALE)
        
        # Calculate the mean squared error (MSE)
        # Lower MSE indicates greater similarity between the images
        mse = np.mean((gray_float - decoded_img.astype(np.float32)) ** 2)
        
        # Keep the best result (lowest MSE)
        if mse < best_mse:
            best_mse = mse
            best_quality = quality
            # Calculate the peak signal-to-noise ratio (PSNR)
            # Higher PSNR (in dB) indicates better quality
            best_psnr = 10 * np.log10(65025.0 / mse) if mse > 0 else float('inf')
    
    return best_quality, best_psnr

def analyze_dct_spectrum(image):
    """Analyse the frequency spectrum using DCT (Discrete Cosine Transform) on 8x8 blocks."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) > 2 else image
    
    # Crop the image to dimensions divisible by 8
    h, w = gray.shape
    h_pad = h - (h % 8)
    w_pad = w - (w % 8)
    
    if h_pad == 0 or w_pad == 0:
        return 0.0, 0.0
    
    gray_crop = gray[:h_pad, :w_pad].astype(np.float32)
    
    # Calculate the number of blocks
    num_blocks_h = h_pad // 8
    num_blocks_w = w_pad // 8
    num_blocks = num_blocks_h * num_blocks_w
    
    # Preallocate the energy array
    dct_energy = np.zeros(num_blocks, dtype=np.float32)
    
    # Calculate the DCT for each block
    idx = 0
    for i in range(0, h_pad, 8):
        for j in range(0, w_pad, 8):
            block = gray_crop[i:i+8, j:j+8]
            dct = cv2.dct(block)
            # AC component energy (all components except DC at [0,0])
            dct_energy[idx] = np.sum(np.abs(dct)) - np.abs(dct[0, 0])
            idx += 1
    
    # The distribution of block energy may indicate JPEG compression
    return float(dct_energy.mean()), float(dct_energy.std())

# Main JPEG compression detection function
def detect_jpeg_compression(image_path):
    # Load the image
    img = cv2.imread(image_path)
    if img is None:
        return "Nie można wczytać obrazu"
    
    # 1. Blockiness
    blockiness_ratios = detect_jpeg_blockiness(img)
    
    # 2. Frequency spectrum analysis
    energy_mean, energy_std = analyze_dct_spectrum(img)
    
    # 3. Estimate compression quality using recompression
    estimated_quality, psnr = estimate_jpeg_quality(img)
    
    # Blockiness statistics
    blockiness_mean = float(np.mean(blockiness_ratios))
    blockiness_max = float(np.max(blockiness_ratios))
    blockiness_std = float(np.std(blockiness_ratios))
    
    # Build the results dictionary
    result = {
        "energy_mean": energy_mean,
        "energy_std": energy_std,
        "estimated_quality": int(estimated_quality),
        "psnr": float(psnr) if np.isfinite(psnr) else None,
        "blockiness_mean": blockiness_mean,
        "blockiness_max": blockiness_max,
        "blockiness_std": blockiness_std
    }
    
    # Add the blockiness ratios
    for i, val in enumerate(blockiness_ratios):
        result[f"blockiness_{i}"] = float(val)

    return result