"""
Crawler de exploración automática de apps Android vía uiautomator2.
Recorre en profundidad los elementos clickeables de una app, guardando
por cada nodo un .txt legible, un .json estructurado y un manifest.json
incremental del árbol completo.
"""

import os
import re
import json
import time
import logging
from datetime import datetime
from lxml import etree
import uiautomator2 as u2

from Customlib.sgna_graph import generate_graph

_MAPS_REACHED = {"explored", "leaf_depth_limit", "broken_state"}

from .sgna_crawler_config import (
    MAX_DEPTH, SPEED_FACTOR, SIMILARITY_THRESHOLD, SLEEP_STABLE,        # Operation
    SLEEP_BACK, SLEEP_START, SLEEP_EXIT, MAX_RELAUNCH, MAX_BACK,
    GHOST_SIMILARITY_THRESHOLD,
    MARGIN_TOP, MARGIN_BOTTOM, MARGIN_LEFT, MARGIN_RIGHT, DURATION,     # FUNCTION SWIPE
    ROOT_NAME, ENABLE_CAPTURE, MAX_SCROLL,                              # CAPTURA DE PANTALLA
    filter_blocked                                                      # FUNCTION
    )

logger = logging.getLogger(__name__)


class Crawler:

    def __init__(self, OUTPUT, speed=SPEED_FACTOR):
        self.OUTPUT = os.path.abspath(OUTPUT)
        self.speed = speed
        self.d = None
        self._manifest_cache = {}  # pkg -> manifest dict, evita releer el .json en cada nodo

    def _wait(self, seconds):
        time.sleep(max(0, seconds * self.speed))

    def _pkg_actual(self):
        r = self.d.app_current()
        if r:
            return r.get("package", "")
        return ""

    # ------------------------------------------------
    #   PREPARACION DE SALIDA
    # ------------------------------------------------

    def _preparar_salida(self):
        os.makedirs(self.OUTPUT, exist_ok=True)

    def _preparar_salida_pkg(self, pkg):
        """
        Crea OUTPUT/{pkg}/nodes/ y OUTPUT/{pkg}/screenshots/ para los
        .json/.txt de cada nodo y las capturas de pantalla.
        """
        os.makedirs(os.path.join(self.OUTPUT, pkg, "nodes"), exist_ok=True)
        os.makedirs(os.path.join(self.OUTPUT, pkg, "screenshots"), exist_ok=True)

    # ------------------------------------------------
    #   TAP // SCREENSHOTS // SWIPE // PRINTS
    # ------------------------------------------------

    def _tap(self, x, y):
        self.d.click(x, y)

    def _back(self):
        self.d.press("back")
        self._wait(SLEEP_BACK)

    def _screenshot(self, pkg, filename):
        self._wait(SLEEP_STABLE)
        path = os.path.join(self.OUTPUT, pkg, "screenshots", filename)
        self.d.screenshot(path)

    def _swipe(self, direction, margin_top=MARGIN_TOP, margin_bottom=MARGIN_BOTTOM, margin_left=MARGIN_LEFT, margin_right=MARGIN_RIGHT, duration=DURATION):
        width, height = self.d.window_size()

        left = int(width * margin_left)
        right = int(width * (1 - margin_right))
        top = int(height * margin_top)
        bottom = int(height * (1 - margin_bottom))

        center_x = (left + right) // 2
        center_y = (top + bottom) // 2

        if direction == "up":
            self.d.swipe(center_x, bottom, center_x, top, duration)
        elif direction == "down":
            self.d.swipe(center_x, top, center_x, bottom, duration)
        elif direction == "left":
            self.d.swipe(right, center_y, left, center_y, duration)
        elif direction == "right":
            self.d.swipe(left, center_y, right, center_y, duration)
        else:
            raise ValueError(f"Dirección inválida: {direction}")

    def _volcar_index(self, pkg):
        shots_dir = os.path.join(self.OUTPUT, pkg, "screenshots")
        index_path = os.path.join(self.OUTPUT, pkg, "screenshots.index")
        tmp_path = index_path + ".tmp"
        with open(tmp_path, "w", encoding="utf-8") as f:
            for s in sorted(os.listdir(shots_dir)):
                if s.endswith(".png"):
                    f.write(f"screenshots/{s}\n")
        os.replace(tmp_path, index_path)

    def _volcar_maps(self, pkg):
        nodes_dir = os.path.join(self.OUTPUT, pkg, "nodes")
        if not os.path.isdir(nodes_dir):
            return

        nodes_out = {}
        for fname in sorted(os.listdir(nodes_dir)):
            if not fname.endswith(".json"):
                continue
            nid = fname[:-5]
            with open(os.path.join(nodes_dir, fname), "r", encoding="utf-8") as f:
                detail = json.load(f)

            node_out = {
                "parent_id": nid.rsplit(".", 1)[0] if "." in nid else None,
                "depth": nid.count("."),
                "status": detail.get("status"),
                "timestamp": detail.get("timestamp"),
                "screenshots": [f"{pkg}/{s}" for s in detail.get("screenshots", [])],
                "actions": {},
            }
            if detail.get("trigger"):
                node_out["trigger"] = detail["trigger"]
            nodes_out[nid] = node_out

        if not nodes_out:
            return

        for nid, node_out in nodes_out.items():
            parent = nodes_out.get(node_out["parent_id"]) if node_out["parent_id"] else None
            if parent is None:
                continue
            parent["actions"][nid.rsplit(".", 1)[1]] = {
                "label": (node_out.get("trigger") or {}).get("label", ""),
                "target": nid,
                "status": node_out["status"],
            }

        maps = {
            "schema_version": 2,
            "generated": datetime.now().isoformat(timespec="seconds"),
            "paquetes": [{
                "paquete": pkg,
                "ok": True,
                "root_status": nodes_out.get("0", {}).get("status"),
            }],
            "nodes": {pkg: nodes_out},
        }

        maps_path = os.path.join(self.OUTPUT, pkg, "maps.json")
        tmp = maps_path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(maps, f, ensure_ascii=False, indent=2)
        os.replace(tmp, maps_path)

    def _cargar_status(self):
        path = os.path.join(self.OUTPUT, ".status")
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return set(line.strip() for line in f if line.strip())
        return set()

    def _marcar_status(self, pkg):
        path = os.path.join(self.OUTPUT, ".status")
        with open(path, "a", encoding="utf-8") as f:
            f.write(f"{pkg}\n")

    def _formatear_clickables(self, clickables):
        """Reduce cada clickable a la tupla (i, label, tipo, desc, res)
        usada tanto para el print de consola como para el .txt del nodo."""
        rows = []
        for i, c in enumerate(clickables, 1):
            info = c.get("info", {})
            className = info.get("className", "")
            tipo = className.split(".")[-1] if className else ""
            label = info.get("text") or info.get("contentDescription") or info.get("resourceName") or ""
            desc = info.get("contentDescription", "")
            res = info.get("resourceName", "")
            rows.append((i, label, tipo, desc, res))
        return rows

    def _imprimir_tabla(self, node_id, depth, clickables):
        print(f"  Node: {node_id} (L{depth})")
        print(f"  Clickables: {len(clickables)}")
        print(f"  Scrollable: {'yes' if self.d(scrollable=True).exists else 'no'}")
        print()

        for i, label, tipo, desc, res in self._formatear_clickables(clickables):
            print(f"  [{i:3}] {label[:34]:<35} {tipo[:14]:<15} {desc[:19]:<20} {res[:14]:<15}")

        print()

    # ------------------------------------------------
    #   CONSTRUCCION Y EXPLORACION DE NODOS
    # ------------------------------------------------

    def _marcar_ocurrencias(self, clickables):
        """
        Le agrega a cada clickable un índice 'occurrence': la posición
        (0-based) entre otros clickables con la misma firma
        (resourceName, contentDescription, text, className) dentro de
        ESTA lectura de pantalla. Sin esto, varios ítems idénticos de un
        RecyclerView/lista (íconos sin label, por ejemplo) colapsaban en
        uno solo al deduplicar, y el resto nunca se exploraba.

        Es una heurística basada en el orden del dump de jerarquía, no una
        identidad real — Android Accessibility no expone IDs únicos por
        ítem de lista.
        """
        vistos = {}
        for c in clickables:
            info = c["info"]
            clave = (info.get("resourceName"), info.get("contentDescription"), info.get("text"), info.get("className"))
            vistos[clave] = vistos.get(clave, 0) + 1
            info["occurrence"] = vistos[clave] - 1
        return clickables

    def _inferir_label(self, node):
        """
        Busca un label para un nodo clickable sin text/content-desc propio.
        Prioriza hijos DIRECTOS antes de bajar a nietos, para evitar
        heredar el texto de un badge o contador anidado que no representa
        al control real.
        """
        directos = list(node)
        for child in directos:
            if child.get("text"):
                return child.get("text"), ""
            if child.get("content-desc"):
                return "", child.get("content-desc")

        for descendant in node.iter():
            if descendant is node or descendant in directos:
                continue
            if descendant.get("text"):
                return descendant.get("text"), ""
            if descendant.get("content-desc"):
                return "", descendant.get("content-desc")

        return "", ""

    def _leer_clickables(self, volatile=False):
        root = etree.fromstring(self.d.dump_hierarchy().encode("utf-8"))
        clickables = []

        for node in root.iter():
            if node.get("clickable") != "true":
                continue

            text = node.get("text", "") or ""
            desc = node.get("content-desc", "") or ""

            if not text and not desc:
                text, desc = self._inferir_label(node)

            info = {
                "text": text,
                "contentDescription": desc,
                "className": node.get("class", ""),
                "resourceName": node.get("resource-id", ""),
            }

            if volatile:
                info["bounds"] = node.get("bounds", "")

            clickables.append({"info": info})

        return self._marcar_ocurrencias(clickables)

    def _calcular_posicion(self, bounds):
        """Única responsabilidad: convertir 'bounds' ("[x1,y1][x2,y2]")
        en el punto central (x, y) para el tap."""
        match = re.match(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]", bounds or "")
        if not match:
            return None

        x1, y1, x2, y2 = map(int, match.groups())
        return (x1 + x2) // 2, (y1 + y2) // 2

    def _encontrar_clickable(self, info):
        swipes = 0
        clave = (
            info.get("resourceName"),
            info.get("contentDescription"),
            info.get("text"),
            info.get("className"),
            info.get("occurrence", 0),
        )
        clave_debil = (info.get("resourceName"), info.get("className"), info.get("occurrence", 0)) if info.get("resourceName") else None

        for _ in range(MAX_SCROLL + 1):
            actuales = self._leer_clickables(volatile=True)
            candidato_debil = None

            for c in actuales:
                ci = c["info"]
                actual = (ci.get("resourceName"), ci.get("contentDescription"), ci.get("text"), ci.get("className"), ci.get("occurrence", 0))

                if actual == clave:
                    pos = self._calcular_posicion(ci.get("bounds", ""))
                    if pos:
                        return pos, True
                elif clave_debil and (ci.get("resourceName"), ci.get("className"), ci.get("occurrence", 0)) == clave_debil:
                    candidato_debil = ci

            if candidato_debil:
                pos = self._calcular_posicion(candidato_debil.get("bounds", ""))
                if pos:
                    logger.info("[EXPLORE] match débil por resourceName=%s occurrence=%s (label cambió)", clave_debil[0], clave_debil[2])
                    return pos, True

            if swipes == MAX_SCROLL:
                break
            self._swipe("up")
            swipes += 1
            # Sin esta espera, la siguiente lectura puede capturar la
            # lista a mitad de la animación de scroll: los 'bounds' no
            # corresponden a la posición final, el tap cae en el lugar
            # equivocado (o en nada) y la pantalla queda scrolleada sin
            # haber navegado a ningún lado.
            self._wait(SLEEP_STABLE)

        for _ in range(swipes):
            self._swipe("down")
        return None, False

    def _eye(self, clickables):
        return {(
            c["info"].get("resourceName"),
            c["info"].get("contentDescription"),
            c["info"].get("text"),
            c["info"].get("className"),)
            for c in clickables
            if c and c.get("info")}

    def _memoria(self, anteriores, actuales, threshold=SIMILARITY_THRESHOLD):
        a = self._eye(anteriores)
        b = self._eye(actuales)

        if not a and not b:
            return False

        similitud = len(a & b) / max(len(a), len(b))
        return similitud > threshold

    def _descubrir_nodo(self, pkg, node_id=ROOT_NAME, max_scroll=MAX_SCROLL, capturar=ENABLE_CAPTURE):
        clickables = []
        screenshots = []
        anteriores = None
        swipes = 0

        if self.d(scrollable=True).exists:
            for swipe in range(max_scroll):
                if anteriores is not None:
                    self._swipe("up")
                    swipes += 1
                    self._wait(SLEEP_STABLE)

                actuales = self._leer_clickables()
                clickables.extend(actuales)

                if anteriores is not None and self._memoria(anteriores, actuales):
                    break

                if capturar:
                    filename = f"{node_id}_{swipe}.png"
                    self._screenshot(pkg, filename)
                    screenshots.append(f"screenshots/{filename}")
                anteriores = actuales

            for _ in range(swipes):
                self._swipe("down")
        else:
            if capturar:
                filename = f"{node_id}.png"
                self._screenshot(pkg, filename)
                screenshots.append(f"screenshots/{filename}")
            clickables = self._leer_clickables()

        clickables = list({
            (c["info"].get("resourceName"), c["info"].get("contentDescription"), c["info"].get("text"), c["info"].get("className"), c["info"].get("occurrence")): c
            for c in clickables if c and c.get("info")
        }.values())
        clickables = filter_blocked(clickables)
        return clickables, screenshots

    def _guardar_nodo(self, pkg, node_id, clickables):
        path = os.path.join(self.OUTPUT, pkg, "nodes", f"{node_id}.txt")
        rows = self._formatear_clickables(clickables)

        w_label = max(len(r[1]) for r in rows) if rows else 0
        w_tipo = max(len(r[2]) for r in rows) if rows else 0
        w_desc = max(len(r[3]) for r in rows) if rows else 0

        with open(path, "w", encoding="utf-8") as f:
            for i, label, tipo, desc, res in rows:
                f.write(f"[{i:3}] {label:<{w_label}} | {tipo:<{w_tipo}} | {desc:<{w_desc}} | {res}\n")

    def _guardar_nodo_json(self, pkg, node_id, parent_id, trigger, status, clickables, screenshots=None):
        """Guarda el nodo en formato estructurado en OUTPUT/{pkg}/nodes/{node_id}.json"""
        path = os.path.join(self.OUTPUT, pkg, "nodes", f"{node_id}.json")
        data = {
            "pkg": pkg,
            "node_id": node_id,
            "parent_id": parent_id,
            "depth": node_id.count("."),
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "trigger": trigger,
            "status": status,
            "screenshots": screenshots or [],
            "clickables": [c["info"] for c in clickables],
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _actualizar_manifest(self, pkg, node_id, parent_id, status):
        """
        Índice liviano del árbol completo del paquete en
        OUTPUT/{pkg}/manifest.json. Se actualiza incrementalmente y se
        escribe a disco en cada nodo (para sobrevivir una interrupción a
        mitad de crawl), pero se mantiene en memoria (self._manifest_cache)
        para no tener que releer el archivo completo en cada llamada.
        """
        path = os.path.join(self.OUTPUT, pkg, "manifest.json")

        manifest = self._manifest_cache.get(pkg)
        if manifest is None:
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    manifest = json.load(f)
            else:
                manifest = {"pkg": pkg, "nodes": {}}
            self._manifest_cache[pkg] = manifest

        manifest["nodes"][node_id] = {
            "parent_id": parent_id,
            "children": manifest["nodes"].get(node_id, {}).get("children", []),
            "status": status,
        }
        if parent_id and parent_id in manifest["nodes"]:
            hijos = manifest["nodes"][parent_id]["children"]
            if node_id not in hijos:
                hijos.append(node_id)

        tmp = path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(manifest, f, ensure_ascii=False, indent=2)
        os.replace(tmp, path)

    def _cerrar_nodo(self, pkg, node_id, parent_id, trigger, status, clickables, screenshots):
        """Agrupa el par guardar_nodo_json + actualizar_manifest que se
        repetía en cada salida de _explorar_nodo / _intentar_click."""
        self._guardar_nodo_json(pkg, node_id, parent_id, trigger, status, clickables, screenshots)
        self._actualizar_manifest(pkg, node_id, parent_id, status)

    def _asegurar_back(self, pkg, parent_visible, max_back=MAX_BACK, max_relaunch=MAX_RELAUNCH):
        """
        Retorna (ok, relanzado):
        (True,  False) -> back normal confirmado contra parent_visible
        (True,  True)  -> hubo que relanzar; el estado real es ROOT_NAME, NO parent_visible
        (False, False) -> no se pudo recuperar ningún estado conocido
        """
        # Antes de presionar nada: ¿ya estamos en parent_visible? Sin este
        # chequeo, cada ancestro que llama a esta función presiona "back" a
        # ciegas incluso cuando el dispositivo YA está exactamente en la
        # pantalla esperada. Eso pasa en concreto justo después de que un
        # descendiente haya tenido que relanzar: el relanzamiento deja al
        # dispositivo parado en ROOT_NAME, y si el ancestro que pregunta es
        # precisamente el nodo raíz (o cualquiera cuyo parent_visible
        # coincide con la pantalla actual), presionar "back" de todos modos
        # saca de la app, falla la comparación, y fuerza un SEGUNDO
        # relanzamiento que no hacía falta — amplificando en cadena la
        # pérdida de cobertura de un único relanzamiento real.
        if self._memoria(parent_visible, self._leer_clickables()):
            return True, False

        for _ in range(max_back):
            self._back()
            actual = self._leer_clickables()
            if self._memoria(parent_visible, actual):
                return True, False

        for _ in range(max_relaunch):
            self.d.app_stop(pkg)
            result = self.d.shell(f"monkey -p {pkg} -c android.intent.category.LAUNCHER 1")
            if result.exit_code != 0:
                continue

            self._wait(SLEEP_START)

            # No confiar ciegamente en exit_code == 0: verificar que el
            # paquete quedó realmente en foreground y que la pantalla
            # tiene contenido interactivo antes de darlo por recuperado.
            if self._pkg_actual() != pkg:
                logger.warning("[RECOVER] relanzamiento reportó éxito pero %s no quedó en foreground", pkg)
                continue

            actual = self._leer_clickables()
            if not actual:
                logger.warning("[RECOVER] %s relanzado pero sin clickables visibles, estado sospechoso", pkg)
                continue

            return True, True

        return False, False

    def _intentar_click(self, pkg, c, child_id, i, clickables):
        """
        Intenta clickear un elemento y determina qué pasó.
        Retorna (status, child_clickables, child_screenshots, parent_visible)
        donde status es uno de:
        "not_found", "left_package", "broken_state", "ghost", "ok"

        parent_visible se captura DESPUÉS de _encontrar_clickable (que
        puede scrollear internamente para localizar el elemento) y ANTES
        del tap — es decir, en la posición de scroll real desde la que se
        hace click, no en la posición inicial del nodo. Esto importa
        porque Android normalmente conserva la posición de scroll de una
        lista al volver con "back" (no la resetea al tope); comparar
        contra un parent_visible capturado antes de scrollear produce
        falsos negativos en _asegurar_back aunque el back haya funcionado.
        """
        info = c["info"]
        label = info.get("text") or info.get("contentDescription") or info.get("resourceName") or ""

        pos, found = self._encontrar_clickable(info)
        if not found:
            logger.debug("[EXPLORE] [%3d] NOT FOUND: %s", i, label[:40])
            return "not_found", [], [], None

        parent_visible = self._leer_clickables()

        logger.debug("[EXPLORE] [%3d] found at %s, tapping: %s", i, pos, label[:40])
        self._tap(*pos)
        self._wait(SLEEP_START)

        #if self._pkg_actual() != pkg:
        #    logger.info("[EXPLORE] [%3d] salió de %s (ahora en %s), recuperando", i, pkg, self._pkg_actual())
        #    ok, relanzado = self._asegurar_back(pkg, parent_visible)
        #    if relanzado or not ok:
        #        return "broken_state", [], [], parent_visible
        #    return "left_package", [], [], parent_visible

        child_clickables, child_screenshots = self._descubrir_nodo(pkg, child_id)
        is_ghost = self._memoria(clickables, child_clickables, threshold=GHOST_SIMILARITY_THRESHOLD)
        if is_ghost:
            logger.debug("[EXPLORE] [%3d] GHOST, continuing (no back)", i)
            return "ghost", child_clickables, child_screenshots, parent_visible

        return "ok", child_clickables, child_screenshots, parent_visible

    def _explorar_nodo(self, pkg, node_id, depth=MAX_DEPTH, clickables=None, screenshots=None, parent_id=None, trigger=None):
        logger.debug("[EXPLORE] enter node=%s depth=%s", node_id, depth)
        if clickables is None:
            clickables, screenshots = self._descubrir_nodo(pkg, node_id)
            logger.debug("[EXPLORE] discovered %d clickables", len(clickables))
        screenshots = screenshots or []
        self._imprimir_tabla(node_id, depth, clickables)
        self._guardar_nodo(pkg, node_id, clickables)

        if depth + 1 >= MAX_DEPTH:
            logger.debug("[EXPLORE] depth limit reached (%d+1 >= %d)", depth, MAX_DEPTH)
            self._cerrar_nodo(pkg, node_id, parent_id, trigger, "leaf_depth_limit", clickables, screenshots)
            return True

        for i, c in enumerate(clickables, 1):
            child_id = f"{node_id}.{i}"
            info = c["info"]
            child_trigger = {
                "index": i,
                "label": info.get("text") or info.get("contentDescription") or info.get("resourceName") or "",
                "text": info.get("text"),
                "contentDescription": info.get("contentDescription"),
                "className": info.get("className"),
                "resourceName": info.get("resourceName"),
            }

            # parent_visible ya NO se precalcula aquí: _intentar_click lo
            # captura internamente, después de que _encontrar_clickable
            # termine de scrollear y justo antes del tap. Ver el docstring
            # de _intentar_click para el porqué.
            status, child_clickables, child_screenshots, parent_visible = self._intentar_click(pkg, c, child_id, i, clickables)

            if status == "not_found":
                self._cerrar_nodo(pkg, child_id, node_id, child_trigger, "not_found", [], [])
                continue

            if status == "broken_state":
                logger.warning("[EXPLORE] [%3d] estado no recuperable, abortando %s", i, node_id)
                self._cerrar_nodo(pkg, node_id, parent_id, trigger, "broken_state", clickables, screenshots)
                return False

            if status == "left_package":
                logger.info("[EXPLORE] [%3d] recuperado, %s quedó fuera de %s", i, child_id, pkg)
                self._cerrar_nodo(pkg, child_id, node_id, child_trigger, "left_package", [], [])
                continue

            if status == "ghost":
                self._cerrar_nodo(pkg, child_id, node_id, child_trigger, "ghost", child_clickables, child_screenshots)
                continue

            # status == "ok" -> recursar
            logger.debug("[EXPLORE] [%3d] recursing into %s (depth %d)", i, child_id, depth + 1)
            child_ok = self._explorar_nodo(pkg, child_id, depth + 1, clickables=child_clickables, screenshots=child_screenshots, parent_id=node_id, trigger=child_trigger)

            if not child_ok:
                logger.warning("[EXPLORE] [%3d] hijo reportó estado roto, abortando %s también", i, node_id)
                self._cerrar_nodo(pkg, node_id, parent_id, trigger, "broken_state", clickables, screenshots)
                return False

            ok, relanzado = self._asegurar_back(pkg, parent_visible)
            if relanzado:
                # El back NO falló: _asegurar_back sí recuperó un estado
                # válido (tuvo que relanzar la app, pero confirmó foreground
                # + clickables). Antes esto se trataba como un error fatal:
                # se marcaba "broken_state" y se hacía return False, lo que
                # obligaba a CADA ancestro hacia arriba a también abortar en
                # cascada (return False -> el padre lo ve como "hijo roto"
                # -> también aborta -> así hasta la raíz), deteniendo toda
                # la exploración restante del paquete por un solo
                # relanzamiento en cualquier punto del árbol.
                #
                # La posición real tras relanzar es ROOT_NAME, no
                # parent_visible, así que sí hay que abandonar el resto de
                # los HERMANOS de este nodo (no hay forma de saber si están
                # en la misma posición de scroll). Pero eso no significa que
                # el padre también deba abortar: se trata igual que "not ok"
                # -> se corta el loop de ESTE nodo, se cierra normalmente y
                # el padre sigue su propio flujo sin heredar un fallo que no
                # es tal.
                logger.warning("[EXPLORE] [%3d] tocó relanzar (estado real = %s), se descartan hermanos restantes de %s", i, ROOT_NAME, node_id)
                break
            if not ok:
                logger.warning("[EXPLORE] [%3d] BRANCH DISCARDED, stopping", i)
                break

        logger.debug("[EXPLORE] exit node=%s depth=%s", node_id, depth)
        self._cerrar_nodo(pkg, node_id, parent_id, trigger, "explored", clickables, screenshots)
        return True

    # ------------------------------------------------
    #   CRAWLER
    # ------------------------------------------------

    def crawlear(self, package_list):
        self.d = u2.connect()
        self.d.shell("input keyevent KEYCODE_WAKEUP")
        self._preparar_salida()
        status = self._cargar_status()

        for pkg, _ in package_list:
            if pkg in status:
                continue

            try:
                self.d.app_stop(pkg)
                self._wait(SLEEP_EXIT)
                result = self.d.shell(f"monkey -p {pkg} -c android.intent.category.LAUNCHER 1")
            except Exception as e:
                # NOTA: antes esto hacía 'continue' sin marcar status, así
                # que un fallo de app_stop reintentaba el paquete en cada
                # corrida (potencial loop infinito). Ahora se marca igual
                # que un fallo de lanzamiento, para que el comportamiento
                # sea consistente. Si prefieres reintentar estos casos con
                # un límite, avísame y lo agrego con un contador aparte.
                logger.error("ERROR %s: %s: %s", pkg, type(e).__name__, e)
                self._marcar_status(pkg)
                continue

            if result.exit_code == 0:
                logger.info("OK   %-35s", pkg)
                self._preparar_salida_pkg(pkg)
                self._wait(SLEEP_START)
                self._explorar_nodo(pkg, ROOT_NAME, 0)
                self._volcar_index(pkg)
                self._volcar_maps(pkg)
                try:
                    generate_graph(self.OUTPUT, pkg)
                except Exception as e:
                    logger.error("ERROR graph %s: %s: %s", pkg, type(e).__name__, e)
            else:
                reason = next(
                    (line.strip() for line in result.output.splitlines()
                     if line.strip().startswith("**")),
                    "launch failed"
                )
                logger.warning("SKIP %-35s | %-20s", pkg, reason)

            self._manifest_cache.pop(pkg, None)
            self._marcar_status(pkg)