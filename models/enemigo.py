# models/enemigo.py

class Enemigo:
    def __init__(self, nombre: str, puntos_vida: int, ataque: int, defensa: int, tipo: str):
        self.nombre = nombre
        self.puntos_vida = puntos_vida
        self.ataque = ataque
        self.defensa = defensa
        
        # Validación del requerimiento R1.2
        if tipo.lower() not in ["volador", "terrestre"]:
            raise ValueError("El tipo de enemigo debe ser 'volador' o 'terrestre'")
        self.tipo = tipo.lower()

    def esta_vivo(self) -> bool:
        return self.puntos_vida > 0
    
    def recibir_dano(self, cantidad: int):
        self.puntos_vida -= cantidad
        if self.puntos_vida < 0:
            self.puntos_vida = 0

    def mostrar_estadisticas(self):
        print(f"--- {self.nombre} (Tipo: {self.tipo.capitalize()}) ---")
        print(f"HP: {self.puntos_vida} | ATK: {self.ataque} | DEF: {self.defensa}")