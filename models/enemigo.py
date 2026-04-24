# models/enemigo.py
import math

class Enemigo:
    def __init__(self, nombre: str, puntos_vida: int, ataque: int, defensa: int, tipo: str = "terrestre"):
        self.nombre = nombre
        self.puntos_vida = puntos_vida
        self.ataque = ataque
        self.defensa = defensa
        
        if tipo not in ["volador", "terrestre"]:
            raise ValueError("El tipo de enemigo debe ser 'volador' o 'terrestre'")
        self.tipo = tipo

        # --- NUEVO: Variables para Inteligencia Artificial (IA) en el mapa ---
        self.x = 0
        self.y = 0
        self.velocidad = 2
        self.rango_vision = 150 # Distancia en píxeles a la que te detecta
        
        # Estado de IA
        self.estado_ia = "PATRULLANDO"
        self.limite_patrulla_izq = 0
        self.limite_patrulla_der = 0
        self.direccion_patrulla = 1 # 1 (Derecha) o -1 (Izquierda)

    def inicializar_posicion(self, start_x, start_y):
        """Llamado al cargar la zona para poner al orco en el mapa y definir su área de patrulla"""
        self.x = start_x
        self.y = start_y
        self.limite_patrulla_izq = start_x - 100
        self.limite_patrulla_der = start_x + 100

    def esta_vivo(self) -> bool:
        return self.puntos_vida > 0

    def recibir_dano(self, cantidad: int):
        self.puntos_vida -= cantidad
        if self.puntos_vida < 0:
            self.puntos_vida = 0

    def actualizar_ia(self, heroe_x, heroe_y):
        """Lógica de IA: Patrulla o Persigue según la distancia al héroe"""
        if not self.esta_vivo(): return
        
        # 1. Calcular distancia usando el Teorema de Pitágoras
        dx = heroe_x - self.x
        dy = heroe_y - self.y
        distancia = math.sqrt(dx**2 + dy**2)

        # 2. Tomar decisión (Transición de Estado)
        if distancia < self.rango_vision:
            self.estado_ia = "PERSIGUIENDO"
        else:
            self.estado_ia = "PATRULLANDO"

        # 3. Ejecutar Estado
        if self.estado_ia == "PATRULLANDO":
            # Se mueve entre los límites
            self.x += self.velocidad * self.direccion_patrulla
            if self.x > self.limite_patrulla_der:
                self.x = self.limite_patrulla_der
                self.direccion_patrulla = -1 # Da la vuelta a la izquierda
            elif self.x < self.limite_patrulla_izq:
                self.x = self.limite_patrulla_izq
                self.direccion_patrulla = 1  # Da la vuelta a la derecha
                
        elif self.estado_ia == "PERSIGUIENDO":
            # Normalizar el vector de dirección para moverse directo hacia el héroe
            if distancia > 0:
                vector_x = dx / distancia
                vector_y = dy / distancia
                # El enemigo se mueve un poco más rápido (velocidad * 1.5) cuando te persigue
                self.x += vector_x * (self.velocidad * 1.5)
                self.y += vector_y * (self.velocidad * 1.5)