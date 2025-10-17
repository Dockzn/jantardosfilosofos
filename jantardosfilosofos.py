import threading
import time
import tkinter as tk
from tkinter import ttk
import math

class Filosofo(threading.Thread):
    def __init__(self, id, garfos, estados, mutex_estado, canvas):
        super().__init__(daemon=True)
        self.id = id
        self.garfos = garfos
        self.estados = estados
        self.mutex_estado = mutex_estado
        self.canvas = canvas
        self.cores = {
            "Pensando": "gray",
            "Faminto": "orange",
            "Comendo": "green"
        }

    def run(self):
        while True:
            self.pensar()
            self.pegar_garfos()
            self.comer()
            self.soltar_garfos()

    def pensar(self):
        self.atualizar_estado("Pensando")
        time.sleep(2)

    def pegar_garfos(self):
        garfo_esq = self.id
        garfo_dir = (self.id + 1) % 5
        self.atualizar_estado("Faminto")

        # Estratégia para evitar deadlock: pegar sempre o garfo de menor ID primeiro
        primeiro, segundo = sorted([garfo_esq, garfo_dir])
        self.garfos[primeiro].acquire()
        self.garfos[segundo].acquire()

    def comer(self):
        self.atualizar_estado("Comendo")
        time.sleep(3)

    def soltar_garfos(self):
        garfo_esq = self.id
        garfo_dir = (self.id + 1) % 5
        self.garfos[garfo_esq].release()
        self.garfos[garfo_dir].release()

    def atualizar_estado(self, estado):
        with self.mutex_estado:
            self.estados[self.id] = estado
            self.canvas.after(0, self.atualizar_gui)

    def atualizar_gui(self):
        for i, estado in enumerate(self.estados):
            cor = self.cores[estado]
            self.canvas.itemconfig(f"filosofo_{i}", fill=cor)

class JantarDosFilosofosGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Jantar dos Filósofos")
        
        self.canvas = tk.Canvas(root, width=600, height=600, bg="white")
        self.canvas.pack()

        # Estados iniciais e mutex para controle
        self.estados = ["Pensando"] * 5
        self.mutex_estado = threading.Lock()
        self.garfos = [threading.Semaphore(1) for _ in range(5)]

        centro_x, centro_y = 300, 300
        raio = 200
        self.posicoes_filosofos = []
        for i in range(5):
            angulo = math.radians(90 + i * 72) 
            x = centro_x + raio * math.cos(angulo)
            y = centro_y - raio * math.sin(angulo)  
            self.posicoes_filosofos.append((x, y))

        self.posicoes_garfos = []
        for i in range(5):
            x1, y1 = self.posicoes_filosofos[i]
            x2, y2 = self.posicoes_filosofos[(i+1)%5]
            garfo_x = (x1 + x2) / 2
            garfo_y = (y1 + y2) / 2
            self.posicoes_garfos.append((garfo_x, garfo_y))

        for i, (x, y) in enumerate(self.posicoes_garfos):
            self.canvas.create_rectangle(x-10, y-10, x+10, y+10, fill="silver", tags=f"garfo_{i}")

        for i, (x, y) in enumerate(self.posicoes_filosofos):
            self.canvas.create_oval(x-30, y-30, x+30, y+30, 
                                   fill="gray", outline="black",
                                   tags=f"filosofo_{i}")
            self.canvas.create_text(x, y, text=str(i+1), font=("Arial", 12))

        # Inicia as threads dos filósofos
        self.filosofos = [
            Filosofo(i, self.garfos, self.estados, self.mutex_estado, self.canvas)
            for i in range(5)
        ]
        for f in self.filosofos:
            f.start()

if __name__ == "__main__":
    root = tk.Tk()
    app = JantarDosFilosofosGUI(root)
    root.mainloop()