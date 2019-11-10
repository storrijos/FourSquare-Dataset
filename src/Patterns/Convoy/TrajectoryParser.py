#!/usr/bin/env python
""" generated source for module TrajectoryParser """
import csv
from Trajectory import Trajectory
from STPoint import STPoint
import pandas as pd
class TrajectoryParser(object):
    """ generated source for class TrajectoryParser """
    inputFile =""
    reader = None
    delim = ","

    def __init__(self, path):
        """ generated source for method __init__ """

        try:
            self.inputFile = path
            self.reader = csv.reader(open(path), delimiter=',')
        except Exception as e:
            print("Cannot find File.")

    def get_traj_set(self):
        """ generated source for method get_traj_set """
        result = []
        data = pd.read_csv(self.inputFile, nrows=1)
        prev_id = data['obj_id'].values[0]
        try:

            tmp = None
            index = 0
            for line in self.reader:

                if index == 0:
                    index = index + 1
                    continue
                obj_id = int(line[0])
                if tmp == None:
                    tmp = Trajectory(obj_id)

                if tmp != None and obj_id != prev_id:
                    result.append(tmp)
                    tmp = Trajectory(obj_id)
                    prev_id = obj_id

                point = STPoint(obj_id, float(line[1]), float(line[2]), float(line[3]))
                tmp.points.append(point)

        except Exception as e:
            print(e.message)

        return result
