"""Shared pieces of the HTML pages concepts.py writes (graph.html, modes.html): chess boards drawn
as SVG with python-chess's piece set, and a latent's card.

    BOARD_DEFS, MOVE_HEAD   put once in the page body (piece shapes, the move arrow's head)
    BOARD_CSS               goes in the page's <style>
    BOARD_JS                goes in the page's <script>: board(fen, uci, cls) draws a position
                            from the side to move's point of view, the move as an arrow and its
                            squares highlighted (cls "sm" = a small board, no arrow);
                            latentHTML(j) is a latent's card and needs D.nodes, D.A, D.B on the page
"""
import chess.svg

BOARD_DEFS = ('<svg width="0" height="0" style="position:absolute"><defs>'
              + "".join(chess.svg.PIECES.values()) + "</defs></svg>")
BOARD_CSS = """.bd{display:block;margin:4px 0}.mv{font-family:monospace;font-size:12px;margin-bottom:10px}
.why{margin:4px 0 6px;padding:4px 6px;background:#f3f1ea;border-radius:4px;font-size:12px}"""
BOARD_JS = r"""const PIECE = {k: "king", q: "queen", r: "rook", b: "bishop", n: "knight", p: "pawn"};
function board(fen, uci, cls) {
  const q = cls === "sm" ? 16 : 32, W = 8 * q, flip = fen.split(" ")[1] === "b";   // the side to move at the bottom
  const xy = sq => { const f = sq.charCodeAt(0) - 97, r = +sq[1] - 1;
                     return flip ? [(7 - f) * q, r * q] : [f * q, (7 - r) * q]; };
  let h = `<svg class="bd" width="${W}" height="${W}" viewBox="0 0 ${W} ${W}">`;
  for (let r = 0; r < 8; r++) for (let f = 0; f < 8; f++)
    h += `<rect x="${f * q}" y="${r * q}" width="${q}" height="${q}" fill="${(r + f) % 2 ? "#b58863" : "#f0d9b5"}"/>`;
  if (uci) for (const sq of [uci.slice(0, 2), uci.slice(2, 4)]) {
    const [x, y] = xy(sq); h += `<rect x="${x}" y="${y}" width="${q}" height="${q}" fill="#cdd26a" fill-opacity="0.75"/>`; }
  fen.split(" ")[0].split("/").forEach((row, r) => {
    let f = 0;
    for (const ch of row) {
      if (/\d/.test(ch)) { f += +ch; continue; }
      const [x, y] = xy("abcdefgh"[f] + (8 - r));
      h += `<use href="#${ch === ch.toUpperCase() ? "white" : "black"}-${PIECE[ch.toLowerCase()]}" transform="translate(${x},${y}) scale(${q / 45})"/>`;
      f++;
    }
  });
  if (uci && q > 16) {
    const [x1, y1] = xy(uci.slice(0, 2)), [x2, y2] = xy(uci.slice(2, 4)), c = q / 2;
    h += `<line x1="${x1 + c}" y1="${y1 + c}" x2="${x2 + c}" y2="${y2 + c}" stroke="#15781b" stroke-width="${q / 7}"
          stroke-opacity="0.8" stroke-linecap="round" marker-end="url(#mvhead)"/>`;
  }
  return h + "</svg>";
}
// A latent's explanation (explain.py): the predicate that predicts its firing and its held-out
// score, facts nearly always true when it fires, then what its top positions share (d.why)
function explHTML(d, short) {
  const e = d.expl, p = x => (100 * x).toFixed(0) + "%";
  let h = "";
  if (!e) h += "";
  else if (e.status === "too rare") h += `<div class="why">fires too rarely to score an explanation</div>`;
  else {
    const col = {explained: "#1d7a2e", weak: "#a66b00", unexplained: "#999"}[e.status];
    h += `<div class="why" style="border-left:4px solid ${col}"><b style="color:${col}">${e.status}</b>`;
    h += e.status === "unexplained" ? ` (best guess: ${e.explanation}, F1 ${e.f1.toFixed(2)})`
       : `: fires when <b>${e.explanation}</b><br><span style="color:#666">held-out F1 ${e.f1.toFixed(2)}
          (precision ${p(e.precision)}, recall ${p(e.recall)}; an unrelated fact: ${e.f1_null.toFixed(2)})</span>`;
    if (!short && e.always && e.always.length)
      h += "<br>when it fires, also: " + e.always.map(([n, t, r, b]) => `${t} (${p(r)} vs ${p(b)} overall)`).join("; ");
    h += "</div>";
    // engine link: how far Stockfish's evaluation where it fires is from what the board predicts
    if (e.engine_text) h += `<div class="why"${e.engine_linked ? ' style="border-left:4px solid #5b6bd6"' : ""}>`
      + `${e.engine_linked ? "<b>engine-linked</b>: " : "Stockfish: "}${e.engine_text}</div>`;
  }
  if (d.why && (!short || !e)) h += `<div class="why">${d.why}</div>`;
  return h;
}
function latentHTML(j) {
  const d = D.nodes[j];
  let h = `<b>latent ${j}</b> &nbsp; fires in ${(100 * d.rate).toFixed(2)}% of positions; decoder ${(100 * (1 - d.r)).toFixed(0)}% ${D.A} / ${(100 * d.r).toFixed(0)}% ${D.B}`;
  h += explHTML(d);
  for (const [fen, moves, nxt, uci] of d.ex) {
    const tm = fen.split(" ")[1] === "w" ? "white" : "black";
    h += board(fen, uci) + `<div class="mv">${moves} &rarr; <b>${nxt}</b> (${tm} to move, shown at the bottom)
      <a target="_blank" href="https://lichess.org/analysis/${fen.replace(/ /g, "_")}">lichess</a></div>`;
  }
  return h;
}"""
MOVE_HEAD = ('<svg width="0" height="0" style="position:absolute"><defs><marker id="mvhead" viewBox="0 0 10 10" refX="6" '
             'refY="5" markerWidth="3" markerHeight="3" orient="auto"><path d="M0,0L10,5L0,10z" fill="#15781b"/></marker></defs></svg>')
