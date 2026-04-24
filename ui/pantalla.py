# ui/pantalla.py
import pygame
import os
import random
import json
from ui.constantes import *
from ui.estados import (EstadoMenuPrincipal, EstadoExploracion, EstadoCombate, 
                        EstadoTienda, EstadoFinJuego, EstadoPausa)
from models.personaje import Personaje
from core.escenario import Escenario
from models.objeto import Equipamiento, Tesoro

class MotorGrafico:
    def __init__(self, heroe: Personaje, mundo: Escenario):
        pygame.init()
        pygame.mixer.init()
        
        self.pantalla_completa = False
        self.volumen_musica = 0.5
        self.volumen_sfx = 0.5
        
        self.pantalla = pygame.display.set_mode((ANCHO_VENTANA, ALTO_VENTANA), pygame.SCALED)
        pygame.display.set_caption("La Leyenda de los 17 Girasoles")
        self.reloj = pygame.time.Clock()
        self.corriendo = True
        
        self.heroe = heroe
        self.mundo = mundo
        self.indice_zona_actual = 0 
        
        self.fuente = pygame.font.SysFont("Arial", 20, bold=True)
        self.fuente_grande = pygame.font.SysFont("Arial", 40, bold=True)
        self.fuente_gigante = pygame.font.SysFont("Arial", 55, bold=True)
        
        self.estado_menu = EstadoMenuPrincipal(self)
        self.estado_exploracion = EstadoExploracion(self)
        self.estado_combate = EstadoCombate(self)
        self.estado_tienda = EstadoTienda(self)
        self.estado_fin = EstadoFinJuego(self)
        self.estado_pausa = EstadoPausa(self)
        
        self.estado_actual = self.estado_menu 
        
        self.turno_actual = "JUGADOR"
        self.mensaje_combate = "¡Un enemigo bloquea el paso!"
        self.mensaje_tienda = "¡Bienvenido! ¿Qué vas a llevar?"
        self.objeto_tienda = Equipamiento("Espada Maestra", 15, 5, 150, 75)
        
        self.textos_flotantes = []
        
        self.posicion_jugador_x = 50 
        self.posicion_jugador_y = ((ALTO_VENTANA - 60) // 2) - (TAMANO_CELDA // 2)
        self.indice_animacion = 0
        self.tiempo_ultima_animacion = 0
        self.velocidad_animacion_ms = 120 
        self.accion_actual_heroe = "IDLE" 
        self.mirando_izquierda = False 
        self.efecto_combate_activo = None 
        self.tiempo_inicio_efecto = 0    
        
        self.cargar_recursos_graficos()
        self.cargar_sonidos()
        self.cargar_zona() 

    def alternar_pantalla_completa(self):
        self.pantalla_completa = not self.pantalla_completa
        if self.pantalla_completa:
            self.pantalla = pygame.display.set_mode((ANCHO_VENTANA, ALTO_VENTANA), pygame.FULLSCREEN | pygame.SCALED)
        else:
            self.pantalla = pygame.display.set_mode((ANCHO_VENTANA, ALTO_VENTANA), pygame.SCALED)

    def ajustar_volumen_musica(self, incremento):
        self.volumen_musica = max(0.0, min(1.0, self.volumen_musica + incremento))
        pygame.mixer.music.set_volume(self.volumen_musica)

    def ajustar_volumen_sfx(self, incremento):
        self.volumen_sfx = max(0.0, min(1.0, self.volumen_sfx + incremento))
        if self.usar_sonidos:
            self.sonido_ataque.set_volume(self.volumen_sfx)
            self.sonido_moneda.set_volume(self.volumen_sfx)
            for paso in self.sonidos_pasos:
                paso.set_volume(self.volumen_sfx * 0.4) 

    def cargar_zona(self):
        zona_actual = self.mundo.zonas[self.indice_zona_actual]
        self.enemigo_en_zona = zona_actual.enemigo
        self.objeto_en_zona = zona_actual.objeto
        self.es_tienda = zona_actual.es_tienda
        self.nombre_zona_actual = zona_actual.nombre
        
        if self.enemigo_en_zona: 
            self.rectangulo_enemigo = pygame.Rect(600, 300, TAMANO_CELDA, TAMANO_CELDA)
        if self.objeto_en_zona: 
            self.rectangulo_objeto = pygame.Rect(300, 400, TAMANO_CELDA, TAMANO_CELDA)
        if self.es_tienda: 
            self.rectangulo_mercader = pygame.Rect(ANCHO_VENTANA // 2, 200, TAMANO_CELDA, TAMANO_CELDA)

    def _recortar_hoja_sprites(self, ruta_archivo, escala_destino):
        hoja = pygame.image.load(ruta_archivo).convert_alpha()
        alto_frame = hoja.get_height()
        numero_columnas = hoja.get_width() // alto_frame
        lista_frames = []
        for i in range(numero_columnas):
            area_recorte = pygame.Rect(i * alto_frame, 0, alto_frame, alto_frame)
            frame_recortado = hoja.subsurface(area_recorte)
            lista_frames.append(pygame.transform.scale(frame_recortado, escala_destino))
        return lista_frames

    def cargar_recursos_graficos(self):
        self.usar_sprites = False
        self.imagen_objeto = None
        try:
            esc_mapa = (TAMANO_CELDA, TAMANO_CELDA) 
            esc_personaje = (ESCALA_PERSONAJE, ESCALA_PERSONAJE)
            
            self.anim_heroe_idle = self._recortar_hoja_sprites(os.path.join("assets", "Heroe", "Soldier", "Soldier-Idle.png"), esc_personaje)
            self.anim_heroe_walk = self._recortar_hoja_sprites(os.path.join("assets", "Heroe", "Soldier", "Soldier-Walk.png"), esc_personaje)
            self.anim_heroe_attack = self._recortar_hoja_sprites(os.path.join("assets", "Heroe", "Soldier", "Soldier-Attack01.png"), esc_personaje)
            
            self.anim_enemigo_idle = self._recortar_hoja_sprites(os.path.join("assets", "Enemigo", "Orc", "Orc-Idle.png"), esc_personaje)
            self.anim_enemigo_attack = self._recortar_hoja_sprites(os.path.join("assets", "Enemigo", "Orc", "Orc-Attack01.png"), esc_personaje)
            
            self.imagen_suelo = pygame.transform.scale(pygame.image.load(os.path.join("assets", "Suelo", "Grass_Middle.png")).convert(), esc_mapa)
            
            try: self.imagen_objeto = pygame.transform.scale(pygame.image.load(os.path.join("assets", "Objeto", "item.png")).convert_alpha(), esc_mapa)
            except: pass
            
            self.usar_sprites = True
        except Exception as error: 
            print(f"Modo gráfico simplificado activado. Error: {error}")

    def cargar_sonidos(self):
        self.usar_sonidos = False
        try:
            self.sonido_ataque = pygame.mixer.Sound(os.path.join("assets", "Sonidos", "knifeSlice.ogg"))
            self.sonido_moneda = pygame.mixer.Sound(os.path.join("assets", "Sonidos", "handleCoins.ogg"))
            
            self.sonidos_pasos = []
            for i in range(10): 
                paso = pygame.mixer.Sound(os.path.join("assets", "Sonidos", f"footstep0{i}.ogg"))
                self.sonidos_pasos.append(paso)
            
            self.ajustar_volumen_sfx(0)
            pygame.mixer.music.set_volume(self.volumen_musica)
            self.usar_sonidos = True
        except Exception as error: 
            print(f"Jugando en silencio. Error: {error}")

    def manejar_eventos(self):
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT: 
                self.corriendo = False
            self.estado_actual.manejar_evento(evento)

    def dibujar_hud_inferior(self):
        if self.estado_actual in [self.estado_menu, self.estado_fin, self.estado_pausa]: 
            return
            
        rect_panel = pygame.Rect(0, ALTO_VENTANA - 60, ANCHO_VENTANA, 60)
        pygame.draw.rect(self.pantalla, COLOR_GRIS_PANEL, rect_panel)
        pygame.draw.rect(self.pantalla, COLOR_BLANCO, rect_panel, 2)
        
        t_hp = self.fuente.render(f"HP: {self.heroe.puntos_vida}/{self.heroe.puntos_vida_max}", True, (255, 100, 100))
        t_inv = self.fuente.render(f"ATK: {self.heroe.ataque} | DEF: {self.heroe.defensa} | Pts: {self.heroe.puntaje}", True, COLOR_AMARILLO_MENU)
        color_z = (100, 255, 100) if self.es_tienda else COLOR_BLANCO
        t_z = self.fuente.render(f"{self.nombre_zona_actual} ({self.indice_zona_actual+1}/20)", True, color_z)
        
        self.pantalla.blit(t_hp, (20, ALTO_VENTANA - 40))
        self.pantalla.blit(t_inv, (180, ALTO_VENTANA - 40))
        self.pantalla.blit(t_z, (500, ALTO_VENTANA - 40))

    def actualizar(self):
        self.estado_actual.actualizar()
        tiempo_actual = pygame.time.get_ticks()
        if tiempo_actual - self.tiempo_ultima_animacion > self.velocidad_animacion_ms:
            self.tiempo_ultima_animacion = tiempo_actual
            self.indice_animacion += 1
            if self.accion_actual_heroe == "WALK" and self.usar_sonidos:
                if self.indice_animacion % 2 == 0: random.choice(self.sonidos_pasos).play()
        self.reloj.tick(FOTOGRAMAS_POR_SEGUNDO)

    def dibujar(self):
        self.estado_actual.dibujar()
        self.dibujar_hud_inferior()
        pygame.display.flip()

    def salir(self): 
        pygame.quit()

    # =========================================================
    # LÓGICA DE PERSISTENCIA (GUARDADO Y CARGA EN JSON)
    # =========================================================
    def guardar_partida(self):
        datos_guardado = {
            "zona_actual": self.indice_zona_actual,
            "heroe": {
                "nombre": self.heroe.nombre,
                "puntos_vida": self.heroe.puntos_vida,
                "puntos_vida_max": getattr(self.heroe, "puntos_vida_max", 100),
                "ataque": self.heroe.ataque,
                "defensa": self.heroe.defensa,
                "nivel": getattr(self.heroe, "nivel", 1),
                "experiencia": getattr(self.heroe, "experiencia", 0),
                "puntaje": self.heroe.puntaje,
                "zonas_exploradas": getattr(self.heroe, "zonas_exploradas", 0),
                # Guardamos los nombres de los objetos para reconstruirlos
                "inventario": [{"nombre": obj.nombre} for obj in self.heroe.inventario]
            }
        }
        try:
            with open("savegame.json", "w") as archivo:
                json.dump(datos_guardado, archivo, indent=4)
            return True
        except Exception as e:
            print(f"Error al guardar partida: {e}")
            return False

    def cargar_partida(self):
        if not os.path.exists("savegame.json"):
            return False
            
        try:
            with open("savegame.json", "r") as archivo:
                datos = json.load(archivo)
            
            # 1. Restaurar posición en el mapa
            self.indice_zona_actual = datos["zona_actual"]
            
            # 2. Restaurar estadísticas del héroe
            d_heroe = datos["heroe"]
            self.heroe.nombre = d_heroe["nombre"]
            self.heroe.puntos_vida = d_heroe["puntos_vida"]
            self.heroe.ataque = d_heroe["ataque"]
            self.heroe.defensa = d_heroe["defensa"]
            self.heroe.puntaje = d_heroe["puntaje"]
            
            if hasattr(self.heroe, "puntos_vida_max"): self.heroe.puntos_vida_max = d_heroe["puntos_vida_max"]
            if hasattr(self.heroe, "nivel"): self.heroe.nivel = d_heroe["nivel"]
            if hasattr(self.heroe, "experiencia"): self.heroe.experiencia = d_heroe["experiencia"]
            if hasattr(self.heroe, "zonas_exploradas"): self.heroe.zonas_exploradas = d_heroe["zonas_exploradas"]
            
            # 3. Restaurar inventario creando objetos Tesoro genéricos para la UI
            self.heroe.inventario = []
            for obj in d_heroe["inventario"]:
                self.heroe.inventario.append(Tesoro(obj["nombre"], valor_monetario=0))
            
            self.cargar_zona()
            return True
        except Exception as e:
            print(f"Error al cargar partida: {e}")
            return False