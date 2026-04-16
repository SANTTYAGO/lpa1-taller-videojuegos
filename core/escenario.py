# core/escenario.py
import random
from models.enemigo import Enemigo
from models.objeto import Tesoro, Trampa, Equipamiento

class Zona:
    def __init__(self, id_zona: int):
        self.id_zona = id_zona
        self.nombre = f"Área {id_zona}"
        self.enemigo = None
        self.objeto = None
        self.es_tienda = False

    def mostrar_info(self):
        print(f"\n🗺️ --- {self.nombre} ---")
        if self.es_tienda:
            print("🏪 ¡Es una Zona Segura! Hay un mercader aquí dispuesto a comerciar.")
        
        if self.enemigo:
            print(f"⚠️ Peligro inminente: Un '{self.enemigo.nombre}' acecha en las sombras.")
            
        if self.objeto:
            print(f"📦 Has avistado algo en el suelo: {self.objeto.nombre}.")
            
        if not self.es_tienda and not self.enemigo and not self.objeto:
            print("🍃 Un lugar tranquilo. No hay amenazas ni objetos a la vista.")

class Escenario:
    def __init__(self):
        # R4.1: Generación de escenario con 20 áreas explorables
        self.zonas = [Zona(i) for i in range(1, 21)]
        self.generar_entorno()

    def generar_entorno(self):
        # 1. Configurar tiendas aleatorias (evitando la zona 20)
        tiendas_ids = random.sample(range(19), 2)
        for i in tiendas_ids:
            self.zonas[i].es_tienda = True
            self.zonas[i].nombre = "Refugio del Mercader"

        # 2. Configurar el Jefe Final en la última zona (R7.2)
        zona_final = self.zonas[-1] # La zona 20
        zona_final.nombre = "Guarida del Rey Demonio"
        zona_final.enemigo = Enemigo(
            nombre="Rey Demonio", 
            puntos_vida=200, 
            ataque=30, 
            defensa=20, 
            tipo="terrestre"
        )

        # 3. Distribuir Elementos en el resto del mapa
        zonas_disponibles = [z for z in self.zonas[:-1] if not z.es_tienda]
        zonas_seleccionadas = random.sample(zonas_disponibles, 16) # 16 para dejar espacios vacíos
        
        for zona in zonas_seleccionadas:
            if random.choice([True, False]):
                tipos = ["volador", "terrestre"]
                zona.enemigo = Enemigo(
                    nombre=random.choice(["Esqueleto", "Limo", "Murciélago"]),
                    puntos_vida=random.randint(20, 50),
                    ataque=random.randint(5, 15),
                    defensa=random.randint(2, 8),
                    tipo=random.choice(tipos)
                )
            else:
                if random.choice([True, False]):
                    zona.objeto = Tesoro("Bolsa de Monedas", random.randint(10, 100))
                else:
                    zona.objeto = Trampa("Mina Oculta", alcance_explosion=1, dano_explosion=25)