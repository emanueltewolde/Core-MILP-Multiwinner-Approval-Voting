\ Model Core
\ LP format - for model browsing. Use MPS format to capture full model detail.
Maximize
  v
Subject To
 simplex_constraint: x[0] + x[1] + x[2] + x[3] = 1
 y-constraint: y[0,0] + y[0,1] >= 1
 y-constraint: y[1,0] + y[1,1] >= 1
 minmax_constraint: 3 y[0,0] + v <= 2.5
 minmax_constraint: - x[2] + 3 y[0,1] + v <= 2.5
 minmax_constraint: - x[1] + 3 y[1,0] + v <= 2.5
 minmax_constraint: 3 y[1,1] + v <= 2.5
Bounds
 x[0] <= 1
 x[1] <= 1
 x[2] <= 1
 x[3] <= 1
 -2 <= v <= 2
Binaries
 y[0,0] y[0,1] y[1,0] y[1,1]
End
