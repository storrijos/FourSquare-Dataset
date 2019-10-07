#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  fpFlockOnline.py
#  
#  Copyright 2014 Omar Ernesto Cabrera Rosero <omarcabrera@udenar.edu.co>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 3 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#  

import LCMmaximal
import time
import csv
import os
import io
import sys
import pandas as pd
import numpy
import matplotlib.pyplot as plt

class FPFlockOnline(object):
    """ This class is intanced with epsilon, mu and delta"""
    def __init__(self, epsilon, mu, delta):
        self.epsilon = epsilon
        self.mu = mu
        self.delta = delta

    def getTransactions(maximalDisks):
        newKey = set()
        oldKey = set()
        for maximal in maximalDisks:
            for member in maximalDisks[maximal].members:
                if not member  in traj.keys():
                    traj[member]= []
                    traj[member].append(maximalDisks[maximal].id)
                    newKey.add(member)
                else:
                    traj[member].append(maximalDisks[maximal].id)
                    oldKey.add(member)
        keys = set(traj.keys())
        keysToDelete = (keys.difference(oldKey).difference(newKey))
        for key in keysToDelete:
            del traj[key]
        return traj

    def addNewLine(output_file, keyFlock, begin, end, b):
        with open(output_file, "a") as outputFile:
            output = "KeyFlock: " + str(keyFlock) + " Begin: " + str(begin) + " End " + str(end) + ' ' + str(b) + '\n'
            outputFile.write(output)

    def flocks(self, output_file, output1, totalMaximalDisks, keyFlock):
        elements_in_flock_count = 0
        lines = output1.readlines()
        for line in lines:
            lineSplit = line.split(' ')
            array = list(map(int, lineSplit[:-1]))
            array.sort()
            if len(array) < delta:
                continue
            members = totalMaximalDisks[int(str(array[0]))].members
            begin = totalMaximalDisks[int(str(array[0]))].timestamp
            end = begin


            for element in range(1, len(array)):
                now = totalMaximalDisks[int(str(array[element]))].timestamp
                if(now == end + 1 or now == end):
                    if(now == end + 1):
                        members = members.intersection(totalMaximalDisks[int(str(array[element]))].members)
                    end = now
                elif end-begin >= delta - 1:
                    b = list(members)
                    b.sort()
                    stdin.append('{0}\t{1}\t{2}\t{3}'.format(keyFlock, begin, end, b))
                    keyFlock += 1
                    begin = end = now
                else:
                    begin = end = now

            if end-begin >= delta - 1:
                b = list(members)
                b.sort()
                stdin.append('{0}\t{1}\t{2}\t{3}'.format(keyFlock, begin, end, b))
                FPFlockOnline.addNewLine(output_file, keyFlock, begin, end, b)
                elements_in_flock_count = len(b)
                keyFlock += 1
        
        return stdin, keyFlock, elements_in_flock_count

    def preprocessDataset(self, filename):
        dataset = pd.read_csv(filename, delim_whitespace=True, header=None)
        dataset.columns = ["id", "item_id", "latitude", "longitude", "real_timestamp"]
        dataset.sort_values(['id', 'real_timestamp'], ascending=[True, True], inplace=True)
        dataset['timestamp'] = dataset.groupby(['id']).cumcount()
        dataset = dataset.drop(columns=['item_id'])
        return dataset

    def flockFinder(self, filename, output_file):
        global traj
        global stdin
        global delta
        global keyFlock
               
        LCMmaximal.epsilon = self.epsilon
        LCMmaximal.mu = self.mu
        delta = self.delta
        LCMmaximal.precision = 0.001

        dataset = FPFlockOnline.preprocessDataset(self, filename)

        if os.path.exists('output.mfi'):
            os.system('rm output.mfi')

        t1 = time.time()

        points = LCMmaximal.pointTimestamp(dataset)

        timestamps = list(map(int, points.keys()))
        timestamps.sort()

        keyFlock = 1
        diskID = 1

        traj = {}
        totalMaximalDisks = {}
        stdin = []

        elements_in_flock_count = 0
        flocks_avg = 0
        for timestamp in timestamps:
            output = open('output.dat','w')
            LCMmaximal.disksTimestamp(points, timestamp)
            if not os.path.exists('outputDisk.dat'):
                continue

            maximalDisks, diskID = LCMmaximal.maximalDisksTimestamp(timestamp, diskID)
            totalMaximalDisks.update(maximalDisks)
             
            traj = FPFlockOnline.getTransactions(maximalDisks)
            
            st = ''                     
            for i in traj:
                if len(traj[i]) < delta:
                    continue
                st += (str(traj[i])+'\n')
            output.write(st)
                
            output.close()

            if os.path.getsize('output.dat') == 0:
                continue

            os.system("./fim_closed output.dat " + str(LCMmaximal.mu) + " output.mfi > /dev/null")
                          
            if os.path.exists('output.mfi'):
                output1 = open('output.mfi','r')				   
                stdin, keyFlock, elems = FPFlockOnline.flocks(self, output_file, output1, totalMaximalDisks, keyFlock)
                elements_in_flock_count += elems

        if len(stdin) != 0:
            flocks_avg = elements_in_flock_count / len(stdin)
        writeEndOfFile(output_file, 'Flocks_avg: ' + str(flocks_avg))
        print("Flocks: ", len(stdin))
        flocks = len(stdin)
        t2 = round(time.time()-t1,3)
        print("\nTime: ", t2)
        return flocks_avg

def writeEndOfFile(output_file, text):
    with open(output_file, "a") as outputFile:
        outputFile.write(text)

def experimentos():
    min_mu = 2
    max_mu = 10
    min_delta = 2
    max_delta = 10
    min_epsilon = 0.01
    max_epsilon = 0.21
    i = 0

    res = []

    for epsilon in numpy.arange(min_epsilon, max_epsilon, 0.05):
        for mu in numpy.arange(min_mu, max_mu, 2):
            for delta in numpy.arange(min_delta, max_delta, 2):
                output_file = 'Experiments/experimento_' + str(i) + '.txt'
                fp = FPFlockOnline(epsilon, mu, delta)
                flock_avg = fp.flockFinder('Datasets/US_NewYork_POIS_Coords_short_10k.txt', output_file)
                res.append({"epsilon": epsilon, "mu": mu, "delta": delta, "flock_avg": flock_avg})
                i += 1
                print('Porcentaje:' + str((i/64)*100) + '%')

    numpy.set_printoptions(threshold=sys.maxsize)
    df = pd.DataFrame(res, columns=['epsilon', 'mu', 'delta', 'flock_avg'])

    #Imprimimos los resultados
    #print(df.to_string())

    writeEndOfFile('df_results.txt', df.to_string())


#plot_x_y_values(df, 'flock_avg', 'epsilon')
    #plot_x_y_values(df, 'flock_avg', 'mu')
    #plot_x_y_values(df, 'flock_avg', 'delta')

def plot_x_y_values(df, x_label, y_label):
    df.plot(x=x_label, y=y_label, marker='.')
    plt.show()

def main():
    #output_file = sys.argv[1]
    #fp = FPFlockOnline(0.2,3,2)
    #fp.flockFinder('Datasets/US_NewYork_POIS_Coords_short.txt', output_file)

    experimentos()
if __name__ == '__main__':
    main()