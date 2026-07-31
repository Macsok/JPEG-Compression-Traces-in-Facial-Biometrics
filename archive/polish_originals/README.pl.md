# Detekcja kompresji JPEG

Projekt badawczy dotyczący wykrywania i analizy kompresji JPEG w obrazach, wykorzystujący metody analizy blokowości, spektrum DCT oraz modele uczenia maszynowego.

## Struktura projektu

### Skrypty Python

- **`index_script.py`** - Główny moduł z funkcjami do wykrywania kompresji JPEG: detekcja blokowości (bloki 8x8), estymacja jakości kompresji, analiza spektrum DCT
- **`batch_script.py`** - Skrypt do przetwarzania wsadowego obrazów z katalogów, zapis wyników do CSV
- **`web-cam.py`** - Narzędzie testowe do symulacji wstrzykiwania obrazów jako źródło kamery

### Notebooki Jupyter

- **`ML-compression-detection.ipynb`** - Budowa modeli ML do detekcji kompresji
- **`ML-compression-detection-load-model.ipynb`** - Wczytywanie i ewaluacja wytrenowanych modeli
- **`ML-evaluation-and-tests.ipynb`** - Ewaluacja i testy modeli uczenia maszynowego
- **`ML-compression-tests.ipynb`** - Testy różnych metod detekcji kompresji
- **`ML.ipynb`** - Eksperymenty z modelami ML
- **`multiple-compression.ipynb`** - Analiza wielokrotnej kompresji obrazów
- **`multiple-compression-visualise.ipynb`** - Wizualizacja efektów wielokrotnej kompresji
- **`jpeg-testing-quantization-table.ipynb`** - Testowanie tablic kwantyzacji JPEG
- **`testing-notebook.ipynb`** - Ogólne testy funkcjonalności
- **`testing-notebook-single-blockiness.ipynb`** - Ogólne testy funkcjonalności (pojedyncza blokowość)
- **`TEST-quality-and-jfif-or-ppm.ipynb`** - Testy jednostkowe z wykorzystaniem wytrenowanych modeli
- **`web-cam.ipynb`** - Notebook do eksperymentów z kamerą

## Uwaga

Zbiory danych obrazów nie są dołączone do repozytorium ze względów licencyjnych. Zapisane wyniki (pliki CSV) i wyznaczone wagi do modeli nie zostały załączone ze względu na ograniczenie wielkości przesyłanych plików.