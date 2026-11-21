# Washigochi

Petit jeu façon tamagotchi : on fait grandir **Washi**, un chiot berger australien noir tricolore (noir sur le
dessus, liste blanche, sourcils et pattes feu, yeux bleus), en pixel art, en 3 à 4 semaines.
Application web installable (PWA) pour iPhone et Android, sans store, qui fonctionne hors ligne.

C'est une version dérivée du [Kikougochi](https://github.com/nathba-perso/kikougochi) : même moteur, mêmes
règles, mêmes formats de sprites. Ce qui change :

| Kikougochi | Washigochi |
|---|---|
| Le kikou, un bébé guépard | Washi, un berger australien noir tricolore (`tools/vendor/washi.py`) |
| Pip (une main touche le nez) | **Coussin** : on donne un coussin à Washi, qui le serre entre ses pattes et fait des allers-retours très enthousiastes (mime comique, rien d'explicite) |
| Rêves : photos de bébés guépards | Rêves : 12 coussins en pixel art (`tools/make_assets.py`) |

Le coussin garde le rôle du pip dans les règles : il rend heureux, mais **excite** Washi et le fatigue un peu.
Trop excité, il ne s'endort pas et s'agace. Quand il en a envie, une bulle montre un petit coussin.

## Lancer

```bash
npm install
npm run dev        # serveur de développement (ajouter ?debug à l'URL pour le panneau de test)
npm run build      # build de production dans dist/
npm run simulate   # vérifie l'équilibrage du moteur (200 parties par profil de joueur)
```

Le jeu est publié sur GitHub Pages à chaque push sur `main` (`.github/workflows/pages.yml`).
Dans les réglages du dépôt, *Settings › Pages › Source* doit être sur **GitHub Actions**.

## Organisation

| Dossier | Rôle |
|---|---|
| `src/engine/` | Moteur : variables cachées, pas de 5 min, rattrapage hors ligne, actions, rêves. Constantes dans `params.ts`. |
| `src/render/` | Scène canvas 48×40 agrandie sans lissage, planches de sprites, séquences (actions, réactions, arrivée, évolution, départ). Le coussin est dans `clips.ts`. |
| `src/main.ts` | Boucle de jeu, sauvegarde, écrans (victoire, départ, rêve, album, code de sauvegarde, installation). |
| `public/sprites/` | Planches PNG + `manifest.json`, générées depuis `tools/vendor/washi.py` et `tools/vendor/etats.py`. |
| `public/reves/` | Les coussins rêvés et `reves.json` (noms de fichiers et titres). |
| `tools/` | Scripts Python : sprites, planches, accessoires, icônes et coussins. |

Le code garde les noms internes du Kikougochi (`Kikou`, `kikouPose`…) pour rester facile à comparer avec lui.

## Mettre à jour les sprites

```bash
python3 tools/make_sprites.py    # sprites de base + accessoires (dont le coussin) -> src/sprites/sprites.json
python3 tools/import_sheets.py   # planches d'états et de réactions -> public/sprites/
python3 tools/make_assets.py     # icônes de l'app + coussins des rêves
```

Légende des grilles de `washi.py` : `o` contour, `f` pelage noir, `l` blanc, `s` feu, `e` œil bleu, `w` reflet,
`n` truffe, `p` rose (langue).

## Soins et propreté

| Action | Rôle |
|---|---|
| Nourrir | Remplit la satiété. 2 à 4 h après chaque repas, Washi fait un caca (seulement réveillé, 3 au plus). |
| Coussin | Jouer : bonheur, mais ça l'**excite** et le fatigue un peu. Réaction : il finit avec le coussin, puis étoiles. |
| Câlin | Calmer : fait baisser la colère et l'excitation, peut l'endormir le soir. |
| Bisou | Aimer : bonheur, et il pardonne un peu. 3 par jour au plus, ensuite « beurk ». |
| Nettoyer | Enlève les cacas (ne le réveille pas). |

Les envies (bulles coussin, cœur, lèvres), la sauvegarde, le code de sauvegarde (`WASHI1:…`) et les cartes
postales fonctionnent comme dans le Kikougochi.

## Cohabitation avec le Kikougochi

Les deux jeux sont servis depuis la même origine (`nathba-perso.github.io`). Le Washigochi utilise donc ses
propres clés de stockage (`washigochi.v1`, `washigochi.social`, `wg_…`) et son propre cache hors ligne
(`washigochi-…`) : il ne lit ni n'efface jamais les parties de kikou.

## Mode test

Ajouter `?debug` à l'URL : affiche les variables cachées et permet d'avancer le temps (+1 h, +6 h, +1 j, +5 j).
