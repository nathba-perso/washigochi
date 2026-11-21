// Séquences animées : actions du joueur, réactions de Washi, arrivée, évolution.
import type { Action } from '../engine/params';
import type { Reaction } from '../engine/kikou';
import { noseOf, prop } from './sprites';
import { type Clip, type Scene, type Box, FLOOR, W, H, POOP_X, drawPoop, confetti, floatingZ, bubble, smallHeart, bigHeart } from './scene';

const lerp = (a: number, b: number, p: number) => a + (b - a) * Math.max(0, Math.min(1, p));

/** Position du bol, devant Washi (il regarde vers la gauche). */
const bowlX = (k: Box) => Math.max(1, k.x - 8);

/**
 * Coussin donné à Washi. Grand (≥ 15 px de large) : il serre le coussin entre ses pattes avant
 * (dessiné devant lui) et fait des allers-retours rapides. Petit : il grimpe dessus.
 * Mime suggestif et comique, rien d'explicite.
 */
const hugs = (k: Box) => k.w >= 15;
const COUSSIN_W = 11;
function cushionPos(k: Box): [number, number] {
  if (!hugs(k)) return [k.x - 6, FLOOR - 7];
  const x = k.w >= 20 ? k.x + 1 : k.x + Math.round((k.w - COUSSIN_W) / 2);
  return [x, FLOOR - 9];
}
function humpOffset(k: Box, t: number, t0: number, t1: number): [number, number] {
  const beat = Math.floor(t / 110) % 2;
  if (hugs(k)) return t >= t0 && t <= t1 ? [beat ? -1 : 1, 0] : [0, 0];
  if (t < t0 - 300 || t > t1 + 200) return [0, 0];
  if (t < t0) return [-Math.round(lerp(0, 3, (t - t0 + 300) / 300)), -Math.round(lerp(0, 2, (t - t0 + 300) / 300))];
  if (t > t1) return [-2, -1];
  return [beat ? -2 : -4, -2];
}
/** Dessine le coussin (derrière Washi s'il grimpe dessus, devant s'il le serre). */
function drawCushion(sc: Scene, t: number, k: Box, front: boolean, drop = 0) {
  if (hugs(k) !== front) return;
  const [x, y] = cushionPos(k);
  sc.prop('coussin', x, drop ? Math.round(lerp(-9, y, t / drop)) : y);
}
export function actionClip(a: Action, idleAnim: string, stage: number, onKiss?: () => void, poops = 0): Clip {
  switch (a) {
    case 'nettoyer':
      // le balai passe de droite à gauche sur le sol ; chaque caca disparaît à son passage
      return {
        dur: 1600, anim: idleAnim, caption: 'Tu nettoies',
        under: (sc, t) => {
          const bx = lerp(W + 1, 28, t / 1300);
          for (let i = 0; i < Math.min(poops, POOP_X.length); i++) if (POOP_X[i] < bx - 2) drawPoop(sc, i, t);
        },
        over: (sc, t) => {
          const bx = lerp(W + 1, 28, t / 1300) + (Math.floor(t / 90) % 2);
          sc.prop('balai', bx, FLOOR - 9);
          if (t < 1300) for (let i = 0; i < 3; i++) sc.px(bx + 5 + ((t / 60 + i * 3) % 6), FLOOR - 1 - (i % 2), 'rgba(200,180,140,0.9)');
        },
      };
    case 'nourrir':
      return {
        dur: 1900, anim: idleAnim === 'dort' ? 'dort' : 'faim', caption: 'Tu nourris Washi',
        under: (sc, t, k) => sc.prop('bol', bowlX(k), FLOOR - 3, t < 1300 ? 999 : 0),
        over: (sc, t, k) => {
          const bx = bowlX(k);
          const y = t < 500 ? lerp(-8, 8, t / 500) : t < 1500 ? 8 + (Math.floor(t / 120) % 2) : lerp(8, -8, (t - 1500) / 400);
          sc.prop('main', bx - 1, y);
          if (t > 500 && t < 1600) for (let i = 0; i < 6; i++) {
            const p = ((t - 500) / 600 + i / 6) % 1;
            sc.prop('miette', bx + 1 + (i % 4) + (i % 2), 15 + p * (FLOOR - 19));
          }
        },
      };
    case 'coussin': {
      // un coussin tombe devant Washi, qui s'en occupe… avec beaucoup d'entrain
      let base: Box | null = null; // position de Washi sans le mouvement
      const at = (k: Box, _t: number) => (base ??= { ...k }); // 1re image : pas encore de mouvement
      return {
        dur: 2800, anim: 'calme', caption: 'Tu donnes un coussin à Washi',
        offset: (t) => (base ? humpOffset(base, t, 800, 2500) : [0, 0]),
        under: (sc, t, k) => drawCushion(sc, t, at(k, t), false, t < 500 ? 500 : 0),
        over: (sc, t, k) => {
          const b = at(k, t);
          if (t < 500) { if (hugs(b)) drawCushion(sc, t, b, true, 500); return; }
          drawCushion(sc, t, b, true);
          if (t > 800 && t < 2500) {
            smallHeart(sc, t - 800, k, 800);
            if (Math.floor(t / 110) % 2) { sc.px(k.x + k.w + 1, k.y + Math.floor(k.h / 2), '#ffffff'); sc.px(k.x + k.w + 2, k.y + Math.floor(k.h / 2) + 1, '#ffffff'); }
          }
        },
      };
    }
    case 'calin':
      return {
        dur: 1700, anim: idleAnim === 'dort' ? 'dort' : 'content', caption: 'Tu fais un câlin',
        over: (sc, t, k) => {
          const rmax = Math.max(k.w, k.h) * 0.75 + 4;
          bigHeart(sc, k, lerp(1, rmax, t / 1100), t > 1100);
        },
      };
    case 'bisou':
      return {
        dur: 1300, anim: idleAnim, caption: 'Tu fais un bisou',
        onStart: onKiss,
        over: (sc, t, k) => {
          if (t < 1100) sc.prop('bouche', k.x - 6, k.y + Math.floor(k.h / 3) - 2, t < 500 ? 0 : 999);
          if (t > 500) smallHeart(sc, t - 500, { ...k, x: k.x - 6 }, 1200);
        },
      };
  }
}

// Textes des réactions : des exclamations, pour ne pas se confondre avec l'état affiché ensuite.
const CAPTIONS: Record<Reaction, string> = {
  mange: 'Miam, miam !', refuse: 'Non merci, plus faim !', content: 'Il a adoré ça !',
  sendort: "Il s'endort dans tes bras…", fete: 'Youpiii !', pascontent: "Grrr, il n'a pas aimé !",
  reveille: "Oh ! Tu l'as réveillé…", dortsourit: 'Il sourit en dormant', apaise: 'Ça le calme un peu…',
  propre: 'Tout propre !', rien: 'Rien à nettoyer', surexcite: 'Il est tout excité, il ne lâche plus le coussin !',
  caca: 'Oups ! Washi a fait caca…',
  amuse: "Il s'est bien occupé du coussin !", blotti: 'Il se blottit contre toi…', bisou: 'Il te fait un bisou aussi !',
  pardonne: 'Il te pardonne !', ravi: "C'est exactement ce qu'il voulait !",
  bof: "Bof… ce n'est pas ce qu'il voulait", beurk: 'Beurk, assez de bisous pour aujourd’hui !',
};

export function reactionClip(r: Reaction): Clip {
  const c: Clip = { dur: 1500, anim: r, caption: CAPTIONS[r], decor: true };
  switch (r) {
    case 'mange':
      c.dur = 2000;
      c.under = (sc, t, k) => sc.prop('bol', bowlX(k), FLOOR - 3, t < 1400 ? 0 : 999);
      c.offset = (t) => [-2, Math.floor(t / 250) % 2];
      break;
    case 'refuse':
      c.under = (sc, t, k) => sc.prop('bol', bowlX(k), FLOOR - 3, 0);
      c.over = (sc, t, k) => bubble(sc, k, (x, y) => sc.prop('croix', x + 2, y + 1));
      break;
    case 'content': c.over = (sc, t, k) => smallHeart(sc, t, k, 1500); break;
    case 'apaise': c.dur = 1600; c.over = (sc, t, k) => smallHeart(sc, t, k, 1600); break;
    case 'fete': c.dur = 2000; c.over = (sc, t, k) => confetti(sc, t, 30); break;
    case 'pascontent': c.over = (sc, t, k) => sc.prop('nuage', k.x + k.w - 2, Math.max(0, k.y - 6), t); break;
    case 'reveille': c.dur = 1100; c.over = (sc, t, k) => sc.prop('exclam', k.x + k.w + 1, Math.max(0, k.y - 6)); break;
    case 'propre': c.over = (sc, t, k) => { smallHeart(sc, t, k, 1500); sparkles(sc, t); }; break;
    case 'rien': c.dur = 1100; break;
    case 'surexcite': c.dur = 1800; c.over = (sc, t, k) => { if (t % 500 < 350) sc.prop('exclam', k.x + k.w + 1, Math.max(0, k.y - 6)); }; break;
    case 'caca': c.dur = 1800; break;
    case 'sendort': c.dur = 1800; c.over = (sc, t, k) => floatingZ(sc, t, k); break;
    case 'dortsourit': c.dur = 1800; c.over = (sc, t, k) => { floatingZ(sc, t, k); smallHeart(sc, t, k, 1800); }; break;
    // une réaction propre à chaque soin : coussin puis étoiles pour le coussin, ondes douces pour câlin, bisou rendu pour bisou
    case 'amuse': { // il finit avec le coussin, puis fait le fier
      let base: Box | null = null;
      const at = (k: Box, _t: number) => (base ??= { ...k }); // 1re image : pas encore de mouvement
      c.dur = 1800; c.offset = (t) => (base ? humpOffset(base, t, 0, 900) : [0, 0]);
      c.under = (sc, t, k) => { if (t < 1300) drawCushion(sc, t, at(k, t), false); };
      c.over = (sc, t, k) => { if (t < 1300) drawCushion(sc, t, at(k, t), true); if (t > 900) stars(sc, t, k); };
      break;
    }
    case 'blotti': c.dur = 1800; c.offset = (t) => [0, t > 200 && t < 1500 ? 1 : 0]; c.over = (sc, t, k) => softWaves(sc, t, k); break;
    case 'bisou': c.dur = 1600; c.over = (sc, t, k) => kissBack(sc, t, k); break;
    case 'pardonne': c.dur = 1800; c.over = (sc, t, k) => { bigHeart(sc, k, lerp(3, 7, Math.min(1, t / 700)), t > 700); kissBack(sc, t, k); }; break;
    case 'ravi': c.dur = 1500; c.over = (sc, t, k) => { sparkles(sc, t, k.x - 3, k.y - 2, k.w + 6); smallHeart(sc, t, k, 1500); }; break;
    case 'bof': c.dur = 1400; c.over = (sc, t, k) => bubble(sc, k, (x, y) => { for (let i = 0; i < 3; i++) if (t > 250 * (i + 1)) sc.px(x + 1 + i * 3, y + 3, '#3b2414'); }); break;
    case 'beurk': c.dur = 1600; c.over = (sc, t, k) => bubble(sc, k, (x, y) => { sc.prop('bouche', x + 1, y + 1); if (t % 600 < 400) sc.prop('croix', x + 2, y); }); break;
  }
  return c;
}

/** Petites étincelles (par défaut sur le sol propre). */
function sparkles(sc: Scene, t: number, x0 = 32, y0 = FLOOR - 3, w = 16) {
  for (let i = 0; i < 4; i++) {
    if ((t / 200 + i) % 3 > 1.5) continue;
    const x = x0 + Math.round((i * w) / 4), y = y0 - (i % 2) * 2;
    sc.px(x, y, '#ffffff'); sc.px(x - 1, y, '#fbf6d8'); sc.px(x + 1, y, '#fbf6d8'); sc.px(x, y - 1, '#fbf6d8'); sc.px(x, y + 1, '#fbf6d8');
  }
}

/** Coussin : petites étoiles jaunes qui sautent autour de la tête. */
function stars(sc: Scene, t: number, k: Box) {
  for (let i = 0; i < 3; i++) {
    const p = ((t / 900) + i / 3) % 1;
    const x = k.x - 2 + i * Math.round((k.w + 4) / 2), y = k.y - 1 - Math.round(Math.sin(p * Math.PI) * 5);
    sc.px(x, y, '#f5d742'); sc.px(x - 1, y, '#fbf6d8'); sc.px(x + 1, y, '#fbf6d8'); sc.px(x, y - 1, '#fbf6d8'); sc.px(x, y + 1, '#fbf6d8');
  }
}

/** Câlin : ondes roses qui s'élargissent doucement autour du kikou. */
function softWaves(sc: Scene, t: number, k: Box) {
  const cx = k.x + k.w / 2, cy = k.y + k.h / 2;
  for (let j = 0; j < 2; j++) {
    const p = ((t / 1400) + j * 0.5) % 1;
    const r = Math.max(k.w, k.h) / 2 + 1 + p * 6;
    const col = `rgba(242,163,163,${(1 - p).toFixed(2)})`;
    for (let a = -Math.PI * 0.9; a < -Math.PI * 0.1; a += 0.18) sc.px(cx + Math.cos(a) * r, cy + Math.sin(a) * r, col);
  }
}

/** Bisou rendu : des lèvres de son côté, puis un cœur rouge qui monte. */
function kissBack(sc: Scene, t: number, k: Box) {
  if (t < 700) sc.prop('bouche', k.x + k.w - 1, k.y + Math.floor(k.h / 3) - 2, 0, true);
  if (t > 400) sc.prop('coeur', k.x + k.w + 1, k.y - 1 - ((t - 400) / 1200) * 7);
}

/** Arrivée : Washi sort du carton couché sur le côté et roule jusqu'au centre. */
export function introClip(stage: number): Clip {
  return {
    dur: 4200, anim: 'calme', stage: () => stage, caption: 'Un carton… quelque chose bouge dedans !',
    under: (sc, t) => sc.prop('carton', 1, FLOOR - 11),
    offset: (t) => {
      if (t < 1600) return [-15, -3 + (t > 900 && Math.floor(t / 150) % 2 ? -1 : 0)];
      const p = Math.min(1, (t - 1600) / 1800);
      return [Math.round(lerp(-15, 0, p)), -Math.round(Math.abs(Math.sin(p * Math.PI * 3)) * 3 * (1 - p))];
    },
    hideKikou: (t) => t < 900,
    over: (sc, t) => { if (t > 900 && t < 1500) sc.prop('exclam', 13, 18); },
  };
}

/** Évolution : Washi s'étire, petit flash, nouvelle silhouette. */
export function evolveClip(from: number, to: number): Clip {
  return {
    dur: 2600, anim: 'content', caption: 'Washi grandit !',
    stage: (t) => (t < 1500 ? (Math.floor(t / (260 - t / 8)) % 2 ? to : from) : to),
    over: (sc, t) => {
      if (t > 1300 && t < 1700) { sc.ctx.fillStyle = `rgba(255,255,255,${1 - Math.abs(t - 1500) / 200})`; sc.ctx.fillRect(0, 0, W, H); }
      if (t > 1500) confetti(sc, t, 16);
    },
  };
}

/** Washi s'en va (départ). */
export function goneClip(stage: number): Clip {
  return {
    dur: 2600, anim: 'grognon', stage: () => stage, caption: 'Washi s’en va…',
    offset: (t) => [Math.round(lerp(0, 36, t / 2400)), 0],
  };
}

export type { Scene };
