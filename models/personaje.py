# models/personaje.py
from models.objeto import Equipamiento

class Personaje:
    def __init__(self, nombre: str, puntos_vida: int, ataque: int, defensa: int):
        self.nombre = nombre
        self.puntos_vida = puntos_vida
        self.puntos_vida_max = puntos_vida 
        self.puntos_magia = 50
        self.puntos_magia_max = 50
        
        self.ataque = ataque
        self.defensa = defensa
        self.nivel = 1
        self.experiencia = 0
        self.puntaje = 0
        self.zonas_exploradas = 0
        self.inventario = []
        self.equipamiento_actual = None 
        
        # --- NUEVO: Rastreador de Estados Alterados ---
        self.estados = {"veneno": 0, "aturdido": 0}

    def aplicar_estado(self, estado: str, turnos: int):
        """Aplica un efecto negativo al personaje"""
        self.estados[estado] = turnos

    def procesar_estados(self):
        """Se ejecuta al inicio del turno. Retorna (esta_aturdido, mensajes, dano_sufrido)"""
        mensajes = []
        aturdido = False
        dano_total = 0

        if self.estados["veneno"] > 0:
            dano = 5 # El veneno quita 5 de vida fijos por turno
            self.recibir_dano(dano)
            self.estados["veneno"] -= 1
            dano_total += dano
            mensajes.append(f"El Veneno consume {dano} HP.")

        if self.estados["aturdido"] > 0:
            aturdido = True
            self.estados["aturdido"] -= 1
            mensajes.append("¡Estás Aturdido y no puedes moverte!")

        return aturdido, mensajes, dano_total

    def esta_vivo(self) -> bool:
        return self.puntos_vida > 0

    def mostrar_estadisticas(self):
        print(f"--- {self.nombre} (Nivel {self.nivel} | EXP: {self.experiencia}/100) ---")
        print(f"HP: {self.puntos_vida}/{self.puntos_vida_max} | MP: {self.puntos_magia}/{self.puntos_magia_max} | ATK: {self.ataque} | DEF: {self.defensa}")
        if self.equipamiento_actual:
            print(f"Equipado: {self.equipamiento_actual.nombre}")
        print(f"Inventario: {len(self.inventario)} objetos")

    def recolectar_objeto(self, objeto):
        self.inventario.append(objeto)
        print(f"🎒 {self.nombre} ha guardado '{objeto.nombre}' en su inventario.")

    def equipar(self, equipamiento: Equipamiento):
        if self.equipamiento_actual:
            self.ataque -= self.equipamiento_actual.aumento_ataque
            self.defensa -= self.equipamiento_actual.aumento_defensa
            self.inventario.append(self.equipamiento_actual)
            print(f"🔄 {self.nombre} se ha desequipado '{self.equipamiento_actual.nombre}'.")
        
        self.equipamiento_actual = equipamiento
        self.ataque += equipamiento.aumento_ataque
        self.defensa += equipamiento.aumento_defensa
        if equipamiento in self.inventario:
            self.inventario.remove(equipamiento) 
        print(f"⚔️ {self.nombre} se ha equipado '{equipamiento.nombre}' (+{equipamiento.aumento_ataque} ATK, +{equipamiento.aumento_defensa} DEF).")

    def recibir_dano(self, cantidad: int):
        self.puntos_vida -= cantidad
        if self.puntos_vida < 0:
            self.puntos_vida = 0

    def ganar_experiencia(self, cantidad: int):
        self.experiencia += cantidad
        print(f"✨ {self.nombre} ha ganado {cantidad} puntos de experiencia.")
        if self.experiencia >= 100:
            self.subir_nivel()

    def subir_nivel(self):
        self.nivel += 1
        self.experiencia -= 100 
        
        self.puntos_vida_max += 20
        self.puntos_vida = self.puntos_vida_max 
        self.puntos_magia_max += 15
        self.puntos_magia = self.puntos_magia_max
        self.ataque += 5
        self.defensa += 3
        
        # Al subir de nivel, tu cuerpo se limpia de los venenos
        self.estados["veneno"] = 0
        self.estados["aturdido"] = 0
        
        print(f"\n🎉 ¡Felicidades! {self.nombre} ha alcanzado el Nivel {self.nivel}! 🎉")

    def ganar_puntaje(self, cantidad: int):
        self.puntaje += cantidad
        print(f"🌟 +{cantidad} Puntos! (Puntaje Total: {self.puntaje})")

    def registrar_exploracion(self):
        self.zonas_exploradas += 1