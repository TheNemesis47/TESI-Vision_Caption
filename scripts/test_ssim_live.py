import cv2
import numpy as np
from skimage.metrics import structural_similarity as ssim
import time

def main():
    # Soglia iniziale letta dalla tua configurazione
    threshold = 0.58
    
    print("Inizializzazione webcam...")
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("Errore: Impossibile accedere alla webcam.")
        return
        
    old_img = None
    
    cv2.namedWindow("Test SSIM Live")
    # Creiamo uno slider per modificare la soglia in tempo reale (0-100)
    cv2.createTrackbar("Threshold", "Test SSIM Live", int(threshold * 100), 100, lambda x: None)
    
    print("Premi 'q' sulla finestra del video per uscire.")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        # Leggiamo il valore corrente dello slider
        current_threshold = cv2.getTrackbarPos("Threshold", "Test SSIM Live") / 100.0
        
        # Simuliamo il comportamento del frontend: ridimensioniamo e passiamo in scala di grigi
        frame_resized = cv2.resize(frame, (640, 480))
        gray_img = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2GRAY)
        
        score = 1.0
        is_change = False
        
        if old_img is None:
            old_img = gray_img
            is_change = True
        else:
            t0 = time.perf_counter()
            score = ssim(old_img, gray_img)
            t1 = time.perf_counter()
            
            # Se lo score scende SOTTO la soglia, è un cambio scena!
            if score < current_threshold:
                is_change = True
                # Aggiorniamo l'immagine di riferimento solo quando c'è un vero cambio
                old_img = gray_img
                
        # Grafica a schermo
        color = (0, 0, 255) if is_change else (0, 255, 0)
        text = f"SSIM Score: {score:.3f} | Soglia: {current_threshold:.2f}"
        
        cv2.putText(frame_resized, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        
        if is_change:
            cv2.putText(frame_resized, "CAMBIO SCENA RILEVATO!", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            
        cv2.imshow("Test SSIM Live", frame_resized)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
