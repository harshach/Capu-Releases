/* <capu-mascot mood="idle|wave|loading|working|think|celebrate|sleep" size="96" part="full|head|icon" still>  icon = full figure cropped tight, for app icons */
(function () {
  if (customElements.get("capu-mascot")) return;
  const MAP = [
    "....HHHHH.....",
    "...HHHHHHH....",
    "..HFFFFFFFH...",
    ".LHFEFFFEFHR..",
    ".LHFEFFFEFHR..",
    "..HFFFFFFFH...",
    "..HHFFMFFHH...",
    "...HHHHHHH....",
    "....HHHHH.....",
    "...HHHHHHH...T",
    "..AHHHHHHHB..T",
    "..AHHFFFHHB..T",
    "...HHFFFHH.TT.",
    "...PP...PPTT.."
  ];
  const STOPS = [[1, [20, 184, 166]], [5, [34, 197, 94]], [8, [59, 130, 246]], [12, [139, 92, 246]]];
  const lerp = (a, b, t) => a.map((v, i) => Math.round(v + (b[i] - v) * t));
  const colAt = c => { for (let i = 0; i < STOPS.length - 1; i++) { const [c0, a] = STOPS[i], [c1, b] = STOPS[i + 1]; if (c <= c1) return lerp(a, b, Math.max(0, (c - c0) / (c1 - c0))); } return STOPS[STOPS.length - 1][1]; };
  const mix = (rgb, w, t) => lerp(rgb, w, t);
  const hex = rgb => "#" + rgb.map(v => v.toString(16).padStart(2, "0")).join("");
  const W = [255, 255, 255], K = [10, 10, 22];
  const px = (x, y, fill) => `<rect x="${x}" y="${y}" width="1.04" height="1.04" fill="${fill}"/>`;
  function build(part) {
    const g = { head: [], eyes: [], body: [], armL: [], armR: [], tail: [], feet: [] };
    MAP.forEach((row, y) => [...row].forEach((ch, x) => {
      if (ch === ".") return;
      let base = colAt(x);
      if (y <= 1) base = mix(base, W, 0.12);
      if (y >= 9) base = mix(base, K, 0.06);
      const face = mix(colAt(x), W, 0.62);
      const fill = ch === "H" ? hex(base) : ch === "F" ? hex(face) : ch === "E" ? "#0A0A16" : ch === "M" ? hex(mix(colAt(x), K, 0.35)) : ch === "L" ? "#FDBA9A" : ch === "R" ? "#C4B5FD" : ch === "T" ? hex(y > 11 ? [147, 92, 246] : [168, 85, 247]) : ch === "P" ? hex(mix(colAt(x), W, 0.5)) : hex(base);
      const key = ch === "E" ? "eyes" : ch === "A" ? "armL" : ch === "B" ? "armR" : ch === "T" ? "tail" : ch === "P" ? "feet" : y <= 7 ? "head" : "body";
      g[key].push(px(x, y, fill));
    }));
    const spark = (x, y, d, c) => `<g class="sp" style="transform-origin:${x + .5}px ${y + .5}px;animation-delay:${d}s"><rect x="${x}" y="${y - 1}" width="1" height="3" fill="${c}"/><rect x="${x - 1}" y="${y}" width="3" height="1" fill="${c}"/></g>`;
    const vb = part === "head" ? "0.6 -0.4 12.8 9" : part === "icon" ? "-0.4 -0.7 14.8 15.6" : "-3 -5 20 20";
    return { vb, svg: `
      <ellipse class="sh" cx="7" cy="14.4" rx="4.2" ry=".7" fill="rgba(0,0,0,.32)"/>
      <g class="sparks">${spark(-1.5, 2, 0, "#FDE68A")}${spark(15, 0, .25, "#A5F3FC")}${spark(14, 8, .5, "#F9A8D4")}${spark(-2, 9, .7, "#C4B5FD")}</g>
      <g class="zz"><rect class="z1" x="12" y="-1" width="2" height=".5" fill="#C4B5FD"/><rect class="z1" x="13.5" y="-1" width=".5" height="2" fill="#C4B5FD" transform="rotate(0)"/></g>
      <g class="q"><rect x="6.4" y="-4.2" width="2" height=".8" fill="#FDE68A"/><rect x="8" y="-3.6" width=".8" height="1.4" fill="#FDE68A"/><rect x="7.2" y="-2.4" width=".8" height="1" fill="#FDE68A"/><rect x="7.2" y="-.9" width=".8" height=".8" fill="#FDE68A"/></g>
      <g class="root">
        <g class="tail">${g.tail.join("")}</g>
        <g class="body">${g.body.join("")}${g.feet.join("")}</g>
        <g class="armL">${g.armL.join("")}</g>
        <g class="armR">${g.armR.join("")}</g>
        <g class="head">${g.head.join("")}<g class="eyes">${g.eyes.join("")}</g></g>
      </g>` };
  }
  const CSS = `
    :host{display:inline-block;line-height:0}
    svg{overflow:visible;shape-rendering:crispEdges;display:block}
    g,ellipse,rect{transform-box:view-box}
    .tail{transform-origin:10.5px 13.5px;animation:cm-wag 1.6s ease-in-out infinite}
    .eyes{transform-origin:6.5px 5px;animation:cm-blink 4.6s steps(1) infinite}
    .root{animation:cm-bob 2.8s steps(2) infinite}
    .head{transform-origin:6.5px 8px}
    .armL{transform-origin:3px 10px}.armR{transform-origin:10px 10px}
    .sh{transform-origin:7px 14.4px}
    .sparks,.zz,.q{display:none}
    :host([mood=wave]) .armR{animation:cm-wave 1.1s ease-in-out infinite}
    :host([mood=loading]) .root{animation:cm-hop .72s cubic-bezier(.3,.7,.4,1) infinite}
    :host([mood=loading]) .sh{animation:cm-squash .72s cubic-bezier(.3,.7,.4,1) infinite}
    :host([mood=loading]) .tail{animation-duration:.5s}
    :host([mood=working]) .eyes{animation:cm-look 2.6s steps(1) infinite}
    :host([mood=working]) .head{animation:cm-nod 1.3s steps(2) infinite}
    :host([mood=working]) .armL,:host([mood=working]) .armR{animation:cm-type .32s steps(2) infinite}
    :host([mood=working]) .armR{animation-delay:.16s}
    :host([mood=working]) .tail{animation-duration:2.4s}
    :host([mood=think]) .head{animation:cm-tilt 2.2s ease-in-out infinite}
    :host([mood=think]) .q{display:block;animation:cm-blinkq 1.1s steps(1) infinite}
    :host([mood=think]) .eyes{transform:translateY(-.4px);animation:none}
    :host([mood=celebrate]) .root{animation:cm-jump .9s cubic-bezier(.3,.7,.4,1) infinite}
    :host([mood=celebrate]) .sh{animation:cm-squash2 .9s cubic-bezier(.3,.7,.4,1) infinite}
    :host([mood=celebrate]) .armL{animation:cm-armL .9s ease-in-out infinite}
    :host([mood=celebrate]) .armR{animation:cm-armR .9s ease-in-out infinite}
    :host([mood=celebrate]) .tail{animation-duration:.36s}
    :host([mood=celebrate]) .sparks{display:block}
    :host([mood=celebrate]) .sp{animation:cm-spark .9s ease-out infinite}
    :host([mood=sleep]) .eyes{transform:scaleY(.18);animation:none}
    :host([mood=sleep]) .root{animation:cm-bob 3.6s ease-in-out infinite}
    :host([mood=sleep]) .tail{animation:none;transform:rotate(-8deg)}
    :host([mood=sleep]) .zz{display:block;animation:cm-z 2.4s ease-out infinite}
    :host([part=head]) .tail,:host([part=head]) .body,:host([part=head]) .armL,:host([part=head]) .armR,:host([part=head]) .sh{display:none}
    :host([part=head]) .root{animation:none}
    :host([still]) *{animation:none!important}
    @keyframes cm-wag{0%,100%{transform:rotate(-12deg)}50%{transform:rotate(16deg)}}
    @keyframes cm-blink{0%,93%{transform:scaleY(1)}94%,97%{transform:scaleY(.15)}98%,100%{transform:scaleY(1)}}
    @keyframes cm-bob{0%,100%{transform:translateY(0)}50%{transform:translateY(.5px)}}
    @keyframes cm-hop{0%,100%{transform:translateY(0) scale(1,1)}10%{transform:translateY(.3px) scale(1.04,.96)}45%{transform:translateY(-2.2px)}60%{transform:translateY(-2.2px)}90%{transform:translateY(0)}}
    @keyframes cm-squash{0%,100%{transform:scaleX(1);opacity:1}45%,60%{transform:scaleX(.6);opacity:.5}}
    @keyframes cm-squash2{0%,100%{transform:scaleX(1);opacity:1}40%,55%{transform:scaleX(.45);opacity:.35}}
    @keyframes cm-look{0%,30%{transform:translateX(0)}31%,60%{transform:translateX(.6px)}61%,90%{transform:translateX(-.6px)}91%,100%{transform:translateX(0)}}
    @keyframes cm-nod{0%,100%{transform:translateY(0)}50%{transform:translateY(.4px)}}
    @keyframes cm-type{0%,100%{transform:translateY(0)}50%{transform:translateY(-.6px)}}
    @keyframes cm-tilt{0%,100%{transform:rotate(-7deg)}50%{transform:rotate(5deg)}}
    @keyframes cm-blinkq{0%,60%{opacity:1}61%,100%{opacity:.25}}
    @keyframes cm-wave{0%,100%{transform:rotate(0)}20%,60%{transform:rotate(-150deg)}40%,80%{transform:rotate(-110deg)}}
    @keyframes cm-jump{0%,100%{transform:translateY(0)}12%{transform:translateY(.4px) scale(1.05,.95)}40%,52%{transform:translateY(-3.4px)}80%{transform:translateY(0)}}
    @keyframes cm-armL{0%,100%{transform:rotate(0)}40%,55%{transform:rotate(150deg)}}
    @keyframes cm-armR{0%,100%{transform:rotate(0)}40%,55%{transform:rotate(-150deg)}}
    @keyframes cm-spark{0%{transform:scale(0);opacity:0}35%{transform:scale(1);opacity:1}70%,100%{transform:scale(.2);opacity:0}}
    @keyframes cm-z{0%{transform:translate(0,1px);opacity:0}30%{opacity:1}100%{transform:translate(1.6px,-3px);opacity:0}}
    @media (prefers-reduced-motion: reduce){*{animation:none!important}}
  `;
  class CapuMascot extends HTMLElement {
    static get observedAttributes() { return ["mood", "size", "part", "still"]; }
    constructor() { super(); this.attachShadow({ mode: "open" }); }
    set mood(v) { this.setAttribute("mood", v); } get mood() { return this.getAttribute("mood"); }
    set size(v) { this.setAttribute("size", v); } get size() { return this.getAttribute("size"); }
    set part(v) { this.setAttribute("part", v); } get part() { return this.getAttribute("part"); }
    connectedCallback() { if (!this.hasAttribute("mood")) this.setAttribute("mood", "idle"); this.render(); }
    attributeChangedCallback(n) { if (n !== "mood" && this.isConnected) this.render(); }
    render() {
      const part = this.getAttribute("part") || "full", size = Number(this.getAttribute("size")) || 96;
      if (this._k === part + size && this.shadowRoot.firstChild) return;
      this._k = part + size;
      const b = build(part), [, , vw, vh] = b.vb.split(" ").map(Number);
      this.shadowRoot.innerHTML = `<style>${CSS}</style><svg width="${size}" height="${Math.round(size * vh / vw)}" viewBox="${b.vb}" aria-hidden="true">${b.svg}</svg>`;
    }
  }
  customElements.define("capu-mascot", CapuMascot);
})();
