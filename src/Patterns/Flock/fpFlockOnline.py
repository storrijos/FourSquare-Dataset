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

import src.Patterns.Flock.LCMmaximal as LCMmaximal
import time
import pandas as pd
import numpy
import matplotlib.pyplot as plt
import os, sys
import click
import src.Utils.utils as Utils
import gc
import os.path
from os import path
import math
#Import
from src.Processing.pre_process import ProcessData

class FPFlockOnline(object):
    """ This class is intanced with epsilon, mu and delta"""
    def __init__(self, epsilon, mu, delta):
        self.epsilon = epsilon
        self.mu = mu
        self.delta = delta
        self.df = pd.DataFrame(columns=['keyFlock', 'begin', 'end', 'traj'])  #c
        self.df[['keyFlock','begin', 'end']] = self.df[['keyFlock','begin', 'end']].astype('int32') #c

    def getTransactions(maximalDisks):
        newKey = set()
        oldKey = set()
        for maximal in maximalDisks:
            for member in maximalDisks[maximal].members:
                if not member in traj.keys():
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
        #print('TRAJ')
        #print(traj)
        return traj

    def addNewLine(output_file, keyFlock, begin, end, b):
        with open(output_file, "a") as outputFile:
            #keyFlock, Begin, End, Trajs
            output = str(keyFlock) + " " + str(begin) + " " + str(end) + " " + str(b) + '\n'
            outputFile.write(output)

    def flocks(self, output_file, output1, totalMaximalDisks, keyFlock):
        elements_in_flock_count = 0
        lines = output1.readlines()
        for line in lines:
            #print('LINE : ' + str(line))
            lineSplit = line.split(' ')
            array = list(map(int, lineSplit[:-1]))
            array.sort()
            if len(array) < delta:
                continue
            members = totalMaximalDisks[int(str(array[0]))].members
            begin = totalMaximalDisks[int(str(array[0]))].timestamp
            #print('ELEMENTOS ' + str(members) + ' ' + str(begin))
            end = begin

            for element in range(1, len(array)):
                now = totalMaximalDisks[int(str(array[element]))].timestamp
                #print('NOW: ' + str(now) + 'END ' + str(end))
                if(now == end + 1 or now == end):
                    if(now == end + 1):
                        members = members.intersection(totalMaximalDisks[int(str(array[element]))].members)
                        #print('MEMBERS ' + str(members))
                    end = now
                elif end-begin >= delta - 1:
                    b = list(members)
                    b.sort()
                    #stdin.append('{0}\t{1}\t{2}\t{3}'.format(keyFlock, begin, end, b))
                    elements_in_flock_count += len(b)
                    #print('IMPRIMO2')
                    FPFlockOnline.addNewLine(output_file, keyFlock, begin, end, b)
                    #data = {'keyFlock': keyFlock, 'begin': begin, 'end': end, 'traj': str(b)}  # c
                    #self.df = self.df.append(data, ignore_index=True)  # c

                    keyFlock += 1
                    begin = end = now
                else:
                    begin = end = now

            if end-begin >= delta - 1:
                b = list(members)
                #print('MEMBERS_IMPRS ' + str(b))
                b.sort()
                #print('IMPRIMO3')
                #stdin.append('{0}\t{1}\t{2}\t{3}'.format(keyFlock, begin, end, b))
                FPFlockOnline.addNewLine(output_file, keyFlock, begin, end, b)

                data = {'keyFlock': keyFlock, 'begin': begin, 'end': end, 'traj': str(b)} #c
                self.df = self.df.append(data, ignore_index=True) #c

                elements_in_flock_count += len(b)
                #print('LONGITUD')
                #print(elements_in_flock_count)
                keyFlock += 1

        return stdin, keyFlock, elements_in_flock_count

    def flockFinder(self, filename, output_file, neighbors_output):

        global traj
        global stdin
        global delta
        global keyFlock

        LCMmaximal.epsilon = self.epsilon
        LCMmaximal.mu = self.mu
        delta = self.delta
        LCMmaximal.precision = 0.001

        #print(filename)
        #print(output_file)
        #print(neighbors_output)


        ProcessData.flock_preprocessDataset(self, filename)
        dataset = pd.read_pickle('./FlockID.df')
        #print(dataset)
        #os.chdir(str(os.getcwd()) + '/../Patterns/Flock')

        if os.path.exists('output.mfi'):
            os.system('rm output.mfi')

        t1 = time.time()

        points = LCMmaximal.pointTimestamp(dataset)

        del dataset
        gc.collect()

        timestamps = list(map(int, points.keys()))
        #print('LEN' + str(len(timestamps)))
        #print('timestamps: ' + str(timestamps))
        timestamps.sort()

        keyFlock = 1
        diskID = 1

        traj = {}
        totalMaximalDisks = {}
        stdin = []

        elements_in_flock_count = 0
        flocks_avg = 0
        counter = 0

        original_path = os.path.abspath(os.getcwd())
        curent_file_abs_path = os.path.dirname(os.path.realpath(__file__))
        os.chdir(curent_file_abs_path)

        for timestamp in timestamps:
            output = open('output.dat','w')
            LCMmaximal.disksTimestamp(points, timestamp)
            if not os.path.exists('outputDisk.dat'):
                continue
            maximalDisks, diskID = LCMmaximal.maximalDisksTimestamp(timestamp, diskID)
            totalMaximalDisks.update(maximalDisks)
            traj = FPFlockOnline.getTransactions(maximalDisks)
            counter = counter + 1 + len(traj)
            #Utils.progressBar(counter, len(timestamps), bar_length=20)

            st = ''
            for i in traj:
                if int(len(traj[i])) < self.mu:
                    continue
                st += (str(traj[i])+'\n')
                #print('aqui' + st)
            #print('ST ' + st)
            output.write(st)
            #print(st)
            output.close()

            if os.path.exists('output.dat') and os.path.getsize('output.dat') == 0:
                continue
            os.system("./fim_closed output.dat " + str(LCMmaximal.mu) + " output.mfi > /dev/null")
            if os.path.exists('output.mfi'):
                output1 = open('output.mfi','r')
                output2 = open('output.mfi','r')
                stdin, keyFlock, elems = FPFlockOnline.flocks(self, output_file, output1, totalMaximalDisks, keyFlock)
                elements_in_flock_count += elems
                #print('ELEMENTOS')
                #print(elements_in_flock_count)

        if len(stdin) != 0:
            #print('stdin')
            #print(len(stdin))
            #print ('elements flock')
            #print(elements_in_flock_count)
            flocks_avg = elements_in_flock_count / len(stdin)

        if "partial" not in neighbors_output:
            os.chdir(original_path)
        print(os.getcwd())

        neighbors_classified = self.printFinalResultDataFrame(self.df, neighbors_output) #c

        #self.writeEndOfFile(output_file, 'Flocks_avg: ' + str(flocks_avg)) #c
        #print("Flocks: ", len(stdin))
        flocks = len(stdin)
        t2 = round(time.time()-t1,3)
        #print("\nTime: ", t2)
        #print(neighbors_classified)
        return neighbors_classified, original_path #c

    def dataset_to_list_of_lists(self, dataset):
        result = []
        if not dataset.empty:
            string_list = list(dataset.traj.values)
            for row in string_list:
                row = row.replace("]", "")
                row = row.replace("[", "")
                result.append([int(x) for x in row.split(',')])
        return result

    def deep_search(self, elem, list):

        neighbors = []
        for row in list:
            if elem in row:
                neighbors.append(row)

        flatten = sum(neighbors, [])
        return [(ii, 1.0) for n, ii in enumerate(flatten) if ii not in flatten[:n] and ii != elem]

    def clasify_neighbors(self, list):

        flatten_list = sum(list, [])
        dict = {}

        for elem in flatten_list:
            search = self.deep_search(elem, list)
            if search != None:
                dict[elem] = search
        return dict

    def writeEndOfFile(self, output_file, text):
        with open(output_file, "a") as outputFile:
            outputFile.write(text)

    """
    def dump_to_file(self, neighbors_classified, neighbors_output):
        process = ProcessData()
        final_df = process.dump_to_pandas(neighbors_classified)
        #curent_file_abs_path = os.path.dirname(os.path.realpath(__file__))

        #final_df.to_csv(str(curent_file_abs_path) + "/../../Recommender/" + str(neighbors_output), sep=" ", encoding='utf-8', index=False, header=False)
        os.chdir("../../..")

        final_df.to_csv(neighbors_output, sep=" ", encoding='utf-8', index=False, header=False)
    """
    def printFinalResultDataFrame(self, df, neighbors_output):
        # Remove Duplicates from DataFrame
        if not df.empty:
            df = df.drop_duplicates(subset=['begin', 'end', 'traj']).apply(list)
            #print(df)
            neighbors_classified = self.clasify_neighbors(self.dataset_to_list_of_lists(df))
            process = ProcessData()
            #return self.dump_to_file(neighbors_classified, neighbors_output)
            return process.dump_to_file(neighbors_classified, neighbors_output)

        print('No neighbors')

"""
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
                flock_avg = fp.flockFinder('Datasets/US_NewYork_POIS_Coords_short.txt', output_file)
                FPFlockOnline.printFinalResultDataFrame(fp)

                res.append({"epsilon": epsilon, "mu": mu, "delta": delta, "flock_avg": flock_avg})
                i += 1
                #print('Porcentaje:' + str((i/64)*100) + '%')

    numpy.set_printoptions(threshold=sys.maxsize)
    df = pd.DataFrame(res, columns=['epsilon', 'mu', 'delta', 'flock_avg'])
    #Imprimimos los resultados
    #print(df.to_string())

    FPFlockOnline.writeEndOfFile('df_results.txt', df.to_string())
"""

def calculate_flock(filename, output, epsilon, mu, delta):
    if path.exists(output):
        print('El fichero ' + str(output) + ' ya existe')
        return

    partial_output = (filename.rsplit('.', 1)[0]).rsplit('/', 1)[-1] + '_partial_traj' + '.txt'

    fp = FPFlockOnline(epsilon, mu, delta)

    # partial_output = 'partial.txt'
    _, route = fp.flockFinder(filename, partial_output, output)
    #print(fp.df)
    return route

def plot_x_y_values(df, x_label, y_label):
    df.plot(x=x_label, y=y_label, marker='.')
    plt.show()


@click.command()
@click.option('--filename', default='US_NewYork_POIS_Coords_short.txt', help='Dataset.')
@click.option('--output', default='similarity_output_convoy.txt', help='Output file.')
@click.option('--epsilon', default=0.2, help='Epsilon.')
@click.option('--mu', default=2, help='Mu.')
@click.option('--delta', default=0.2, help='Delta.')

def flock(filename, output, epsilon, mu, delta):
    if path.exists(output):
        print('El fichero ' + str(output) + ' ya existe')
        return
    fp = FPFlockOnline(epsilon,mu,delta)

    partial_output = (filename.rsplit('.', 1)[0]).rsplit('/', 1)[-1] + '_partial_traj' + '.txt'
    #partial_output = 'partial.txt'
    fp.flockFinder(filename, partial_output, output)

#def main():
    #output_file = 'output_prueba.txt' #sys.argv[1]
    #fp = FPFlockOnline(0.2,3,2)
    #fp.flockFinder('Datasets/US_NewYork_POIS_Coords_short.txt', output_file)


    #experimentos()
if __name__ == '__main__':
    flock()
