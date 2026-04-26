# core/combate.py
import random
# Necesitamos saber si el personaje es un Pícaro para el golpe crítico
from models.personaje import Picaro 

class HabilidadCombate:
    """Clase Base (Interfaz) para cualquier tipo de habilidad en combate"""
    def __init__(self, nombre, costo_mp=0):
        self.nombre = nombre
        self.costo_mp = costo_mp

    def ejecutar(self, atacante, defensor):
        raise NotImplementedError("Este método debe ser sobrescrito por las clases hijas.")


class AtaqueBasico(HabilidadCombate):
    """Ataque normal sin costo. Resta defensa directamente."""
    def __init__(self):
        super().__init__("Ataque Básico", costo_mp=0)

    def ejecutar(self, atacante, defensor):
        variacion = random.randint(-2, 2)
        dano_base = atacante.ataque - defensor.defensa + variacion
        
        # --- NUEVO: Mecánica de Crítico para Pícaro ---
        es_critico = False
        if isinstance(atacante, Picaro) and random.random() < 0.25:
            dano_base *= 2
            es_critico = True

        dano = max(1, dano_base)
        
        # Guardamos si el defensor recibió el golpe o lo esquivó
        golpe_acertado = defensor.recibir_dano(dano)
        
        if not golpe_acertado:
            return 0, f"¡{defensor.nombre} ESQUIVÓ el ataque!"
            
        msg = f"¡{atacante.nombre} ataca! Causa {dano} pts."
        if es_critico:
            msg = "¡GOLPE CRÍTICO! " + msg
            
        return dano, msg


class GolpeEspecial(HabilidadCombate):
    """Ataque poderoso. Consume MP y puede causar ATURDIMIENTO."""
    def __init__(self):
        super().__init__("Golpe Feroz", costo_mp=15)

    def ejecutar(self, atacante, defensor):
        atacante.puntos_magia -= self.costo_mp
        dano_base = atacante.ataque * 1.8
        dano = max(5, int(dano_base - (defensor.defensa * 0.4))) 
        
        golpe_acertado = defensor.recibir_dano(dano)
        if not golpe_acertado:
            return 0, f"¡{defensor.nombre} esquivó el golpe especial!"
        
        msg = f"¡{atacante.nombre} usa {self.nombre}! Causa {dano} pts."
        
        if random.random() < 0.30:
            defensor.aplicar_estado("aturdido", 1) 
            msg += " ¡El enemigo quedó ATURDIDO!"
            
        return dano, msg


class Curacion(HabilidadCombate):
    """Magia defensiva. Consume mucho MP pero restaura HP."""
    def __init__(self):
        super().__init__("Luz Sanadora", costo_mp=20)

    def ejecutar(self, atacante, defensor):
        atacante.puntos_magia -= self.costo_mp
        cura = 30 + (atacante.nivel * 10)
        atacante.puntos_vida = min(atacante.puntos_vida_max, atacante.puntos_vida + cura)
        return 0, f"¡{atacante.nombre} usa {self.nombre}! Recupera {cura} HP."


class AtaqueEnemigo(HabilidadCombate):
    """Ataque que usa la IA, tiene probabilidad de causar VENENO."""
    def __init__(self):
        super().__init__("Ataque Tóxico", costo_mp=0)

    def ejecutar(self, atacante, defensor):
        variacion = random.randint(-2, 2)
        dano = max(1, atacante.ataque - defensor.defensa + variacion)
        
        golpe_acertado = defensor.recibir_dano(dano)
        if not golpe_acertado:
            return 0, f"¡Esquivaste ágilmente el ataque de {atacante.nombre}!"
        
        msg = f"¡{atacante.nombre} ataca! Causa {dano} pts."
        
        if random.random() < 0.25:
            defensor.aplicar_estado("veneno", 3) 
            msg += " ¡Te ha ENVENENADO!"
            
        return dano, msg