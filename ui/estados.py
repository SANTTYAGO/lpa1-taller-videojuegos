# ui/estados.py
import pygame
import os
from ui.constantes import *
from ui.elementos import TextoFlotante
from core.combate import SistemaCombate
from models.objeto import Equipamiento

class EstadoJuego:
    """Clase base abstracta para definir el comportamiento de cada pantalla."""
    def __init__(self, motor_grafico):
        self.motor = motor_grafico 

    def manejar_evento(self, evento): pass
    def actualizar(self): pass
    def dibujar(self): pass

class EstadoMenuPrincipal(EstadoJuego):
    """Pantalla inicial del juego con estética armoniosa."""
    def manejar_evento(self, evento):
        if evento.type == pygame.KEYDOWN and evento.key == pygame.K_RETURN:
            if self.motor.usar_sonidos:
                pygame.mixer.music.load(os.path.join("assets", "Sonidos", "game soundtrack.mp3"))
                pygame.mixer.music.play(-1)
            self.motor.estado_actual = self.motor.estado_exploracion

    def dibujar(self):
        self.motor.pantalla.fill(COLOR_NEGRO_FONDO)
        
        texto_titulo = self.motor.fuente_gigante.render("La Leyenda de los 17 Girasoles", True, COLOR_GIRASOL_ACENTO)
        posicion_x_titulo = ANCHO_VENTANA // 2 - texto_titulo.get_width() // 2
        self.motor.pantalla.blit(texto_titulo, (posicion_x_titulo, ALTO_VENTANA // 3))
        
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

class EstadoPausa(EstadoJuego):
    """Menú de pausa e inventario detallado con fondo semi-transparente."""
    def manejar_evento(self, evento):
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_ESCAPE or evento.key == pygame.K_i:
                self.motor.estado_actual = self.motor.estado_exploracion

    def dibujar(self):
        self.motor.estado_exploracion.dibujar()
        
        superficie_oscura = pygame.Surface((ANCHO_VENTANA, ALTO_VENTANA))
        superficie_oscura.set_alpha(220) 
        superficie_oscura.fill(COLOR_NEGRO_FONDO)
        self.motor.pantalla.blit(superficie_oscura, (0, 0))

        titulo = self.motor.fuente_gigante.render("Menú de Campamento", True, COLOR_GIRASOL_ACENTO)
        self.motor.pantalla.blit(titulo, (ANCHO_VENTANA // 2 - titulo.get_width() // 2, 50))

        rect_stats = pygame.Rect(100, 150, 250, 300)
        pygame.draw.rect(self.motor.pantalla, COLOR_GRIS_PANEL, rect_stats)
        pygame.draw.rect(self.motor.pantalla, COLOR_BLANCO, rect_stats, 2)

        tit_stats = self.motor.fuente_grande.render("Estadísticas", True, COLOR_BLANCO)
        self.motor.pantalla.blit(tit_stats, (120, 160))

        textos_stats = [
            f"Héroe: {self.motor.heroe.nombre}",
            f"Nivel: {self.motor.heroe.nivel}",
            f"EXP: {self.motor.heroe.experiencia}",
            f"HP: {self.motor.heroe.puntos_vida} / {self.motor.heroe.puntos_vida_max}",
            f"Ataque: {self.motor.heroe.ataque}",
            f"Defensa: {self.motor.heroe.defensa}",
            f"Zonas: {self.motor.heroe.zonas_exploradas}/20"
        ]

        for indice, texto in enumerate(textos_stats):
            render_txt = self.motor.fuente.render(texto, True, COLOR_AMARILLO_MENU)
            self.motor.pantalla.blit(render_txt, (120, 220 + (indice * 30)))

        rect_inv = pygame.Rect(400, 150, 300, 300)
        pygame.draw.rect(self.motor.pantalla, COLOR_GRIS_PANEL, rect_inv)
        pygame.draw.rect(self.motor.pantalla, COLOR_GIRASOL_ACENTO, rect_inv, 2)

        tit_inv = self.motor.fuente_grande.render("Mochila", True, COLOR_BLANCO)
        self.motor.pantalla.blit(tit_inv, (420, 160))

        girasoles_encontrados = sum(1 for item in self.motor.heroe.inventario if "Girasol" in item.nombre)

        txt_girasoles = self.motor.fuente_grande.render(f"Girasoles: {girasoles_encontrados} / 17", True, COLOR_GIRASOL_ACENTO)
        self.motor.pantalla.blit(txt_girasoles, (420, 220))

        txt_items = self.motor.fuente.render(f"Otros objetos: {len(self.motor.heroe.inventario) - girasoles_encontrados}", True, COLOR_BLANCO)
        self.motor.pantalla.blit(txt_items, (420, 280))

        txt_puntos = self.motor.fuente.render(f"Oro (Puntos): {self.motor.heroe.puntaje}", True, (100, 255, 100))
        self.motor.pantalla.blit(txt_puntos, (420, 330))

        instruccion = self.motor.fuente.render("▶ Presiona 'ESC' o 'I' para continuar", True, COLOR_BLANCO)
        self.motor.pantalla.blit(instruccion, (ANCHO_VENTANA // 2 - instruccion.get_width() // 2, ALTO_VENTANA - 80))

class EstadoExploracion(EstadoJuego):
    """Lógica de movimiento por el mapa y transiciones de zonas."""
    def manejar_evento(self, evento):
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_t and self.motor.es_tienda:
                self.motor.estado_actual = self.motor.estado_tienda
                self.motor.mensaje_tienda = "¡Bienvenido! Tengo mercancía de primera."
            elif evento.key == pygame.K_ESCAPE or evento.key == pygame.K_i:
                self.motor.estado_actual = self.motor.estado_pausa

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
        self.motor.posicion_jugador_y = max(0, min(self.motor.posicion_jugador_y, ALTO_VENTANA - 60 - TAMANO_CELDA))
        
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
        
        if self.motor.enemigo_en_zona and self.motor.enemigo_en_zona.esta_vivo():
            if rectangulo_heroe.colliderect(self.motor.rectangulo_enemigo):
                self.motor.estado_actual = self.motor.estado_combate 
                self.motor.turno_actual = "JUGADOR"
                self.motor.mensaje_combate = f"¡Emboscada! {self.motor.enemigo_en_zona.nombre} te ataca."
                self.motor.posicion_jugador_x -= 40 
                self.motor.efecto_combate_activo = None 
                
                if self.motor.usar_sonidos:
                    pygame.mixer.music.load(os.path.join("assets", "Sonidos", "fight soundtrack.ogg"))
                    pygame.mixer.music.play(-1)
                    
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
                        
                self.motor.mundo.zonas[self.motor.indice_zona_actual].objeto = None
                self.motor.objeto_en_zona = None

    def dibujar(self):
        if self.motor.usar_sprites:
            for x in range(0, ANCHO_VENTANA, TAMANO_CELDA):
                for y in range(0, ALTO_VENTANA - 60, TAMANO_CELDA):
                    self.motor.pantalla.blit(self.motor.imagen_suelo, (x, y))
        else: 
            self.motor.pantalla.fill(COLOR_VERDE_PASTO)
            
        if self.motor.es_tienda:
            pygame.draw.rect(self.motor.pantalla, COLOR_MORADO_MERCADER, self.motor.rectangulo_mercader)
            texto_tienda = self.motor.fuente.render("Refugio del Mercader ('T')", True, COLOR_BLANCO)
            self.motor.pantalla.blit(texto_tienda, (ANCHO_VENTANA//2 - texto_tienda.get_width()//2, 160))
            
        if self.motor.objeto_en_zona:
            if self.motor.imagen_objeto: 
                self.motor.pantalla.blit(self.motor.imagen_objeto, self.motor.rectangulo_objeto.topleft)
            else:
                color_obj = (139, 0, 0) if hasattr(self.motor.objeto_en_zona, 'dano_explosion') else COLOR_NARANJA_TESORO
                pygame.draw.rect(self.motor.pantalla, color_obj, self.motor.rectangulo_objeto)
                
        if self.motor.enemigo_en_zona and self.motor.enemigo_en_zona.esta_vivo():
            if self.motor.usar_sprites:
                indice_frame = self.motor.indice_animacion % len(self.motor.anim_enemigo_idle)
                self.motor.pantalla.blit(self.motor.anim_enemigo_idle[indice_frame], self.motor.rectangulo_enemigo.topleft)
            else: 
                pygame.draw.rect(self.motor.pantalla, COLOR_ROJO_ENEMIGO, self.motor.rectangulo_enemigo)
                
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
    """Pantalla de batalla por turnos con vista lateral JRPG e indicadores de daño."""
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
                
                texto_danio = TextoFlotante(f"-{danio}", 500, 150, COLOR_BLANCO, self.motor.fuente_gigante)
                self.motor.textos_flotantes.append(texto_danio)
                
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
                
                texto_danio = TextoFlotante(f"-{danio}", 200, 150, COLOR_ROJO_ENEMIGO, self.motor.fuente_gigante)
                self.motor.textos_flotantes.append(texto_danio)
                
                if not self.motor.heroe.esta_vivo():
                    self.motor.turno_actual = "DERROTA"
                    self.motor.estado_fin.es_victoria = False
                else: 
                    self.motor.turno_actual = "JUGADOR"
                    
        elif self.motor.turno_actual == "VICTORIA":
            if evento.key == pygame.K_RETURN:
                self.motor.heroe.ganar_experiencia(100)
                self.motor.efecto_combate_activo = None
                self.motor.textos_flotantes.clear() 
                
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
                self.motor.textos_flotantes.clear()
                self.motor.estado_actual = self.motor.estado_fin

    def actualizar(self):
        for texto in self.motor.textos_flotantes[:]:
            texto.actualizar()
            if texto.opacidad <= 0:
                self.motor.textos_flotantes.remove(texto)

    def dibujar(self):
        self.motor.pantalla.fill(COLOR_NEGRO_FONDO)
        
        texto_vs = self.motor.fuente_grande.render(f"VS {self.motor.enemigo_en_zona.nombre}", True, COLOR_ROJO_ENEMIGO)
        texto_vida_e = self.motor.fuente.render(f"Vida Enemigo: {self.motor.enemigo_en_zona.puntos_vida}", True, COLOR_BLANCO)
        
        self.motor.pantalla.blit(texto_vs, (ANCHO_VENTANA // 2 - texto_vs.get_width() // 2, 30))
        self.motor.pantalla.blit(texto_vida_e, (ANCHO_VENTANA // 2 - texto_vida_e.get_width() // 2, 80))
        
        if self.motor.usar_sprites:
            tiempo_actual = pygame.time.get_ticks()
            duracion = tiempo_actual - self.motor.tiempo_inicio_efecto
            
            if self.motor.efecto_combate_activo == "HEROE_ATACA" and duracion < 600:
                frame_idx = min(self.motor.indice_animacion, len(self.motor.anim_heroe_attack) - 1)
                img_heroe = self.motor.anim_heroe_attack[frame_idx]
            else:
                frame_idx = self.motor.indice_animacion % len(self.motor.anim_heroe_idle)
                img_heroe = self.motor.anim_heroe_idle[frame_idx]
                
            if self.motor.efecto_combate_activo == "ENEMIGO_ATACA" and duracion < 600:
                frame_idx = min(self.motor.indice_animacion, len(self.motor.anim_enemigo_attack) - 1)
                img_enemigo = self.motor.anim_enemigo_attack[frame_idx]
            else:
                frame_idx = self.motor.indice_animacion % len(self.motor.anim_enemigo_idle)
                img_enemigo = self.motor.anim_enemigo_idle[frame_idx]
                
            self.motor.pantalla.blit(pygame.transform.scale(img_heroe, (192, 192)), (150, 120))
            enemigo_g = pygame.transform.scale(img_enemigo, (192, 192))
            self.motor.pantalla.blit(pygame.transform.flip(enemigo_g, True, False), (450, 120))
            
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

        for texto in self.motor.textos_flotantes:
            texto.dibujar(self.motor.pantalla)

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