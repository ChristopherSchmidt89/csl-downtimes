library('causaleffect')
library('igraph')

edge_list <- read.csv('./edgeExample.csv',sep=",")
x <- as.matrix(edge_list)
u <- graph_from_edgelist(x, directed = TRUE)
Formular  <- causal.effect(y = "s1", x = "qcspeed", z = NULL, G = u, expr = T)
cat(Formular, '\n')
