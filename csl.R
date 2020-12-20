library('pcalg')
library('ParallelPC')
library('parallel')
library('graph')

df <- read.csv( paste0("./observations_disc.csv"),sep=",", header=TRUE, check.names=FALSE)
num.cores <-40
p <- ncol(df)
df <- data.matrix(df)
nlev <- vapply(seq_len(p), function(j) length(levels(factor(df[,j]))), 1L)
sufficient_stats <- list(dm=df, adaptDF=FALSE, nlev=nlev)
res <- pc_parallel(sufficient_stats, indepTest=disCItest, p=p, skel.method="parallel", alpha=0.01, num.cores=num.cores)

edges <- edges(res@'graph')
edge_list <- list(from_node=c(), to_node=c())
i <- 1
for (node in names(edges)){
	for (edge in edges[[node]]){
		edge_list[['from_node']][[i]] <- colnames(df)[strtoi(node)]
        edge_list[['to_node']][[i]] <- colnames(df)[strtoi(edge)]
        i <- i + 1
    }
}
edge_list <- data.frame(edge_list)

write.csv(edge_list, './edges.csv', row.names=FALSE)
