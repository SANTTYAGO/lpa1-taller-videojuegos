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

        self.x = 0
        self.y = 0
        self.velocidad = 2
        self.rango_vision = 150 
        
        self.estado_ia = "PATRULLANDO"
        self.limite_patrulla_izq = 0
        self.limite_patrulla_der = 0
        self.direccion_patrulla = 1 
        
        # --- NUEVO: Rastreador de Estados para el Enemigo ---
        self.estados = {"veneno": 0, "aturdido": 0}

    def aplicar_estado(self, estado: str, turnos: int):
        self.estados[estado] = turnos

    def procesar_estados(self):
        """Se ejecuta al inicio de su turno. Retorna (esta_aturdido, mensajes, dano_sufrido)"""
        mensajes = []
        aturdido = False
        dano_total = 0

        if self.estados["veneno"] > 0:
            dano = 5
            self.recibir_dano(dano)
            self.estados["veneno"] -= 1
            dano_total += dano
            mensajes.append(f"Sufre por Veneno (-{dano} HP)")

        if self.estados["aturdido"] > 0:
            aturdido = True
            self.estados["aturdido"] -= 1
            mensajes.append("¡Está Aturdido!")

        return aturdido, mensajes, dano_total

    def inicializar_posicion(self, start_x, start_y):
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
        if not self.esta_vivo(): return
        
        dx = heroe_x - self.x
        dy = heroe_y - self.y
        distancia = math.sqrt(dx**2 + dy**2)

        if distancia < self.rango_vision:
            self.estado_ia = "PERSIGUIENDO"
        else:
            self.estado_ia = "PATRULLANDO"

        if self.estado_ia == "PATRULLANDO":
            self.x += self.velocidad * self.direccion_patrulla
            if self.x > self.limite_patrulla_der:
                self.x = self.limite_patrulla_der
                self.direccion_patrulla = -1 
            elif self.x < self.limite_patrulla_izq:
                self.x = self.limite_patrulla_izq
                self.direccion_patrulla = 1  
                
        elif self.estado_ia == "PERSIGUIENDO":
            if distancia > 0:
                vector_x = dx / distancia
                vector_y = dy / distancia
                self.x += vector_x * (self.velocidad * 1.5)
                self.y += vector_y * (self.velocidad * 1.5)