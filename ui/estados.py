# ui/estados.py
import pygame
import os
import math
import random
from ui.constantes import *
from ui.elementos import TextoFlotante
from core.combate import AtaqueBasico, GolpeEspecial, Curacion, AtaqueEnemigo
from models.objeto import Equipamiento, Consumible, Tesoro, Trampa 

OFFSET_X = (ESCALA_PERSONAJE - TAMANO_CELDA) // 2
OFFSET_Y = ESCALA_PERSONAJE - TAMANO_CELDA
COLOR_VENENO = (148, 0, 211)

class EstadoJuego:
    def __init__(self, motor_grafico): self.motor = motor_grafico 
    def manejar_evento(self, evento): pass
    def actualizar(self): pass
    def dibujar(self): pass

class EstadoMenuPrincipal(EstadoJuego):
    def __init__(self, motor_grafico):
        super().__init__(motor_grafico)
        self.opciones = ["Nueva Aventura", "Cargar Partida"]
        self.opcion_seleccionada = 0
        self.mensaje_error = ""

    def manejar_evento(self, evento):
        if evento.type == pygame.KEYDOWN:
            self.mensaje_error = ""
            if evento.key == pygame.K_UP: self.opcion_seleccionada = (self.opcion_seleccionada - 1) % len(self.opciones)
            elif evento.key == pygame.K_DOWN: self.opcion_seleccionada = (self.opcion_seleccionada + 1) % len(self.opciones)
            elif evento.key == pygame.K_RETURN:
                if self.opcion_seleccionada == 0:
                    if self.motor.usar_sonidos:
                        pygame.mixer.music.load(os.path.join("assets", "Sonidos", "game soundtrack.mp3"))
                        pygame.mixer.music.play(-1)
                    self.motor.estado_actual = self.motor.estado_exploracion
                elif self.opcion_seleccionada == 1:
                    exito = self.motor.cargar_partida()
                    if exito:
                        if self.motor.usar_sonidos:
                            pygame.mixer.music.load(os.path.join("assets", "Sonidos", "game soundtrack.mp3"))
                            pygame.mixer.music.play(-1)
                        self.motor.estado_actual = self.motor.estado_exploracion
                    else:
                        self.mensaje_error = "¡No hay ninguna partida guardada!"

    def dibujar(self):
        self.motor.pantalla.fill(COLOR_NEGRO_FONDO)
        texto_titulo = self.motor.fuente_gigante.render(TITULO_JUEGO, True, COLOR_GIRASOL_ACENTO)
        self.motor.pantalla.blit(texto_titulo, (ANCHO_VENTANA // 2 - texto_titulo.get_width() // 2, ALTO_VENTANA // 4))
        
        for i, opcion in enumerate(self.opciones):
            color = COLOR_GIRASOL_ACENTO if i == self.opcion_seleccionada else COLOR_BLANCO
            marcador = "> " if i == self.opcion_seleccionada else "  "
            texto_render = self.motor.fuente_grande.render(f"{marcador}{opcion}", True, color)
            self.motor.pantalla.blit(texto_render, (ANCHO_VENTANA // 2 - 120, ALTO_VENTANA // 2 + (i * 60)))
            
        if self.mensaje_error:
            txt_err = self.motor.fuente.render(self.mensaje_error, True, COLOR_ROJO_ENEMIGO)
            self.motor.pantalla.blit(txt_err, (ANCHO_VENTANA // 2 - txt_err.get_width() // 2, ALTO_VENTANA - 80))

class EstadoFinJuego(EstadoJuego):
    def __init__(self, motor_grafico):
        super().__init__(motor_grafico)
        self.es_victoria = False 

    def manejar_evento(self, evento):
        if evento.type == pygame.KEYDOWN and evento.key == pygame.K_RETURN: self.motor.corriendo = False 

    def dibujar(self):
        self.motor.pantalla.fill(COLOR_NEGRO_FONDO)
        if self.es_victoria:
            texto_principal = self.motor.fuente_gigante.render("¡VICTORIA SUPREMA!", True, COLOR_GIRASOL_ACENTO)
            texto_secundario = self.motor.fuente.render("El Rey Demonio ha caido. El mundo esta a salvo.", True, COLOR_BLANCO)
        else:
            texto_principal = self.motor.fuente_gigante.render("FIN DEL JUEGO", True, COLOR_ROJO_ENEMIGO)
            texto_secundario = self.motor.fuente.render("Tu viaje ha terminado en la derrota...", True, COLOR_BLANCO)
            
        texto_salir = self.motor.fuente.render("Presiona ENTER para salir", True, COLOR_GRIS_PANEL)
        self.motor.pantalla.blit(texto_principal, (ANCHO_VENTANA // 2 - texto_principal.get_width() // 2, ALTO_VENTANA // 3))
        self.motor.pantalla.blit(texto_secundario, (ANCHO_VENTANA // 2 - texto_secundario.get_width() // 2, ALTO_VENTANA // 2))
        self.motor.pantalla.blit(texto_salir, (ANCHO_VENTANA // 2 - texto_salir.get_width() // 2, ALTO_VENTANA - 100))

class EstadoPausa(EstadoJuego):
    def __init__(self, motor_grafico):
        super().__init__(motor_grafico)
        self.opciones = ["Guardar Partida", "Musica", "Efectos (SFX)", "Pantalla Completa", "Volver al Juego", "Salir del Juego"]
        self.opcion_seleccionada = 0
        self.mensaje_guardado = ""

    def manejar_evento(self, evento):
        if evento.type == pygame.KEYDOWN:
            self.mensaje_guardado = ""
            if evento.key == pygame.K_ESCAPE: 
                self.motor.estado_actual = self.motor.estado_exploracion
            elif evento.key == pygame.K_UP: 
                self.opcion_seleccionada = (self.opcion_seleccionada - 1) % len(self.opciones)
            elif evento.key == pygame.K_DOWN: 
                self.opcion_seleccionada = (self.opcion_seleccionada + 1) % len(self.opciones)
            elif evento.key == pygame.K_LEFT:
                if self.opcion_seleccionada == 1: self.motor.ajustar_volumen_musica(-0.1)
                elif self.opcion_seleccionada == 2: self.motor.ajustar_volumen_sfx(-0.1)
            elif evento.key == pygame.K_RIGHT:
                if self.opcion_seleccionada == 1: self.motor.ajustar_volumen_musica(0.1)
                elif self.opcion_seleccionada == 2: self.motor.ajustar_volumen_sfx(0.1)
            elif evento.key == pygame.K_RETURN:
                if self.opcion_seleccionada == 0:
                    if self.motor.guardar_partida(): self.mensaje_guardado = "¡Partida Guardada!"
                    else: self.mensaje_guardado = "¡Error al guardar!"
                elif self.opcion_seleccionada == 3: self.motor.alternar_pantalla_completa()
                elif self.opcion_seleccionada == 4: self.motor.estado_actual = self.motor.estado_exploracion
                elif self.opcion_seleccionada == 5: self.motor.corriendo = False

    def dibujar(self):
        self.motor.estado_exploracion.dibujar()
        superficie_oscura = pygame.Surface((ANCHO_VENTANA, ALTO_VENTANA))
        superficie_oscura.set_alpha(220) 
        superficie_oscura.fill(COLOR_NEGRO_FONDO)
        self.motor.pantalla.blit(superficie_oscura, (0, 0))

        titulo = self.motor.fuente_gigante.render("Pausa - Sistema", True, COLOR_GIRASOL_ACENTO)
        self.motor.pantalla.blit(titulo, (ANCHO_VENTANA // 2 - titulo.get_width() // 2, 80))

        rect_config = pygame.Rect(200, 180, 400, 280)
        pygame.draw.rect(self.motor.pantalla, COLOR_GRIS_PANEL, rect_config, border_radius=15)
        pygame.draw.rect(self.motor.pantalla, COLOR_BLANCO, rect_config, 3, border_radius=15)
        
        texto_cabecera = self.mensaje_guardado if self.mensaje_guardado else "Ajustes de Juego"
        color_cabecera = (100, 255, 100) if self.mensaje_guardado else COLOR_BLANCO
        tit_ajustes = self.motor.fuente_grande.render(texto_cabecera, True, color_cabecera)
        self.motor.pantalla.blit(tit_ajustes, (ANCHO_VENTANA // 2 - tit_ajustes.get_width() // 2, 200))

        pygame.draw.line(self.motor.pantalla, COLOR_GIRASOL_ACENTO, (220, 240), (580, 240), 2)

        for i, opcion in enumerate(self.opciones):
            color = COLOR_GIRASOL_ACENTO if i == self.opcion_seleccionada else COLOR_BLANCO
            marcador = "> " if i == self.opcion_seleccionada else "  "
            if i == 0: texto = f"{marcador}Guardar Progreso"
            elif i == 1: texto = f"{marcador}Musica: {int(self.motor.volumen_musica * 100)}%"
            elif i == 2: texto = f"{marcador}Efectos SFX: {int(self.motor.volumen_sfx * 100)}%"
            elif i == 3: estado_pant = "Completa" if self.motor.pantalla_completa else "Ventana"; texto = f"{marcador}Pantalla: {estado_pant}"
            elif i == 4: texto = f"{marcador}Volver al Juego"
            elif i == 5: texto = f"{marcador}Salir del Juego"
            self.motor.pantalla.blit(self.motor.fuente.render(texto, True, color), (250, 260 + (i * 30)))

# =======================================================
# NUEVO: INVENTARIO MEJORADO CON EQUIPAMIENTO
# =======================================================
class EstadoInventario(EstadoJuego):
    def __init__(self, motor_grafico):
        super().__init__(motor_grafico)
        self.cursor_inventario = 0

    def manejar_evento(self, evento):
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_ESCAPE or evento.key == pygame.K_i: 
                self.motor.estado_actual = self.motor.estado_exploracion
            else:
                inventario_actual = self.motor.heroe.inventario
                if evento.key == pygame.K_UP and len(inventario_actual) > 0:
                    self.cursor_inventario = (self.cursor_inventario - 1) % len(inventario_actual)
                elif evento.key == pygame.K_DOWN and len(inventario_actual) > 0:
                    self.cursor_inventario = (self.cursor_inventario + 1) % len(inventario_actual)
                elif evento.key == pygame.K_RETURN and len(inventario_actual) > 0:
                    objeto_seleccionado = inventario_actual[self.cursor_inventario]
                    
                    if isinstance(objeto_seleccionado, Consumible):
                        objeto_seleccionado.usar(self.motor.heroe) 
                        self.motor.heroe.inventario.remove(objeto_seleccionado) 
                        if self.motor.usar_sonidos: self.motor.sonido_moneda.play()
                    
                    elif isinstance(objeto_seleccionado, Equipamiento):
                        self.motor.heroe.equipar(objeto_seleccionado)
                        if self.motor.usar_sonidos: self.motor.sonido_ataque.play()

                    if self.cursor_inventario >= len(self.motor.heroe.inventario):
                        self.cursor_inventario = max(0, len(self.motor.heroe.inventario) - 1)

    def dibujar(self):
        self.motor.estado_exploracion.dibujar()
        superficie_oscura = pygame.Surface((ANCHO_VENTANA, ALTO_VENTANA))
        superficie_oscura.set_alpha(230) 
        superficie_oscura.fill((20, 20, 30)) 
        self.motor.pantalla.blit(superficie_oscura, (0, 0))

        titulo = self.motor.fuente_gigante.render("Perfil e Inventario", True, COLOR_GIRASOL_ACENTO)
        self.motor.pantalla.blit(titulo, (ANCHO_VENTANA // 2 - titulo.get_width() // 2, 30))

        # --- PANEL IZQUIERDO: Estadísticas y Equipo Activo ---
        rect_stats = pygame.Rect(40, 100, 360, 440)
        pygame.draw.rect(self.motor.pantalla, COLOR_NEGRO_FONDO, rect_stats, border_radius=10)
        pygame.draw.rect(self.motor.pantalla, COLOR_AZUL_HEROE, rect_stats, 3, border_radius=10)
        
        self.motor.pantalla.blit(self.motor.fuente_grande.render("Estadisticas", True, COLOR_BLANCO), (60, 115))
        pygame.draw.line(self.motor.pantalla, COLOR_AZUL_HEROE, (60, 150), (380, 150), 2)
        
        textos_stats = [
            f"Nivel: {self.motor.heroe.nivel}  (EXP: {self.motor.heroe.experiencia}/100)",
            f"Vida: {self.motor.heroe.puntos_vida}/{self.motor.heroe.puntos_vida_max} | Mana: {self.motor.heroe.puntos_magia}/{self.motor.heroe.puntos_magia_max}",
            f"Ataque: {self.motor.heroe.ataque} | Defensa: {self.motor.heroe.defensa}",
            f"Oro: {self.motor.heroe.puntaje} pts"
        ]
        for indice, texto in enumerate(textos_stats):
            color = (100, 255, 100) if "Oro" in texto else COLOR_AMARILLO_MENU
            self.motor.pantalla.blit(self.motor.fuente.render(texto, True, color), (60, 160 + (indice * 30)))

        # Cajas visuales de equipo
        self.motor.pantalla.blit(self.motor.fuente_grande.render("Equipo Activo", True, COLOR_BLANCO), (60, 300))
        
        # Caja Arma
        pygame.draw.rect(self.motor.pantalla, (50, 20, 20), pygame.Rect(60, 340, 320, 45), border_radius=5)
        pygame.draw.rect(self.motor.pantalla, (255, 100, 100), pygame.Rect(60, 340, 320, 45), 2, border_radius=5)
        txt_arma = f"Arma: {self.motor.heroe.arma_equipada.nombre}" if self.motor.heroe.arma_equipada else "Arma: (Nada equipado)"
        self.motor.pantalla.blit(self.motor.fuente.render(txt_arma, True, COLOR_BLANCO), (70, 355))

        # Caja Armadura
        pygame.draw.rect(self.motor.pantalla, (20, 40, 60), pygame.Rect(60, 400, 320, 45), border_radius=5)
        pygame.draw.rect(self.motor.pantalla, (100, 200, 255), pygame.Rect(60, 400, 320, 45), 2, border_radius=5)
        txt_armadura = f"Armadura: {self.motor.heroe.armadura_equipada.nombre}" if self.motor.heroe.armadura_equipada else "Armadura: (Nada equipado)"
        self.motor.pantalla.blit(self.motor.fuente.render(txt_armadura, True, COLOR_BLANCO), (70, 415))


        # --- PANEL DERECHO: Mochila interactiva ---
        rect_inv = pygame.Rect(420, 100, 340, 440)
        pygame.draw.rect(self.motor.pantalla, COLOR_NEGRO_FONDO, rect_inv, border_radius=10)
        pygame.draw.rect(self.motor.pantalla, COLOR_GIRASOL_ACENTO, rect_inv, 3, border_radius=10)
        
        self.motor.pantalla.blit(self.motor.fuente_grande.render("Tu Mochila", True, COLOR_BLANCO), (440, 115))
        self.motor.pantalla.blit(self.motor.fuente.render("Usa Flechas y ENTER (Equipar/Usar)", True, COLOR_AMARILLO_MENU), (440, 155))
        pygame.draw.line(self.motor.pantalla, COLOR_GIRASOL_ACENTO, (440, 185), (740, 185), 2)

        inventario = self.motor.heroe.inventario
        if len(inventario) == 0:
            self.motor.pantalla.blit(self.motor.fuente.render("(La mochila esta vacia)", True, (150,150,150)), (440, 200))
        else:
            max_items = min(len(inventario), 8)
            inicio_lista = 0
            if self.cursor_inventario >= 8: inicio_lista = self.cursor_inventario - 7
                
            for i in range(max_items):
                idx_real = inicio_lista + i
                item = inventario[idx_real]
                
                es_sel = (idx_real == self.cursor_inventario)
                color_item = COLOR_BLANCO if es_sel else (150, 150, 150)
                marcador = "> " if es_sel else "  "
                
                if isinstance(item, Equipamiento): tipo_str = "[Arma]" if item.tipo == "arma" else "[Defensa]"
                elif isinstance(item, Consumible): tipo_str = "[Pocion]"
                else: tipo_str = "[Tesoro]"
                
                texto_item = f"{marcador}{tipo_str} {item.nombre}"
                self.motor.pantalla.blit(self.motor.fuente.render(texto_item, True, color_item), (440, 200 + (i * 28)))

# =======================================================
# NUEVO: TIENDA CON PESTAÑAS (COMPRAR / VENDER)
# =======================================================
class EstadoTienda(EstadoJuego):
    def __init__(self, motor_grafico):
        super().__init__(motor_grafico)
        self.pestana = "COMPRAR" # o "VENDER"
        self.cursor_compra = 0
        self.cursor_venta = 0

    def manejar_evento(self, evento):
        if evento.type != pygame.KEYDOWN: return
        if evento.key == pygame.K_ESCAPE or (evento.key == pygame.K_t and self.pestana == "COMPRAR"): 
            self.motor.estado_actual = self.motor.estado_exploracion
            return

        zona = self.motor.mundo.zonas[self.motor.indice_zona_actual]
        inventario = self.motor.heroe.inventario
        
        # Cambiar de Pestaña
        if evento.key == pygame.K_LEFT or evento.key == pygame.K_RIGHT:
            self.pestana = "VENDER" if self.pestana == "COMPRAR" else "COMPRAR"
            self.motor.mensaje_tienda = "¿Que vas a llevar?" if self.pestana == "COMPRAR" else "¡Muestrame tu basura!"
            return

        # Lógica de Pestaña COMPRAR
        if self.pestana == "COMPRAR":
            if evento.key == pygame.K_UP and len(zona.mercancia) > 0: self.cursor_compra = (self.cursor_compra - 1) % len(zona.mercancia)
            elif evento.key == pygame.K_DOWN and len(zona.mercancia) > 0: self.cursor_compra = (self.cursor_compra + 1) % len(zona.mercancia)
            elif evento.key == pygame.K_RETURN and len(zona.mercancia) > 0:
                obj = zona.mercancia[self.cursor_compra]
                if self.motor.heroe.puntaje >= obj.precio_compra:
                    self.motor.heroe.puntaje -= obj.precio_compra
                    if self.motor.usar_sonidos: self.motor.sonido_moneda.play()
                    
                    if isinstance(obj, Equipamiento): self.motor.heroe.recolectar_objeto(Equipamiento(obj.nombre, obj.tipo, obj.aumento_ataque, obj.aumento_defensa, obj.precio_compra, obj.valor_monetario))
                    elif isinstance(obj, Consumible): self.motor.heroe.recolectar_objeto(Consumible(obj.nombre, obj.tipo_restauracion, obj.cantidad, obj.precio_compra))
                    self.motor.mensaje_tienda = f"¡Compraste {obj.nombre}!"
                else: self.motor.mensaje_tienda = "¡No tienes suficiente Oro!"

        # Lógica de Pestaña VENDER
        elif self.pestana == "VENDER":
            if len(inventario) > 0:
                if evento.key == pygame.K_UP: self.cursor_venta = (self.cursor_venta - 1) % len(inventario)
                elif evento.key == pygame.K_DOWN: self.cursor_venta = (self.cursor_venta + 1) % len(inventario)
                elif evento.key == pygame.K_RETURN:
                    obj = inventario[self.cursor_venta]
                    ganancia = obj.valor_monetario
                    if ganancia > 0:
                        self.motor.heroe.puntaje += ganancia
                        inventario.remove(obj)
                        if self.motor.usar_sonidos: self.motor.sonido_moneda.play()
                        self.motor.mensaje_tienda = f"Vendido {obj.nombre} por {ganancia} Oro."
                        if self.cursor_venta >= len(inventario): self.cursor_venta = max(0, len(inventario) - 1)
                    else:
                        self.motor.mensaje_tienda = "Esa basura no vale nada."

    def dibujar(self):
        self.motor.estado_exploracion.dibujar()
        superficie = pygame.Surface((ANCHO_VENTANA, ALTO_VENTANA))
        superficie.set_alpha(235)
        superficie.fill((20, 15, 30)) 
        self.motor.pantalla.blit(superficie, (0, 0))

        # Pestañas Superiores
        color_compra = COLOR_GIRASOL_ACENTO if self.pestana == "COMPRAR" else (100, 100, 100)
        color_venta = COLOR_GIRASOL_ACENTO if self.pestana == "VENDER" else (100, 100, 100)
        self.motor.pantalla.blit(self.motor.fuente_gigante.render("[ COMPRAR ]", True, color_compra), (150, 30))
        self.motor.pantalla.blit(self.motor.fuente_gigante.render("[ VENDER ]", True, color_venta), (450, 30))
        self.motor.pantalla.blit(self.motor.fuente.render("Usa <- y -> para cambiar de pestaña", True, COLOR_BLANCO), (250, 90))

        # Cuadro Central
        rect_main = pygame.Rect(50, 130, 700, 300)
        pygame.draw.rect(self.motor.pantalla, COLOR_GRIS_PANEL, rect_main, border_radius=15)
        pygame.draw.rect(self.motor.pantalla, COLOR_MORADO_MERCADER, rect_main, 3, border_radius=15)
        
        self.motor.pantalla.blit(self.motor.fuente_grande.render(f"Tu Oro: {self.motor.heroe.puntaje}", True, (100, 255, 100)), (70, 150))
        pygame.draw.line(self.motor.pantalla, COLOR_MORADO_MERCADER, (70, 190), (730, 190), 2)

        if self.pestana == "COMPRAR":
            mercancia = self.motor.mundo.zonas[self.motor.indice_zona_actual].mercancia
            for i, obj in enumerate(mercancia):
                color_item = COLOR_BLANCO if i == self.cursor_compra else (150, 150, 150)
                marcador = "> " if i == self.cursor_compra else "  "
                texto = f"{marcador}{obj.nombre}  ..............  {obj.precio_compra} Oro"
                self.motor.pantalla.blit(self.motor.fuente.render(texto, True, color_item), (70, 210 + (i * 35)))
        else:
            inventario = self.motor.heroe.inventario
            if len(inventario) == 0:
                self.motor.pantalla.blit(self.motor.fuente.render("No tienes nada para vender.", True, (150, 150, 150)), (70, 210))
            else:
                max_items = min(len(inventario), 6)
                inicio = max(0, self.cursor_venta - 5) if self.cursor_venta >= 6 else 0
                for i in range(max_items):
                    idx = inicio + i
                    obj = inventario[idx]
                    color_item = COLOR_BLANCO if idx == self.cursor_venta else (150, 150, 150)
                    marcador = "> " if idx == self.cursor_venta else "  "
                    texto = f"{marcador}{obj.nombre}  ..............  + {obj.valor_monetario} Oro"
                    self.motor.pantalla.blit(self.motor.fuente.render(texto, True, color_item), (70, 210 + (i * 35)))

        # Cuadro Inferior Diálogo
        rect_msg = pygame.Rect(50, 450, 700, 100)
        pygame.draw.rect(self.motor.pantalla, COLOR_NEGRO_FONDO, rect_msg, border_radius=10)
        pygame.draw.rect(self.motor.pantalla, COLOR_GIRASOL_ACENTO, rect_msg, 2, border_radius=10)
        
        self.motor.pantalla.blit(self.motor.fuente.render(f"Mercader: \"{self.motor.mensaje_tienda}\"", True, COLOR_BLANCO), (70, 470))
        self.motor.pantalla.blit(self.motor.fuente.render("ENTER: Confirmar | ESC: Salir", True, COLOR_AMARILLO_MENU), (70, 510))

class EstadoExploracion(EstadoJuego):
    def manejar_evento(self, evento):
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_t and self.motor.es_tienda:
                self.motor.estado_actual = self.motor.estado_tienda
                self.motor.mensaje_tienda = "¡Bienvenido! Tengo mercancia de primera."
            elif evento.key == pygame.K_ESCAPE:
                self.motor.estado_actual = self.motor.estado_pausa
            elif evento.key == pygame.K_i:
                self.motor.estado_actual = self.motor.estado_inventario

    def actualizar(self):
        self._procesar_movimiento_heroe()
        if self.motor.enemigo_en_zona and self.motor.enemigo_en_zona.esta_vivo():
            self.motor.enemigo_en_zona.actualizar_ia(self.motor.posicion_jugador_x, self.motor.posicion_jugador_y)
            self.motor.rectangulo_enemigo.x = self.motor.enemigo_en_zona.x
            self.motor.rectangulo_enemigo.y = self.motor.enemigo_en_zona.y
        self._verificar_colisiones_entidades()

    def _procesar_movimiento_heroe(self):
        teclas = pygame.key.get_pressed()
        esta_moviendose = False
        if teclas[pygame.K_LEFT] or teclas[pygame.K_a]: self.motor.posicion_jugador_x -= VELOCIDAD_MOVIMIENTO; self.motor.mirando_izquierda = True; esta_moviendose = True
        if teclas[pygame.K_RIGHT] or teclas[pygame.K_d]: self.motor.posicion_jugador_x += VELOCIDAD_MOVIMIENTO; self.motor.mirando_izquierda = False; esta_moviendose = True
        if teclas[pygame.K_UP] or teclas[pygame.K_w]: self.motor.posicion_jugador_y -= VELOCIDAD_MOVIMIENTO; esta_moviendose = True
        if teclas[pygame.K_DOWN] or teclas[pygame.K_s]: self.motor.posicion_jugador_y += VELOCIDAD_MOVIMIENTO; esta_moviendose = True
        self.motor.accion_actual_heroe = "WALK" if esta_moviendose else "IDLE"
        self.motor.posicion_jugador_y = max(0, min(self.motor.posicion_jugador_y, ALTO_VENTANA - 60 - TAMANO_CELDA))

        if self.motor.posicion_jugador_x > ANCHO_VENTANA - TAMANO_CELDA:
            if self.motor.indice_zona_actual < len(self.motor.mundo.zonas) - 1:
                self.motor.indice_zona_actual += 1; self.motor.cargar_zona(); self.motor.posicion_jugador_x = 0; self.motor.heroe.zonas_exploradas += 1 
            else: self.motor.posicion_jugador_x = ANCHO_VENTANA - TAMANO_CELDA 
        elif self.motor.posicion_jugador_x < 0:
            if self.motor.indice_zona_actual > 0:
                self.motor.indice_zona_actual -= 1; self.motor.cargar_zona(); self.motor.posicion_jugador_x = ANCHO_VENTANA - TAMANO_CELDA 
            else: self.motor.posicion_jugador_x = 0 

    def _verificar_colisiones_entidades(self):
        rectangulo_heroe = pygame.Rect(self.motor.posicion_jugador_x, self.motor.posicion_jugador_y, TAMANO_CELDA, TAMANO_CELDA)
        if self.motor.enemigo_en_zona and self.motor.enemigo_en_zona.esta_vivo():
            if rectangulo_heroe.colliderect(self.motor.rectangulo_enemigo):
                self.motor.estado_actual = self.motor.estado_combate; self.motor.turno_actual = "EVALUAR_JUGADOR"
                self.motor.mensaje_combate = f"¡Emboscada! {self.motor.enemigo_en_zona.nombre} te ataca."
                if self.motor.enemigo_en_zona.x < self.motor.posicion_jugador_x: self.motor.posicion_jugador_x += 40 
                else: self.motor.posicion_jugador_x -= 40
                self.motor.efecto_combate_activo = None 
                if self.motor.usar_sonidos:
                    pygame.mixer.music.load(os.path.join("assets", "Sonidos", "fight soundtrack.ogg")); pygame.mixer.music.play(-1)
                    
        zona_actual = self.motor.mundo.zonas[self.motor.indice_zona_actual]
        objetos_a_eliminar = []
        for obj in zona_actual.objetos:
            rect_obj = pygame.Rect(obj.x, obj.y, TAMANO_CELDA, TAMANO_CELDA)
            if rectangulo_heroe.colliderect(rect_obj):
                if hasattr(obj, 'dano_explosion'):
                    self.motor.heroe.recibir_dano(obj.dano_explosion)
                    if not self.motor.heroe.esta_vivo(): self.motor.estado_fin.es_victoria = False; self.motor.estado_actual = self.motor.estado_fin
                else:
                    self.motor.heroe.recolectar_objeto(obj)
                    if self.motor.usar_sonidos: self.motor.sonido_moneda.play()
                objetos_a_eliminar.append(obj)
        for obj in objetos_a_eliminar: zona_actual.objetos.remove(obj)

    def dibujar(self):
        if self.motor.usar_sprites:
            for x in range(0, ANCHO_VENTANA, TAMANO_CELDA):
                for y in range(0, ALTO_VENTANA - 60, TAMANO_CELDA): self.motor.pantalla.blit(self.motor.imagen_suelo, (x, y))
        else: self.motor.pantalla.fill(COLOR_VERDE_PASTO)
            
        if self.motor.es_tienda:
            if hasattr(self.motor, 'img_tienda') and self.motor.img_tienda:
                self.motor.pantalla.blit(self.motor.img_tienda, (self.motor.rectangulo_mercader.x - (TAMANO_CELDA // 2), self.motor.rectangulo_mercader.y - TAMANO_CELDA))
            else: pygame.draw.rect(self.motor.pantalla, COLOR_MORADO_MERCADER, self.motor.rectangulo_mercader)
            self.motor.pantalla.blit(self.motor.fuente.render("Refugio del Mercader ('T')", True, COLOR_BLANCO), (ANCHO_VENTANA//2 - 100, 100))
            
        for obj in self.motor.mundo.zonas[self.motor.indice_zona_actual].objetos:
            dibujado = False
            if isinstance(obj, Tesoro):
                if obj.valor_monetario > 40 and hasattr(self.motor, 'img_monedas_muchas') and self.motor.img_monedas_muchas: self.motor.pantalla.blit(self.motor.img_monedas_muchas, (obj.x + 16, obj.y + 16)); dibujado = True
                elif hasattr(self.motor, 'img_monedas_pocas') and self.motor.img_monedas_pocas: self.motor.pantalla.blit(self.motor.img_monedas_pocas, (obj.x + 16, obj.y + 16)); dibujado = True
            elif isinstance(obj, Consumible):
                if obj.tipo_restauracion == "HP" and hasattr(self.motor, 'img_pocion_vida') and self.motor.img_pocion_vida: self.motor.pantalla.blit(self.motor.img_pocion_vida, (obj.x + 16, obj.y + 16)); dibujado = True
                elif obj.tipo_restauracion == "MP" and hasattr(self.motor, 'img_pocion_mana') and self.motor.img_pocion_mana: self.motor.pantalla.blit(self.motor.img_pocion_mana, (obj.x + 16, obj.y + 16)); dibujado = True
            elif isinstance(obj, Trampa):
                if hasattr(self.motor, 'img_trampa') and self.motor.img_trampa: self.motor.pantalla.blit(self.motor.img_trampa, (obj.x + 16, obj.y + 16)); dibujado = True
            elif isinstance(obj, Equipamiento):
                if hasattr(self.motor, 'img_hacha') and self.motor.img_hacha: self.motor.pantalla.blit(self.motor.img_hacha, (obj.x + 16, obj.y + 16)); dibujado = True

            if not dibujado:
                if self.motor.imagen_objeto and not isinstance(obj, Tesoro) and not isinstance(obj, Consumible): self.motor.pantalla.blit(self.motor.imagen_objeto, (obj.x, obj.y))
                else:
                    if isinstance(obj, Consumible): pygame.draw.circle(self.motor.pantalla, (0, 200, 255) if obj.tipo_restauracion == "MP" else (255, 50, 50), (obj.x + 32, obj.y + 32), 12)
                    elif hasattr(obj, 'dano_explosion'): pygame.draw.polygon(self.motor.pantalla, (139, 0, 0), [(obj.x+32, obj.y+15), (obj.x+15, obj.y+49), (obj.x+49, obj.y+49)])
                    else: pygame.draw.rect(self.motor.pantalla, COLOR_NARANJA_TESORO, pygame.Rect(obj.x + 16, obj.y + 16, 32, 32))
                
        if self.motor.enemigo_en_zona and self.motor.enemigo_en_zona.esta_vivo():
            if self.motor.usar_sprites:
                anim_orco = self.motor.anim_enemigo_walk if self.motor.enemigo_en_zona.estado_ia == "PERSIGUIENDO" else self.motor.anim_enemigo_idle
                imagen_orco = anim_orco[self.motor.indice_animacion % len(anim_orco)]
                if self.motor.enemigo_en_zona.direccion_patrulla == -1 or (self.motor.enemigo_en_zona.estado_ia == "PERSIGUIENDO" and self.motor.posicion_jugador_x < self.motor.enemigo_en_zona.x): imagen_orco = pygame.transform.flip(imagen_orco, True, False)
                self.motor.pantalla.blit(imagen_orco, (self.motor.rectangulo_enemigo.x - OFFSET_X, self.motor.rectangulo_enemigo.y - OFFSET_Y))
            else: pygame.draw.rect(self.motor.pantalla, COLOR_ROJO_ENEMIGO, self.motor.rectangulo_enemigo)
                
        if self.motor.usar_sprites:
            lista_frames = self.motor.anim_heroe_walk if self.motor.accion_actual_heroe == "WALK" else self.motor.anim_heroe_idle
            imagen_actual = lista_frames[self.motor.indice_animacion % len(lista_frames)]
            if self.motor.mirando_izquierda: imagen_actual = pygame.transform.flip(imagen_actual, True, False)
            self.motor.pantalla.blit(imagen_actual, (self.motor.posicion_jugador_x - OFFSET_X, self.motor.posicion_jugador_y - OFFSET_Y))
        else: pygame.draw.rect(self.motor.pantalla, COLOR_AZUL_HEROE, pygame.Rect(self.motor.posicion_jugador_x, self.motor.posicion_jugador_y, TAMANO_CELDA, TAMANO_CELDA))

        if not self.motor.es_tienda and self.motor.usar_sprites:
            superficie_niebla = pygame.Surface((ANCHO_VENTANA, ALTO_VENTANA), pygame.SRCALPHA)
            superficie_niebla.fill((5, 5, 10, 250)) 
            superficie_niebla.blit(self.motor.imagen_luz, ((self.motor.posicion_jugador_x + 32) - 250, (self.motor.posicion_jugador_y + 32) - 250), special_flags=pygame.BLEND_RGBA_MIN)
            self.motor.pantalla.blit(superficie_niebla, (0, 0))

class EstadoCombate(EstadoJuego):
    def manejar_evento(self, evento):
        if evento.type != pygame.KEYDOWN: return
        if self.motor.turno_actual == "TURNO_PERDIDO_JUGADOR":
            if evento.key == pygame.K_RETURN: self.motor.turno_actual = "EVALUAR_ENEMIGO"
        elif self.motor.turno_actual == "TURNO_PERDIDO_ENEMIGO":
            if evento.key == pygame.K_RETURN: self.motor.turno_actual = "EVALUAR_JUGADOR"
        elif self.motor.turno_actual == "JUGADOR":
            habilidad = None
            if evento.key == pygame.K_a: habilidad = AtaqueBasico()
            elif evento.key == pygame.K_s: habilidad = GolpeEspecial()
            elif evento.key == pygame.K_c: habilidad = Curacion()
                
            if habilidad:
                if self.motor.heroe.puntos_magia < habilidad.costo_mp:
                    self.motor.mensaje_combate = "¡No tienes suficiente Mana (MP) para hacer eso!"
                    return 
                if self.motor.usar_sonidos and evento.key != pygame.K_c: self.motor.sonido_ataque.play()
                self.motor.tiempo_inicio_efecto = pygame.time.get_ticks(); self.motor.indice_animacion = 0 
                danio, msg = habilidad.ejecutar(self.motor.heroe, self.motor.enemigo_en_zona)
                self.motor.mensaje_combate = msg
                
                if danio > 0: self.motor.textos_flotantes.append(TextoFlotante(f"-{danio}", 500, 150, COLOR_BLANCO, self.motor.fuente_gigante))
                elif evento.key == pygame.K_c: self.motor.textos_flotantes.append(TextoFlotante("+HP", 200, 150, (100, 255, 100), self.motor.fuente_gigante))

                self.motor.turno_actual = "VICTORIA" if not self.motor.enemigo_en_zona.esta_vivo() else "EVALUAR_ENEMIGO"
                    
        elif self.motor.turno_actual == "ENEMIGO":
            if evento.key == pygame.K_SPACE:
                self.motor.efecto_combate_activo = "ENEMIGO_ATACA"
                self.motor.tiempo_inicio_efecto = pygame.time.get_ticks(); self.motor.indice_animacion = 0
                danio, msg = AtaqueEnemigo().ejecutar(self.motor.enemigo_en_zona, self.motor.heroe)
                self.motor.mensaje_combate = msg
                self.motor.textos_flotantes.append(TextoFlotante(f"-{danio}", 200, 150, COLOR_ROJO_ENEMIGO, self.motor.fuente_gigante))
                self.motor.turno_actual = "DERROTA" if not self.motor.heroe.esta_vivo() else "EVALUAR_JUGADOR"
                    
        elif self.motor.turno_actual == "VICTORIA":
            if evento.key == pygame.K_RETURN:
                self.motor.heroe.ganar_experiencia(100)
                self.motor.efecto_combate_activo = None
                self.motor.textos_flotantes.clear() 
                
                if self.motor.enemigo_en_zona.nombre == "Rey Demonio":
                    self.motor.estado_fin.es_victoria = True; self.motor.estado_actual = self.motor.estado_fin
                else:
                    probabilidad_loot = random.random()
                    botin = None
                    if probabilidad_loot < 0.25: botin = Consumible("Pocion Menor de Vida", "HP", 50, 30)
                    elif probabilidad_loot < 0.50: botin = Consumible("Pocion Menor de Mana", "MP", 50, 30)
                    elif probabilidad_loot < 0.70: botin = Tesoro("Bolsa de Oro", valor_monetario=random.randint(20, 60))
                    elif probabilidad_loot < 0.75: botin = Equipamiento("Arma de Orco Caido", "arma", 10, 2, 80, 40)
                        
                    if botin:
                        botin.x = self.motor.enemigo_en_zona.x; botin.y = self.motor.enemigo_en_zona.y
                        self.motor.mundo.zonas[self.motor.indice_zona_actual].objetos.append(botin)
                        self.motor.textos_flotantes.append(TextoFlotante("¡Botin Soltado!", self.motor.enemigo_en_zona.x, self.motor.enemigo_en_zona.y - 20, COLOR_AMARILLO_MENU, self.motor.fuente))

                    self.motor.estado_actual = self.motor.estado_exploracion
                    if self.motor.usar_sonidos: pygame.mixer.music.load(os.path.join("assets", "Sonidos", "game soundtrack.mp3")); pygame.mixer.music.play(-1)
                        
        elif self.motor.turno_actual == "DERROTA":
            if evento.key == pygame.K_RETURN:
                self.motor.textos_flotantes.clear(); self.motor.estado_actual = self.motor.estado_fin

    def actualizar(self):
        for texto in self.motor.textos_flotantes[:]:
            texto.actualizar()
            if texto.opacidad <= 0: self.motor.textos_flotantes.remove(texto)

        if self.motor.turno_actual == "EVALUAR_JUGADOR":
            aturdido, mensajes, dano_veneno = self.motor.heroe.procesar_estados()
            if dano_veneno > 0: self.motor.textos_flotantes.append(TextoFlotante(f"-{dano_veneno}", 200, 150, COLOR_VENENO, self.motor.fuente_gigante))
            if mensajes: self.motor.mensaje_combate = " | ".join(mensajes)
            if not self.motor.heroe.esta_vivo(): self.motor.turno_actual = "DERROTA"; self.motor.estado_fin.es_victoria = False
            elif aturdido: self.motor.turno_actual = "TURNO_PERDIDO_JUGADOR"
            else:
                if not mensajes: self.motor.mensaje_combate = "¡Es tu turno! ¿Que vas a hacer?"
                self.motor.turno_actual = "JUGADOR"
                
        elif self.motor.turno_actual == "EVALUAR_ENEMIGO":
            aturdido, mensajes, dano_veneno = self.motor.enemigo_en_zona.procesar_estados()
            if dano_veneno > 0: self.motor.textos_flotantes.append(TextoFlotante(f"-{dano_veneno}", 500, 150, COLOR_VENENO, self.motor.fuente_gigante))
            if mensajes: self.motor.mensaje_combate = "Enemigo: " + " | ".join(mensajes)
            if not self.motor.enemigo_en_zona.esta_vivo(): self.motor.turno_actual = "VICTORIA"
            elif aturdido: self.motor.turno_actual = "TURNO_PERDIDO_ENEMIGO"
            else:
                if not mensajes: self.motor.mensaje_combate = f"¡{self.motor.enemigo_en_zona.nombre} se prepara para atacar!"
                self.motor.turno_actual = "ENEMIGO"

    def dibujar(self):
        self.motor.pantalla.fill(COLOR_NEGRO_FONDO)
        self.motor.pantalla.blit(self.motor.fuente_grande.render(f"VS {self.motor.enemigo_en_zona.nombre}", True, COLOR_ROJO_ENEMIGO), (ANCHO_VENTANA // 2 - 80, 30))
        self.motor.pantalla.blit(self.motor.fuente.render(f"Vida Enemigo: {self.motor.enemigo_en_zona.puntos_vida}", True, COLOR_BLANCO), (ANCHO_VENTANA // 2 - 80, 80))
        
        if self.motor.usar_sprites:
            duracion = pygame.time.get_ticks() - self.motor.tiempo_inicio_efecto
            if self.motor.efecto_combate_activo == "HEROE_ATACA" and duracion < 600: img_heroe = self.motor.anim_heroe_attack[min(self.motor.indice_animacion, len(self.motor.anim_heroe_attack) - 1)]
            else: img_heroe = self.motor.anim_heroe_idle[self.motor.indice_animacion % len(self.motor.anim_heroe_idle)]
                
            if self.motor.efecto_combate_activo == "ENEMIGO_ATACA" and duracion < 600: img_enemigo = self.motor.anim_enemigo_attack[min(self.motor.indice_animacion, len(self.motor.anim_enemigo_attack) - 1)]
            else: img_enemigo = self.motor.anim_enemigo_idle[self.motor.indice_animacion % len(self.motor.anim_enemigo_idle)]
                
            self.motor.pantalla.blit(pygame.transform.scale(img_heroe, (250, 250)), (100, 100))
            self.motor.pantalla.blit(pygame.transform.flip(pygame.transform.scale(img_enemigo, (250, 250)), True, False), (450, 100))
            
            txt_est_h = ", ".join([k.capitalize() for k, v in self.motor.heroe.estados.items() if v > 0])
            if txt_est_h: self.motor.pantalla.blit(self.motor.fuente.render(txt_est_h, True, COLOR_VENENO), (180, 320))
            txt_est_e = ", ".join([k.capitalize() for k, v in self.motor.enemigo_en_zona.estados.items() if v > 0])
            if txt_est_e: self.motor.pantalla.blit(self.motor.fuente.render(txt_est_e, True, COLOR_VENENO), (530, 320))

        rect_mensaje = pygame.Rect(100, 350, 600, 150)
        pygame.draw.rect(self.motor.pantalla, COLOR_GRIS_PANEL, rect_mensaje)
        pygame.draw.rect(self.motor.pantalla, COLOR_AMARILLO_MENU, rect_mensaje, 3)
        self.motor.pantalla.blit(self.motor.fuente.render(self.motor.mensaje_combate, True, COLOR_BLANCO), (120, 370))
        
        if self.motor.turno_actual == "JUGADOR": inst = "[A] Basico | [S] Feroz (-15 MP) | [C] Curar (-20 MP)"; color_inst = COLOR_AMARILLO_MENU
        elif self.motor.turno_actual == "ENEMIGO": inst = "▶ Presiona 'ESPACIO' para recibir ataque"; color_inst = COLOR_AMARILLO_MENU
        elif self.motor.turno_actual == "TURNO_PERDIDO_JUGADOR": inst = "▶ Estas aturdido. Presiona 'ENTER' para pasar turno"; color_inst = COLOR_VENENO
        elif self.motor.turno_actual == "TURNO_PERDIDO_ENEMIGO": inst = "▶ Enemigo aturdido. Presiona 'ENTER' para pasar turno"; color_inst = (100, 255, 100)
        elif self.motor.turno_actual == "VICTORIA": inst = "▶ ¡Victoria! Presiona 'ENTER' para seguir"; color_inst = (100, 255, 100)
        elif self.motor.turno_actual == "DERROTA": inst = "▶ Has caido... Presiona 'ENTER'"; color_inst = COLOR_ROJO_ENEMIGO
        else: inst = ""; color_inst = COLOR_BLANCO
            
        if inst: self.motor.pantalla.blit(self.motor.fuente.render(inst, True, color_inst), (120, 450))
        for texto in self.motor.textos_flotantes: texto.dibujar(self.motor.pantalla)