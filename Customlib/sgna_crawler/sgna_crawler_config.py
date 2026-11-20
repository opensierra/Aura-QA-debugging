"""
        SGNA_CRAWLER CONFIGURATION MODULE

            INCLUDES OPERATING PARAMETERS AND RULES
            THAT MODIFY OR RESTRICT THE CRAWLER'S BEHAVIOR
"""

from Customlib.sgna_vivotune import BLOCKED, BLOCKED_CLASSES, BLOCKED_LABELS


MAX_DEPTH              = 2                               # Profundidad maxima de exploracion 
SPEED_FACTOR           = 1                               # MUltiplicador de latencias:
                                                         #  parametro ajustable para responder a latencia de respuesta androd 
                                                         #    >1  = slower
                                                         #    <1  = faster
SIMILARITY_THRESHOLD   = 0.85                            # Umbral de similitud 
GHOST_SIMILARITY_THRESHOLD = 0.95                        # Umbral para detectar tap "ghost" (mas estricto que SIMILARITY_THRESHOLD:
                                                          #   comparar screens distintas no es lo mismo que estabilidad de scroll)
MAX_BACK               = 2                               # Reintentos de back para regresar al padre (retry)
MAX_RELAUNCH           = 2                               # Max relaunch allowed


"""                      
        SWIPE FUNTION CONFIGURATION
"""                    
                       
MARGIN_TOP             = 0.30                            # 
MARGIN_BOTTOM          = 0.10                            #
MARGIN_LEFT            = 0.20                            #
MARGIN_RIGHT           = 0.20                            #
DURATION               = 0.3 * SPEED_FACTOR              # Respuesta precalculada (parametro por defecto no llama _wait)


"""
        SLEEPTIME
"""
SLEEP_STABLE           = 0.7
SLEEP_BACK             = 0.3                             # Cualquier parametro de tiempo de repsuesta debe multiplicar por el speed_factor
SLEEP_EXIT             = 0.1
SLEEP_START            = 1.0


"""
        SCREENSHOTS CONFIGURATION
"""
ROOT_NAME              = "0"
ENABLE_CAPTURE         = True                            # Captura de pantalla habilitada por defecto 
SCREENSHOTS_FOLDER     = "Screenshots"                   # Sub folder del output para guardar los screenshots 
MAX_SCROLL             = 15                              # Swipes maximos permitidos


"""
        PROBLEMATIC ITEMS

def filter_blocked(clicklist):
    return [c for c in clicklist
            if c.get("info", {}).get("className", "") not in BLOCKED_CLASSES
            and c.get("info", {}).get("text", "") not in BLOCKED_LABELS
            and c.get("info", {}).get("contentDescription", "") not in BLOCKED_LABELS
            and c.get("info", {}).get("resourceName", "") not in BLOCKED]

"""

def filter_blocked(clicklist):
    filtrados = []
    for c in clicklist:
        info = c.get("info", {})
        # className viene calificado (ej. "android.widget.Switch"), pero
        # BLOCKED_CLASSES se define con el nombre corto (ej. "Switch") -
        # comparar el string completo contra la lista nunca hacía match.
        className = info.get("className", "")
        tipo = className.split(".")[-1] if className else ""

        if tipo in BLOCKED_CLASSES:
            continue
        if info.get("text", "") in BLOCKED_LABELS:
            continue
        if info.get("contentDescription", "") in BLOCKED_LABELS:
            continue
        if info.get("resourceName", "") in BLOCKED:
            continue
        filtrados.append(c)

    return filtrados