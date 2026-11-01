#!/usr/bin/env python3
"""Vérifie l'accès aux sources ouvertes et enregistre leurs métadonnées réelles
(licence, date de mise à jour, liste des champs) dans data/sources-verifiees.json.

Usage : python3 scripts/verifier_sources.py
"""
import json, pathlib, urllib.request

API = "https://data.enseignementsup-recherche.gouv.fr/api/explore/v2.1/catalog/datasets/"
DATASETS = {"parcoursup": "fr-esr-parcoursup", "insersup": "fr-esr-insersup"}
# Champs lus par mapLive() dans src/app.html
CHAMPS_ATTENDUS = ["fil_lib_voe_acc", "g_ea_lib_vx", "ville_etab", "contrat_etab", "select_form",
                   "capa_fin", "voe_tot", "taux_acces_ens", "acc_tot", "pct_bours", "pct_f", "lien_form_psup"]

def get(url):
    with urllib.request.urlopen(url, timeout=20) as r:
        return json.load(r)

resultat = {}
for cle, ds in DATASETS.items():
    try:
        d = get(API + ds)
        meta = d.get("metas", {}).get("default", {})
        champs = [f["name"] for f in d.get("fields", [])]
        resultat[cle] = {"dataset": ds, "titre": meta.get("title"), "licence": meta.get("license"),
                         "modifie": meta.get("modified"), "lignes": meta.get("records_count"), "champs": champs}
        if cle == "parcoursup":
            manquants = [c for c in CHAMPS_ATTENDUS if c not in champs]
            resultat[cle]["champs_attendus_absents"] = manquants
        print(f"OK  {ds} : {meta.get('license')} · maj {meta.get('modified')} · {len(champs)} champs")
    except Exception as e:
        resultat[cle] = {"dataset": ds, "erreur": str(e)}
        print(f"ÉCHEC {ds} : {e}")

out = pathlib.Path(__file__).resolve().parent.parent / "data" / "sources-verifiees.json"
out.parent.mkdir(exist_ok=True)
out.write_text(json.dumps(resultat, ensure_ascii=False, indent=2))
print(f"Écrit : {out}")
