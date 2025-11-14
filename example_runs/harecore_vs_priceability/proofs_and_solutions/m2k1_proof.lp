\ Model Core
\ LP format - for model browsing. Use MPS format to capture full model detail.
Minimize
  0 g[0,0] + 0 g[0,1] + 0 g[0,2] + 0 g[0,3] + 0 g[1,0] + 0 g[1,2] + 0 g[1,3]
   + 0 g[2,0] + 0 g[2,1] + 0 g[2,2] + 0 g[2,3] + 0 g[3,0] + 0 g[3,1]
   + 0 g[3,2] + v
Subject To
 simplex_constraint: x[0] + x[1] + x[2] + x[3] = 1
 minmax_constraint: - x[1] + v >= -1
 dual_constraint: t[0] + t[1] <= 1
 R3: g[1,1] + g[3,3] = 1
 qc0: - g[1,1] + [ x[1] * t[0] ] >= 0
 qc1: [ x[2] * t[1] ] >= 0
 qc2: - g[3,3] + [ x[3] * t[0] ] >= 0
 qc3: - g[3,3] + [ x[3] * t[1] ] >= 0
Bounds
 x[0] <= 1
 x[1] <= 1
 x[2] <= 1
 x[3] <= 1
 -2 <= v <= 2
End
