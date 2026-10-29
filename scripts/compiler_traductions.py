"""Compile locale/*/LC_MESSAGES/django.po en .mo sans dépendre de gettext (msgfmt).

    python scripts/compiler_traductions.py

Gère les fichiers .po simples de ce projet (msgid/msgstr sur une ligne, sans pluriels).
Là où gettext est installé (PythonAnywhere), `python manage.py compilemessages` fait la même chose.
"""

import ast
import struct
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent


def lire_po(chemin):
    entrees, msgid, header = {}, None, []
    for ligne in chemin.read_text(encoding="utf-8").splitlines():
        if ligne.startswith("msgid "):
            msgid = ast.literal_eval(ligne[6:])
        elif ligne.startswith("msgstr ") and msgid is not None:
            entrees[msgid] = ast.literal_eval(ligne[7:])
        elif ligne.startswith('"') and msgid == "":
            header.append(ast.literal_eval(ligne))
    entrees[""] = "".join(header)
    return entrees


def ecrire_mo(entrees, chemin):
    cles = sorted(entrees)
    ids = [k.encode() for k in cles]
    strs = [entrees[k].encode() for k in cles]
    n = len(cles)
    debut_ids = 7 * 4 + 16 * n
    debut_strs = debut_ids + sum(len(i) + 1 for i in ids)
    table_ids, table_strs, pos_i, pos_s = [], [], debut_ids, debut_strs
    for i, s in zip(ids, strs):
        table_ids += [len(i), pos_i]
        table_strs += [len(s), pos_s]
        pos_i += len(i) + 1
        pos_s += len(s) + 1
    donnees = struct.pack("Iiiiiii", 0x950412DE, 0, n, 7 * 4, 7 * 4 + 8 * n, 0, 0)
    donnees += struct.pack(f"{2 * n}i", *table_ids) + struct.pack(f"{2 * n}i", *table_strs)
    donnees += b"".join(i + b"\0" for i in ids) + b"".join(s + b"\0" for s in strs)
    chemin.write_bytes(donnees)


if __name__ == "__main__":
    for po in RACINE.glob("locale/*/LC_MESSAGES/*.po"):
        ecrire_mo(lire_po(po), po.with_suffix(".mo"))
        print(f"compilé : {po.relative_to(RACINE)}")
