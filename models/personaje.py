# models/personaje.py
from models.objeto import Equipamiento

class Personaje:
    def __init__(self, nombre: str, puntos_vida: int, ataque: int, defensa: int):
        self.nombre = nombre
        self.puntos_vida = puntos_vida
        self.puntos_vida_max = puntos_vida # Para saber el tope al curarse o subir de nivel
        
        # --- NUEVO: Estadísticas de Magia (Maná) para las habilidades ---
        self.puntos_magia = 50
        self.puntos_magia_max = 50
        
        self.ataque = ataque
        self.defensa = defensa
        self.nivel = 1
        self.experiencia = 0
        self.puntaje = 0
        self.zonas_exploradas = 0
        self.inventario = []
        self.equipamiento_actual = None # R3.3: Espacio para el arma/armadura equipada

    def esta_vivo(self) -> bool:
        return self.puntos_vida > 0

    def mostrar_estadisticas(self):
        print(f"--- {self.nombre} (Nivel {self.nivel} | EXP: {self.experiencia}/100) ---")
        # Actualizado para mostrar también el Maná en consola
        print(f"HP: {self.puntos_vida}/{self.puntos_vida_max} | MP: {self.puntos_magia}/{self.puntos_magia_max} | ATK: {self.ataque} | DEF: {self.defensa}")
        if self.equipamiento_actual:
            print(f"Equipado: {self.equipamiento_actual.nombre}")
        print(f"Inventario: {len(self.inventario)} objetos")

    # Requerimiento R3.2: Recolectar objetos
    def recolectar_objeto(self, objeto):
        self.inventario.append(objeto)
        print(f"🎒 {self.nombre} ha guardado '{objeto.nombre}' en su inventario.")

    # Requerimiento R3.3: Usar equipamiento
    def equipar(self, equipamiento: Equipamiento):
        if self.equipamiento_actual:
            # Si ya tiene algo equipado, le restamos los bonos anteriores
            self.ataque -= self.equipamiento_actual.aumento_ataque
            self.defensa -= self.equipamiento_actual.aumento_defensa
            self.inventario.append(self.equipamiento_actual)
            print(f"🔄 {self.nombre} se ha desequipado '{self.equipamiento_actual.nombre}'.")
        
        # Equipamos el nuevo objeto y sumamos los bonos
        self.equipamiento_actual = equipamiento
        self.ataque += equipamiento.aumento_ataque
        self.defensa += equipamiento.aumento_defensa
        if equipamiento in self.inventario:
            self.inventario.remove(equipamiento) # Lo sacamos del inventario al usarlo
        print(f"⚔️ {self.nombre} se ha equipado '{equipamiento.nombre}' (+{equipamiento.aumento_ataque} ATK, +{equipamiento.aumento_defensa} DEF).")

    def recibir_dano(self, cantidad: int):
        self.puntos_vida -= cantidad
        if self.puntos_vida < 0:
            self.puntos_vida = 0

    # Requerimientos R6.1 y R6.2: Ganar experiencia y subir de nivel
    def ganar_experiencia(self, cantidad: int):
        self.experiencia += cantidad
        print(f"✨ {self.nombre} ha ganado {cantidad} puntos de experiencia.")
        
        # Verificamos si alcanza los 100 puntos para subir de nivel
        if self.experiencia >= 100:
            self.subir_nivel()

    def subir_nivel(self):
        self.nivel += 1
        self.experiencia -= 100 # Reiniciamos la barra de experiencia
        
        # Mejora de atributos por nivel (R6.2)
        self.puntos_vida_max += 20
        self.puntos_vida = self.puntos_vida_max # Le curamos la vida al subir de nivel
        
        # --- NUEVO: El maná máximo sube y se restaura al subir de nivel ---
        self.puntos_magia_max += 15
        self.puntos_magia = self.puntos_magia_max
        
        self.ataque += 5
        self.defensa += 3
        
        print(f"\n🎉 ¡Felicidades! {self.nombre} ha alcanzado el Nivel {self.nivel}! 🎉")
        print("Tus atributos han aumentado.")

    def ganar_puntaje(self, cantidad: int):
        self.puntaje += cantidad
        print(f"🌟 +{cantidad} Puntos! (Puntaje Total: {self.puntaje})")

    def registrar_exploracion(self):
        self.zonas_exploradas += 1