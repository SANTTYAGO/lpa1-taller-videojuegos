# models/personaje.py

class Personaje:
    def __init__(self, nombre: str, puntos_vida: int, ataque: int, defensa: int):
        self.nombre = nombre
        self.puntos_vida = puntos_vida
        self.ataque = ataque
        self.defensa = defensa
        self.nivel = 1
        self.inventario = []

    def esta_vivo(self) -> bool:
        return self.puntos_vida > 0

    def mostrar_estadisticas(self):
        print(f"--- {self.nombre} (Nivel {self.nivel}) ---")
        print(f"HP: {self.puntos_vida} | ATK: {self.ataque} | DEF: {self.defensa}")
        print(f"Inventario: {len(self.inventario)} objetos")

    # NUEVO: Método para recibir daño (útil para ataques o trampas)
    def recibir_dano(self, cantidad: int):
        self.puntos_vida -= cantidad
        if self.puntos_vida < 0:
            self.puntos_vida = 0
            
    # NUEVO: Requerimiento R3.2 - Recolección de Objetos
    def recolectar_objeto(self, objeto):
        self.inventario.append(objeto)
        print(f"🎒 {self.nombre} ha guardado '{objeto.nombre}' en su inventario.")