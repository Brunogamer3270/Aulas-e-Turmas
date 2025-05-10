# ✅ Importar as bibliotecas necessárias
import cv2
import mediapipe as mp
import time
import winsound
import tkinter as tk
import random # Para posições e mensagens aleatórias!

# 🔴 Definimos os tempos
TEMPO_LIMITE = 2  # Segundos para o primeiro alerta se os olhos não forem detectados
INTERVALO_NOVA_JANELA = 0.1 # Segundos entre cada nova janela de alerta (depois da primeira)

# ✅ Inicialização do detector de rosto do MediaPipe
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(min_detection_confidence=0.5)

# ✅ Variáveis de controle
tempo_ausente = 0           # Marca quando os olhos sumiram
olhos_detectados = True     # Começamos achando que os olhos estão lá
alerta_popups_ativo = False # Controla se o modo de "mostrar muitas janelas" está ligado
tempo_proxima_janela = 0    # Controla quando a PRÓXIMA janela deve aparecer

# ✅ Captura de vídeo da webcam
cam = cv2.VideoCapture(0)

# ✅ Inicializar o Tkinter
root = tk.Tk()
root.withdraw() # Esconde a janela principal do Tkinter

# ✅ Lista para guardar as janelas de alerta
popup_windows_list = []

# Lista de mensagens divertidas para as janelas
mensagens_amigaveis = [
    "Olha para a câmera!",
    "Estou te esperando! 😊",
    "Vem logo!!!",
    "Volte a olhar para cá!",
    "Um alô da sua tela! 👋",
    "Psst... por aqui!",
    "Alerta de atenção! 🔔"
]

# Função para criar UMA janela de alerta em posição aleatória com mensagem aleatória
def criar_uma_janela_alerta_aleatoria():
    global popup_windows_list # Acessa a lista de janelas

    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    popup_width = 280  # Um pouco menor para caberem mais
    popup_height = 90

    random_x = random.randint(0, max(0, screen_width - popup_width))
    random_y = random.randint(0, max(0, screen_height - popup_height))

    popup = tk.Toplevel(root)
    num_janela = len(popup_windows_list) + 1
    popup.title(f"Alerta Olhos #{num_janela}!")
    popup.geometry(f"{popup_width}x{popup_height}+{random_x}+{random_y}")
    popup.attributes("-topmost", True) # Tenta manter no topo
    popup.resizable(False, False) # Não deixa mudar o tamanho

    mensagem_escolhida = random.choice(mensagens_amigaveis) # Sorteia uma mensagem
    label = tk.Label(popup, text=mensagem_escolhida, padx=15, pady=10, font=("Arial", 10, "bold"))
    label.pack(expand=True, fill=tk.BOTH)

    popup_windows_list.append(popup)

# Função para fechar todas as janelas de alerta
def fechar_alertas_popup():
    global popup_windows_list, alerta_popups_ativo
    # A mensagem de "fechando" será dita no loop principal
    for popup in popup_windows_list:
        if popup.winfo_exists():
            popup.destroy()
    popup_windows_list.clear()
    alerta_popups_ativo = False # Desliga o modo de "mostrar muitas janelas"

# ✅ Loop infinito para capturar os frames da câmera
while True:
    ok, frame = cam.read()
    if not ok:
        break

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    resultado = face_mesh.process(rgb)

    if resultado.multi_face_landmarks: # Se detectou um rosto (e os olhos)
        for face_landmarks in resultado.multi_face_landmarks:
            for i in [33, 133, 362, 263]: # Pontos dos olhos
                ponto = face_landmarks.landmark[i]
                h, w, _ = frame.shape
                x, y = int(ponto.x * w), int(ponto.y * h)
                cv2.circle(frame, (x, y), 2, (0, 255, 0), -1)

        if alerta_popups_ativo: # Se as janelinhas estavam aparecendo
            print("Oba! Você voltou a olhar! Fechando os alertas. 😄")
            fechar_alertas_popup() # Fecha todas

        olhos_detectados = True
        # tempo_ausente é resetado aqui ou não, dependendo da lógica de re-alerta.
        # Para este caso, deixar como está, pois a ausência acabou.
        # Se quisermos que o tempo_ausente zere, descomente a linha abaixo:
        # tempo_ausente = time.time() 

    else: # Se NÃO detectou um rosto (ou os olhos)
        if olhos_detectados: # Se foi a PRIMEIRA vez que os olhos sumiram
            olhos_detectados = False
            tempo_ausente = time.time() # Marca quando a ausência começou
            # alerta_popups_ativo ainda é False, espera o TEMPO_LIMITE
            print("Hum... Parece que você desviou o olhar. Vou começar a contar...")

        # Se os olhos continuam ausentes (olhos_detectados já é False)
        # E o TEMPO_LIMITE já passou desde que sumiram
        if not olhos_detectados and (time.time() - tempo_ausente > TEMPO_LIMITE):
            if not alerta_popups_ativo:
                # É a primeira vez que o TEMPO_LIMITE passou nesta ausência
                print(f"⚠️ Ei! Já se passaram {TEMPO_LIMITE} segundos! Cadê você?")
                winsound.Beep(3500, 400) # Som de alerta inicial
                alerta_popups_ativo = True # Liga o modo de mostrar janelas!
                
                criar_uma_janela_alerta_aleatoria() # Cria a PRIMEIRA janela
                print(f"Abri a janela de alerta #{len(popup_windows_list)}!")
                tempo_proxima_janela = time.time() # Marca o tempo para a próxima

            elif alerta_popups_ativo: # Se o modo de mostrar janelas JÁ está ligado
                # Verifica se já passou o tempo para abrir MAIS UMA janela
                if time.time() - tempo_proxima_janela > INTERVALO_NOVA_JANELA:
                    criar_uma_janela_alerta_aleatoria()
                    print(f"Mais uma janela aberta! Total: #{len(popup_windows_list)}.")
                    # winsound.Beep(2000, 100) # Um bip mais curto para novas janelas (opcional)
                    tempo_proxima_janela = time.time() # Marca o tempo para a próxima

    cv2.imshow("Detector de Olhar Divertido", frame)

    root.update_idletasks()
    root.update()

    if cv2.waitKey(1) == 27: # Tecla ESC para sair
        break

# ✅ Fecha tudo direitinho ao sair do programa
if alerta_popups_ativo: # Se saiu com alertas ativos, fecha eles
    fechar_alertas_popup()
cam.release()
cv2.destroyAllWindows()
# root.destroy() # Opcional, pois o programa está fechando