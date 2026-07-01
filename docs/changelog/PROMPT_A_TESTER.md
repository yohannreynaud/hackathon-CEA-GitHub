# 📋 PROMPTS DE TEST POUR COMPARAISON ANCIENS vs NOUVEAUX TOOLS

> **Objectif** : Fournir des exemples de prompts élémentaires pour tester chaque outil factorisable et son équivalent unifié.
> **Méthodologie** : Pour chaque groupe de tools factorisés, un exemple de prompt est fourni pour l'ancien tool et son équivalent unifié.

---

## 🔹 **Groupe 1 : Recherche par serial number**

### **1.1 - Module Quad**
- **Ancien tool** : `find_quad_module_by_serial_tool`
- **Nouveau tool** : `find_component_by_serial_unified_tool`

**Prompt pour l'ancien tool** :
```json
{
  "tool": "find_quad_module_by_serial_tool",
  "parameters": {
    "serial_number": "20UPGM24830846",
    "partial": false,
    "limit": 5,
    "projection": {"serialNumber": 1, "componentType": 1, "currentStage": 1}
  }
}
```

**Prompt pour le nouveau tool** :
```json
{
  "tool": "find_component_by_serial_unified_tool",
  "parameters": {
    "serial_number": "20UPGM24830846",
    "component_type": "module",
    "partial": false,
    "limit": 5,
    "projection": {"serialNumber": 1, "componentType": 1, "currentStage": 1}
  }
}
```

**Cas d'usage** : Trouver un module quad spécifique par son numéro de série ATLAS.

---

### **1.2 - Flex PCB**
- **Ancien tool** : `find_flex_pcb_by_serial_tool`
- **Nouveau tool** : `find_component_by_serial_unified_tool`

**Prompt pour l'ancien tool** :
```json
{
  "tool": "find_flex_pcb_by_serial_tool",
  "parameters": {
    "serial_number": "20UPGPQ2830070",
    "partial": false,
    "limit": 5,
    "projection": {"serialNumber": 1, "componentType": 1, "properties.PCB_DESIGN_VERSION": 1}
  }
}
```

**Prompt pour le nouveau tool** :
```json
{
  "tool": "find_component_by_serial_unified_tool",
  "parameters": {
    "serial_number": "20UPGPQ2830070",
    "component_type": "module_pcb",
    "partial": false,
    "limit": 5,
    "projection": {"serialNumber": 1, "componentType": 1, "properties.PCB_DESIGN_VERSION": 1}
  }
}
```

**Cas d'usage** : Trouver un PCB flexible par son numéro de série.

---

### **1.3 - Bare Module**
- **Ancien tool** : `find_bare_module_by_serial_tool`
- **Nouveau tool** : `find_component_by_serial_unified_tool`

**Prompt pour l'ancien tool** :
```json
{
  "tool": "find_bare_module_by_serial_tool",
  "parameters": {
    "serial_number": "20UPGB42000033",
    "partial": false,
    "limit": 5,
    "projection": {"serialNumber": 1, "componentType": 1, "properties.FECHIP_VERSION": 1}
  }
}
```

**Prompt pour le nouveau tool** :
```json
{
  "tool": "find_component_by_serial_unified_tool",
  "parameters": {
    "serial_number": "20UPGB42000033",
    "component_type": "bare_module",
    "partial": false,
    "limit": 5,
    "projection": {"serialNumber": 1, "componentType": 1, "properties.FECHIP_VERSION": 1}
  }
}
```

**Cas d'usage** : Trouver un bare module par son numéro de série.

---

### **1.4 - Composant générique**
- **Ancien tool** : `find_component_by_serial_tool`
- **Nouveau tool** : `find_component_by_serial_unified_tool`

**Prompt pour l'ancien tool** :
```json
{
  "tool": "find_component_by_serial_tool",
  "parameters": {
    "serial_number": "20UPGM24830846",
    "partial": false,
    "limit": 5,
    "projection": {"serialNumber": 1, "componentType": 1}
  }
}
```

**Prompt pour le nouveau tool** :
```json
{
  "tool": "find_component_by_serial_unified_tool",
  "parameters": {
    "serial_number": "20UPGM24830846",
    "partial": false,
    "limit": 5,
    "projection": {"serialNumber": 1, "componentType": 1}
  }
}
```

**Cas d'usage** : Recherche générique sans filtrer par type de composant.

---

## 🔹 **Groupe 2 : Recherche par alternative_id**

### **2.1 - Module Quad par alternative_id**
- **Ancien tool** : `find_quad_module_by_alternative_id_tool`
- **Nouveau tool** : `find_component_by_alternative_id_unified_tool`

**Prompt pour l'ancien tool** :
```json
{
  "tool": "find_quad_module_by_alternative_id_tool",
  "parameters": {
    "alternative_id": "Paris0076",
    "partial": false,
    "limit": 5,
    "projection": {"serialNumber": 1, "componentType": 1, "properties.ALTERNATIVE_IDENTIFIER": 1}
  }
}
```

**Prompt pour le nouveau tool** :
```json
{
  "tool": "find_component_by_alternative_id_unified_tool",
  "parameters": {
    "alternative_id": "Paris0076",
    "component_type": "module",
    "partial": false,
    "limit": 5,
    "projection": {"serialNumber": 1, "componentType": 1, "properties.ALTERNATIVE_IDENTIFIER": 1}
  }
}
```

**Cas d'usage** : Trouver un module quad par son identifiant alternatif (ex: Paris0076).

---

## 🔹 **Groupe 3 : Composants de production**

### **3.1 - Modules Quad de production**
- **Ancien tool** : `find_production_quad_modules_tool`
- **Nouveau tool** : `find_production_components_unified_tool`

**Prompt pour l'ancien tool** :
```json
{
  "tool": "find_production_quad_modules_tool",
  "parameters": {
    "fe_chip_version": "3",
    "is_preproduction": false,
    "limit": 10,
    "skip": 0,
    "projection": {
      "serialNumber": 1,
      "componentType": 1,
      "properties.FECHIP_VERSION": 1,
      "properties.IS_PREPRODUCTION_MODULE": 1
    }
  }
}
```

**Prompt pour le nouveau tool** :
```json
{
  "tool": "find_production_components_unified_tool",
  "parameters": {
    "component_type": "module",
    "fe_chip_version": "3",
    "is_preproduction": false,
    "limit": 10,
    "skip": 0,
    "projection": {
      "serialNumber": 1,
      "componentType": 1,
      "properties.FECHIP_VERSION": 1,
      "properties.IS_PREPRODUCTION_MODULE": 1
    }
  }
}
```

**Cas d'usage** : Trouver tous les modules quad de production avec FE chip version 3 (ITkpix_v2).

---

### **3.2 - Flex PCBs de production**
- **Ancien tool** : `find_production_flex_pcbs_tool`
- **Nouveau tool** : `find_production_components_unified_tool`

**Prompt pour l'ancien tool** :
```json
{
  "tool": "find_production_flex_pcbs_tool",
  "parameters": {
    "manufacturer": "Tecnomec",
    "limit": 10,
    "skip": 0,
    "projection": {
      "serialNumber": 1,
      "componentType": 1,
      "properties.PCB_DESIGN_VERSION": 1,
      "properties.MANUFACTURER": 1
    }
  }
}
```

**Prompt pour le nouveau tool** :
```json
{
  "tool": "find_production_components_unified_tool",
  "parameters": {
    "component_type": "module_pcb",
    "manufacturer": "Tecnomec",
    "limit": 10,
    "skip": 0,
    "projection": {
      "serialNumber": 1,
      "componentType": 1,
      "properties.PCB_DESIGN_VERSION": 1,
      "properties.MANUFACTURER": 1
    }
  }
}
```

**Cas d'usage** : Trouver tous les PCBs flex de production fabriqués par Tecnomec.

---

### **3.3 - Bare Modules de production**
- **Ancien tool** : `find_production_bare_modules_tool`
- **Nouveau tool** : `find_production_components_unified_tool`

**Prompt pour l'ancien tool** :
```json
{
  "tool": "find_production_bare_modules_tool",
  "parameters": {
    "fe_chip_version": "3",
    "vendor": "LPNHE",
    "with_sensor": true,
    "limit": 10,
    "skip": 0,
    "projection": {
      "serialNumber": 1,
      "componentType": 1,
      "properties.FECHIP_VERSION": 1,
      "properties.VENDOR": 1,
      "properties.WITH_SENSOR": 1
    }
  }
}
```

**Prompt pour le nouveau tool** :
```json
{
  "tool": "find_production_components_unified_tool",
  "parameters": {
    "component_type": "bare_module",
    "fe_chip_version": "3",
    "vendor": "LPNHE",
    "with_sensor": true,
    "limit": 10,
    "skip": 0,
    "projection": {
      "serialNumber": 1,
      "componentType": 1,
      "properties.FECHIP_VERSION": 1,
      "properties.VENDOR": 1,
      "properties.WITH_SENSOR": 1
    }
  }
}
```

**Cas d'usage** : Trouver tous les bare modules de production avec FE chip version 3 et capteur, du fournisseur LPNHE.

---

## 🔹 **Groupe 4 : Derniers tests**

### **4.1 - Dernier test pour un Quad Module**
- **Ancien tool** : `find_latest_quad_module_test_tool`
- **Nouveau tool** : `find_latest_test_unified_tool`

**Prompt pour l'ancien tool** :
```json
{
  "tool": "find_latest_quad_module_test_tool",
  "parameters": {
    "component_id": "67c981355ae416616e2a8974",
    "test_type": "MASS_MEASUREMENT",
    "stage": "MODULE/ASSEMBLY",
    "projection": {
      "testType": 1,
      "stage": 1,
      "passed": 1,
      "results.MASS": 1,
      "prodDB_record.date": 1
    }
  }
}
```

**Prompt pour le nouveau tool** :
```json
{
  "tool": "find_latest_test_unified_tool",
  "parameters": {
    "component_id": "67c981355ae416616e2a8974",
    "test_type": "MASS_MEASUREMENT",
    "stage": "MODULE/ASSEMBLY",
    "projection": {
      "testType": 1,
      "stage": 1,
      "passed": 1,
      "results.MASS": 1,
      "prodDB_record.date": 1
    }
  }
}
```

**Cas d'usage** : Trouver le dernier test de mesure de masse pour un module quad à l'étape ASSEMBLY.

---

### **4.2 - Dernier test pour un Flex PCB**
- **Ancien tool** : `find_latest_pcb_test_tool`
- **Nouveau tool** : `find_latest_test_unified_tool`

**Prompt pour l'ancien tool** :
```json
{
  "tool": "find_latest_pcb_test_tool",
  "parameters": {
    "component_id": "6703f4b8ef991c0043ea26c4",
    "test_type": "IV_MEASURE",
    "projection": {
      "testType": 1,
      "passed": 1,
      "results.IV_MEASURE": 1,
      "prodDB_record.date": 1
    }
  }
}
```

**Prompt pour le nouveau tool** :
```json
{
  "tool": "find_latest_test_unified_tool",
  "parameters": {
    "component_id": "6703f4b8ef991c0043ea26c4",
    "test_type": "IV_MEASURE",
    "stage": "PCB_RECEPTION_MODULE_SITE",
    "projection": {
      "testType": 1,
      "passed": 1,
      "results.IV_MEASURE": 1,
      "prodDB_record.date": 1
    }
  }
}
```

**Cas d'usage** : Trouver le dernier test de mesure IV pour un PCB à l'étape de réception.

---

### **4.3 - Dernier test pour un Bare Module**
- **Ancien tool** : `find_latest_bare_module_test_tool`
- **Nouveau tool** : `find_latest_test_unified_tool`

**Prompt pour l'ancien tool** :
```json
{
  "tool": "find_latest_bare_module_test_tool",
  "parameters": {
    "component_id": "67d3e456789abc1234567890",
    "test_type": "MASS_MEASUREMENT",
    "projection": {
      "testType": 1,
      "passed": 1,
      "results.MASS": 1,
      "prodDB_record.date": 1
    }
  }
}
```

**Prompt pour le nouveau tool** :
```json
{
  "tool": "find_latest_test_unified_tool",
  "parameters": {
    "component_id": "67d3e456789abc1234567890",
    "test_type": "MASS_MEASUREMENT",
    "stage": "BAREMODULERECEPTION",
    "projection": {
      "testType": 1,
      "passed": 1,
      "results.MASS": 1,
      "prodDB_record.date": 1
    }
  }
}
```

**Cas d'usage** : Trouver le dernier test de mesure de masse pour un bare module à l'étape de réception.

---

## 🔹 **Groupe 5 : Composants avec tests valides**

### **5.1 - Flex PCBs avec tests valides**
- **Ancien tool** : `find_pcb_with_valid_tests_tool`
- **Nouveau tool** : `find_components_with_valid_tests_unified_tool`

**Prompt pour l'ancien tool** :
```json
{
  "tool": "find_pcb_with_valid_tests_tool",
  "parameters": {
    "test_types": ["MASS", "METROLOGY", "VISUAL_INSPECTION"],
    "limit": 10,
    "skip": 0,
    "projection": {
      "serialNumber": 1,
      "componentType": 1,
      "QC_results_pdb.PCB_RECEPTION_MODULE_SITE.MASS": 1,
      "QC_results_pdb.PCB_RECEPTION_MODULE_SITE.METROLOGY": 1
    }
  }
}
```

**Prompt pour le nouveau tool** :
```json
{
  "tool": "find_components_with_valid_tests_unified_tool",
  "parameters": {
    "component_type": "PCB",
    "test_types": ["MASS", "METROLOGY", "VISUAL_INSPECTION"],
    "limit": 10,
    "skip": 0,
    "projection": {
      "serialNumber": 1,
      "componentType": 1,
      "QC_results_pdb.PCB_RECEPTION_MODULE_SITE.MASS": 1,
      "QC_results_pdb.PCB_RECEPTION_MODULE_SITE.METROLOGY": 1
    }
  }
}
```

**Cas d'usage** : Trouver tous les PCBs flex qui ont des tests valides de masse, métrologie et inspection visuelle.

---

### **5.2 - Bare Modules avec tests valides**
- **Ancien tool** : `find_bare_modules_with_valid_tests_tool`
- **Nouveau tool** : `find_components_with_valid_tests_unified_tool`

**Prompt pour l'ancien tool** :
```json
{
  "tool": "find_bare_modules_with_valid_tests_tool",
  "parameters": {
    "test_types": ["MASS_MEASUREMENT", "VISUAL_INSPECTION"],
    "limit": 10,
    "skip": 0,
    "projection": {
      "serialNumber": 1,
      "componentType": 1,
      "QC_results_pdb.BAREMODULERECEPTION.MASS_MEASUREMENT": 1
    }
  }
}
```

**Prompt pour le nouveau tool** :
```json
{
  "tool": "find_components_with_valid_tests_unified_tool",
  "parameters": {
    "component_type": "BARE_MODULE",
    "test_types": ["MASS_MEASUREMENT", "VISUAL_INSPECTION"],
    "limit": 10,
    "skip": 0,
    "projection": {
      "serialNumber": 1,
      "componentType": 1,
      "QC_results_pdb.BAREMODULERECEPTION.MASS_MEASUREMENT": 1
    }
  }
}
```

**Cas d'usage** : Trouver tous les bare modules qui ont des tests valides de mesure de masse et d'inspection visuelle.

---

## 📊 **Résumé des correspondances**

| **Groupe** | **Ancien Tool** | **Nouveau Tool** | **Nombre de prompts** |
|------------|----------------|------------------|---------------------|
| 1. Serial number | 4 tools | `find_component_by_serial_unified_tool` | 4 |
| 2. Alternative ID | 1 tool | `find_component_by_alternative_id_unified_tool` | 1 |
| 3. Production | 3 tools | `find_production_components_unified_tool` | 3 |
| 4. Derniers tests | 3 tools | `find_latest_test_unified_tool` | 3 |
| 5. Tests valides | 2 tools | `find_components_with_valid_tests_unified_tool` | 2 |
| **Total** | **13 tools** | **5 tools** | **13 prompts** |

---

## 🎯 **Protocole de test recommandé**

Pour chaque paire (ancien/nouveau) :

1. **Exécuter l'ancien tool** avec le prompt fourni
2. **Exécuter le nouveau tool** avec le prompt équivalent
3. **Comparer** :
   - Temps de réponse
   - Structure de la réponse JSON
   - Complétude des données retournées
   - Filtres appliqués (vérifier dans les logs si possible)
   - Nombre de documents retournés

4. **Valider** :
   - ✅ Les résultats sont identiques
   - ✅ Les performances sont comparables (ou meilleures)
   - ✅ Aucune régression fonctionnelle

---

## 📝 **Notes**

- Tous les exemples utilisent des identifiants **réalistes** basés sur la documentation existante
- Les projections sont **identiques** entre anciens et nouveaux tools pour faciliter la comparaison
- Les paramètres `limit` et `skip` sont conservés pour permettre la pagination
- Le paramètre `partial` est testé avec `false` pour une recherche exacte
- Pour les tests de production, des filtres spécifiques (fe_chip_version, manufacturer, etc.) sont inclus

---

> **Date de création** : 2026-06-30  
> **Auteur** : Mistral Vibe (pour comparaison performance anciens vs nouveaux tools)  
> **Fichier source** : Basé sur `unification_tool.md` et `TOOL_MANUAL.md`