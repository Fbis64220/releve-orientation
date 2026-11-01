#!/usr/bin/env python3
"""Vérifie l'accès aux sources ouvertes et enregistre leurs métadonnées réelles
(licence, date de mise à jour, liste des champs) dans data/sources-verifiees.json.

Usage : python3 scripts/verifier_sources.py
"""
import json, pathlib, time, urllib.request

API = "https://data.enseignementsup-recherche.gouv.fr/api/explore/v2.1/catalog/datasets/"
DATASETS = {"parcoursup": "fr-esr-parcoursup", "insersup": "fr-esr-insersup"}
# Champs lus par mapLive() dans src/app.html
CHAMPS_ATTENDUS = {
    "parcoursup": ["session", "fili", "fil_lib_voe_acc", "detail_forma", "g_ea_lib_vx", "ville_etab", "contrat_etab",
                   "select_form", "capa_fin", "voe_tot", "taux_acces_ens", "acc_tot", "pct_bg", "pct_bt", "pct_bp",
                   "pct_tb", "pct_tbf", "pct_b", "pct_ab", "pct_sansmention", "pct_bours", "pct_f", "pct_aca_orig",
                   "lien_form_psup", "cod_aff_form"],
    "insersup": ["uo_lib", "type_diplome", "libelle_diplome", "promo", "genre", "nationalite", "regime_inscription",
                 "obtention_diplome", "nb_sortants_12", "nb_poursuivants_12", "tx_sortants_en_emploi_sal_fr_12",
                 "tx_sortants_en_emploi_stable_12", "salaire_q2_12"],
}

def get(url, essais=10):
    for i in range(essais):
        try:
            with urllib.request.urlopen(url, timeout=30) as r:
                return json.load(r)
        except Exception:
            if i == essais - 1:
                raise
            time.sleep(2)

resultat = {}
for cle, ds in DATASETS.items():
    try:
        d = get(API + ds)
        meta = d.get("metas", {}).get("default", {})
        champs = [f["name"] for f in d.get("fields", [])]
        resultat[cle] = {"dataset": ds, "titre": meta.get("title"), "licence": meta.get("license"),
                         "modifie": meta.get("modified"), "lignes": meta.get("records_count"), "champs": champs}
        manquants = [c for c in CHAMPS_ATTENDUS[cle] if c not in champs]
        resultat[cle]["champs_attendus_absents"] = manquants
        if manquants:
            print(f"    Champs attendus absents : {', '.join(manquants)}")
        print(f"OK  {ds} : {meta.get('license')} · maj {meta.get('modified')} · {len(champs)} champs")
    except Exception as e:
        resultat[cle] = {"dataset": ds, "erreur": str(e)}
        print(f"ÉCHEC {ds} : {e}")

out = pathlib.Path(__file__).resolve().parent.parent / "data" / "sources-verifiees.json"
out.parent.mkdir(exist_ok=True)
out.write_text(json.dumps(resultat, ensure_ascii=False, indent=2))
print(f"Écrit : {out}")
