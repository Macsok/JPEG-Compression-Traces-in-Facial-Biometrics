'use strict';
const messages = {
  en: {
    heroAction: 'Inspect your images', originalResolution: 'Original resolution', batchAnalysis: 'Batch analysis',
    figureStill: 'Still',
    figureNumber: 'FIG. 01', figureTitle: 'The pixel inspection bench', figureHint: 'Explore a column', column: 'Column', figurePause: 'Pause', figurePlay: 'Play',
    figureCaption: 'An illustrative 8 × 8 pixel block. JPEG works with blocks of this size; your analysis uses the full image.',
    workspaceLabel: 'YOUR WORKSPACE', workspaceTitle: 'From image to evidence.',
    stepSelect: 'Select images', stepSelectHint: 'A file, a batch, or a folder',
    stepAnalyse: 'Read the traces', stepAnalyseHint: 'Classification & quality estimate',
    stepExport: 'Explore & export', stepExportHint: 'Every result, in one report',
    fieldNotes: 'FIELD NOTES', formatNote: 'A signature in the pixels', qualityNote: 'An estimate, with context',
    pageTitle: 'Compression Inspector — image analysis', language: 'Language',
    theme: 'Theme', themeLight: 'Light', themeDark: 'Dark',
    languageEnglish: 'English', languagePolish: 'Polish',
    eyebrow: 'IMAGE COMPRESSION ANALYSIS', headline: 'What lies within the pixels?',
    intro: 'Look for traces of JPEG compression. Select images or a whole folder to predict PPM / JFIF and JPEG quality.',
    connecting: 'Connecting to the models…', ready: '● Models ready', offline: 'Connection unavailable — refresh the page',
    uploadTitle: 'Add images to analyse', uploadSelected: 'Images selected — ready to analyse', uploadEmpty: 'No supported images found',
    uploadDescription: 'Drag files here or choose them from your device.', uploadNext: 'Click “Start analysis” below to upload your images and see the results.',
    chooseImages: 'Choose images', chooseFolder: 'Choose folder', folderHint: 'Folders include subfolders. Images are analysed at their original resolution.',
    limits: ' · up to {mb} MB / image · up to {mp} MP', chosen: 'Selected images: {count}.', more: ' · and {count} more', skipped: 'Other files skipped: {count}.',
    unsupportedSelection: 'Skipped files: {count}. Choose images in one of the formats listed below.', noSelection: 'No images selected yet.',
    start: 'Start analysis', stop: 'Stop after the current image', stopping: 'Stopping after the current image…', progress: 'Analysis progress',
    finished: 'Completed', stopped: 'Stopped', completion: '{state}: {done} / {total} images. Exports include results collected so far.',
    report: 'REPORT', results: 'Analysis results', csv: 'Download CSV', json: 'Download JSON',
    summary: 'Processed: {total} · JFIF: {jfif} · PPM: {ppm} · Errors: {errors}',
    histogramHeading: 'Distribution of predicted quality', image: 'Image', prediction: 'Prediction', confidence: 'Model confidence', quality: 'JPEG quality', details: 'Details',
    interpreting: 'How to read the results', explanationFormat: 'JFIF indicates features typical of JPEG compression, while PPM indicates features typical of uncompressed images in the training set. This is a prediction from pixels, not a reading of the file format.',
    explanationQuality: 'JPEG quality is a model estimate, not a camera setting or a visual rating. For PPM predictions, quality is indicative only. Confidence applies to the PPM / JFIF classification and does not guarantee accuracy.',
    footer: 'All images are processed locally. This application was generated using AI.',
    ppmNote: 'indicative for PPM', featureDetails: 'Features and probabilities', probabilities: 'Probabilities', indicators: 'Features', width: 'Width', height: 'Height', duration: 'Analysis time (s)',
    histTitle: 'JPEG quality histogram for JFIF and PPM', histDescription: 'X axis: quality 10–95, bins of 5. Y axis: sample count. JFIF: {jfif}, PPM: {ppm}. The bars for both groups overlap.',
    histBin: 'Quality {interval}: JFIF {jfif}, PPM {ppm}', histX: 'Predicted JPEG quality', histY: 'Number of samples', histEmpty: 'No results in the 10–95 range',
    histNote: 'Bins of 5: [10, 15), …, [90, 95]. Groups follow model predictions. Samples shown: {count}.', histOutside: ' Outside the 10–95 range: {count} (not shown).', histHover: ' Hover over the bars to see both group counts.',
    'error.upload_limit': 'The upload exceeds the request size limit.', 'error.busy': 'The server is busy. Please try again later.', 'error.network': 'Unable to connect to the server.',
    'error.http': 'HTTP error {status}.', 'error.required': 'Upload exactly one image in the file field.', 'error.extension': 'Unsupported image extension.',
    'error.format': 'Unsupported image format.', 'error.small': 'The minimum image size is 16 × 16 pixels.', 'error.pixels': 'The image exceeds the limit of {limit} pixels.',
    'error.frames': 'Choose a single-frame / single-page image.', 'error.invalid_image': 'The image could not be read. Choose a valid, supported image.',
    'error.invalid_features': 'Cannot calculate features: {features}. The image may be uniform or too small.', 'error.server': 'Analysis failed. Details are available in the server logs.',
  },
  pl: {
    heroAction: 'Sprawdź swoje obrazy', originalResolution: 'Oryginalna rozdzielczość', batchAnalysis: 'Analiza wielu plików',
    figureStill: 'Bez ruchu',
    figureNumber: 'RYS. 01', figureTitle: 'Stanowisko inspekcji pikseli', figureHint: 'Wybierz kolumnę', column: 'Kolumna', figurePause: 'Pauza', figurePlay: 'Odtwórz',
    figureCaption: 'Przykładowy blok 8 × 8 pikseli. JPEG operuje na blokach tej wielkości; analiza obejmuje cały obraz.',
    workspaceLabel: 'TWOJE STANOWISKO', workspaceTitle: 'Od obrazu do śladów kompresji.',
    stepSelect: 'Wybierz obrazy', stepSelectHint: 'Jeden plik, wiele zdjęć lub folder',
    stepAnalyse: 'Odczytaj ślady', stepAnalyseHint: 'Klasyfikacja i estymacja jakości',
    stepExport: 'Sprawdź i eksportuj', stepExportHint: 'Wszystkie wyniki w jednym raporcie',
    fieldNotes: 'NOTATKI DO ANALIZY', formatNote: 'Ślad zapisany w pikselach', qualityNote: 'Estymacja z kontekstem',
    pageTitle: 'Compression Inspector — analiza obrazów', language: 'Język',
    theme: 'Motyw', themeLight: 'Jasny', themeDark: 'Ciemny',
    languageEnglish: 'Angielski', languagePolish: 'Polski',
    eyebrow: 'ANALIZA KOMPRESJI OBRAZÓW', headline: 'Co kryje się w pikselach?',
    intro: 'Sprawdź ślady kompresji JPEG. Wybierz zdjęcia lub cały folder, aby uzyskać predykcję PPM / JFIF i jakości kompresji.',
    connecting: 'Łączenie z modelami…', ready: '● Modele gotowe', offline: 'Brak połączenia — odśwież stronę',
    uploadTitle: 'Dodaj obrazy do analizy', uploadSelected: 'Obrazy wybrane — gotowe do analizy', uploadEmpty: 'Nie znaleziono obsługiwanych obrazów',
    uploadDescription: 'Przeciągnij tutaj pliki lub wybierz je z dysku.', uploadNext: 'Kliknij „Rozpocznij analizę” poniżej, aby przesłać obrazy i uzyskać wyniki.',
    chooseImages: 'Wybierz zdjęcia', chooseFolder: 'Wybierz folder', folderHint: 'Folder obejmuje również podfoldery. Obrazy są analizowane w oryginalnej rozdzielczości.',
    limits: ' · do {mb} MB / obraz · do {mp} MP', chosen: 'Wybrane obrazy: {count}.', more: ' · i jeszcze {count}', skipped: 'Pominięto innych plików: {count}.',
    unsupportedSelection: 'Pominięto plików: {count}. Wybierz zdjęcia w jednym z formatów wymienionych poniżej.', noSelection: 'Nie wybrano jeszcze obrazów.',
    start: 'Rozpocznij analizę', stop: 'Zatrzymaj po bieżącym obrazie', stopping: 'Zatrzymywanie po bieżącym obrazie…', progress: 'Postęp analizy',
    finished: 'Zakończono', stopped: 'Zatrzymano', completion: '{state}: {done} / {total} obrazów. Eksport zawiera dotychczasowe wyniki.',
    report: 'RAPORT', results: 'Wyniki analizy', csv: 'Pobierz CSV', json: 'Pobierz JSON',
    summary: 'Przeanalizowano: {total} · JFIF: {jfif} · PPM: {ppm} · Błędy: {errors}',
    histogramHeading: 'Rozkład przewidywanej jakości', image: 'Obraz', prediction: 'Predykcja', confidence: 'Pewność modelu', quality: 'Jakość JPEG', details: 'Szczegóły',
    interpreting: 'Jak czytać wynik?', explanationFormat: 'JFIF oznacza cechy typowe dla kompresji JPEG, a PPM — dla obrazów nieskompresowanych ze zbioru treningowego. To predykcja na podstawie pikseli, nie odczyt formatu pliku.',
    explanationQuality: 'Jakość JPEG to estymacja modelu, nie odczyt ustawień aparatu ani ocena wizualna zdjęcia. Dla klasy PPM wynik jakości jest orientacyjny. Pewność dotyczy klasyfikacji PPM / JFIF; nie jest gwarancją poprawności.',
    footer: 'Wszystkie zdjęcia są przetwarzane lokalnie. Aplikacja została wygenerowana przy użyciu AI.',
    ppmNote: 'orientacyjnie dla PPM', featureDetails: 'Cechy i prawdopodobieństwa', probabilities: 'Prawdopodobieństwa', indicators: 'Cechy', width: 'Szerokość', height: 'Wysokość', duration: 'Czas analizy (s)',
    histTitle: 'Histogram jakości JPEG dla klas JFIF i PPM', histDescription: 'Oś X: jakość 10–95, przedziały co 5. Oś Y: liczba próbek. JFIF: {jfif}, PPM: {ppm}. Słupki obu grup nakładają się.',
    histBin: 'Jakość {interval}: JFIF {jfif}, PPM {ppm}', histX: 'Przewidywana jakość JPEG', histY: 'Liczba próbek', histEmpty: 'Brak wyników w zakresie 10–95',
    histNote: 'Przedziały co 5: [10, 15), …, [90, 95]. Grupy według predykcji modelu. Próbek na wykresie: {count}.', histOutside: ' Poza zakresem 10–95: {count} (pominięte na wykresie).', histHover: ' Najedź na słupki, aby zobaczyć liczebność obu grup.',
    'error.upload_limit': 'Plik przekracza limit przesyłania.', 'error.busy': 'Serwer jest zajęty. Spróbuj ponownie później.', 'error.network': 'Brak połączenia z serwerem.',
    'error.http': 'Błąd HTTP {status}.', 'error.required': 'Prześlij jeden obraz w polu file.', 'error.extension': 'Nieobsługiwane rozszerzenie obrazu.',
    'error.format': 'Nieobsługiwany format obrazu.', 'error.small': 'Minimalny rozmiar obrazu to 16 × 16 pikseli.', 'error.pixels': 'Obraz przekracza limit {limit} pikseli.',
    'error.frames': 'Wybierz obraz z jedną klatką / stroną.', 'error.invalid_image': 'Nie można odczytać obrazu. Wybierz poprawny obraz w obsługiwanym formacie.',
    'error.invalid_features': 'Nie można obliczyć cech: {features}. Obraz może być jednolity lub zbyt mały.', 'error.server': 'Błąd analizy. Szczegóły znajdują się w logach serwera.',
  },
};
let language = 'en';
try { if (localStorage.getItem('compression-language') === 'pl') language = 'pl'; } catch (_) { /* Storage can be unavailable in private contexts. */ }
function t(key, values = {}) {
  return (messages[language][key] || messages.en[key] || key).replace(/\{(\w+)\}/g, (_, name) => String(values[name] ?? ''));
}
function locale() { return language === 'pl' ? 'pl-PL' : 'en-US'; }
function number(value, digits = 0) { return value.toLocaleString(locale(), {minimumFractionDigits: digits, maximumFractionDigits: digits}); }
function translatePage() {
  document.documentElement.lang = language;
  document.title = t('pageTitle');
  document.querySelectorAll('[data-i18n]').forEach(el => { el.textContent = t(el.dataset.i18n); });
  document.querySelectorAll('[data-i18n-aria]').forEach(el => { el.setAttribute('aria-label', t(el.dataset.i18nAria)); });
  document.querySelectorAll('[data-i18n-title]').forEach(el => { el.title = t(el.dataset.i18nTitle); });
  document.querySelectorAll('[data-language]').forEach(el => { el.setAttribute('aria-pressed', String(el.dataset.language === language)); });
}
