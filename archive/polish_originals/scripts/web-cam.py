# Test: Wstrzyknięcie obrazu jako źródło kamery
import cv2
import numpy as np

FILE_EXTENSION = '.png'  # Możliwe opcje: '.png', '.jpg', '.jpeg', '.bmp'
print("=== TEST WSTRZYKIWANIA OBRAZU JAKO ŹRÓDŁO KAMERY ===\n")

# Krok 1: Wczytaj obraz, który chcemy wstrzyknąć
source_image_path = 'jfif/person_0000.jfif'
injected_image = cv2.imread(source_image_path)

if injected_image is None:
    print(f"Nie można wczytać obrazu z {source_image_path}")
else:
    print(f"Wczytano obraz do wstrzyknięcia: {source_image_path}")
    print(f"Shape: {injected_image.shape}, dtype: {injected_image.dtype}")
    
    # Krok 2: Uruchom kamerę
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("\nKamera niedostępna - używam symulacji")
        # Symulacja: bezpośrednie zapisanie
        simulated_capture = injected_image.copy()
        capture_filename = f'camera_injected_capture{FILE_EXTENSION}'
        cv2.imwrite(capture_filename, simulated_capture)
        print(f"Zapisano symulowane przechwycenie: {capture_filename}")
        
    else:
        print("\n✓ Kamera dostępna")
        
        # Krok 3: Pobierz rzeczywisty rozmiar klatki z kamery
        ret, test_frame = cap.read()
        if ret:
            camera_shape = test_frame.shape
            print(f"Rozmiar klatki kamery: {camera_shape}")
            
            # Krok 4: Przeskaluj obraz wstrzykiwany do rozmiaru kamery
            injected_resized = cv2.resize(injected_image, 
                                         (camera_shape[1], camera_shape[0]))
            print(f"Przeskalowano obraz do: {injected_resized.shape}")
            
            # Krok 5: Wyświetl obraz wstrzyknięty na ekranie
            # (w praktyce, kamera by go "zobaczyła")
            cv2.imshow('Obraz wstrzykniety - skieruj kamere tutaj', injected_resized)
            print("\nObraz wyświetlony. W normalnej sytuacji:")
            print("1. Skieruj kamerę na ekran z obrazem")
            print("2. Naciśnij 'c' aby przechwycić")
            print("3. Naciśnij 'q' aby zakończyć bez przechwytywania")
            
            captured = False
            captured_frame = None
            
            # Krok 6: Pętla kamery - czekaj na przechwycenie
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Pokaż podgląd kamery
                cv2.imshow('Podglad kamery - nacisnij C aby przechwycic', frame)
                
                key = cv2.waitKey(1) & 0xFF
                if key == ord('c'):
                    # Przechwyt klatki
                    captured_frame = frame.copy()
                    captured = True
                    print("\n✓ Przechwycono klatkę!")
                    break
                elif key == ord('q'):
                    print("\nAnulowano bez przechwytywania")
                    break
            
            # Zamknij okna i kamerę
            cv2.destroyAllWindows()
            cap.release()
            
            # Krok 7: Zapisz przechwycony obraz
            if captured and captured_frame is not None:
                capture_filename = f'camera_injected_capture{FILE_EXTENSION}'
                cv2.imwrite(capture_filename, captured_frame)
                print(f"Zapisano przechwycony obraz: {capture_filename}")
                
                # Krok 8: Porównaj obraz oryginalny z przechwyconym
                print("\n=== PORÓWNANIE ===")
                print(f"Oryginalny obraz: {injected_image.shape}")
                print(f"Przeskalowany: {injected_resized.shape}")
                print(f"Przechwycony z kamery: {captured_frame.shape}")
                
                # Porównaj przeskalowany z przechwyconym
                if injected_resized.shape == captured_frame.shape:
                    are_identical = np.array_equal(injected_resized, captured_frame)
                    print(f"\nObraz przeskalowany vs przechwycony: {are_identical}")
                    
                    if not are_identical:
                        diff = cv2.absdiff(injected_resized, captured_frame)
                        print(f"Suma różnic: {np.sum(diff)}")
                        print(f"Max różnica: {np.max(diff)}")
                        print(f"Średnia różnica: {np.mean(diff):.2f}")
                else:
                    print("\nRozmiary się różnią - nie można porównać piksel po pikselu")
                
            else:
                print("\nBrak przechwyconego obrazu - używam alternatywnej metody")
                # Alternatywa: bezpośrednie "wstrzyknięcie" poprzez przepisanie
                # Symulujemy że obraz przeszedł przez kamerę
                capture_filename = f'camera_injected_capture{FILE_EXTENSION}'
                cv2.imwrite(capture_filename, injected_resized)
                print(f"Zapisano: {capture_filename}")
        else:
            print("Nie można odczytać z kamery")
            cap.release()

print("\n" + "="*60)
print("WNIOSEK:")
print("Jeśli obraz został przechwycony z ekranu przez kamerę,")
print("przeszedł przez rzeczywiste mechanizmy kamery:")
print("  - Optyka i obiektyw")
print("  - Sensor kamery") 
print("  - Przetwarzanie sygnału")
print("  - Kompresja kamery (jeśli jest)")
print("="*60)