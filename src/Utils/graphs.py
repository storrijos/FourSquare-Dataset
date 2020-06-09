import numpy as np
import matplotlib.pyplot as plt


def graph_mae():
    convoy_values = [0.3525040793, 0.3525040793, 0.3525040793, 0.3525040793, 0.3525040793, 0.3525040793]
    dtw_values = [1.290312806,	2.839748133,	5.424707961,	8.421931016,	10.99929635,	13.69066971]
    flock_values = [0.3525040793, 0.3525040793, 0.3525040793, 0.3525040793, 0.3525040793, 0.3525040793]
    hauss_values = [0.5784518469,	0.7879834728,	1.673699473,	4.340679077,	8.155504729,	12.57900271]
    stdbscan_values = [0.3530356993, 0.3530356993, 0.3530356993, 0.3530356993, 0.3530356993, 0.3530356993]
    adhoc_values = [0.3487827392,	0.3487827392,	0.3487827392,	0.3487827392,	0.3487827392,	0.3487827392]

    x_values = [10, 20, 40, 80, 160, 300]
    xi = list(range(len(x_values)))
    plt.xticks(xi, x_values)

    plt.plot(xi, convoy_values, "-b", label="Convoy")
    plt.plot(xi, dtw_values, "-c", label="DTW")
    plt.plot(xi, flock_values, "-y", label="Flock")
    plt.plot(xi, hauss_values, "-g", label="Hauss")
    plt.plot(xi, stdbscan_values, "-m", label="ST-DBSCAN")
    plt.plot(xi, adhoc_values, "-r", label="Adhoc")
    plt.legend(loc="upper left")
    plt.title('Comparativa MAE')
    plt.xlabel('Número de vecinos')
    plt.ylabel('MAE')

    plt.show()

def graph_precision():
    convoy_values = [0.03683774834, 0.03683774834, 0.03683774834, 0.03683774834, 0.03683774834, 0.03683774834]
    dtw_values = [0.01332781457,0.009768211921,	0.008857615894,	0.01208609272,	0.01655629139,	0.02061258278]
    flock_values = [0.0369205298,	0.0369205298,	0.0369205298,	0.0369205298,	0.0369205298,	0.0369205298]
    hauss_values = [0.005380794702,	0.004966887417,	0.005463576159,	0.007036423841,	0.009105960265,	0.01754966887]
    stdbscan_values = [0.0369205298,	0.0369205298,	0.0369205298,	0.0369205298,	0.0369205298,	0.0369205298]
    adhoc_values = [0.03493377483, 0.03493377483, 0.03493377483, 0.03493377483, 0.03493377483, 0.03493377483]
    x_values = [10, 20, 40, 80, 160, 300]
    xi = list(range(len(x_values)))
    plt.xticks(xi, x_values)

    plt.plot(xi, convoy_values, "-b", label="Convoy")
    plt.plot(xi, dtw_values, "-c", label="DTW")
    plt.plot(xi, flock_values, "-y", label="Flock")
    plt.plot(xi, hauss_values, "-g", label="Hauss")
    plt.plot(xi, stdbscan_values, "-m", label="ST-DBSCAN")
    plt.plot(xi, adhoc_values, "-r", label="Adhoc")
    plt.legend(loc="upper left")
    plt.title('Comparativa Precisión')
    plt.xlabel('Número de vecinos')
    plt.ylabel('Precisión')

    plt.show()

def comparativa_recomendador():

    KNN_Convoy = 0.352504
    KNN_DTW =1.290313
    KNN_Flock= 0.352504
    KNN_Hauss=0.578452
    KNN_ST_DBSCAN=0.353036
    SVD=0.333831
    Random=0.475569
    KNN_Baseline=0.343762
    NMF=0.272056

    elems = [KNN_Convoy, KNN_DTW, KNN_Flock, KNN_Hauss, KNN_ST_DBSCAN, SVD, Random, KNN_Baseline, NMF]
    objects = ('KNN_Convoy', 'KNN_DTW', 'KNN_Flock', 'KNN_Hauss', 'KNN_ST_DBSCAN', 'SVD', 'Random', 'KNN_Baseline', 'NMF')

    x = np.arange(9)

    plt.bar(x, elems, align='center', alpha=0.5)
    plt.xticks(x, objects, rotation=90)
    plt.tight_layout()
    plt.ylabel('MAE')
    plt.title('Comparativa MAE utilizando vecinos vs recomendadores')

    plt.show()
if __name__ == "__main__":
    graph_precision()
    graph_mae()
    comparativa_recomendador()
