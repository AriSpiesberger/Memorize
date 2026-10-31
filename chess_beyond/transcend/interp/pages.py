"""Chess boards for the HTML pages (concept_graph.py's map), drawn as SVG with python-chess's piece set.

    BOARD_DEFS, MOVE_HEAD   put once in the page body (piece shapes, the move arrow's head)
    BOARD_JS                goes in the page's <script>: board(fen, uci, cls) draws a position from the side to move's
                            point of view, the move as an arrow and its squares highlighted (cls "sm" = a small board,
                            no arrow; "md" = medium)
"""
import chess.svg

BOARD_DEFS = ('<svg width="0" height="0" style="position:absolute"><defs>'
              + "".join(chess.svg.PIECES.values()) + "</defs></svg>")
BOARD_JS = r"""const PIECE = {k: "king", q: "queen", r: "rook", b: "bishop", n: "knight", p: "pawn"};
function board(fen, uci, cls) {
  const q = cls === "sm" ? 16 : cls === "md" ? 22 : 32, W = 8 * q, flip = fen.split(" ")[1] === "b";   // the side to move at the bottom
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
"""
MOVE_HEAD = ('<svg width="0" height="0" style="position:absolute"><defs><marker id="mvhead" viewBox="0 0 10 10" refX="6" '
             'refY="5" markerWidth="3" markerHeight="3" orient="auto"><path d="M0,0L10,5L0,10z" fill="#15781b"/></marker></defs></svg>')
