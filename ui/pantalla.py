# ui/pantalla.py
import pygame
import os
import random
from models.personaje import Personaje
from core.escenario import Escenario
from core.combate import SistemaCombate
from models.objeto import Objeto, Equipamiento

# =================================================================
# CONFIGURACIÓN Y CONSTANTES GLOBALES
# =================================================================
ANCHO_VENTANA = 800
ALTO_VENTANA = 600
FOTOGRAMAS_POR_SEGUNDO = 60
TAMANO_CELDA = 64 
VELOCIDAD_MOVIMIENTO = 5

# Paleta de colores para la Interfaz (UI/UX)
COLOR_NEGRO_FONDO = (15, 15, 20)
COLOR_BLANCO = (255, 255, 255)
COLOR_VERDE_PASTO = (34, 139, 34) 
COLOR_AZUL_HEROE = (30, 144, 255)
COLOR_ROJO_ENEMIGO = (220, 20, 60) 
COLOR_GRIS_PANEL = (50, 50, 50)
COLOR_AMARILLO_MENU = (255, 215, 0)
COLOR_NARANJA_TESORO = (255, 140, 0)
COLOR_MORADO_MERCADER = (128, 0, 128)
COLOR_GIRASOL_ACENTO = (255, 204, 51) 

# =================================================================
# PATRÓN DE DISEÑO: ESTADOS (STATE PATTERN)
# =================================================================

class EstadoJuego:
    """Clase base abstracta para definir el comportamiento de cada pantalla."""
    def __init__(self, motor_grafico):
        self.motor = motor_grafico 

    def manejar_evento(self, evento): 
        pass
    def actualizar(self): 
        pass
    def dibujar(self): 
        pass


class EstadoMenuPrincipal(EstadoJuego):
    """Pantalla inicial del juego con estética armoniosa."""
    def manejar_evento(self, evento):
        if evento.type == pygame.KEYDOWN and evento.key == pygame.K_RETURN:
            # Al iniciar, cargamos la música de exploración
            if self.motor.usar_sonidos:
                pygame.mixer.music.load(os.path.join("assets", "Sonidos", "game soundtrack.mp3"))
                pygame.mixer.music.play(-1)
            self.motor.estado_actual = self.motor.estado_exploracion

    def dibujar(self):
        self.motor.pantalla.fill(COLOR_NEGRO_FONDO)
        
        # Título principal
        texto_titulo = self.motor.fuente_gigante.render("La Leyenda de los 17 Girasoles", True, COLOR_GIRASOL_ACENTO)
        posicion_x_titulo = ANCHO_VENTANA // 2 - texto_titulo.get_width() // 2
        self.motor.pantalla.blit(texto_titulo, (posicion_x_titulo, ALTO_VENTANA // 3))
        
        # Efecto de parpadeo suave para la instrucción
        tiempo_milisegundos = pygame.time.get_ticks()
        factor_parpadeo = abs(tiempo_milisegundos % 2000 - 1000) / 1000.0 
        brillo_texto = int(255 * factor_parpadeo)
        color_instruccion = (brillo_texto, brillo_texto, brillo_texto)
        
        texto_instruccion = self.motor.fuente.render("Presiona ENTER para comenzar la aventura", True, color_instruccion)
        posicion_x_inst = ANCHO_VENTANA // 2 - texto_instruccion.get_width() // 2
        self.motor.pantalla.blit(texto_instruccion, (posicion_x_inst, ALTO_VENTANA // 2 + 50))


class EstadoFinJuego(EstadoJuego):
    """Pantalla de Game Over o Victoria final."""
    def __init__(self, motor_grafico):
        super().__init__(motor_grafico)
        self.es_victoria = False 

    def manejar_evento(self, evento):
        if evento.type == pygame.KEYDOWN and evento.key == pygame.K_RETURN:
            self.motor.corriendo = False 

    def dibujar(self):
        self.motor.pantalla.fill(COLOR_NEGRO_FONDO)
        
        if self.es_victoria:
            texto_principal = self.motor.fuente_gigante.render("¡VICTORIA SUPREMA!", True, COLOR_GIRASOL_ACENTO)
            texto_secundario = self.motor.fuente.render("Has superado todas las zonas con honor.", True, COLOR_BLANCO)
        else:
            texto_principal = self.motor.fuente_gigante.render("FIN DEL JUEGO", True, COLOR_ROJO_ENEMIGO)
            texto_secundario = self.motor.fuente.render("Tu viaje ha terminado en la derrota...", True, COLOR_BLANCO)
            
        texto_salir = self.motor.fuente.render("Presiona ENTER para salir", True, COLOR_GRIS_PANEL)
        
        self.motor.pantalla.blit(texto_principal, (ANCHO_VENTANA // 2 - texto_principal.get_width() // 2, ALTO_VENTANA // 3))
        self.motor.pantalla.blit(texto_secundario, (ANCHO_VENTANA // 2 - texto_secundario.get_width() // 2, ALTO_VENTANA // 2))
        self.motor.pantalla.blit(texto_salir, (ANCHO_VENTANA // 2 - texto_salir.get_width() // 2, ALTO_VENTANA - 100))


class EstadoExploracion(EstadoJuego):
    """Lógica de movimiento por el mapa y transiciones de zonas."""
    def manejar_evento(self, evento):
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_t and self.motor.es_tienda:
                self.motor.estado_actual = self.motor.estado_tienda
                self.motor.mensaje_tienda = "¡Bienvenido! Tengo mercancía de primera."

    def actualizar(self):
        self._procesar_movimiento_heroe()
        self._verificar_colisiones_entidades()

    def _procesar_movimiento_heroe(self):
        teclas_presionadas = pygame.key.get_pressed()
        esta_moviendose = False
        
        if teclas_presionadas[pygame.K_LEFT] or teclas_presionadas[pygame.K_a]:
            self.motor.posicion_jugador_x -= VELOCIDAD_MOVIMIENTO
            self.motor.mirando_izquierda = True
            esta_moviendose = True
        if teclas_presionadas[pygame.K_RIGHT] or teclas_presionadas[pygame.K_d]:
            self.motor.posicion_jugador_x += VELOCIDAD_MOVIMIENTO
            self.motor.mirando_izquierda = False
            esta_moviendose = True
        if teclas_presionadas[pygame.K_UP] or teclas_presionadas[pygame.K_w]:
            self.motor.posicion_jugador_y -= VELOCIDAD_MOVIMIENTO
            esta_moviendose = True
        if teclas_presionadas[pygame.K_DOWN] or teclas_presionadas[pygame.K_s]:
            self.motor.posicion_jugador_y += VELOCIDAD_MOVIMIENTO
            esta_moviendose = True

        self.motor.accion_actual_heroe = "WALK" if esta_moviendose else "IDLE"

        # Límite vertical para no salirse de la zona de juego
        self.motor.posicion_jugador_y = max(0, min(self.motor.posicion_jugador_y, ALTO_VENTANA - 60 - TAMANO_CELDA))
        
        # Lógica de cambio de habitación (Scroll Lateral)
        if self.motor.posicion_jugador_x > ANCHO_VENTANA - TAMANO_CELDA:
            if self.motor.indice_zona_actual < len(self.motor.mundo.zonas) - 1:
                self.motor.indice_zona_actual += 1
                self.motor.cargar_zona()
                self.motor.posicion_jugador_x = 0 
                self.motor.heroe.zonas_exploradas += 1 
            else: 
                self.motor.posicion_jugador_x = ANCHO_VENTANA - TAMANO_CELDA 
        elif self.motor.posicion_jugador_x < 0:
            if self.motor.indice_zona_actual > 0:
                self.motor.indice_zona_actual -= 1
                self.motor.cargar_zona()
                self.motor.posicion_jugador_x = ANCHO_VENTANA - TAMANO_CELDA 
            else: 
                self.motor.posicion_jugador_x = 0 

    def _verificar_colisiones_entidades(self):
        rectangulo_heroe = pygame.Rect(self.motor.posicion_jugador_x, self.motor.posicion_jugador_y, TAMANO_CELDA, TAMANO_CELDA)
        
        # Colisión con Enemigo
        if self.motor.enemigo_en_zona and self.motor.enemigo_en_zona.esta_vivo():
            if rectangulo_heroe.colliderect(self.motor.rectangulo_enemigo):
                self.motor.estado_actual = self.motor.estado_combate 
                self.motor.turno_actual = "JUGADOR"
                self.motor.mensaje_combate = f"¡Emboscada! {self.motor.enemigo_en_zona.nombre} te ataca."
                self.motor.posicion_jugador_x -= 40 # Separación técnica
                self.motor.efecto_combate_activo = None 
                
                if self.motor.usar_sonidos:
                    pygame.mixer.music.load(os.path.join("assets", "Sonidos", "fight soundtrack.ogg"))
                    pygame.mixer.music.play(-1)
                    
        # Colisión con Objetos (Tesoros o Trampas)
        if self.motor.objeto_en_zona:
            if rectangulo_heroe.colliderect(self.motor.rectangulo_objeto):
                if hasattr(self.motor.objeto_en_zona, 'dano_explosion'):
                    self.motor.heroe.recibir_dano(self.motor.objeto_en_zona.dano_explosion)
                    if not self.motor.heroe.esta_vivo():
                        self.motor.estado_fin.es_victoria = False
                        self.motor.estado_actual = self.motor.estado_fin
                else:
                    self.motor.heroe.recolectar_objeto(self.motor.objeto_en_zona)
                    self.motor.heroe.ganar_puntaje(50) 
                    if self.motor.usar_sonidos: 
                        self.motor.sonido_moneda.play()
                        
                # Borramos el objeto del mundo
                self.motor.mundo.zonas[self.motor.indice_zona_actual].objeto = None
                self.motor.objeto_en_zona = None

    def dibujar(self):
        # Dibujar Suelo (Tiling)
        if self.motor.usar_sprites:
            for x in range(0, ANCHO_VENTANA, TAMANO_CELDA):
                for y in range(0, ALTO_VENTANA - 60, TAMANO_CELDA):
                    self.motor.pantalla.blit(self.motor.imagen_suelo, (x, y))
        else: 
            self.motor.pantalla.fill(COLOR_VERDE_PASTO)
            
        # Dibujar Mercader
        if self.motor.es_tienda:
            pygame.draw.rect(self.motor.pantalla, COLOR_MORADO_MERCADER, self.motor.rectangulo_mercader)
            texto_tienda = self.motor.fuente.render("Refugio del Mercader ('T')", True, COLOR_BLANCO)
            self.motor.pantalla.blit(texto_tienda, (ANCHO_VENTANA//2 - texto_tienda.get_width()//2, 160))
            
        # Dibujar Objeto
        if self.motor.objeto_en_zona:
            if self.motor.imagen_objeto: 
                self.motor.pantalla.blit(self.motor.imagen_objeto, self.motor.rectangulo_objeto.topleft)
            else:
                color_obj = (139, 0, 0) if hasattr(self.motor.objeto_en_zona, 'dano_explosion') else COLOR_NARANJA_TESORO
                pygame.draw.rect(self.motor.pantalla, color_obj, self.motor.rectangulo_objeto)
                
        # Dibujar Enemigo
        if self.motor.enemigo_en_zona and self.motor.enemigo_en_zona.esta_vivo():
            if self.motor.usar_sprites:
                indice_frame = self.motor.indice_animacion % len(self.motor.anim_enemigo_idle)
                self.motor.pantalla.blit(self.motor.anim_enemigo_idle[indice_frame], self.motor.rectangulo_enemigo.topleft)
            else: 
                pygame.draw.rect(self.motor.pantalla, COLOR_ROJO_ENEMIGO, self.motor.rectangulo_enemigo)
                
        # Dibujar Héroe Animado
        if self.motor.usar_sprites:
            lista_frames = self.motor.anim_heroe_walk if self.motor.accion_actual_heroe == "WALK" else self.motor.anim_heroe_idle
            indice_frame = self.motor.indice_animacion % len(lista_frames)
            imagen_actual = lista_frames[indice_frame]
            
            if self.motor.mirando_izquierda: 
                imagen_actual = pygame.transform.flip(imagen_actual, True, False)
                
            self.motor.pantalla.blit(imagen_actual, (self.motor.posicion_jugador_x, self.motor.posicion_jugador_y))
        else:
            rect_h = pygame.Rect(self.motor.posicion_jugador_x, self.motor.posicion_jugador_y, TAMANO_CELDA, TAMANO_CELDA)
            pygame.draw.rect(self.motor.pantalla, COLOR_AZUL_HEROE, rect_h)


class EstadoCombate(EstadoJuego):
    """Pantalla de batalla por turnos con vista lateral JRPG."""
    def manejar_evento(self, evento):
        if evento.type != pygame.KEYDOWN: 
            return
            
        if self.motor.turno_actual == "JUGADOR":
            if evento.key == pygame.K_a:
                if self.motor.usar_sonidos: 
                    self.motor.sonido_ataque.play()
                self.motor.efecto_combate_activo = "HEROE_ATACA"
                self.motor.tiempo_inicio_efecto = pygame.time.get_ticks()
                self.motor.indice_animacion = 0 
                
                danio = SistemaCombate.calcular_dano(self.motor.heroe.ataque, self.motor.enemigo_en_zona.defensa)
                self.motor.enemigo_en_zona.recibir_dano(danio)
                self.motor.mensaje_combate = f"¡{self.motor.heroe.nombre} corta con fuerza! Causa {danio} de daño."
                
                if not self.motor.enemigo_en_zona.esta_vivo():
                    self.motor.turno_actual = "VICTORIA"
                else:
                    self.motor.turno_actual = "ENEMIGO"
                    
        elif self.motor.turno_actual == "ENEMIGO":
            if evento.key == pygame.K_SPACE:
                self.motor.efecto_combate_activo = "ENEMIGO_ATACA"
                self.motor.tiempo_inicio_efecto = pygame.time.get_ticks()
                self.motor.indice_animacion = 0
                
                danio = SistemaCombate.calcular_dano(self.motor.enemigo_en_zona.ataque, self.motor.heroe.defensa)
                self.motor.heroe.recibir_dano(danio)
                self.motor.mensaje_combate = f"¡{self.motor.enemigo_en_zona.nombre} ruge y causa {danio} de daño!"
                
                if not self.motor.heroe.esta_vivo():
                    self.motor.turno_actual = "DERROTA"
                    self.motor.estado_fin.es_victoria = False
                else: 
                    self.motor.turno_actual = "JUGADOR"
                    
        elif self.motor.turno_actual == "VICTORIA":
            if evento.key == pygame.K_RETURN:
                self.motor.heroe.ganar_experiencia(100)
                self.motor.efecto_combate_activo = None
                
                if self.motor.enemigo_en_zona.nombre == "Rey Demonio":
                    self.motor.estado_fin.es_victoria = True
                    self.motor.estado_actual = self.motor.estado_fin
                else:
                    self.motor.estado_actual = self.motor.estado_exploracion
                    if self.motor.usar_sonidos:
                        pygame.mixer.music.load(os.path.join("assets", "Sonidos", "game soundtrack.mp3"))
                        pygame.mixer.music.play(-1)
                        
        elif self.motor.turno_actual == "DERROTA":
            if evento.key == pygame.K_RETURN:
                self.motor.estado_actual = self.motor.estado_fin

    def dibujar(self):
        self.motor.pantalla.fill(COLOR_NEGRO_FONDO)
        
        texto_vs = self.motor.fuente_grande.render(f"VS {self.motor.enemigo_en_zona.nombre}", True, COLOR_ROJO_ENEMIGO)
        texto_vida_e = self.motor.fuente.render(f"Vida Enemigo: {self.motor.enemigo_en_zona.puntos_vida}", True, COLOR_BLANCO)
        
        self.motor.pantalla.blit(texto_vs, (ANCHO_VENTANA // 2 - texto_vs.get_width() // 2, 30))
        self.motor.pantalla.blit(texto_vida_e, (ANCHO_VENTANA // 2 - texto_vida_e.get_width() // 2, 80))
        
        if self.motor.usar_sprites:
            tiempo_actual = pygame.time.get_ticks()
            duracion = tiempo_actual - self.motor.tiempo_inicio_efecto
            
            # Animación Héroe
            if self.motor.efecto_combate_activo == "HEROE_ATACA" and duracion < 600:
                frame_idx = min(self.motor.indice_animacion, len(self.motor.anim_heroe_attack) - 1)
                img_heroe = self.motor.anim_heroe_attack[frame_idx]
            else:
                frame_idx = self.motor.indice_animacion % len(self.motor.anim_heroe_idle)
                img_heroe = self.motor.anim_heroe_idle[frame_idx]
                
            # Animación Enemigo
            if self.motor.efecto_combate_activo == "ENEMIGO_ATACA" and duracion < 600:
                frame_idx = min(self.motor.indice_animacion, len(self.motor.anim_enemigo_attack) - 1)
                img_enemigo = self.motor.anim_enemigo_attack[frame_idx]
            else:
                frame_idx = self.motor.indice_animacion % len(self.motor.anim_enemigo_idle)
                img_enemigo = self.motor.anim_enemigo_idle[frame_idx]
                
            self.motor.pantalla.blit(pygame.transform.scale(img_heroe, (192, 192)), (150, 120))
            enemigo_g = pygame.transform.scale(img_enemigo, (192, 192))
            self.motor.pantalla.blit(pygame.transform.flip(enemigo_g, True, False), (450, 120))
            
        # Caja de Mensajes
        rect_mensaje = pygame.Rect(100, 350, 600, 150)
        pygame.draw.rect(self.motor.pantalla, COLOR_GRIS_PANEL, rect_mensaje)
        pygame.draw.rect(self.motor.pantalla, COLOR_AMARILLO_MENU, rect_mensaje, 3)
        
        txt_msg = self.motor.fuente.render(self.motor.mensaje_combate, True, COLOR_BLANCO)
        self.motor.pantalla.blit(txt_msg, (120, 370))
        
        if self.motor.turno_actual == "JUGADOR": 
            inst = "▶ Presiona 'A' para Atacar"; color_inst = COLOR_AMARILLO_MENU
        elif self.motor.turno_actual == "ENEMIGO": 
            inst = "▶ Presiona 'ESPACIO' para recibir ataque"; color_inst = COLOR_AMARILLO_MENU
        elif self.motor.turno_actual == "VICTORIA": 
            inst = "▶ ¡Victoria! Presiona 'ENTER' para seguir"; color_inst = (100, 255, 100)
        elif self.motor.turno_actual == "DERROTA": 
            inst = "▶ Has caído... Presiona 'ENTER'"; color_inst = COLOR_ROJO_ENEMIGO
            
        render_inst = self.motor.fuente.render(inst, True, color_inst)
        self.motor.pantalla.blit(render_inst, (120, 450))


class EstadoTienda(EstadoJuego):
    """Menú de compras interactivo."""
    def manejar_evento(self, evento):
        if evento.type != pygame.KEYDOWN: return
        if evento.key == pygame.K_b:
            if self.motor.heroe.puntaje >= self.motor.objeto_tienda.precio_compra:
                self.motor.heroe.puntaje -= self.motor.objeto_tienda.precio_compra
                self.motor.heroe.equipar(self.motor.objeto_tienda)
                self.motor.mensaje_tienda = f"¡Equipado: {self.motor.objeto_tienda.nombre}!"
                self.motor.objeto_tienda = Equipamiento("Armadura Épica", 5, 20, 300, 150)
            else: self.motor.mensaje_tienda = "No tienes puntos suficientes."
        elif evento.key == pygame.K_RETURN or evento.key == pygame.K_ESCAPE:
            self.motor.estado_actual = self.motor.estado_exploracion 

    def dibujar(self):
        self.motor.pantalla.fill(COLOR_NEGRO_FONDO)
        titulo_t = self.motor.fuente_grande.render("Refugio del Mercader", True, COLOR_MORADO_MERCADER)
        self.motor.pantalla.blit(titulo_t, (ANCHO_VENTANA // 2 - titulo_t.get_width() // 2, 50))
        
        rect_item = pygame.Rect(200, 150, 400, 200)
        pygame.draw.rect(self.motor.pantalla, COLOR_GRIS_PANEL, rect_item)
        pygame.draw.rect(self.motor.pantalla, COLOR_GIRASOL_ACENTO, rect_item, 2)
        
        self.motor.pantalla.blit(self.motor.fuente_grande.render(self.motor.objeto_tienda.nombre, True, COLOR_AMARILLO_MENU), (ANCHO_VENTANA // 2 - 150, 170))
        self.motor.pantalla.blit(self.motor.fuente.render(f"+{self.motor.objeto_tienda.aumento_ataque} ATK / +{self.motor.objeto_tienda.aumento_defensa} DEF", True, COLOR_BLANCO), (ANCHO_VENTANA // 2 - 100, 230))
        self.motor.pantalla.blit(self.motor.fuente.render(f"Costo: {self.motor.objeto_tienda.precio_compra} Puntos", True, (100, 255, 100)), (ANCHO_VENTANA // 2 - 80, 280))
        
        rect_msg_t = pygame.Rect(100, 400, 600, 120)
        pygame.draw.rect(self.motor.pantalla, COLOR_GRIS_PANEL, rect_msg_t)
        pygame.draw.rect(self.motor.pantalla, COLOR_MORADO_MERCADER, rect_msg_t, 3)
        self.motor.pantalla.blit(self.motor.fuente.render(self.motor.mensaje_tienda, True, COLOR_BLANCO), (120, 420))
        self.motor.pantalla.blit(self.motor.fuente.render("▶ 'B' Comprar | 'ENTER' Salir", True, COLOR_AMARILLO_MENU), (120, 480))


# =================================================================
# CLASE PRINCIPAL: MOTOR GRÁFICO (CONTEXTO)
# =================================================================

class MotorGrafico:
    def __init__(self, heroe: Personaje, mundo: Escenario):
        pygame.init()
        pygame.mixer.init()
        
        self.pantalla = pygame.display.set_mode((ANCHO_VENTANA, ALTO_VENTANA))
        pygame.display.set_caption("La Leyenda de los 17 Girasoles")
        self.reloj = pygame.time.Clock()
        self.corriendo = True
        
        self.heroe = heroe
        self.mundo = mundo
        self.indice_zona_actual = 0 
        
        self.fuente = pygame.font.SysFont("Arial", 20, bold=True)
        self.fuente_grande = pygame.font.SysFont("Arial", 40, bold=True)
        self.fuente_gigante = pygame.font.SysFont("Arial", 55, bold=True)
        
        # Instancias de Estados
        self.estado_menu = EstadoMenuPrincipal(self)
        self.estado_exploracion = EstadoExploracion(self)
        self.estado_combate = EstadoCombate(self)
        self.estado_tienda = EstadoTienda(self)
        self.estado_fin = EstadoFinJuego(self)
        
        self.estado_actual = self.estado_menu 
        
        # Variables de Sistema Compartidas
        self.turno_actual = "JUGADOR"
        self.mensaje_combate = "¡Un enemigo bloquea el paso!"
        self.mensaje_tienda = "¡Bienvenido! ¿Qué vas a llevar?"
        self.objeto_tienda = Equipamiento("Espada Maestra", 15, 5, 150, 75)
        
        self.posicion_jugador_x = 50 
        self.posicion_jugador_y = ((ALTO_VENTANA - 60) // 2) - (TAMANO_CELDA // 2)
        self.frame_index_anim = 0
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
            esc = (TAMANO_CELDA, TAMANO_CELDA) 
            # Héroe
            self.anim_heroe_idle = self._recortar_hoja_sprites(os.path.join("assets", "Heroe", "Soldier", "Soldier-Idle.png"), esc)
            self.anim_heroe_walk = self._recortar_hoja_sprites(os.path.join("assets", "Heroe", "Soldier", "Soldier-Walk.png"), esc)
            self.anim_heroe_attack = self._recortar_hoja_sprites(os.path.join("assets", "Heroe", "Soldier", "Soldier-Attack01.png"), esc)
            # Enemigo
            self.anim_enemigo_idle = self._recortar_hoja_sprites(os.path.join("assets", "Enemigo", "Orc", "Orc-Idle.png"), esc)
            self.anim_enemigo_attack = self._recortar_hoja_sprites(os.path.join("assets", "Enemigo", "Orc", "Orc-Attack01.png"), esc)
            # Suelo
            self.imagen_suelo = pygame.transform.scale(pygame.image.load(os.path.join("assets", "Suelo", "Grass_Middle.png")).convert(), esc)
            # Objeto
            try: self.imagen_objeto = pygame.transform.scale(pygame.image.load(os.path.join("assets", "Objeto", "item.png")).convert_alpha(), esc)
            except: pass
            
            self.usar_sprites = True
        except Exception as error: 
            print(f"Modo gráfico simplificado. Error: {error}")

    def cargar_sonidos(self):
        self.usar_sonidos = False
        try:
            self.sonido_ataque = pygame.mixer.Sound(os.path.join("assets", "Sonidos", "knifeSlice.ogg"))
            self.sonido_moneda = pygame.mixer.Sound(os.path.join("assets", "Sonidos", "handleCoins.ogg"))
            self.sonido_ataque.set_volume(0.4) 
            self.sonido_moneda.set_volume(0.5)
            self.usar_sonidos = True
        except: 
            print("Jugando en silencio (Sonidos no encontrados).")

    def manejar_eventos(self):
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT: 
                self.corriendo = False
            self.estado_actual.manejar_evento(evento)

    def dibujar_hud_inferior(self):
        if self.estado_actual in [self.estado_menu, self.estado_fin]: 
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
            
        self.reloj.tick(FOTOGRAMAS_POR_SEGUNDO)

    def dibujar(self):
        self.estado_actual.dibujar()
        self.dibujar_hud_inferior()
        pygame.display.flip()

    def salir(self): 
        pygame.quit()