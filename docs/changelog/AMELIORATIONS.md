# Améliorations pour le Serveur MCP et l'Agent ITk

> **Objectif** : Optimiser le serveur MCP et l'agent pour répondre **efficacement** à des questions sur la base de données MongoDB de production ITk.
> **Contexte** : Le serveur expose ~50 tools pour interagir avec la base, mais leur utilisation peut être optimisée pour améliorer la performance, la maintenabilité et l'expérience utilisateur.

---

## 📋 Table des Matières
1. [Diagnostic Préliminaire](#-diagnostic-préliminaire)
2. [Pistes d'Amélioration par Priorité](#-pistes-damélioration-par-priorité)
   - [🥇 Priorité 1 : Optimiser les Tools Existants](#-priorité-1--optimiser-les-tools-existants)
   - [🥈 Priorité 2 : Ajouter des "Meta-Tools" pour la Découverte](#-priorité-2--ajouter-des-meta-tools-pour-la-découverte)
   - [🥉 Priorité 3 : Optimiser les Requêtes Fréquentes](#-priorité-3--optimiser-les-requêtes-fréquentes)
   - [🏆 Priorité 4 : Améliorer l'Agent (Côté Client)](#-priorité-4--améliorer-lagent-côté-client)
3. [Exemples Concrets d'Amélioration](#-exemples-concrets-damélioration)
4. [Checklist d'Implémentation](#-checklist-dimplémentation)
5. [Recommandations Finales](#-recommandations-finales)
6. [Ressources Utiles](#-ressources-utiles)

---

## 🔍 Diagnostic Préliminaire

D'après l'analyse du codebase, le serveur MCP expose déjà de nombreux tools pour interagir avec la base de données MongoDB, mais plusieurs **points de friction** limitent son efficacité :

| **Problème** | **Conséquence** | **Solution Proposée** |
|--------------|-----------------|-----------------------|
| Tools trop spécifiques (ex: `find_quad_module_by_serial_tool`, `find_bare_module_by_serial_tool`) | Redondance, maintenance lourde, risque d'oubli de mise à jour | **Factoriser** avec des tools génériques + paramètres optionnels |
| Résultats bruts/non structurés (JSON MongoDB brut) | L'agent doit parser manuellement les résultats | **Standardiser les retours** (schémas clairs, champs prévisibles) |
| Pas de "meta-tools" pour découvrir les données | L'agent ne sait pas quelles questions poser ou quelles données sont disponibles | **Ajouter des tools de découverte** (list collections, sample data, schema) |
| Requêtes coûteuses (ex: `find_all_tool` sans filtres) | Timeout, gaspillage de tokens, latence élevée | **Ajouter des limites par défaut**, paginer, suggérer des projections |
| Pas de cache pour les requêtes fréquentes | Latence inutile pour les données souvent accédées | **Cacher les résultats** (ex: métadonnées des components) |
| Descriptions de tools peu explicites | Mauvaise sélection des tools par l'agent, erreurs d'utilisation | **Améliorer les `description`** avec exemples et cas d'usage |

---

## 🚀 Pistes d'Amélioration par Priorité

---

### 🥇 Priorité 1 : Optimiser les Tools Existants *(Impact Immédiat)*

#### 1. Factoriser les Tools Redondants
**Problème** : Plusieurs tools font la même chose pour différents types de composants (`quad_module`, `bare_module`, `flex_pcb`).

**Solution** : Créer des **tools génériques** avec un paramètre `component_type`.

**Exemple de Refactor** :
```python
# AVANT (3 tools séparés)
find_quad_module_by_serial_tool
find_bare_module_by_serial_tool
find_flex_pcb_by_serial_tool

# APRÈS (1 tool unifié)
@mcp_tool
def find_component_by_serial_tool(
    serial_number: str,
    component_type: Optional[str] = None,  # "module", "bare_module", "pcb"
    partial: bool = False,
    limit: int = 5,
) -> List[dict]:
    """Trouve un composant par son numéro de série.
    Args:
        serial_number: Numéro de série (ex: '20UPGM24830846' ou 'Paris0076').
        component_type: Type de composant (optionnel). Si omis, cherche dans tous les types.
        partial: Autorise une recherche partielle (ex: '20UPGM').
        limit: Limite le nombre de résultats.
    Returns:
        Liste de composants avec champs standardisés (id, serialNumber, type, currentStage).
    """
    filter = {"serialNumber": {
        "$regex": f"^{serial_number}" if partial else f"^{serial_number}$", 
        "$options": "i"
    }}
    if component_type:
        filter["componentType"] = component_type
    return list(db.component.find(filter).limit(limit))
```

**Bénéfices** :
- Moins de code à maintenir
- Plus flexible pour l'agent
- Évite les oublis de mise à jour

---

#### 2. Standardiser les Retours des Tools
**Problème** : Certains tools retournent des documents MongoDB bruts, d'autres des champs partiels.

**Solution** : **Toujours retourner un format prévisible** avec :
- Champs **obligatoires** : `_id`, `serialNumber`, `componentType`, `currentStage`
- Champs **optionnels** : `properties`, `children`, `tests` (si demandés via `projection`)

**Fonction utilitaire** :
```python
def standardize_component(doc: dict) -> dict:
    """Standardise un document de composant pour un retour cohérent."""
    return {
        "id": str(doc["_id"]),
        "serialNumber": doc.get("serialNumber"),
        "alternativeId": doc.get("properties", {}).get("ALTERNATIVE_IDENTIFIER"),
        "componentType": doc["componentType"],
        "currentStage": doc.get("currentStage"),
        # Ajouter d'autres champs utiles ici
    }
```

---

#### 3. Améliorer les Descriptions et Exemples
**Problème** : Les descriptions comme `"Find a quad module by serial"` ne aident pas l'agent à comprendre **quand** et **comment** utiliser le tool.

**Solution** :
- **Ajouter des exemples concrets** dans la description
- **Préciser les cas d'usage** (ex: "Utilisé pour résoudre des références de composants dans les tests")
- **Indiquer les champs clés** dans le retour

**Exemple amélioré** :
```python
@mcp_tool
def find_component_summary_tool(serial_number: str) -> dict:
    """Récupère un résumé compact d'un composant (ID, numéro de série, type, stage actuel).
    
    **Cas d'usage** :
    - Résoudre une référence de composant depuis un test (ex: `componentId` dans QC.result).
    - Vérifier l'existence d'un composant avant de lancer une requête coûteuse.
    
    **Exemple** :
        Entrée: serial_number="20UPGM24830846"
        Sortie: {"id": "5f8d...", "serialNumber": "20UPGM24830846", "type": "module", "stage": "MODULE/ASSEMBLY"}
    """
    ...
```

---

#### 4. Ajouter des Limites par Défaut et Pagination
**Problème** : Des tools comme `find_all_tool` peuvent retourner **trop de données** (timeout, gaspillage de tokens).

**Solution** :
- **Limite par défaut à 10** pour tous les `find_*` tools
- **Forcer l'usage de `limit`** dans les tools publics
- **Ajouter un tool `count_tool`** pour estimer le volume avant de fetcher

**Exemple** :
```python
@mcp_tool
def find_components_by_type_tool(
    component_type: str,
    limit: int = 10,  # Default safe
    skip: int = 0,
) -> List[dict]:
    """Trouve des composants par type (module, bare_module, pcb).
    **Attention** : Utilise count_tool avant pour vérifier le nombre de résultats.
    """
    return list(db.component.find({"componentType": component_type}).skip(skip).limit(limit))
```

---

---

### 🥈 Priorité 2 : Ajouter des "Meta-Tools" pour la Découverte

L'agent a besoin de **comprendre la structure de la base** pour formuler des requêtes efficaces.

| **Tool à Ajouter** | **Utilité** | **Exemple de Retour** |
|---------------------|-------------|-----------------------|
| `list_collections_tool` | Lister les collections disponibles | `["component", "QC.result", "QC.module.status", "comments"]` |
| `describe_collection_tool` | Schéma d'une collection (champs, types) | `{"component": {"fields": {"serialNumber": "string", "componentType": "enum[module, bare_module, pcb]"}}}` |
| `sample_data_tool` | Échantillon de données pour une collection | `{"component": [{"_id": "...", "serialNumber": "20UPGM..."}, ...]}` |
| `list_stages_tool` | Lister les stages de production possibles | `["MODULE/ASSEMBLY", "MODULE/WIREBONDING", "BAREMODULERECEPTION"]` |
| `list_test_types_tool` | Lister les types de tests disponibles | `["IV_MEASURE", "MASS_MEASUREMENT", "QUAD_MODULE_METROLOGY"]` |

**Implémentation** :
```python
@mcp_tool
def list_collections_tool() -> List[str]:
    """Liste toutes les collections disponibles dans la base de données."""
    return db.list_collection_names()


@mcp_tool
def describe_collection_tool(collection: str) -> dict:
    """Retourne le schéma (champs et types) d'une collection.
    Exemple: collection="component" -> {"fields": {"serialNumber": "str", "componentType": "str", ...}}
    """
    sample = list(db[collection].find().limit(5))
    if not sample:
        return {"error": "Collection vide ou introuvable"}
    fields = {}
    for doc in sample:
        for key, value in doc.items():
            if key not in fields:
                fields[key] = type(value).__name__
    return {"collection": collection, "fields": fields}


@mcp_tool
def sample_data_tool(collection: str, limit: int = 3) -> List[dict]:
    """Retourne un échantillon de données pour une collection."""
    return list(db[collection].find().limit(limit))
```

---

---

### 🥉 Priorité 3 : Optimiser les Requêtes Fréquentes

#### 1. Cacher les Métadonnées des Composants
**Problème** : Les composants sont souvent référencés par `componentId` dans les tests. L'agent doit **toujours** les résoudre avant de répondre.

**Solution** :
- **Cacher les résumés de composants** (ex: `serialNumber`, `alternativeId`, `currentStage`) dans une **cache locale**
- **Invalider le cache** périodiquement (ex: toutes les 5 minutes)

**Implémentation avec `lru_cache`** :
```python
from functools import lru_cache

@lru_cache(maxsize=1000)  # Cache les 1000 derniers composants

def get_component_summary_cached(component_id: str) -> Optional[dict]:
    doc = db.component.find_one({"_id": ObjectId(component_id)})
    if not doc:
        return None
    return {
        "id": str(doc["_id"]),
        "serialNumber": doc.get("serialNumber"),
        "alternativeId": doc.get("properties", {}).get("ALTERNATIVE_IDENTIFIER"),
        "componentType": doc["componentType"],
        "currentStage": doc.get("currentStage"),
    }


@mcp_tool
def get_component_summary_tool(component_id: str) -> Optional[dict]:
    """Récupère un résumé mis en cache d'un composant par son ObjectId."""
    return get_component_summary_cached(component_id)
```

---

#### 2. Ajouter des Tools d'Agrégation "Intelligents"
**Problème** : L'agent doit souvent **compter, grouper, ou filtrer** des données (ex: "Combien de modules ont échoué le test X au stage Y ?").

**Solution** : Ajouter des tools pour :
- **Compter** : `count_components_by_stage_tool`, `count_tests_by_type_tool`
- **Grouper** : `group_tests_by_institution_tool`
- **Agrégations MongoDB** : `aggregate_tool`

**Exemple** :
```python
@mcp_tool
def count_components_by_stage_tool(
    component_type: Optional[str] = None,
    stage: Optional[str] = None,
) -> int:
    """Compte le nombre de composants à un stage donné.
    Exemple: component_type="module", stage="MODULE/WIREBONDING" -> 42
    """
    filter = {}
    if component_type:
        filter["componentType"] = component_type
    if stage:
        filter["currentStage"] = stage
    return db.component.count_documents(filter)
```

---

#### 3. Optimiser les Requêtes sur `QC.result`
La collection `QC.result` est **très grande** et souvent interrogée.

**Solutions** :
1. **Indexer les champs fréquents** dans MongoDB :
   ```python
   # À exécuter une fois dans MongoDB
   db["QC.result"].create_index([("component", 1), ("stage", 1)])
   db["QC.result"].create_index([("testType", 1), ("passed", 1)])
   db["QC.result"].create_index([("date", -1)])  # Pour les requêtes par date
   ```

2. **Ajouter des tools dédiés** :
   ```python
   @mcp_tool
def find_latest_test_for_component_tool(
       component_id: str,
       test_type: Optional[str] = None,
       stage: Optional[str] = None,
   ) -> Optional[dict]:
       """Trouve le dernier test d'un type donné pour un composant.
       Optimisé pour éviter les scans complets de QC.result.
       """
       filter = {"component": ObjectId(component_id)}
       if test_type:
           filter["testType"] = test_type
       if stage:
           filter["stage"] = stage
       return db["QC.result"].find_one(filter, sort=[("date", -1)])
   ```

---

---

### 🏆 Priorité 4 : Améliorer l'Agent (Côté Client)

#### 1. Configurer un Prompt Système Optimisé
Ajoute dans le **prompt système** de ton agent des instructions pour :
- **Toujours utiliser `count_tool` avant `find_*`** pour éviter les requêtes trop lourdes
- **Privilégier les tools génériques** (`find_component_by_serial_tool` plutôt que `find_quad_module_by_serial_tool`)
- **Structurer les réponses** avec des champs standard (ex: `alternativeId` pour les modules)

**Exemple de Prompt Système** :
```
# Instructions pour interagir avec la base de données ITk :

## 1. Découverte
- Utilise `list_collections_tool` et `describe_collection_tool` si tu ne connais pas la structure des données.

## 2. Comptage
- **Avant toute requête `find_*`**, utilise `count_tool` pour vérifier le nombre de résultats.
  - Si count > 50, demande à l'utilisateur de préciser des filtres.

## 3. Résolution de Composants
- Pour un `componentId` (ObjectId), utilise `find_component_summary_tool` pour obtenir `serialNumber` et `alternativeId`.
- Pour un `serialNumber`, utilise `find_component_by_serial_tool`.

## 4. Tests
- Utilise `find_test_summary_tool` pour lister les tests d'un composant avant de fetcher un test spécifique.

## 5. Retours
- Inclus toujours `serialNumber` et `alternativeId` (si module) dans les réponses.
- Formate les dates en ISO 8601 (ex: "2026-06-30T12:00:00Z").
- Si une requête est trop large, suggère à l'utilisateur d'affiner ses critères.
```

---

#### 2. Ajouter des "Shortcuts" pour les Questions Fréquentes
Crée des **fonctions internes** dans ton agent qui combinent plusieurs tools pour répondre à des questions courantes.

**Exemple : Répondre à "Quel est le status du module X ?"**
```python
def answer_module_status_question(serial_number: str) -> dict:
    """Répond à : 'Quel est le status du module X ?'"""
    # 1. Trouver le composant
    component = find_component_by_serial_tool(serial_number, component_type="module")
    if not component:
        return {"error": f"Module {serial_number} introuvable"}

    # 2. Récupérer ses tests
    tests = find_test_summary_tool(component["id"])

    # 3. Structurer la réponse
    return {
        "module": {
            "serialNumber": component["serialNumber"],
            "alternativeId": component.get("alternativeId"),
            "currentStage": component["currentStage"],
        },
        "latest_tests": [
            {
                "type": t["testType"],
                "stage": t["stage"],
                "passed": t["passed"],
                "date": t["date"],
            }
            for t in tests[:5]  # 5 derniers tests
        ],
    }
```

---

#### 3. Gérer les Erreurs et Timeouts
- **Timeouts** : Configurer un timeout par tool (ex: 5 secondes max)
- **Erreurs** : Retourner des messages **clairs et actionnables**

**Exemple** :
```python
@mcp_tool
def find_components_tool(filter: dict, limit: int = 10) -> Union[List[dict], dict]:
    """Trouve des composants avec un filtre personnalisé."""
    try:
        if limit > 50:
            raise ValueError("Limite maximale de 50 résultats. Utilise count_tool d'abord.")
        return list(db.component.find(filter).limit(limit))
    except Exception as e:
        return {
            "error": str(e), 
            "hint": "Essaie avec des filtres plus restrictifs ou une limite plus petite."
        }
```

---

#### 4. Utiliser des "Templates" de Requêtes
Stocke des **requêtes MongoDB pré-construites** pour des questions types :

```python
QUERY_TEMPLATES = {
    "modules_with_failed_tests": {
        "collection": "QC.result",
        "filter": {"testType": "IV_MEASURE", "passed": False},
        "projection": {"component": 1, "stage": 1, "date": 1},
    },
    "recent_signoffs": {
        "collection": "QC.result",
        "filter": {"testType": "SIGN_OFF"},
        "sort": [("date", -1)],
        "limit": 20,
    },
    "modules_by_institution": {
        "collection": "component",
        "filter": {"componentType": "module", "properties.INSTITUTION": None},  # À compléter
        "projection": {"serialNumber": 1, "alternativeId": 1, "currentStage": 1},
    },
}

@mcp_tool
def run_query_template_tool(template_name: str, **params) -> Union[List[dict], dict]:
    """Exécute une requête pré-définie (ex: 'modules_with_failed_tests').
    Args:
        template_name: Nom du template de requête.
        **params: Paramètres à fusionner avec le filtre du template.
    """
    template = QUERY_TEMPLATES.get(template_name)
    if not template:
        return {"error": f"Template {template_name} introuvable. Templates disponibles: {list(QUERY_TEMPLATES.keys())}"}
    
    # Fusionner les filtres
    filter = {**template.get("filter", {}), **params}
    
    # Exécuter la requête
    query = db[template["collection"]].find(filter, template.get("projection"))
    if template.get("sort"):
        query = query.sort(template["sort"])
    if template.get("limit"):
        query = query.limit(template["limit"])
    
    return list(query)
```

---

---

## 📊 Exemples Concrets d'Amélioration

### Avant/Après pour une Question Type

**Question** : *"Combien de modules ont été assemblés à IRFU en juin 2026 ?"*

| **Étape** | **Avant (Problème)** | **Après (Solution)** |
|-----------|----------------------|----------------------|
| 1. Comprendre la question | L'agent ne sait pas quelles collections/interroger. | Utilise `list_collections_tool` → voit `component` et `QC.result`. |
| 2. Trouver les modules | `find_all_tool` sur `component` → **timeout** (trop de résultats). | `count_tool` sur `component` avec filtre → retourne **242**. |
| 3. Filtrer par date | L'agent doit parser manuellement les dates. | `count_tool` avec filtre incluant la date → retourne **42**. |
| 4. Réponse | Réponse lente ou incomplète. | Réponse instantanée : **"42 modules assemblés à IRFU en juin 2026."** |

---

### Implémentation du Tool Optimisé

```python
@mcp_tool
def count_modules_by_institution_and_date_tool(
    institution: str,
    stage: str = "MODULE/ASSEMBLY",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> int:
    """Compte les modules assemblés par une institution dans une période.
    
    Args:
        institution: Code de l'institution (ex: "IRFU").
        stage: Stage de production (default: "MODULE/ASSEMBLY").
        start_date: Date de début (format ISO, ex: "2026-06-01").
        end_date: Date de fin (format ISO, ex: "2026-06-30").
    
    Returns:
        Nombre de modules.
    """
    filter = {
        "componentType": "module",
        "currentStage": stage,
        "properties.INSTITUTION": institution,
    }
    if start_date or end_date:
        date_filter = {}
        if start_date:
            date_filter["$gte"] = start_date
        if end_date:
            date_filter["$lte"] = end_date
        filter["createdAt"] = date_filter
    return db.component.count_documents(filter)
```

---

---

## ✅ Checklist d'Implémentation

| **Tâche** | **Priorité** | **Complexité** | **Impact** | **Statut** |
|-----------|--------------|----------------|------------|------------|
| Factoriser les tools redondants (`find_component_by_*`) | ⭐⭐⭐ | Moyenne | Énorme | ⬜ |
| Standardiser les retours (champs obligatoires) | ⭐⭐⭐ | Faible | Énorme | ⬜ |
| Ajouter `list_collections_tool` et `describe_collection_tool` | ⭐⭐ | Faible | Grand | ⬜ |
| Ajouter des limites par défaut (`limit=10`) | ⭐⭐⭐ | Faible | Grand | ⬜ |
| Implémenter `count_tool` pour toutes les collections | ⭐⭐ | Moyenne | Grand | ⬜ |
| Cacher les résumés de composants (`lru_cache`) | ⭐⭐ | Moyenne | Grand | ⬜ |
| Ajouter des index MongoDB sur `QC.result` | ⭐⭐ | Faible | Grand | ⬜ |
| Créer des templates de requêtes | ⭐ | Moyenne | Moyen | ⬜ |
| Optimiser le prompt système de l'agent | ⭐⭐ | Faible | Grand | ⬜ |
| Ajouter des tools d'agrégation (`group_by_*`) | ⭐ | Moyenne | Moyen | ⬜ |
| Améliorer les descriptions des tools existants | ⭐⭐ | Faible | Grand | ⬜ |

---

---

## 🎯 Recommandations Finales : Par Où Commencer ?

### **Cette semaine (Quick Wins)**
1. ✅ **Factoriser les tools redondants** : Créer `find_component_by_serial_tool` unifié
2. ✅ **Ajouter des limites par défaut** : `limit=10` pour tous les `find_*` tools
3. ✅ **Implémenter les meta-tools** : `list_collections_tool`, `describe_collection_tool`
4. ✅ **Améliorer les descriptions** : Ajouter exemples et cas d'usage à tous les tools

### **Semaine prochaine (Optimisations)**
1. 🔄 **Ajouter `count_tool`** pour toutes les collections principales
2. 🔄 **Implémenter le cache** pour `find_component_summary_tool`
3. 🔄 **Ajouter des index MongoDB** sur `QC.result` (component, stage, testType, date)

### **À long terme (Scalabilité)**
1. 📅 **Créer des templates de requêtes** pour les questions fréquentes
2. 📅 **Optimiser le prompt système** de l'agent
3. 📅 **Ajouter des tools d'agrégation** (`group_tests_by_institution_tool`, etc.)

---

---

## 📚 Ressources Utiles

- **MongoDB Indexes** : [Documentation officielle](https://www.mongodb.com/docs/manual/indexes/)
- **Python `lru_cache`** : [Docs Python](https://docs.python.org/3/library/functools.html#functools.lru_cache)
- **Exemple de serveur MCP optimisé** : [mcp-server-mongodb](https://github.com/modelcontextprotocol/servers/tree/main/src/mongodb) (inspiration pour la structure)
- **Bonnes pratiques MongoDB** : [Performance Best Practices](https://www.mongodb.com/docs/manual/administration/performance/)
- **MCP Specification** : [Model Context Protocol](https://github.com/modelcontextprotocol/specification) (pour les bonnes pratiques d'implémentation)

---

---

## 💡 Conseils Supplémentaires

1. **Monitoring** : Ajoute des logs pour identifier les tools les plus utilisés/lents
2. **Benchmarking** : Mesure le temps d'exécution des requêtes avant/après optimisation
3. **Documentation** : Maintenir ce fichier à jour avec les changements effectués
4. **Tests** : Ajoute des tests unitaires pour les nouveaux tools (ex: vérifier que `find_component_by_serial_tool` retourne bien les champs standardisés)
5. **Feedback Utilisateur** : Collecte les retours des utilisateurs pour identifier les questions fréquentes non couvertes

---

> **Note** : Ce document est conçu pour être **vivant**. N'hésite pas à le mettre à jour au fur et à mesure des implémentations et des nouvelles idées.
>
> *Dernière mise à jour : 2026-06-30*