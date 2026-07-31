import os
import csv
import time
from pathlib import Path
from index_script import detect_jpeg_compression


def process_images_in_directory(input_dir, output_csv):
    """
    Przetwarza wszystkie obrazy w katalogu i zapisuje wyniki do CSV na bieżąco.
    
    Args:
        input_dir: Ścieżka do katalogu z obrazami
        output_csv: Ścieżka do pliku CSV z wynikami
    """
    # Wspierane rozszerzenia obrazów
    supported_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.jfif', '.webp', '.ppm'}
    
    # Pobierz wszystkie pliki obrazów z katalogu (tylko te, których nazwa nie zawiera litery 'q' - case-insensitive)
    input_path = Path(input_dir)
    if not input_path.exists():
        print(f"Katalog {input_dir} nie istnieje!")
        return
    
    image_files = [f for f in input_path.iterdir() 
                   if f.is_file()
                   and f.suffix.lower() in supported_extensions
    ]
                #    and 'q' in f.stem.lower()]
    
    if not image_files:
        print(f"Nie znaleziono obrazów zawierających 'q' w nazwie w katalogu {input_dir}")
        return
    
    print(f"Znaleziono {len(image_files)} obrazów do przetworzenia")
    
    # Całkowity czas przetwarzania
    total_start_time = time.time()
    
    # Licznik przetworzonych obrazów
    processed_count = 0
    
    # Otwórz plik CSV do zapisu
    with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
        writer = None
        fieldnames = None
        
        # Przetwarzanie każdego obrazu
        for idx, image_file in enumerate(image_files, 1):
            print(f"Przetwarzanie {idx}/{len(image_files)}: {image_file.name}")
            
            # Pomiar czasu dla pojedynczego obrazu
            start_time = time.time()
            
            try:
                # Wywołanie funkcji analizy
                metrics = detect_jpeg_compression(str(image_file))
                
                # Czas przetwarzania
                processing_time = time.time() - start_time
                
                # Dodaj nazwę pliku i rozszerzenie
                result = {
                    'filename': image_file.stem,  # nazwa bez rozszerzenia
                    'extension': image_file.suffix  # rozszerzenie z kropką
                }
                
                # Dodaj metryki
                if isinstance(metrics, dict):
                    result.update(metrics)
                else:
                    result['error'] = str(metrics)
                
                # Inicjalizuj writer przy pierwszym zapisie
                if writer is None:
                    # Ustaw nazwy kolumn: filename, extension na początku
                    priority_keys = ['filename', 'extension']
                    other_keys = sorted([k for k in result.keys() if k not in priority_keys])
                    fieldnames = priority_keys + other_keys
                    
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
                
                # Zapisz wiersz natychmiast
                writer.writerow(result)
                csvfile.flush()  # Wymuś zapisanie do pliku
                
                processed_count += 1
                print(f"Przetworzono w {processing_time:.4f}s - zapisano do pliku")
                
            except Exception as e:
                print(f"Błąd: {e}")
                
                # Nawet przy błędzie zapisz wiersz
                error_result = {
                    'filename': image_file.stem,
                    'extension': image_file.suffix,
                    'error': str(e)
                }
                
                if writer is None:
                    fieldnames = ['filename', 'extension', 'error']
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
                
                writer.writerow(error_result)
                csvfile.flush()
                processed_count += 1
    
    # Całkowity czas
    total_time = time.time() - total_start_time
    
    # Podsumowanie
    print(f"\n{'='*60}")
    print(f"Przetworzono {processed_count} obrazów")
    print(f"Całkowity czas: {total_time:.2f}s")
    if processed_count > 0:
        print(f"Średni czas na obraz: {total_time/processed_count:.4f}s")
    print(f"Wyniki zapisano do: {output_csv}")
    print(f"{'='*60}")


if __name__ == "__main__":
    # Przykład użycia
    # input_directory = r"D:\Zbiory danych - praca\Inne\RGB-faces-128x128\RGB-faces-128x128"  # Katalog z obrazami
    input_directory = r"D:\\Zbiory danych - praca\\Zbiory_do_artykulu\\HumaFacesDatasetAndAI\\RealImages"
    output_file = "results_humanFacesDatasetReal.csv"  # Plik wyjściowy CSV
    
    process_images_in_directory(input_directory, output_file)
else:
    print("Moduł batch_script został zaimportowany.")

print("Koniec batch_script.py")