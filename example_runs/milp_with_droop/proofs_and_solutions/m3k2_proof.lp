\ Model Core
\ LP format - for model browsing. Use MPS format to capture full model detail.
Maximize
  0 y[0,0] + 0 y[0,1] + 0 y[1,0] + 0 y[1,2] + 0 y[2,1] + 0 y[2,2] + v
Subject To
 simplex_constraint: x[0] + x[1] + x[2] + x[3] + x[4] + x[5] + x[6] + x[7]
   = 1
 y-constraint: y[0,2] >= 1
 y-constraint: y[1,1] >= 1
 y-constraint: y[2,0] >= 1
 minmax_constraint: - x[3] + 3 y[0,2] + v <= 2.666666666666667
 minmax_constraint: - x[2] + 3 y[1,1] + v <= 2.666666666666667
 minmax_constraint: - x[1] + 3 y[2,0] + v <= 2.666666666666667
Bounds
 x[0] <= 1
 x[1] <= 1
 x[2] <= 1
 x[3] <= 1
 x[4] <= 1
 x[5] <= 1
 x[6] <= 1
 x[7] <= 1
 -2 <= v <= 2
Binaries
 y[0,0] y[0,1] y[0,2] y[1,0] y[1,1] y[1,2] y[2,0] y[2,1] y[2,2]
End
