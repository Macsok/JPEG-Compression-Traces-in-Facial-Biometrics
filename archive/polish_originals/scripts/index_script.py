import os
import cv2
import numpy as np
import matplotlib.pyplot as plt

# Funkcje do wykrywania kompresji JPEG

def detect_jpeg_blockiness(image):
    """Wykrywa blokowość charakterystyczną dla JPEG (bloki 8x8 pikseli)
    
    Zwraca tablicę 8 współczynników blokowości, po jednym dla każdej granicy w bloku 8x8:
    - blockiness_ratios[0]: granica między pikselami 0-1
    - blockiness_ratios[1]: granica między pikselami 1-2
    - ...
    - blockiness_ratios[7]: granica między pikselami 7-8 (główna granica bloków)
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) > 2 else image
    
    # Obliczanie różnic pomiędzy sąsiednimi pikselami (raz, zamiast wielokrotnie)
    h_diff = np.abs(np.diff(gray, axis=1))  # prawy sąsiad
    v_diff = np.abs(np.diff(gray, axis=0))  # dolny sąsiad
    
    blockiness_ratios = np.zeros(8, dtype=np.float32)
    
    # Dla każdej pozycji w bloku 8x8 (0-7)
    for offset in range(8):
        # Analizujemy wartości różnic na granicach dla danego offsetu
        h_block_diff = h_diff[:, offset::8]  # co 8 pikseli w poziomie, zaczynając od offset
        v_block_diff = v_diff[offset::8, :]  # co 8 pikseli w pionie, zaczynając od offset
        
        # Tworzymy maski zamiast używać kosztownego np.delete
        h_mask = np.ones(h_diff.shape[1], dtype=bool)
        h_mask[offset::8] = False
        v_mask = np.ones(v_diff.shape[0], dtype=bool)
        v_mask[offset::8] = False
        
        # Średnia różnica na granicach bloków vs pozostałe różnice
        block_diff_mean = (h_block_diff.mean() + v_block_diff.mean()) * 0.5
        non_block_diff_mean = (h_diff[:, h_mask].mean() + v_diff[v_mask, :].mean()) * 0.5
        
        # Współczynnik blokowości dla danej granicy
        blockiness_ratios[offset] = block_diff_mean / non_block_diff_mean if non_block_diff_mean > 0 else 0.0
    
    return blockiness_ratios


def estimate_jpeg_quality(image):
    """Szacuje jakość kompresji JPEG poprzez porównanie z rekompresją obrazu
    
    Funkcja ta próbuje określić jakość kompresji JPEG oryginalnego obrazu poprzez:
    1. Rekompresję obrazu z różnymi poziomami jakości (10%, 20%, ..., 100%)
    2. Porównanie każdej rekompresji z oryginałem przy użyciu MSE (Mean Squared Error)
    3. Wybranie poziomu jakości, który daje najbardziej podobny obraz
    
    UWAGA: Ta metoda może być niemiarodajna, ponieważ:
    - Nie uwzględnia pierwotnych parametrów kompresji JPEG
    - Nie różnicuje między obrazami nieskompresowanymi a wysoką jakością JPEG
    - Może dawać błędne wyniki dla obrazów z podwójną kompresją
    """
    # Konwersja do skali szarości jeśli obraz jest kolorowy
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) > 2 else image
    gray_float = gray.astype(np.float32)  # Konwersja raz zamiast wielokrotnie
    
    qualities = [10, 20, 30, 40, 50, 60, 70, 75, 78, 80, 82, 84, 86, 88, 89, 90, 91, 92, 93, 94, 95]
    best_quality = 100
    best_mse = float('inf')
    best_psnr = 0.0
    
    for quality in qualities:
        # Zapisz obraz do bufora z określoną jakością JPEG
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), quality]
        _, encoded_img = cv2.imencode('.jpg', gray, encode_param)
        
        # Odczytaj skompresowany obraz z powrotem
        decoded_img = cv2.imdecode(encoded_img, cv2.IMREAD_GRAYSCALE)
        
        # Oblicz MSE (Mean Squared Error) - średni błąd kwadratowy
        # Im mniejszy MSE, tym bardziej podobne obrazy
        mse = np.mean((gray_float - decoded_img.astype(np.float32)) ** 2)
        
        # Zapisz najlepszy wynik (najniższe MSE)
        if mse < best_mse:
            best_mse = mse
            best_quality = quality
            # Oblicz PSNR (Peak Signal-to-Noise Ratio) - stosunek sygnału do szumu
            # Im wyższy PSNR (w dB), tym lepsza jakość
            best_psnr = 10 * np.log10(65025.0 / mse) if mse > 0 else float('inf')
    
    return best_quality, best_psnr

def analyze_dct_spectrum(image):
    """Analizuje widmo częstotliwości poprzez DCT (Discrete Cosine Transform) na blokach 8x8"""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) > 2 else image
    
    # Przekształcamy obraz do wymiaru podzielnego przez 8
    h, w = gray.shape
    h_pad = h - (h % 8)
    w_pad = w - (w % 8)
    
    if h_pad == 0 or w_pad == 0:
        return 0.0, 0.0
    
    gray_crop = gray[:h_pad, :w_pad].astype(np.float32)
    
    # Obliczamy liczbę bloków
    num_blocks_h = h_pad // 8
    num_blocks_w = w_pad // 8
    num_blocks = num_blocks_h * num_blocks_w
    
    # Prealokacja tablicy na energie
    dct_energy = np.zeros(num_blocks, dtype=np.float32)
    
    # Obliczamy DCT dla każdego bloku (optymalizacja poprzez reshape)
    idx = 0
    for i in range(0, h_pad, 8):
        for j in range(0, w_pad, 8):
            block = gray_crop[i:i+8, j:j+8]
            dct = cv2.dct(block)
            # Energia składowych AC (wszystkie oprócz DC, czyli [0,0])
            dct_energy[idx] = np.sum(np.abs(dct)) - np.abs(dct[0, 0])
            idx += 1
    
    # Rozkład energii w blokach może wskazywać na kompresję JPEG
    return float(dct_energy.mean()), float(dct_energy.std())

# Główna funkcja do wykrywania kompresji JPEG
def detect_jpeg_compression(image_path):
    # Wczytaj obraz
    img = cv2.imread(image_path)
    if img is None:
        return "Nie można wczytać obrazu"
    
    # 1. Blokowość
    blockiness_ratios = detect_jpeg_blockiness(img)
    
    # 2. Analiza widma częstotliwości
    energy_mean, energy_std = analyze_dct_spectrum(img)
    
    # 3. Oszacowanie jakości kompresji (używamy połączonej metody)
    estimated_quality, psnr = estimate_jpeg_quality(img)
    
    # Statystyki blokowości
    blockiness_mean = float(np.mean(blockiness_ratios))
    blockiness_max = float(np.max(blockiness_ratios))
    blockiness_std = float(np.std(blockiness_ratios))
    
    # Budowanie słownika wyników
    result = {
        "energy_mean": energy_mean,
        "energy_std": energy_std,
        "estimated_quality": int(estimated_quality),
        "psnr": float(psnr) if np.isfinite(psnr) else None,
        "blockiness_mean": blockiness_mean,
        "blockiness_max": blockiness_max,
        "blockiness_std": blockiness_std
    }
    
    # Dodanie współczynników blokowości
    for i, val in enumerate(blockiness_ratios):
        result[f"blockiness_{i}"] = float(val)

    return result