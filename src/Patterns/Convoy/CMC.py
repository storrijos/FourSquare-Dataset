#!/usr/bin/env python
""" generated source for module CMC """
from STPoint import STPoint
from DBSCAN import DBSCAN
from Convoy import Convoy
from src.Utils.utils import progressBar

class CMC:
    """ generated source for class CMC """
    @classmethod
    def cm_clustering(cls, o, m, k, e):
        """ generated source for method cm_clustering """
        Vs = []
        V_Result = []
        #time_interval = len(o[0].points)
        #time_interval = 20
        values = []
        for i in range(len(o)):
            values.append(len(o[i].points))
        time_interval = max(values)
        print('TIME')
        print(time_interval)
        i = 0
        while i < time_interval:
            progressBar(i, time_interval)
            V_Next = []
            tmp_point = []
            snapshot_cluster = []
            for t in o:
                for s in t.points:
                    if s.t == i + 1:
                        tmp_point.append(s)

            if len(tmp_point) < m:
                i += 1 #Check
                continue

            clusters = DBSCAN.dbscan_to_cluster(tmp_point, e, m)
            for c in clusters:
                snapshot_cluster.append(Convoy(cluster=c.oids))
            for v in Vs:
                v.assigned = False
                for c in snapshot_cluster:
                    if len(c.intersection(v).cluster) >= m:
                        v = c.intersection(v)
                        v.assigned = True
                        v.endTime = i + 1
                        V_Next.append(v)
                        c.assigned = True
                if not v.assigned and (v.endTime - v.startTime + 1) >= k:
                    V_Result.append(v)
            for c in snapshot_cluster:
                if not c.assigned:
                    c.startTime = i + 1
                    c.endTime = i + 1
                    V_Next.append(c)
            Vs = V_Next
            i += 1
        return V_Result
